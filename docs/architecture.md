# Architecture Summary

## Frontend Layer

- React application in `packages/frontend`
- Uses `react-router-dom` for route-based UI
- Uses `react-markdown` for markdown answer rendering
- Uses Cytoscape (`cytoscape`, `cytoscape-panzoom`, `cytoscape-cose-bilkent`) for graph visualization
- Main components: chat, upload, navigation, and graph displays

## API and Lambda Layer

- `chat_handler.py`: receives user messages, retrieves graph evidence, generates evidence-grounded responses
- `graph_processor_handler.py`: processes graph uploads and Neptune ingestion
- `local_http_server.py`: local API Gateway/Lambda simulator for development

## Graph and Data Layer

- Unified graph artifacts live in `packages/lambda/examples`
- Neptune integration helpers are in `packages/lambda/src`
- Local graph retrieval logic supports evidence tracing for answer generation

## Infrastructure Layer (AWS CDK)

- `frontend-stack.ts`: S3/CloudFront frontend hosting
- `graph-processing-stack.ts`: S3 + Lambda + Neptune processing path
- `chat-api-stack.ts`: API Gateway + Lambda chat endpoint
