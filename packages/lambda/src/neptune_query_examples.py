#!/usr/bin/env python3
"""
Example queries for the Neptune diabetes knowledge graph.
This script demonstrates how to connect to Neptune and run various queries.
"""

from gremlin_python.driver import client
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
import json
import os

# Replace with your Neptune endpoint
NEPTUNE_ENDPOINT = "wss://<your-neptune-endpoint>:8182/gremlin"

def connect_to_neptune():
    """Connect to Neptune and return a graph traversal source"""
    # Create a connection to Neptune
    conn = DriverRemoteConnection(NEPTUNE_ENDPOINT, 'g')
    # Create a graph traversal source
    g = traversal().withRemote(conn)
    return g, conn

def print_query_results(results, limit=10):
    """Print query results in a readable format"""
    count = 0
    for result in results:
        print(json.dumps(result, indent=2))
        count += 1
        if count >= limit:
            print(f"... (showing {limit} of {count} results)")
            break
    print(f"Total results: {count}")

def example_queries(g):
    """Run example queries on the Neptune graph"""
    print("\n=== Example Queries ===\n")

    # Query 1: Find all diseases
    print("\n1. Find all diseases:")
    diseases = g.V().hasLabel('Disease').valueMap().toList()
    print_query_results(diseases)

    # Query 2: Find treatments for diabetes
    print("\n2. Find treatments for diabetes:")
    diabetes_treatments = g.V().has('name', 'diabetes') \
        .in_('TREATS') \
        .valueMap().toList()
    print_query_results(diabetes_treatments)

    # Query 3: Find symptoms caused by diabetes
    print("\n3. Find symptoms caused by diabetes:")
    diabetes_symptoms = g.V().has('name', 'diabetes') \
        .out('CAUSES') \
        .valueMap().toList()
    print_query_results(diabetes_symptoms)

    # Query 4: Find examination methods for diagnosing diabetes
    print("\n4. Find examination methods for diagnosing diabetes:")
    diabetes_exams = g.V().has('name', 'diabetes') \
        .in_('DIAGNOSES') \
        .valueMap().toList()
    print_query_results(diabetes_exams)

    # Query 5: Find all chunks that mention diabetes
    print("\n5. Find all chunks that mention diabetes:")
    diabetes_chunks = g.V().has('name', 'diabetes') \
        .in_('MENTIONS') \
        .valueMap().toList()
    print_query_results(diabetes_chunks)

    # Query 6: Find the document sources for chunks mentioning diabetes
    print("\n6. Find document sources for chunks mentioning diabetes:")
    diabetes_docs = g.V().has('name', 'diabetes') \
        .in_('MENTIONS') \
        .in_('CONTAINS') \
        .valueMap().toList()
    print_query_results(diabetes_docs)

    # Query 7: Find relationships between treatments
    print("\n7. Find relationships between treatments:")
    treatment_relations = g.V().hasLabel('Treatment') \
        .both('RELATED_TO') \
        .hasLabel('Treatment') \
        .path().by('name').toList()
    print_query_results(treatment_relations)

    # Query 8: Find all entities related to a specific chunk
    print("\n8. Find all entities mentioned in a specific chunk:")
    chunk_entities = g.V().hasLabel('Chunk').limit(1) \
        .out('MENTIONS') \
        .valueMap().toList()
    print_query_results(chunk_entities)

    # Query 9: Find diseases and their treatments (complex query)
    print("\n9. Find diseases and their treatments:")
    disease_treatments = g.V().hasLabel('Disease') \
        .project('disease', 'treatments') \
        .by('name') \
        .by(__.in_('TREATS').valueMap().fold()) \
        .toList()
    print_query_results(disease_treatments)

    # Query 10: Find the most connected entities (highest degree)
    print("\n10. Find the most connected entities:")
    connected_entities = g.V().hasLabel('Entity') \
        .project('entity', 'connections') \
        .by('name') \
        .by(__.both().count()) \
        .order().by('connections', 'desc') \
        .limit(5) \
        .toList()
    print_query_results(connected_entities)

def main():
    """Main function to demonstrate Neptune queries"""
    # Check if Neptune endpoint is set
    if NEPTUNE_ENDPOINT == "wss://<your-neptune-endpoint>:8182/gremlin":
        print("Please set your Neptune endpoint in the script before running.")
        print("Example queries are provided for reference but won't be executed.")
        
        # Print example Gremlin queries as strings
        print("\n=== Example Gremlin Queries ===\n")
        print("// 1. Find all diseases")
        print("g.V().hasLabel('Disease').valueMap()")
        
        print("\n// 2. Find treatments for diabetes")
        print("g.V().has('name', 'diabetes').in('TREATS').valueMap()")
        
        print("\n// 3. Find symptoms caused by diabetes")
        print("g.V().has('name', 'diabetes').out('CAUSES').valueMap()")
        
        print("\n// 4. Find examination methods for diagnosing diabetes")
        print("g.V().has('name', 'diabetes').in('DIAGNOSES').valueMap()")
        
        print("\n// 5. Find all chunks that mention diabetes")
        print("g.V().has('name', 'diabetes').in('MENTIONS').valueMap()")
        
        print("\n// 6. Find document sources for chunks mentioning diabetes")
        print("g.V().has('name', 'diabetes').in('MENTIONS').in('CONTAINS').valueMap()")
        
        print("\n// 7. Find relationships between treatments")
        print("g.V().hasLabel('Treatment').both('RELATED_TO').hasLabel('Treatment').path().by('name')")
        
        print("\n// 8. Find all entities mentioned in a specific chunk")
        print("g.V().hasLabel('Chunk').limit(1).out('MENTIONS').valueMap()")
        
        print("\n// 9. Find diseases and their treatments")
        print("g.V().hasLabel('Disease').project('disease', 'treatments').by('name').by(__.in('TREATS').valueMap().fold())")
        
        print("\n// 10. Find the most connected entities")
        print("g.V().hasLabel('Entity').project('entity', 'connections').by('name').by(__.both().count()).order().by('connections', desc).limit(5)")
        
        return
    
    try:
        # Connect to Neptune
        g, conn = connect_to_neptune()
        
        # Run example queries
        example_queries(g)
        
        # Close the connection
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to Neptune: {e}")
        print("Please check your Neptune endpoint and ensure the database is accessible.")

if __name__ == "__main__":
    main()
