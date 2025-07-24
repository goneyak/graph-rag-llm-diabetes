#!/usr/bin/env node

/**
 * Script to load environment variables from .env files for CDK deployment
 * 
 * This script loads environment variables from:
 * 1. Root .env file
 * 2. Infrastructure package .env file
 * 
 * Usage:
 * node load-env.js cdk deploy
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// Paths to .env files
const rootEnvPath = path.resolve(__dirname, '../../.env');
const infraEnvPath = path.resolve(__dirname, './.env');

// Load environment variables from .env files
function loadEnvFiles() {
  console.log('Loading environment variables...');
  
  // Check if root .env file exists
  if (fs.existsSync(rootEnvPath)) {
    console.log(`Loading root .env from ${rootEnvPath}`);
    const rootEnv = dotenv.parse(fs.readFileSync(rootEnvPath));
    
    // Set environment variables from root .env
    Object.entries(rootEnv).forEach(([key, value]) => {
      process.env[key] = value;
      console.log(`Set ${key}=${value}`);
    });
  } else {
    console.warn('Root .env file not found');
  }
  
  // Check if infrastructure .env file exists
  if (fs.existsSync(infraEnvPath)) {
    console.log(`Loading infrastructure .env from ${infraEnvPath}`);
    const infraEnv = dotenv.parse(fs.readFileSync(infraEnvPath));
    
    // Process variables with ${VAR} syntax
    const processedEnv = {};
    Object.entries(infraEnv).forEach(([key, value]) => {
      // Replace ${VAR} with process.env.VAR
      const processedValue = value.replace(/\${([^}]+)}/g, (_, varName) => {
        return process.env[varName] || '';
      });
      
      process.env[key] = processedValue;
      processedEnv[key] = processedValue;
      console.log(`Set ${key}=${processedValue}`);
    });
  } else {
    console.warn('Infrastructure .env file not found');
  }
  
  console.log('Environment variables loaded successfully');
}

// Execute the CDK command with the loaded environment variables
function executeCommand(args) {
  console.log(`Executing: cdk ${args.join(' ')}`);
  
  const child = spawn('cdk', args, { 
    stdio: 'inherit',
    env: process.env
  });
  
  child.on('close', (code) => {
    process.exit(code);
  });
}

// Main function
function main() {
  // Load environment variables
  loadEnvFiles();
  
  // Get command line arguments (excluding node and script name)
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('No CDK command provided');
    console.log('Usage: node load-env.js <cdk command>');
    console.log('Example: node load-env.js deploy');
    process.exit(1);
  }
  
  // Execute the CDK command
  executeCommand(args);
}

// Run the main function
main();
