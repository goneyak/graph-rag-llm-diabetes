# Graph-RAG for Evidence-Based Diabetes Care

This project implements a **Graph-augmented Retrieval-Augmented Generation (Graph-RAG)** system for **precision diabetes care**.  
We integrate **ADA Clinical Practice Guidelines** and **FDA drug label data** into a unified **medical knowledge graph**, enabling **transparent, evidence-backed treatment reasoning**.

### Why This Matters
Traditional clinical decision support and RAG systems treat medical knowledge as flat text, ignoring structured relationships between:
- diseases ↔ medications
- mechanisms ↔ adverse effects
- lab values ↔ clinical actions

Our system retrieves **subgraphs** relevant to a patient query and displays:
- **the answer**
- **the supporting evidence**
- **the reasoning path** (nodes + edges)

### Key Results
- **65% accuracy** on the **MRCP Endocrinology & Diabetes exam benchmark** (62.5% passing threshold)  
- Maintains LLM correctness while adding **traceability and interpretability**
- Enables clinicians to **see why** a recommendation was made

### System Pipeline
1. **Entity + Intent Extraction** from ADA and FDA documents
2. **Knowledge Graph Construction**
3. **Subgraph Retrieval** conditioned on user query + context
4. **LLM Answer Generation** with **inline citations**
5. **Interactive UI** displaying the subgraph and reasoning path


# CDK Monorepo with Graph Processing, and Web Frontend

This is a monorepo project using AWS CDK with TypeScript for infrastructure, Python for Lambda functions, and React for the web frontend. It includes a complete graph processing system with a web interface.

## Project Structure

```
cdk-monorepo/
├── packages/
│   ├── infrastructure/  # CDK infrastructure code (TypeScript)
│   │   └── src/
│   │       ├── app.ts
│   │       └── stacks/
│   │           ├── graph-processing-stack.ts  # Defines S3, Lambda, and Neptune
│   │           ├── frontend-stack.ts          # Defines S3 website and CloudFront
│   │           └── chat-api-stack.ts          # Defines API Gateway and Lambda for chat
│   ├── lambda/          # Lambda handler code (Python)
│   │   └── src/
│   │       ├── graph_processor_handler.py   # Processes S3 events and graph data
│   │       ├── chat_handler.py              # Handles chat API requests
│   │       ├── med_knowledge_graph_handler.py # Processes medical text and builds knowledge Lambda
│   │       └── requirements.txt             # Python dependencies
│   └── frontend/        # React web application
│       ├── public/      # Static assets
│       └── src/         # React components and logic
│           └── components/
│               ├── Chat.js       # Chat interface component
│               ├── Home.js       # Home page component
│               ├── Upload.js     # File upload component
│               └── Navigation.js # Navigation component
├── package.json         # Root package.json
└── tsconfig.json        # Root TypeScript configuration
```

## Prerequisites

- Node.js (v14.x or later)
- npm (v7.x or later)
- AWS CLI configured
- Python (v3.9 or later)

## Getting Started

1. Set up environment variables:

```bash
# Copy the example .env files
cp .env.example .env
cp packages/infrastructure/.env.example packages/infrastructure/.env
cp packages/lambda/.env.example packages/lambda/.env
cp packages/frontend/.env.example packages/frontend/.env

# Edit the .env files with your specific values
# At minimum, update the AWS_ACCOUNT_ID in the root .env file
```

2. Install dependencies:

```bash
npm install
cd packages/infrastructure
npm install aws-cdk-lib dotenv
cd ../frontend
npm install dotenv
npm install cytoscape cytoscape‑panzoom cytoscape‑cose‑bilkent
```

3. Build the frontend:

```bash
# Build with environment variables
npm run frontend:build
```

4. Build the infrastructure:

```bash
cd packages/infrastructure
npm run build
```

5. Deploy the CDK stacks:

```bash
# Deploy all stacks with environment variables
npm run deploy

# Or deploy individual stacks
npm run deploy:backend  # Deploy just the graph processing backend
npm run deploy:frontend # Deploy just the web frontend
```

Note: The `npm run deploy` command will deploy all stacks by default. If you want to deploy a specific stack, use the appropriate command.

## System Architecture

This project implements a complete graph processing system:

1. **Web Frontend**: React application hosted on S3 and served via CloudFront
2. **Data Storage**: S3 bucket for uploading graph data files
3. **Processing**: Lambda function triggered by S3 events
4. **Database**: Serverless Neptune graph database for storing and querying graph data (on-demand capacity)

## Graph Processing Workflow

1. Upload a graph file through the web interface or directly to the S3 bucket
2. The Lambda function is automatically triggered by S3 events
3. The Lambda function:
   - Reads the file from S3
   - Parses the graph data (supports both CSV and JSON formats)
   - Connects to the Neptune database
   - Inserts the graph data into Neptune using Gremlin

### Supported Graph File Formats

#### JSON Format

```json
{
  "nodes": [
    {"id": "1", "label": "person", "properties": {"name": "John", "age": 30}},
    {"id": "2", "label": "person", "properties": {"name": "Jane", "age": 28}}
  ],
  "edges": [
    {"source": "1", "target": "2", "label": "knows", "properties": {"since": "2020"}}
  ]
}
```

#### CSV Format

The CSV format should have two sections separated by an empty line:
- First section: nodes with headers id,label,[property1],[property2],...
- Second section: edges with headers source,target,label,[property1],[property2],...

Example:
```
id,label,name,age
1,person,John,30
2,person,Jane,28

source,target,label,since
1,2,knows,2020
```

## Development

### Infrastructure (CDK)

The infrastructure code is located in `packages/infrastructure/`. It defines:
- An S3 bucket for graph data
- A Serverless Neptune database for graph storage (on-demand capacity)
- A Lambda function that processes S3 events and inserts data into Neptune
- An S3 bucket for hosting the web frontend
- A CloudFront distribution for serving the web frontend

The CDK code follows modern AWS CDK v2 patterns:
- Uses props instead of context for configuration
- Defines clear interfaces for stack props
- Follows a modular approach with separate stacks for different components
- Uses cross-stack references for resource sharing

To synthesize the CloudFormation template without deploying:

```bash
npm run synth
```

### Lambda Functions

The Lambda function code is located in `packages/lambda/src/`. It's written in Python and includes:

#### Graph Processor Handler

The `graph_processor_handler.py` is the main Lambda handler that:
- Processes S3 events when new graph data files are uploaded
- Parses graph data from JSON or CSV formats
- Connects to the Neptune database
- Inserts nodes and edges into Neptune using Gremlin

#### Chat Handler

The `chat_handler.py` is a Lambda handler that powers the chat interface:
- Processes user messages from the API Gateway
- Uses Google Gemini API to extract medical entities and intents from user messages
- Queries the knowledge graph to find relevant nodes and connections
- Augments AI responses with information from the knowledge graph
- Returns enriched responses with both text and graph visualization data

The chat handler supports:
- Entity extraction for diseases, treatments, medications, symptoms, and examinations
- Intent detection to understand the user's query type
- Graph-based response augmentation to provide context-specific answers
- Visualization data for displaying relevant graph nodes and connections in the UI

#### Dependencies

The Lambda functions require several Python dependencies listed in `requirements.txt`, including:
- boto3: For AWS service interactions
- gremlinpython: For Neptune graph database operations
- google-genai: For Gemini API integration

### Frontend Application

The React frontend is located in `packages/frontend/`. To start the development server:

```bash
cd packages/frontend
npm start
```

This will start a local development server at http://localhost:3000.

## Local Testing

For local testing of the Lambda function:

```bash
# Run with environment variables
npm run lambda:test
```

## Local Development

### Running the Backend Locally

The backend includes a local HTTP server that simulates API Gateway and serves the Lambda functions locally. It loads the unified JSON graph data and makes it available to the chat handler.

1. Navigate to the lambda package directory:

```bash
cd packages/lambda/src
```

2. Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

3. Create or download a unified graph JSON file (unified_diabetes_graph.json) and place it in the src directory.

4. Run the local HTTP server:

```bash
python local_http_server.py --port 3001 --graph-file unified_diabetes_graph.json
```

This will start a local server on port 3001 with the following endpoints:
- GET /health - Health check endpoint
- GET /api/graph - Returns the graph data
- POST /api/chat - Chat API endpoint
- POST /api/graph/query - Graph query endpoint
- POST /api/graph/upload - Simulates S3 upload and processing

### Running the Frontend Locally

The frontend is a React application that can be run locally for development:

1. Navigate to the frontend package directory:

```bash
cd packages/frontend
```

2. Install the required npm dependencies:

```bash
npm install
```

3. Create a .env.local file with the following content:

```
REACT_APP_API_ENDPOINT=http://localhost:3001
```

4. Start the development server:

```bash
npm start
```

This will start a development server at http://localhost:3000 that connects to the local backend server.

### Running the Medical Knowledge Graph Processing Notebook

The Med_Knowledge_Graph.ipynb notebook in the lambda package can be used to process PDF and CSV files for intent detection, entity recognition, and graph building:

1. Navigate to the lambda package directory:

```bash
cd packages/lambda/src
```

2. Install the required Python dependencies:

```bash
pip install -r requirements.txt
pip install jupyter notebook matplotlib scikit-learn PyPDF2 google-genai gremlinpython nltk boto3
```

3. Start Jupyter Notebook:

```bash
jupyter notebook
```

4. Open the Med_Knowledge_Graph.ipynb notebook.

5. Update the following variables in the notebook:
   - `DATA_DIR`: Path to your PDF and CSV files (e.g., "datasets/diabetes_care")
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - AWS credentials if using Bedrock

6. Run the notebook cells sequentially to:
   - Load and process PDF/CSV files
   - Perform intent detection and entity recognition
   - Build a knowledge graph
   - Visualize the graph
   - Generate a unified JSON graph file

7. The generated unified_diabetes_graph.json file can be used with the local HTTP server.

## Environment Variables

This project uses environment variables for configuration. Each package has its own `.env` file:

### Root Environment Variables

Located in `.env` in the root directory:

- `AWS_REGION`: The AWS region to deploy to (default: eu-west-1)
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `ENVIRONMENT`: The deployment environment (dev, staging, prod)

### Infrastructure Environment Variables

Located in `packages/infrastructure/.env`:

- `CDK_DEFAULT_ACCOUNT`: AWS account ID (inherited from root)
- `CDK_DEFAULT_REGION`: AWS region (inherited from root)
- `AWS_PROFILE`: AWS profile to use for deployment (default: default)
- `NEPTUNE_ENGINE_VERSION`: Neptune engine version (default: 1.2.1.0)
- `NEPTUNE_MIN_CAPACITY`: Minimum Neptune Capacity Units for serverless (default: 1.0)
- `NEPTUNE_MAX_CAPACITY`: Maximum Neptune Capacity Units for serverless (default: 8.0)
- `S3_GRAPH_DATA_BUCKET_NAME`: Name of the S3 bucket for graph data
- `S3_WEBSITE_BUCKET_NAME`: Name of the S3 bucket for the website
- `S3_MEDICAL_DATA_BUCKET_NAME`: Name of the S3 bucket for medical data
- `CLOUDFRONT_PRICE_CLASS`: CloudFront price class (default: PriceClass_100)

#### AWS Profile Configuration

The `AWS_PROFILE` environment variable specifies which AWS profile to use for deployment. This allows you to deploy to different AWS accounts or regions using different profiles.

To use a different AWS profile:

1. Make sure you have the profile configured in your AWS credentials file (`~/.aws/credentials`)
2. Update the `AWS_PROFILE` value in `packages/infrastructure/.env`

For example:
```
AWS_PROFILE=dev
```

To create a new AWS profile, you can use the AWS CLI:

```bash
aws configure --profile dev
```

This will prompt you for your AWS access key ID, secret access key, region, and output format.

### Lambda Environment Variables

Located in `packages/lambda/.env`:

- `ENVIRONMENT`: Deployment environment (inherited from root)
- `NEPTUNE_ENDPOINT`: Neptune endpoint for local testing
- `NEPTUNE_PORT`: Neptune port for local testing
- `S3_GRAPH_DATA_BUCKET_NAME`: Name of the S3 bucket for graph data
- `LOG_LEVEL`: Logging level (default: INFO)

### Frontend Environment Variables

Located in `packages/frontend/.env`:

- `REACT_APP_ENVIRONMENT`: Deployment environment (inherited from root)
- `REACT_APP_API_ENDPOINT`: API endpoint URL
- `REACT_APP_UPLOAD_BUCKET_NAME`: S3 bucket name for file uploads
- `REACT_APP_ENABLE_DEBUG_MODE`: Enable debug mode (true/false)
- `REACT_APP_ENABLE_ANALYTICS`: Enable analytics (true/false)

## Adding Dependencies

### For Infrastructure

```bash
cd packages/infrastructure
npm install <package-name>
```

### For Lambda

Add dependencies to `packages/lambda/src/requirements.txt`.

### For Frontend

```bash
cd packages/frontend
npm install <package-name>
```

## License

This project is licensed under the ISC License.
