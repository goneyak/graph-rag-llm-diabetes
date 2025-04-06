import json
import os
import logging
import boto3
import time
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

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
        
        # In a real application, you would call an AI service here
        # For now, we'll simulate a response
        ai_response = generate_ai_response(user_message)
        
        # Return the response
        return create_response(200, {
            'message': ai_response,
            'messageId': str(uuid.uuid4())
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error'
        })

def generate_ai_response(user_message):
    """
    Generate an AI response to the user message
    
    In a real application, this would call an AI service like Amazon Bedrock,
    Amazon Lex, or a third-party API like OpenAI.
    
    Args:
        user_message (str): The user's message
        
    Returns:
        str: The AI response
    """
    # Simulate processing time
    time.sleep(1)
    
    # Simple response logic based on keywords
    user_message = user_message.lower()
    
    if 'hello' in user_message or 'hi' in user_message:
        return "Hello! How can I help you today?"
    
    elif 'graph' in user_message:
        return "I can help you process and analyze graph data. You can upload JSON or CSV files containing nodes and edges."
    
    elif 'help' in user_message:
        return "I'm here to help! You can ask me questions about graph processing, data analysis, or any other topic."
    
    elif 'thank' in user_message:
        return "You're welcome! Is there anything else I can help you with?"
    
    else:
        return "I understand you're asking about '" + user_message + "'. Could you provide more details so I can assist you better?"

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
