#!/usr/bin/env python3
"""
Script to load environment variables from .env files for local testing

This script loads environment variables from:
1. Root .env file
2. Lambda package .env file

Usage:
python load_env.py python local_test.py
"""

import os
import sys
import subprocess
from pathlib import Path
import re

def load_env_file(file_path):
    """Load environment variables from a .env file"""
    if not file_path.exists():
        print(f"Warning: .env file not found at {file_path}")
        return {}
    
    print(f"Loading .env file from {file_path}")
    env_vars = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            env_vars[key] = value
    
    return env_vars

def process_env_vars(env_vars, existing_vars=None):
    """Process environment variables, resolving ${VAR} references"""
    if existing_vars is None:
        existing_vars = {}
    
    processed_vars = {}
    
    for key, value in env_vars.items():
        # Replace ${VAR} with existing_vars[VAR] or os.environ[VAR]
        def replace_var(match):
            var_name = match.group(1)
            return existing_vars.get(var_name, os.environ.get(var_name, ''))
        
        processed_value = re.sub(r'\${([^}]+)}', replace_var, value)
        processed_vars[key] = processed_value
        
    return processed_vars

def main():
    """Main function"""
    # Get paths to .env files
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    root_env_path = root_dir / '.env'
    lambda_env_path = root_dir / 'packages' / 'lambda' / '.env'
    
    # Load root .env file
    root_env_vars = load_env_file(root_env_path)
    
    # Set environment variables from root .env
    for key, value in root_env_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")
    
    # Load lambda .env file
    lambda_env_vars = load_env_file(lambda_env_path)
    
    # Process and set environment variables from lambda .env
    processed_vars = process_env_vars(lambda_env_vars, root_env_vars)
    for key, value in processed_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")
    
    print("Environment variables loaded successfully")
    
    # Get command line arguments (excluding script name)
    args = sys.argv[1:]
    
    if not args:
        print("No command provided")
        print("Usage: python load_env.py <command>")
        print("Example: python load_env.py python local_test.py")
        sys.exit(1)
    
    # Execute the command with the loaded environment variables
    print(f"Executing: {' '.join(args)}")
    result = subprocess.run(args, env=os.environ)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
