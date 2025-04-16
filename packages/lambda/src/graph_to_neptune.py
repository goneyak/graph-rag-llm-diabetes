#!/usr/bin/env python3
"""
Convert the unified diabetes graph to Neptune-compatible Gremlin queries.

This script reads the unified_diabetes_graph.json file and generates Gremlin queries
that can be used to load the graph into an Amazon Neptune database.
"""

import json
import os
import argparse

def load_graph_data(input_file):
    """Load graph data from JSON file"""
    try:
        with open(input_file, 'r') as f:
            graph_data = json.load(f)
        print(f"Loaded graph data with {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
        return graph_data
    except Exception as e:
        print(f"Error loading graph data: {e}")
        return None

def generate_gremlin_queries(graph_data, output_file):
    """Generate Gremlin queries for Neptune insertion"""
    queries = []
    
    # Generate queries for nodes
    for node in graph_data['nodes']:
        node_id = node.get('id', '')
        if not node_id:
            continue
        
        # Get node type
        node_type = node.get('type', 'Unknown')
        
        # Start query
        query = f"g.addV('{node_type}').property('id', '{node_id}')"
        
        # Add properties
        for key, value in node.items():
            if key not in ['id', 'type']:
                # Handle different property types
                if isinstance(value, str):
                    # Escape single quotes in string values
                    value = value.replace("'", "\\'")
                    query += f".property('{key}', '{value}')"
                elif isinstance(value, (int, float, bool)):
                    query += f".property('{key}', {value})"
                elif isinstance(value, list):
                    # Convert list to JSON string
                    value_str = json.dumps(value).replace("'", "\\'")
                    query += f".property('{key}', '{value_str}')"
                elif value is None:
                    continue
                else:
                    # Convert other types to string
                    value_str = str(value).replace("'", "\\'")
                    query += f".property('{key}', '{value_str}')"
        
        queries.append(query)
    
    # Generate queries for edges
    for edge in graph_data['edges']:
        source_id = edge.get('source', '')
        target_id = edge.get('target', '')
        edge_type = edge.get('type', 'RELATED_TO')
        
        if not source_id or not target_id:
            continue
        
        # Start query
        query = f"g.V('{source_id}').addE('{edge_type}').to(g.V('{target_id}')"
        
        # Add properties
        for key, value in edge.items():
            if key not in ['source', 'target', 'type']:
                # Handle different property types
                if isinstance(value, str):
                    # Escape single quotes in string values
                    value = value.replace("'", "\\'")
                    query += f").property('{key}', '{value}')"
                elif isinstance(value, (int, float, bool)):
                    query += f").property('{key}', {value})"
                elif isinstance(value, list):
                    # Convert list to JSON string
                    value_str = json.dumps(value).replace("'", "\\'")
                    query += f").property('{key}', '{value_str}')"
                elif value is None:
                    continue
                else:
                    # Convert other types to string
                    value_str = str(value).replace("'", "\\'")
                    query += f").property('{key}', '{value_str}')"
        
        # Close the query if no properties were added
        if query.endswith("to(g.V('" + target_id + "')"):
            query += ")"
        
        queries.append(query)
    
    # Write queries to file
    with open(output_file, 'w') as f:
        for query in queries:
            f.write(query + ";\n")
    
    print(f"Generated {len(queries)} Gremlin queries and saved to {output_file}")
    return len(queries)

def generate_neptune_loader_manifest(input_file, output_dir):
    """Generate a Neptune Loader manifest file for bulk loading"""
    manifest_file = os.path.join(output_dir, "neptune-manifest.json")
    
    manifest = {
        "format": "csv",
        "version": "1.0",
        "files": [
            input_file
        ]
    }
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Generated Neptune Loader manifest file: {manifest_file}")

def generate_neptune_loader_commands(bucket_name, region="us-east-1"):
    """Generate Neptune Loader commands for reference"""
    commands = [
        "# Neptune Loader Commands",
        "",
        "# 1. Upload the Gremlin queries file and manifest to S3:",
        f"aws s3 cp neptune_gremlin_queries.txt s3://{bucket_name}/",
        f"aws s3 cp neptune-manifest.json s3://{bucket_name}/",
        "",
        "# 2. Start the Neptune Loader job:",
        f"curl -X POST \\",
        f"    -H 'Content-Type: application/json' \\",
        f"    https://<your-neptune-endpoint>:8182/loader \\",
        f"    -d '{{",
        f"        \"source\" : \"s3://{bucket_name}/neptune-manifest.json\",",
        f"        \"format\" : \"csv\",",
        f"        \"iamRoleArn\" : \"arn:aws:iam::<account-id>:role/<role-name>\",",
        f"        \"region\" : \"{region}\",",
        f"        \"failOnError\" : \"FALSE\"",
        f"    }}'",
        "",
        "# 3. Check the status of the loader job:",
        f"curl -G https://<your-neptune-endpoint>:8182/loader/<load-id>"
    ]
    
    with open("neptune_loader_commands.txt", 'w') as f:
        f.write("\n".join(commands))
    
    print("Generated Neptune Loader commands in neptune_loader_commands.txt")

def main():
    parser = argparse.ArgumentParser(description='Convert graph data to Neptune Gremlin queries')
    parser.add_argument('--input', default='unified_diabetes_graph.json', help='Input graph JSON file')
    parser.add_argument('--output', default='neptune_gremlin_queries.txt', help='Output Gremlin queries file')
    parser.add_argument('--bucket', default='your-s3-bucket', help='S3 bucket name for Neptune Loader')
    parser.add_argument('--region', default='us-east-1', help='AWS region for Neptune Loader')
    args = parser.parse_args()
    
    # Load graph data
    graph_data = load_graph_data(args.input)
    if not graph_data:
        return
    
    # Generate Gremlin queries
    num_queries = generate_gremlin_queries(graph_data, args.output)
    
    # Generate Neptune Loader manifest
    output_dir = os.path.dirname(args.output) or '.'
    generate_neptune_loader_manifest(args.output, output_dir)
    
    # Generate Neptune Loader commands
    generate_neptune_loader_commands(args.bucket, args.region)
    
    print("\nNext steps:")
    print("1. Review the generated Gremlin queries in", args.output)
    print("2. Update the S3 bucket name and Neptune endpoint in neptune_loader_commands.txt")
    print("3. Follow the commands in neptune_loader_commands.txt to load the data into Neptune")

if __name__ == "__main__":
    main()
