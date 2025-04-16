import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';

export interface FrontendStackProps extends cdk.StackProps {
  environment: string;
  s3Config: {
    websiteBucketName?: string;
  };
  cloudfrontConfig: {
    priceClass?: string;
  };
  apiEndpoint: string;
}

export class FrontendStack extends cdk.Stack {
  public readonly cloudfrontDistribution: cloudfront.Distribution;
  public readonly websiteBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    // Get environment values from props
    const { environment, s3Config, cloudfrontConfig, apiEndpoint } = props;

    // Create an S3 bucket for the website
    const bucketName = s3Config.websiteBucketName || `graph-app-website-${environment}-${this.account}`;
    this.websiteBucket = new s3.Bucket(this, 'WebsiteBucket', {
      bucketName: bucketName,
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'index.html', // SPA routing support
      publicReadAccess: false, // We'll use CloudFront for access
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: environment === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: environment !== 'prod', // Only auto-delete in non-prod environments
    });

    // Create an Origin Access Identity for CloudFront
    const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OriginAccessIdentity', {
      comment: `Allow CloudFront to access the website bucket for ${environment}`,
    });

    // Grant read permissions to CloudFront
    this.websiteBucket.addToResourcePolicy(
      new iam.PolicyStatement({
        actions: ['s3:GetObject'],
        resources: [this.websiteBucket.arnForObjects('*')],
        principals: [
          new iam.CanonicalUserPrincipal(
            originAccessIdentity.cloudFrontOriginAccessIdentityS3CanonicalUserId
          ),
        ],
      })
    );

    // Determine price class from config
    let priceClass = cloudfront.PriceClass.PRICE_CLASS_100; // Default to lowest cost
    if (cloudfrontConfig.priceClass === 'PriceClass_200') {
      priceClass = cloudfront.PriceClass.PRICE_CLASS_200;
    } else if (cloudfrontConfig.priceClass === 'PriceClass_ALL') {
      priceClass = cloudfront.PriceClass.PRICE_CLASS_ALL;
    }

    // Create a CloudFront distribution
    this.cloudfrontDistribution = new cloudfront.Distribution(this, 'Distribution', {
      defaultRootObject: 'index.html',
      priceClass: priceClass,
      defaultBehavior: {
        origin: new origins.S3Origin(this.websiteBucket, {
          originAccessIdentity,
        }),
        compress: true,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
      },
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html', // For SPA routing
        },
      ],
    });

    // Deploy the website to S3 with environment variables
    new s3deploy.BucketDeployment(this, 'DeployWebsite', {
      sources: [
        s3deploy.Source.asset(path.join(__dirname, '../../../../packages/frontend/build')),
        s3deploy.Source.jsonData('runtime-config.json', {
          apiEndpoint: apiEndpoint || 'https://api.example.com/dev/chat',
        }),
      ],
      destinationBucket: this.websiteBucket,
      distribution: this.cloudfrontDistribution,
      distributionPaths: ['/*'],
    });
    
    // Output the API endpoint
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: apiEndpoint,
      description: 'The API endpoint for the chat service',
      exportName: `ApiEndpoint-${environment}`,
    });

    // Output the CloudFront URL
    new cdk.CfnOutput(this, 'CloudFrontURL', {
      value: `https://${this.cloudfrontDistribution.distributionDomainName}`,
      description: 'The URL of the CloudFront distribution',
      exportName: `CloudFrontURL-${environment}`,
    });

    // Output the S3 bucket name
    new cdk.CfnOutput(this, 'WebsiteBucketName', {
      value: this.websiteBucket.bucketName,
      description: 'The name of the S3 bucket hosting the website',
      exportName: `WebsiteBucketName-${environment}`,
    });
  }
}
