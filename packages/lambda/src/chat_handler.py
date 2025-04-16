import json
import os
import logging
import boto3
import time
import uuid
import requests
from google import genai

# Global variable to store the graph data
# This will be populated by the local_http_server.py
GRAPH_DATA = None

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize Gemini API client
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyALh382aR4X2viTyJXqMfaxnSll9f5p6kQ')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-pro')
genai_client = genai.Client(api_key=GEMINI_API_KEY)

def handler(event, context):
    """
    Lambda function handler for the chat API
    
    This function processes chat messages and returns AI responses.
    
    Args:
        event (dict): API Gateway event
        context (object): Lambda context
        
    Returns:
        dict: API Gateway response
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        
        if not user_message:
            return create_response(400, {
                'error': 'Missing message in request body'
            })
        
        # Process the message with graph augmentation
        ai_response, graph_data = process_message_with_graph(user_message)
        
        # Return the response
        response_data = {
            'message': ai_response,
            'messageId': str(uuid.uuid4())
        }
        
        # Include graph data if available
        if graph_data:
            response_data['graphData'] = graph_data
        
        return create_response(200, response_data)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error'
        })

def extract_entities_and_intents(message):
    """
    Extract entities and intents from the message using Gemini
    
    Args:
        message (str): The user's message
        
    Returns:
        dict: Extracted entities and intents
    """
    try:
        # Create prompt for entity and intent extraction
        prompt = f"""
        Extract medical entities and intents from the following message:
        
        Message: "{message}"
        
        Return a JSON object with the following structure:
        {{
            "entities": {{
                "diseases": [],
                "treatments": [],
                "medications": [],
                "symptoms": [],
                "examinations": []
            }},
            "intents": []
        }}
        
        For intents, use one or more of: disease_info, treatment_info, medication_info, symptom_info, diagnosis_info, general_question
        """
        
        # Call Gemini API
        response = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        # Parse the response
        try:
            result = json.loads(response.text)
            logger.info(f"Extracted entities and intents: {result}")
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Gemini response as JSON: {response.text}")
            return {
                "entities": {
                    "diseases": [],
                    "treatments": [],
                    "medications": [],
                    "symptoms": [],
                    "examinations": []
                },
                "intents": ["general_question"]
            }
            
    except Exception as e:
        logger.error(f"Error extracting entities and intents: {str(e)}")
        return {
            "entities": {
                "diseases": [],
                "treatments": [],
                "medications": [],
                "symptoms": [],
                "examinations": []
            },
            "intents": ["general_question"]
        }

def find_nodes_in_graph(entities):
    """
    Find nodes in the graph that match the extracted entities
    
    Args:
        entities (dict): Extracted entities
        
    Returns:
        dict: Matching nodes from the graph
    """
    if not GRAPH_DATA:
        logger.warning("Graph data not available")
        return {}
    
    matching_nodes = {
        "diseases": [],
        "treatments": [],
        "medications": [],
        "symptoms": [],
        "examinations": []
    }
    
    # Get all nodes from the graph
    nodes = GRAPH_DATA.get('nodes', [])
    
    # Find matching disease nodes
    for disease_name in entities.get('diseases', []):
        for node in nodes:
            if node.get('type') == 'Disease' and node.get('name', '').lower() == disease_name.lower():
                matching_nodes['diseases'].append(node)
                break
    
    # Find matching treatment nodes
    for treatment_name in entities.get('treatments', []):
        for node in nodes:
            if node.get('type') == 'Treatment' and node.get('name', '').lower() == treatment_name.lower():
                matching_nodes['treatments'].append(node)
                break
    
    # Find matching medication nodes
    for medication_name in entities.get('medications', []):
        for node in nodes:
            if node.get('type') == 'Medication' and node.get('name', '').lower() == medication_name.lower():
                matching_nodes['medications'].append(node)
                break
    
    # Find matching symptom nodes
    for symptom_name in entities.get('symptoms', []):
        for node in nodes:
            if node.get('type') == 'Symptom' and node.get('name', '').lower() == symptom_name.lower():
                matching_nodes['symptoms'].append(node)
                break
    
    # Find matching examination nodes
    for examination_name in entities.get('examinations', []):
        for node in nodes:
            if node.get('type') == 'ExaminationMethod' and node.get('name', '').lower() == examination_name.lower():
                matching_nodes['examinations'].append(node)
                break
    
    logger.info(f"Found matching nodes: {matching_nodes}")
    return matching_nodes

def find_connections(node_id):
    """
    Find connections for a node in the graph
    
    Args:
        node_id (str): The ID of the node
        
    Returns:
        list: Connections for the node
    """
    if not GRAPH_DATA:
        return []
    
    connections = []
    edges = GRAPH_DATA.get('edges', [])
    
    for edge in edges:
        if edge.get('source') == node_id or edge.get('target') == node_id:
            connections.append(edge)
    
    return connections

def get_node_by_id(node_id):
    """
    Get a node by its ID
    
    Args:
        node_id (str): The ID of the node
        
    Returns:
        dict: The node
    """
    if not GRAPH_DATA:
        return None
    
    nodes = GRAPH_DATA.get('nodes', [])
    
    for node in nodes:
        if node.get('id') == node_id:
            return node
    
    return None

def enrich_connections(connections):
    """
    Enrich connections with node information
    
    Args:
        connections (list): List of connections
        
    Returns:
        list: Enriched connections
    """
    enriched = []
    
    for connection in connections:
        source_node = get_node_by_id(connection.get('source'))
        target_node = get_node_by_id(connection.get('target'))
        
        enriched.append({
            'edge': connection,
            'source': source_node,
            'target': target_node
        })
    
    return enriched

def generate_ai_response_with_graph(user_message, extracted_data, graph_nodes):
    """
    Generate an AI response using Gemini with graph data augmentation
    
    Args:
        user_message (str): The user's message
        extracted_data (dict): Extracted entities and intents
        graph_nodes (dict): Matching nodes from the graph
        
    Returns:
        tuple: (AI response, graph data for visualization)
    """
    # Prepare graph context
    graph_context = []
    graph_viz_data = {
        'nodes': [],
        'edges': []
    }
    
    # Process disease nodes and their connections
    for disease in graph_nodes.get('diseases', []):
        disease_id = disease.get('id')
        disease_name = disease.get('name', 'Unknown Disease')
        
        graph_context.append(f"Disease: {disease_name}")
        graph_viz_data['nodes'].append(disease)
        
        # Get connections for this disease
        connections = find_connections(disease_id)
        enriched_connections = enrich_connections(connections)
        
        # Process connections
        treatments = []
        symptoms = []
        medications = []
        examinations = []
        
        for conn in enriched_connections:
            edge = conn.get('edge', {})
            edge_type = edge.get('type', '')
            source = conn.get('source', {})
            target = conn.get('target', {})
            
            # Add to visualization data
            if source and source not in graph_viz_data['nodes']:
                graph_viz_data['nodes'].append(source)
            if target and target not in graph_viz_data['nodes']:
                graph_viz_data['nodes'].append(target)
            if edge:
                graph_viz_data['edges'].append(edge)
            
            # Process by edge type
            if edge_type == 'TREATS' and disease_id == target.get('id'):
                treatment_name = source.get('name', 'Unknown Treatment')
                treatments.append(treatment_name)
            
            elif edge_type == 'CAUSES' and disease_id == source.get('id'):
                symptom_name = target.get('name', 'Unknown Symptom')
                symptoms.append(symptom_name)
            
            elif edge_type == 'DIAGNOSES' and disease_id == target.get('id'):
                exam_name = source.get('name', 'Unknown Examination')
                examinations.append(exam_name)
        
        # Add information to context
        if treatments:
            graph_context.append(f"Treatments for {disease_name}: {', '.join(treatments)}")
        
        if symptoms:
            graph_context.append(f"Symptoms of {disease_name}: {', '.join(symptoms)}")
        
        if examinations:
            graph_context.append(f"Diagnostic methods for {disease_name}: {', '.join(examinations)}")
    
    # Create prompt for Gemini
    graph_context_text = "\n".join(graph_context)
    
    prompt = f"""
    You are a medical assistant with access to a knowledge graph about diabetes and related medical information.
    
    User question: "{user_message}"
    
    Extracted entities and intents: {json.dumps(extracted_data)}
    
    Knowledge graph information:
    {graph_context_text}
    
    Please provide a helpful, accurate response based on the knowledge graph information above.
    If the knowledge graph doesn't contain relevant information, provide a general response based on your knowledge.
    Always be clear about what information comes from the knowledge graph versus your general knowledge.
    """
    
    try:
        # Call Gemini API
        response = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        return response.text, graph_viz_data if graph_viz_data['nodes'] else None
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return "I'm sorry, I couldn't process your request at this time. Please try again later.", None

def process_message_with_graph(user_message):
    """
    Process a message with graph augmentation
    
    Args:
        user_message (str): The user's message
        
    Returns:
        tuple: (AI response, graph data)
    """
    # Extract entities and intents
    extracted_data = extract_entities_and_intents(user_message)
    
    # Find matching nodes in the graph
    graph_nodes = find_nodes_in_graph(extracted_data.get('entities', {}))
    
    # Generate AI response with graph augmentation
    ai_response, graph_data = generate_ai_response_with_graph(
        user_message, 
        extracted_data, 
        graph_nodes
    )
    
    return ai_response, graph_data

def create_response(status_code, body):
    """
    Create an API Gateway response
    
    Args:
        status_code (int): HTTP status code
        body (dict): Response body
        
    Returns:
        dict: API Gateway response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps(body)
    }
