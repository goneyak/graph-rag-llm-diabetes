#!/usr/bin/env node

/**
 * Script to load environment variables from .env files for frontend development
 * 
 * This script loads environment variables from:
 * 1. Root .env file
 * 2. Frontend package .env file
 * 
 * Usage:
 * node load-env.js npm start
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// Paths to .env files
const rootEnvPath = path.resolve(__dirname, '../../.env');
const frontendEnvPath = path.resolve(__dirname, './.env');

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
  
  // Check if frontend .env file exists
  if (fs.existsSync(frontendEnvPath)) {
    console.log(`Loading frontend .env from ${frontendEnvPath}`);
    const frontendEnv = dotenv.parse(fs.readFileSync(frontendEnvPath));
    
    // Process variables with ${VAR} syntax
    const processedEnv = {};
    Object.entries(frontendEnv).forEach(([key, value]) => {
      // Replace ${VAR} with process.env.VAR
      const processedValue = value.replace(/\${([^}]+)}/g, (_, varName) => {
        return process.env[varName] || '';
      });
      
      process.env[key] = processedValue;
      processedEnv[key] = processedValue;
      console.log(`Set ${key}=${processedValue}`);
    });
  } else {
    console.warn('Frontend .env file not found');
  }
  
  console.log('Environment variables loaded successfully');
}

// Execute the command with the loaded environment variables
function executeCommand(args) {
  console.log(`Executing: ${args.join(' ')}`);
  
  const child = spawn(args[0], args.slice(1), { 
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
    console.error('No command provided');
    console.log('Usage: node load-env.js <command>');
    console.log('Example: node load-env.js npm start');
    process.exit(1);
  }
  
  // Execute the command
  executeCommand(args);
}

// Run the main function
main();
