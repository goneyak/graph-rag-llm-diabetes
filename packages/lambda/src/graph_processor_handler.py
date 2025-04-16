import json
import logging
import os
import boto3
import csv
import io
import uuid
from gremlin_python.driver import client
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.structure.graph import Graph

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')

# Get Neptune configuration from environment variables
NEPTUNE_ENDPOINT = os.environ.get('NEPTUNE_ENDPOINT')
NEPTUNE_PORT = os.environ.get('NEPTUNE_PORT', '8182')

def handler(event, context):
    """
    Main Lambda handler function for processing S3 events and inserting graph data into Neptune
    
    Parameters:
    event (dict): The S3 event data passed to the Lambda function
    context (LambdaContext): The runtime information of the Lambda function
    
    Returns:
    dict: Response containing statusCode and body
    """
    logger.info('Event received: %s', json.dumps(event))
    
    try:
        # Process S3 event
        if 'Records' not in event:
            raise ValueError("No Records found in event")
        
        for record in event['Records']:
            # Check if this is an S3 event
            if record['eventSource'] != 'aws:s3':
                logger.warning(f"Skipping non-S3 event: {record['eventSource']}")
                continue
                
            # Get bucket and key information
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            logger.info(f"Processing file {key} from bucket {bucket}")
            
            # Get the file content from S3
            response = s3_client.get_object(Bucket=bucket, Key=key)
            file_content = response['Body'].read().decode('utf-8')
            
            # Process the graph data
            nodes, edges = parse_graph_data(file_content, key)
            
            # Insert data into Neptune
            insert_into_neptune(nodes, edges)
            
            logger.info(f"Successfully processed file {key} and inserted into Neptune")
        
        # Return a successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': f"Successfully processed {len(event['Records'])} records",
                'requestId': context.aws_request_id
            })
        }
    except Exception as e:
        logger.error('Error: %s', str(e), exc_info=True)
        # Return an error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        }

def parse_graph_data(file_content, file_name):
    """
    Parse the graph data from the file content
    
    Parameters:
    file_content (str): The content of the file
    file_name (str): The name of the file
    
    Returns:
    tuple: (nodes, edges) where nodes is a list of node dictionaries and edges is a list of edge dictionaries
    """
    logger.info(f"Parsing graph data from file: {file_name}")
    
    # Determine file format based on extension
    if file_name.endswith('.csv'):
        return parse_csv_graph(file_content)
    elif file_name.endswith('.json'):
        return parse_json_graph(file_content)
    else:
        # Default to JSON format
        try:
            return parse_json_graph(file_content)
        except:
            # Try CSV as fallback
            return parse_csv_graph(file_content)

def parse_csv_graph(file_content):
    """
    Parse graph data from CSV format
    
    Expected format:
    - First section: nodes with id,label,properties
    - Second section: edges with source,target,label,properties
    
    Returns:
    tuple: (nodes, edges)
    """
    nodes = []
    edges = []
    
    # Read CSV content
    csv_reader = csv.reader(io.StringIO(file_content))
    rows = list(csv_reader)
    
    # Find separator between nodes and edges
    separator_index = -1
    for i, row in enumerate(rows):
        if len(row) == 1 and row[0].strip() == "":
            separator_index = i
            break
    
    if separator_index == -1:
        # Assume all rows are nodes (no edges)
        node_rows = rows
        edge_rows = []
    else:
        node_rows = rows[:separator_index]
        edge_rows = rows[separator_index+1:]
    
    # Process nodes
    if node_rows and len(node_rows) > 0:
        headers = node_rows[0]
        for row in node_rows[1:]:
            if not row or len(row) == 0:
                continue
                
            node = {'id': row[0], 'label': row[1]}
            # Add properties
            properties = {}
            for i in range(2, min(len(headers), len(row))):
                if row[i]:  # Only add non-empty properties
                    properties[headers[i]] = row[i]
            node['properties'] = properties
            nodes.append(node)
    
    # Process edges
    if edge_rows and len(edge_rows) > 0:
        headers = edge_rows[0]
        for row in edge_rows[1:]:
            if not row or len(row) == 0:
                continue
                
            if len(row) >= 3:
                edge = {
                    'id': str(uuid.uuid4()),
                    'source': row[0],
                    'target': row[1],
                    'label': row[2]
                }
                # Add properties
                properties = {}
                for i in range(3, min(len(headers), len(row))):
                    if row[i]:  # Only add non-empty properties
                        properties[headers[i]] = row[i]
                edge['properties'] = properties
                edges.append(edge)
    
    logger.info(f"Parsed {len(nodes)} nodes and {len(edges)} edges from CSV")
    return nodes, edges

def parse_json_graph(file_content):
    """
    Parse graph data from JSON format
    
    Expected format:
    {
        "nodes": [
            {"id": "1", "label": "person", "properties": {"name": "John", "age": 30}},
            ...
        ],
        "edges": [
            {"source": "1", "target": "2", "label": "knows", "properties": {"since": "2020"}},
            ...
        ]
    }
    
    Returns:
    tuple: (nodes, edges)
    """
    data = json.loads(file_content)
    
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    
    # Ensure each edge has an ID
    for edge in edges:
        if 'id' not in edge:
            edge['id'] = str(uuid.uuid4())
    
    logger.info(f"Parsed {len(nodes)} nodes and {len(edges)} edges from JSON")
    return nodes, edges

def insert_into_neptune(nodes, edges):
    """
    Insert the graph data into Neptune using Gremlin
    
    Parameters:
    nodes (list): List of node dictionaries
    edges (list): List of edge dictionaries
    """
    logger.info(f"Connecting to Neptune at {NEPTUNE_ENDPOINT}:{NEPTUNE_PORT}")
    
    # Create a Gremlin connection to Neptune
    connection = DriverRemoteConnection(
        f'wss://{NEPTUNE_ENDPOINT}:{NEPTUNE_PORT}/gremlin',
        'g'
    )
    
    try:
        g = traversal().withRemote(connection)
        
        # Insert nodes
        for node in nodes:
            vertex_id = node['id']
            vertex_label = node['label']
            properties = node.get('properties', {})
            
            # Check if vertex already exists
            existing = g.V(vertex_id).hasNext().toList()
            if existing and existing[0]:
                logger.info(f"Vertex {vertex_id} already exists, updating properties")
                vertex = g.V(vertex_id)
                
                # Update properties
                for key, value in properties.items():
                    vertex.property(key, value).iterate()
            else:
                # Create new vertex with properties
                vertex = g.addV(vertex_label).property('id', vertex_id)
                
                # Add properties
                for key, value in properties.items():
                    vertex.property(key, value)
                
                vertex.iterate()
                
            logger.debug(f"Inserted/updated vertex {vertex_id}")
        
        # Insert edges
        for edge in edges:
            source_id = edge['source']
            target_id = edge['target']
            edge_label = edge['label']
            properties = edge.get('properties', {})
            
            # Add edge
            e = g.V(source_id).addE(edge_label).to(g.V(target_id))
            
            # Add properties
            for key, value in properties.items():
                e.property(key, value)
            
            e.iterate()
            logger.debug(f"Inserted edge from {source_id} to {target_id} with label {edge_label}")
        
        logger.info(f"Successfully inserted {len(nodes)} nodes and {len(edges)} edges into Neptune")
    finally:
        connection.close()
