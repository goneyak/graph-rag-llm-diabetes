#!/usr/bin/env python3
"""
Direct Neptune Loader

This script loads Gremlin queries directly into Neptune without using S3.
It reads the queries from a file and executes them one by one using the Gremlin client.
"""

import argparse
import time
import sys
from gremlin_python.driver import client
from gremlin_python.driver.protocol import GremlinServerError
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import boto3

creds = boto3.Session().get_credentials().get_frozen_credentials()

def load_queries(file_path):
    """Load Gremlin queries from a file"""
    try:
        with open(file_path, 'r') as f:
            # Read all lines and filter out empty lines
            queries = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(queries)} queries from {file_path}")
        return queries
    except Exception as e:
        print(f"Error loading queries: {e}")
        return []

def connect_to_neptune(endpoint):
    """Connect to Neptune and return a client"""
    try:
        request = AWSRequest(method="GET", url=endpoint, data=None)
        SigV4Auth(creds, "neptune-db", boto3.Session().region_name).add_auth(request)

        # Create a connection to Neptune
        neptune_client = client.Client(endpoint, 'g', headers=request.headers.items())
        print(f"Connected to Neptune at {endpoint}")
        return neptune_client
    except Exception as e:
        print(f"Error connecting to Neptune: {e}")
        return None

def execute_queries(neptune_client, queries, batch_size=100, retry_count=3, retry_delay=5):
    """Execute queries in Neptune"""
    total_queries = len(queries)
    successful = 0
    failed = 0
    
    print(f"Executing {total_queries} queries in batches of {batch_size}...")
    
    # Process queries in batches
    for i in range(0, total_queries, batch_size):
        batch = queries[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(total_queries + batch_size - 1)//batch_size} ({len(batch)} queries)")
        
        for j, query in enumerate(batch):
            query_num = i + j + 1
            retries = 0
            success = False
            
            while retries < retry_count and not success:
                try:
                    # Execute the query
                    result = neptune_client.submit(query).all().result()
                    successful += 1
                    success = True
                    
                    # Print progress
                    if query_num % 10 == 0 or query_num == total_queries:
                        print(f"Progress: {query_num}/{total_queries} ({successful} successful, {failed} failed)")
                        
                except GremlinServerError as e:
                    retries += 1
                    if retries < retry_count:
                        print(f"Error executing query {query_num}, retrying in {retry_delay} seconds... ({retries}/{retry_count})")
                        print(f"Query: {query[:100]}...")
                        print(f"Error: {e}")
                        time.sleep(retry_delay)
                    else:
                        print(f"Failed to execute query {query_num} after {retry_count} retries")
                        print(f"Query: {query[:100]}...")
                        print(f"Error: {e}")
                        failed += 1
                        
                except Exception as e:
                    print(f"Unexpected error executing query {query_num}: {e}")
                    print(f"Query: {query[:100]}...")
                    failed += 1
                    break
    
    print(f"\nExecution complete: {successful} successful, {failed} failed")
    return successful, failed

def main():
    parser = argparse.ArgumentParser(description='Load Gremlin queries directly into Neptune')
    parser.add_argument('--input', default='neptune_gremlin_queries.txt', help='Input Gremlin queries file')
    parser.add_argument('--endpoint', required=True, help='Neptune endpoint (e.g., wss://your-neptune-endpoint:8182/gremlin)')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of queries to execute in a batch')
    parser.add_argument('--retry-count', type=int, default=3, help='Number of retries for failed queries')
    parser.add_argument('--retry-delay', type=int, default=5, help='Delay in seconds between retries')
    args = parser.parse_args()
    
    # Load queries
    queries = load_queries(args.input)
    if not queries:
        print("No queries to execute. Exiting.")
        sys.exit(1)
    
    # Connect to Neptune
    neptune_client = connect_to_neptune(args.endpoint)
    if not neptune_client:
        print("Failed to connect to Neptune. Exiting.")
        sys.exit(1)
    
    # Execute queries
    try:
        successful, failed = execute_queries(
            neptune_client, 
            queries, 
            batch_size=args.batch_size,
            retry_count=args.retry_count,
            retry_delay=args.retry_delay
        )
        
        # Print summary
        print("\nSummary:")
        print(f"Total queries: {len(queries)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\nSome queries failed. Check the logs for details.")
            sys.exit(1)
        else:
            print("\nAll queries executed successfully.")
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user. Exiting.")
        sys.exit(1)
    finally:
        # Close the connection
        if neptune_client:
            neptune_client.close()
            print("Connection to Neptune closed.")

if __name__ == "__main__":
    main()
