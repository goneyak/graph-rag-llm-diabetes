#!/usr/bin/env python3
"""
Local HTTP Server for Lambda Functions

This script sets up a local HTTP server that simulates API Gateway and serves
the Lambda functions locally. It loads the unified_diabetes_graph.json file
into memory and makes it available to the Lambda handlers.

Usage:
    python local_http_server.py [--port PORT]

Arguments:
    --port PORT - The port to run the server on (default: 3001)
"""

import argparse
import json
import logging
import os
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import Lambda handlers
import index
import chat_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('local_http_server')

# Global variable to store the graph data
GRAPH_DATA = None

# Make graph data available to chat_handler
chat_handler.GRAPH_DATA = GRAPH_DATA

class MockContext:
    """Mock Lambda context object"""
    def __init__(self):
        self.function_name = "local-test"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:eu-west-1:123456789012:function:local-test"
        self.aws_request_id = "mock-request-id-12345"

class LocalHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for local testing"""
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set the response headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self._set_headers()
        self.wfile.write(b'')
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        
        if path == '/health':
            # Health check endpoint
            self._set_headers()
            response = {'status': 'healthy', 'timestamp': time.time()}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/graph':
            # Return the graph data
            self._set_headers()
            if GRAPH_DATA:
                # Optionally limit the response size
                limit = int(query.get('limit', [100])[0])
                nodes = GRAPH_DATA.get('nodes', [])[:limit]
                edges = GRAPH_DATA.get('edges', [])[:limit]
                response = {
                    'nodes': nodes,
                    'edges': edges,
                    'totalNodes': len(GRAPH_DATA.get('nodes', [])),
                    'totalEdges': len(GRAPH_DATA.get('edges', [])),
                    'limit': limit
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'Graph data not loaded'}).encode())
                
        else:
            # Unknown endpoint
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request_body = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
            return
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/chat':
            # Call the chat handler
            event = {
                'body': json.dumps(request_body),
                'httpMethod': 'POST',
                'path': '/api/chat',
                'headers': dict(self.headers),
                'queryStringParameters': {},
                'pathParameters': {},
                'requestContext': {
                    'identity': {
                        'sourceIp': self.client_address[0]
                    }
                }
            }
            
            # Call the Lambda handler
            context = MockContext()
            response = chat_handler.handler(event, context)
            
            # Return the response
            self._set_headers(response.get('statusCode', 200))
            self.wfile.write(response.get('body', '{}').encode())
            
        elif path == '/api/graph/query':
            # Process graph query
            if not GRAPH_DATA:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'Graph data not loaded'}).encode())
                return
            
            # Example query processing
            query_type = request_body.get('type', '')
            query_params = request_body.get('params', {})
            
            if query_type == 'findNodes':
                # Find nodes by type
                node_type = query_params.get('type', '')
                nodes = [n for n in GRAPH_DATA.get('nodes', []) if n.get('label') == node_type]
                self._set_headers()
                self.wfile.write(json.dumps({'nodes': nodes}).encode())
                
            elif query_type == 'findConnections':
                # Find connections for a node
                node_id = query_params.get('nodeId', '')
                connections = []
                
                # Find all edges connected to this node
                for edge in GRAPH_DATA.get('edges', []):
                    if edge.get('source') == node_id or edge.get('target') == node_id:
                        connections.append(edge)
                
                self._set_headers()
                self.wfile.write(json.dumps({'connections': connections}).encode())
                
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Unknown query type'}).encode())
        
        elif path == '/api/graph/upload':
            # Simulate S3 upload and processing
            # Create a mock S3 event
            event = {
                "Records": [
                    {
                        "eventSource": "aws:s3",
                        "s3": {
                            "bucket": {
                                "name": "mock-bucket"
                            },
                            "object": {
                                "key": "mock-upload.json"
                            }
                        }
                    }
                ]
            }
            
            # Mock the S3 client to return our graph data
            class MockS3Client:
                def get_object(self, Bucket, Key):
                    class MockBody:
                        def read(self):
                            return json.dumps(GRAPH_DATA).encode('utf-8')
                    return {'Body': MockBody()}
            
            # Replace the S3 client
            original_s3_client = index.s3_client
            index.s3_client = MockS3Client()
            
            # Mock the Neptune connection
            original_insert = index.insert_into_neptune
            
            def mock_insert(nodes, edges):
                logger.info(f"Mock Neptune insert: {len(nodes)} nodes, {len(edges)} edges")
                return True
            
            index.insert_into_neptune = mock_insert
            
            try:
                # Call the Lambda handler
                context = MockContext()
                response = index.handler(event, context)
                
                # Return the response
                self._set_headers(response.get('statusCode', 200))
                self.wfile.write(json.dumps(response).encode())
            finally:
                # Restore original functions
                index.s3_client = original_s3_client
                index.insert_into_neptune = original_insert
        
        else:
            # Unknown endpoint
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

def load_graph_data(file_path):
    """
    Load the graph data from the JSON file
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: The graph data
    """
    logger.info(f"Loading graph data from {file_path}")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        num_nodes = len(data.get('nodes', []))
        num_edges = len(data.get('edges', []))
        logger.info(f"Loaded {num_nodes} nodes and {num_edges} edges")
        return data
    except Exception as e:
        logger.error(f"Error loading graph data: {str(e)}")
        return None

def run_server(port):
    """
    Run the HTTP server
    
    Args:
        port (int): The port to run the server on
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, LocalHTTPHandler)
    logger.info(f"Starting server on port {port}")
    logger.info(f"API endpoints:")
    logger.info(f"  - GET  /health")
    logger.info(f"  - GET  /api/graph")
    logger.info(f"  - POST /api/chat")
    logger.info(f"  - POST /api/graph/query")
    logger.info(f"  - POST /api/graph/upload")
    httpd.serve_forever()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run a local HTTP server for Lambda functions')
    parser.add_argument('--port', type=int, default=3001, help='Port to run the server on')
    parser.add_argument('--graph-file', type=str, default='unified_diabetes_graph.json', 
                        help='Path to the graph data file')
    args = parser.parse_args()
    
    # Set environment variables for the Lambda functions
    os.environ['NEPTUNE_ENDPOINT'] = 'localhost'
    os.environ['NEPTUNE_PORT'] = '8182'
    
    # Load the graph data from the unified JSON graph file
    global GRAPH_DATA
    GRAPH_DATA = load_graph_data(args.graph_file)
    
    if not GRAPH_DATA:
        logger.error(f"Failed to load graph data from {args.graph_file}")
        logger.info("Attempting to load from default locations...")
        
        # Try to load from common locations
        potential_paths = [
            'unified_diabetes_graph.json',
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                logger.info(f"Found graph file at {path}")
                GRAPH_DATA = load_graph_data(path)
                if GRAPH_DATA:
                    break
        
        if not GRAPH_DATA:
            logger.error("Could not find a valid graph file. Please provide a valid path with --graph-file")
            sys.exit(1)
    
    # Make graph data available to chat_handler
    chat_handler.GRAPH_DATA = GRAPH_DATA
    logger.info("Graph data made available to chat handler")
    
    # Run the server
    run_server(args.port)

if __name__ == "__main__":
    main()
