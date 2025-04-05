#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { GraphProcessingStack } from './stacks/graph-processing-stack';
import { FrontendStack } from './stacks/frontend-stack';

// Create the CDK app
const app = new cdk.App({
  context: {
    environment: process.env.ENVIRONMENT || 'dev',
    neptune: {
      instanceType: process.env.NEPTUNE_INSTANCE_TYPE || 'db.t3.medium',
      engineVersion: process.env.NEPTUNE_ENGINE_VERSION || '1.2.0.0',
    },
    s3: {
      graphDataBucketName: process.env.S3_GRAPH_DATA_BUCKET_NAME,
      websiteBucketName: process.env.S3_WEBSITE_BUCKET_NAME,
    },
    cloudfront: {
      priceClass: process.env.CLOUDFRONT_PRICE_CLASS || 'PriceClass_100',
    }
  }
});

// Define environment from process.env
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'eu-west-1',
  // Add AWS profile configuration
  profile: process.env.AWS_PROFILE || 'default',
};

console.log(`Using AWS profile: ${env.profile}`);

// Log the context values
console.log('Deploying with context:', JSON.stringify(app.node.tryGetContext('environment'), null, 2));

// Create the backend stack for graph processing
const graphProcessingStack = new GraphProcessingStack(app, 'GraphProcessingStack', { env });

// Create the frontend stack for the React application
const frontendStack = new FrontendStack(app, 'FrontendStack', { env });

app.synth();
