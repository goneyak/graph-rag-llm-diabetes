import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';

export interface ChatApiStackProps extends cdk.StackProps {
  environment: string;
}

export class ChatApiStack extends cdk.Stack {
  public readonly apiEndpoint: string;

  constructor(scope: Construct, id: string, props: ChatApiStackProps) {
    super(scope, id, props);

    // Get environment values from props
    const { environment } = props;

    // Create the Lambda function for the chat API
    const chatLambda = new lambda.Function(this, 'ChatLambdaFunction', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'chat_handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../../packages/lambda/src')),
      environment: {
        ENVIRONMENT: environment,
        LOG_LEVEL: 'INFO',
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
    });

    // Create an API Gateway REST API
    const api = new apigateway.RestApi(this, 'ChatApi', {
      restApiName: `chat-api-${environment}`,
      description: 'API Gateway for the chat service',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'Authorization'],
        allowCredentials: true,
      },
      deployOptions: {
        stageName: environment,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
      },
    });

    // Create a resource and method for the chat endpoint
    const chatResource = api.root.addResource('chat');
    
    // Add POST method
    chatResource.addMethod('POST', new apigateway.LambdaIntegration(chatLambda, {
      proxy: true,
    }));

    // Store the API endpoint URL
    this.apiEndpoint = `${api.url}chat`;

    // Output the API endpoint
    new cdk.CfnOutput(this, 'ChatApiEndpoint', {
      value: this.apiEndpoint,
      description: 'The endpoint URL of the Chat API',
      exportName: `ChatApiEndpoint-${environment}`,
    });
  }
}
