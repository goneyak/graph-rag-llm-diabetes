#!/usr/bin/env python3
"""
Local test script for the Lambda function.
This script simulates an S3 event and calls the Lambda handler locally.

Usage:
    python local_test.py [json|csv]

Arguments:
    json|csv - The format of the sample file to use (default: json)
"""

import sys
import os
import json
from index import handler

def create_s3_event(file_key):
    """Create a mock S3 event"""
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "eu-west-1",
                "eventTime": "2023-01-01T12:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "bucket": {
                        "name": "mock-bucket",
                        "arn": "arn:aws:s3:::mock-bucket"
                    },
                    "object": {
                        "key": file_key,
                        "size": 1024,
                        "eTag": "mock-etag"
                    }
                }
            }
        ]
    }

class MockContext:
    """Mock Lambda context object"""
    def __init__(self):
        self.function_name = "local-test"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:eu-west-1:123456789012:function:local-test"
        self.aws_request_id = "mock-request-id-12345"

class MockS3Client:
    """Mock S3 client for local testing"""
    def get_object(self, Bucket, Key):
        """Mock get_object method"""
        print(f"Mock S3 get_object: {Bucket}/{Key}")
        
        # Determine which sample file to use
        if Key.endswith('.json'):
            file_path = 'sample-graph.json'
        elif Key.endswith('.csv'):
            file_path = 'sample-graph.csv'
        else:
            file_path = 'sample-graph.json'
        
        # Read the sample file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Create a mock response object with a read method
        class MockBody:
            def read(self):
                return content.encode('utf-8')
        
        return {
            'Body': MockBody(),
            'ContentLength': len(content),
            'ContentType': 'application/json' if Key.endswith('.json') else 'text/csv'
        }

def mock_neptune_connection():
    """Mock the Neptune connection for local testing"""
    print("This is a local test. No actual connection to Neptune will be made.")
    print("The Neptune connection code will be skipped in this test.")
    
    # Patch the insert_into_neptune function to print instead of connecting to Neptune
    import index
    original_insert = index.insert_into_neptune
    
    def mock_insert(nodes, edges):
        print(f"\n--- MOCK NEPTUNE INSERT ---")
        print(f"Would insert {len(nodes)} nodes and {len(edges)} edges into Neptune")
        print("\nNodes sample (up to 3):")
        for node in nodes[:3]:
            print(f"  - {node}")
        
        print("\nEdges sample (up to 3):")
        for edge in edges[:3]:
            print(f"  - {edge}")
        print("--- END MOCK INSERT ---\n")
        
    index.insert_into_neptune = mock_insert

def main():
    # Determine which file format to use
    file_format = 'json'
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'csv':
        file_format = 'csv'
    
    # Set up mock environment
    os.environ['NEPTUNE_ENDPOINT'] = 'localhost'
    os.environ['NEPTUNE_PORT'] = '8182'
    
    # Create mock objects
    mock_neptune_connection()
    
    # Replace the S3 client with our mock
    import index
    index.s3_client = MockS3Client()
    
    # Create a mock event
    event = create_s3_event(f"test-graph.{file_format}")
    context = MockContext()
    
    print(f"\n=== Testing Lambda handler with {file_format.upper()} sample data ===\n")
    
    # Call the handler
    response = handler(event, context)
    
    # Print the response
    print("\n=== Lambda Response ===")
    print(json.dumps(response, indent=2))
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
