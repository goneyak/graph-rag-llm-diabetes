# Graph-RAG for Evidence-Based Diabetes Care

Graph-RAG clinical decision-support prototype integrating ADA guidelines and FDA labels for traceable diabetes reasoning.

## Why It Matters

Conventional RAG pipelines often return plausible text without transparent evidence paths. This project emphasizes:

- graph-structured evidence retrieval over flat text lookup
- visible node and edge context for answer traceability
- reviewer-friendly separation of runtime code, examples, docs, and assets

## Architecture Snapshot

1. React frontend collects a user question and renders answer plus graph context.
2. Lambda chat handler extracts entities/intents and retrieves relevant subgraph context.
3. Graph evidence is passed into the LLM prompt for evidence-grounded response generation.
4. Graph processor Lambda supports ingestion paths into Neptune-backed storage.

## Repository Map

```text
.
├── datasets/
├── docs/
│   ├── architecture.md
│   ├── setup.md
│   ├── team178poster.pdf
│   └── team178report.pdf
├── packages/
│   ├── frontend/
│   │   ├── src/components/
│   │   │   ├── Chat.js
│   │   │   ├── GraphDisplay.js
│   │   │   ├── Home.js
│   │   │   ├── Navigation.js
│   │   │   ├── SampleGraphDisplay.js
│   │   │   └── Upload.js
│   ├── infrastructure/
│   │   └── src/stacks/
│   │       ├── chat-api-stack.ts
│   │       ├── frontend-stack.ts
│   │       └── graph-processing-stack.ts
│   └── lambda/
│       ├── assets/
│       ├── docs/
│       ├── examples/
│       ├── notebooks/
│       └── src/
│           ├── chat_handler.py
│           ├── graph_processor_handler.py
│           ├── local_http_server.py
│           └── unified_graph_builder.py
├── package.json
└── tsconfig.json
```

## Quickstart

### 1. Set environment files

```bash
cp .env.example .env
cp packages/infrastructure/.env.example packages/infrastructure/.env
cp packages/lambda/.env.example packages/lambda/.env
cp packages/frontend/.env.example packages/frontend/.env
```

Required values:

- `.env`: `AWS_ACCOUNT_ID`
- `packages/lambda/.env`: `GEMINI_API_KEY`

### 2. Install dependencies

```bash
npm install
cd packages/lambda/src && pip install -r requirements.txt
```

### 3. Run local Lambda API

```bash
npm run lambda:test
```

This starts the local server with:

- graph source: `packages/lambda/examples/unified_diabetes_graph.json`
- health endpoint: `http://localhost:3001/health`

### 4. Run frontend

```bash
npm run frontend:start
```

### 5. Build frontend

```bash
npm run frontend:build
```

### 6. Optional CDK deploy

```bash
npm run deploy
```

## Local Development Flow

1. Install workspace dependencies with `npm install`.
2. Install Lambda Python dependencies from `packages/lambda/src/requirements.txt`.
3. Configure `.env` files including `GEMINI_API_KEY`.
4. Start local Lambda server using `npm run lambda:test`.
5. Start frontend using `npm run frontend:start`.
6. Verify backend health at `/health`.

## Frontend Notes

The React frontend includes:

- markdown-rendered answer output via `react-markdown`
- routing-based UI via `react-router-dom`
- graph visualization via Cytoscape (`cytoscape`, `cytoscape-panzoom`, `cytoscape-cose-bilkent`)
- key components for upload, chat, navigation, and graph display

## Infrastructure Notes

CDK stack responsibilities:

- `frontend-stack.ts`: S3 and CloudFront hosting for frontend delivery
- `graph-processing-stack.ts`: graph upload/processing path (S3 + Lambda + Neptune)
- `chat-api-stack.ts`: API Gateway + Lambda chat endpoint

## Prototype Note

This repository is a research and portfolio prototype focused on evidence tracing and explainable reasoning. It is not intended for direct clinical deployment or autonomous medical diagnosis.

## Docs

- setup guide: `docs/setup.md`
- architecture summary: `docs/architecture.md`
- lambda local testing: `packages/lambda/docs/local-testing.md`

## License

Apache-2.0
