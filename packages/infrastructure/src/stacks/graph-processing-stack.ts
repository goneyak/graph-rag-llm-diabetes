import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as neptune from 'aws-cdk-lib/aws-neptune';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';

export class GraphProcessingStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Get environment values from context
    const environment = this.node.tryGetContext('environment') || 'dev';
    const neptuneConfig = this.node.tryGetContext('neptune') || {};
    const s3Config = this.node.tryGetContext('s3') || {};

    // Create a VPC for Neptune
    const vpc = new ec2.Vpc(this, 'NeptuneVPC', {
      maxAzs: 2,
      natGateways: 1
    });

    // Create Neptune Cluster
    const neptuneSubnetGroup = new neptune.CfnDBSubnetGroup(this, 'NeptuneSubnetGroup', {
      dbSubnetGroupDescription: 'Subnet group for Neptune DB',
      subnetIds: vpc.privateSubnets.map(subnet => subnet.subnetId),
    });

    // Create Neptune Security Group
    const neptuneSecurityGroup = new ec2.SecurityGroup(this, 'NeptuneSecurityGroup', {
      vpc,
      description: 'Security group for Neptune DB',
      allowAllOutbound: true,
    });

    // Allow inbound connections on Neptune port
    neptuneSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(8182),
      'Allow Neptune traffic'
    );

    // Create Neptune Cluster
    const neptuneCluster = new neptune.CfnDBCluster(this, 'NeptuneCluster', {
      dbSubnetGroupName: neptuneSubnetGroup.ref,
      vpcSecurityGroupIds: [neptuneSecurityGroup.securityGroupId],
      dbClusterIdentifier: `graph-processor-cluster-${environment}`,
      engineVersion: neptuneConfig.engineVersion || '1.2.0.0',
    });

    // Create Neptune Instance
    const neptuneInstance = new neptune.CfnDBInstance(this, 'NeptuneInstance', {
      dbInstanceClass: neptuneConfig.instanceType || 'db.t3.medium',
      dbClusterIdentifier: neptuneCluster.ref,
      availabilityZone: vpc.availabilityZones[0],
    });
    neptuneInstance.addDependsOn(neptuneCluster);

    // Create S3 bucket for graph data
    const bucketName = s3Config.graphDataBucketName || `graph-data-${environment}-${this.account}`;
    const graphDataBucket = new s3.Bucket(this, 'GraphDataBucket', {
      bucketName: bucketName,
      versioned: true,
      removalPolicy: environment === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: environment !== 'prod', // Only auto-delete in non-prod environments
    });

    // Define the Python Lambda function
    const graphProcessorLambda = new lambda.Function(this, 'GraphProcessorLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../../packages/lambda/src')),
      environment: {
        ENVIRONMENT: environment,
        NEPTUNE_ENDPOINT: neptuneCluster.attrEndpoint,
        NEPTUNE_PORT: '8182',
      },
      timeout: cdk.Duration.seconds(300), // Increased timeout for graph processing
      memorySize: 512, // Increased memory for graph processing
      vpc: vpc, // Place Lambda in the same VPC as Neptune
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [neptuneSecurityGroup],
    });

    // Grant Lambda permissions to access S3 bucket
    graphDataBucket.grantReadWrite(graphProcessorLambda);

    // Grant Lambda permissions to access Neptune
    graphProcessorLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          'neptune-db:*'
        ],
        resources: [`arn:aws:neptune-db:${this.region}:${this.account}:${neptuneCluster.attrClusterResourceId}/*`],
      })
    );

    // Configure S3 event notification to trigger Lambda
    graphDataBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(graphProcessorLambda)
    );

    // Output the Lambda function ARN
    new cdk.CfnOutput(this, 'LambdaFunctionArn', {
      value: graphProcessorLambda.functionArn,
      description: 'The ARN of the Graph Processor Lambda function',
      exportName: `GraphProcessorLambdaArn-${environment}`,
    });

    // Output the S3 bucket name
    new cdk.CfnOutput(this, 'GraphDataBucketName', {
      value: graphDataBucket.bucketName,
      description: 'The name of the S3 bucket for graph data',
      exportName: `GraphDataBucketName-${environment}`,
    });

    // Output the Neptune endpoint
    new cdk.CfnOutput(this, 'NeptuneEndpoint', {
      value: neptuneCluster.attrEndpoint,
      description: 'The endpoint of the Neptune cluster',
      exportName: `NeptuneEndpoint-${environment}`,
    });
  }
}
