# Local Lambda Testing with HTTP Server

This directory contains Lambda functions and tools for local testing with a frontend application.

## Overview

The local HTTP server (`local_http_server.py`) provides a way to:

1. Load the unified diabetes graph data from a local JSON file
2. Expose HTTP endpoints that simulate API Gateway + Lambda
3. Allow frontend applications to interact with the Lambda functions

## Files

- `index.py`: Main Lambda handler for processing graph data
- `chat_handler.py`: Lambda handler for chat functionality
- `local_http_server.py`: HTTP server for local testing
- `local_test.py`: Simple script for testing Lambda functions directly
- `unified_diabetes_graph.json`: The unified graph data

## Running the Local HTTP Server

To run the local HTTP server:

```bash
python local_http_server.py --port 3001 --graph-file unified_diabetes_graph.json
```

This will:
1. Load the graph data from `unified_diabetes_graph.json`
2. Start an HTTP server on port 3001
3. Expose API endpoints for frontend interaction

## API Endpoints

The local HTTP server exposes the following endpoints:

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1681612345.678
}
```

### GET /api/graph

Get graph data with optional pagination.

**Query Parameters:**
- `limit` (optional): Maximum number of nodes/edges to return (default: 100)

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "totalNodes": 1000,
  "totalEdges": 2000,
  "limit": 100
}
```

### POST /api/chat

Send a message to the chat handler. The handler will:
1. Extract entities and intents from the message using Gemini
2. Look up nodes in the graph that match the extracted entities
3. Generate a response using Gemini with the graph data as context

**Request:**
```json
{
  "message": "Tell me about diabetes treatments"
}
```

**Response:**
```json
{
  "message": "There are several treatments for diabetes...",
  "messageId": "12345-67890",
  "graphData": {
    "nodes": [...],
    "edges": [...]
  }
}
```

The `graphData` field is optional and will only be included if relevant graph data was found for the query. It contains nodes and edges that can be used for visualization.

### POST /api/graph/query

Query the graph data.

**Request:**
```json
{
  "type": "findNodes",
  "params": {
    "type": "Disease"
  }
}
```

**Response:**
```json
{
  "nodes": [...]
}
```

**Request:**
```json
{
  "type": "findConnections",
  "params": {
    "nodeId": "disease_diabetes"
  }
}
```

**Response:**
```json
{
  "connections": [...]
}
```

### POST /api/graph/upload

Simulate uploading and processing a graph file.

**Response:**
```json
{
  "message": "Successfully processed 1 records",
  "requestId": "mock-request-id-12345"
}
```

## Connecting with Frontend

To connect your frontend application with this local server:

1. Start the local HTTP server as described above
2. Configure your frontend to use `http://localhost:3001` as the API base URL
3. Make API requests to the endpoints described above

Example frontend code (React):

```javascript
// API service
const API_BASE_URL = 'http://localhost:3001';

async function fetchGraph(limit = 100) {
  const response = await fetch(`${API_BASE_URL}/api/graph?limit=${limit}`);
  return response.json();
}

async function sendChatMessage(message) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });
  return response.json();
}

async function queryGraph(type, params) {
  const response = await fetch(`${API_BASE_URL}/api/graph/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ type, params }),
  });
  return response.json();
}
```

## Troubleshooting

If you encounter issues:

1. Check the server logs for error messages
2. Verify that `unified_diabetes_graph.json` exists and is valid JSON
3. Ensure the port is not already in use
4. Check CORS settings if your frontend is running on a different port
