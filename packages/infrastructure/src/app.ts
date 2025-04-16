#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { GraphProcessingStack } from './stacks/graph-processing-stack';
import { FrontendStack } from './stacks/frontend-stack';
import { ChatApiStack } from './stacks/chat-api-stack';

// Create the CDK app
const app = new cdk.App();

// Define environment from process.env
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'eu-west-1',
};

// Define configuration
const environment = process.env.ENVIRONMENT || 'dev';
const neptuneConfig = {
  instanceType: process.env.NEPTUNE_INSTANCE_TYPE || 'db.t3.medium',
  engineVersion: process.env.NEPTUNE_ENGINE_VERSION || '1.2.0.0',
};
const s3Config = {
  graphDataBucketName: process.env.S3_GRAPH_DATA_BUCKET_NAME,
  websiteBucketName: process.env.S3_WEBSITE_BUCKET_NAME,
  medicalDataBucketName: process.env.S3_MEDICAL_DATA_BUCKET_NAME,
};
const cloudfrontConfig = {
  priceClass: process.env.CLOUDFRONT_PRICE_CLASS || 'PriceClass_100',
};

console.log(`Using AWS profile: ${process.env.AWS_PROFILE || 'default'}`);
console.log('Deploying with environment:', environment);

// Create the backend stack for graph processing
const graphProcessingStack = new GraphProcessingStack(app, 'GraphProcessingStack', {
  env,
  environment,
  neptuneConfig,
  s3Config,
} as any);

// Create the chat API stack
const chatApiStack = new ChatApiStack(app, 'ChatApiStack', {
  env,
  environment,
} as any);

// Create the frontend stack for the React application
const frontendStack = new FrontendStack(app, 'FrontendStack', { 
  env,
  environment,
  s3Config,
  cloudfrontConfig,
  apiEndpoint: chatApiStack.apiEndpoint,
} as any);

// Add dependency to ensure the API is deployed before the frontend
frontendStack.addDependency(chatApiStack);

app.synth();
