# Setup Guide

This guide provides a reproducible local setup flow for Graph-RAG Diabetes.

## 1) Prerequisites

- Node.js 18+
- npm
- Python 3.9+
- Optional: AWS CLI and configured credentials (for CDK deployment)

## 2) Environment Files

Create local env files from examples:

```bash
cp .env.example .env
cp packages/lambda/.env.example packages/lambda/.env
cp packages/frontend/.env.example packages/frontend/.env
cp packages/infrastructure/.env.example packages/infrastructure/.env
```

Minimum required for local chat functionality:

- `packages/lambda/.env`
  - `GEMINI_API_KEY`

## 3) Install Dependencies

From repository root:

```bash
npm install
pip install -r packages/lambda/src/requirements.txt
```

## 4) Start Frontend

```bash
cd packages/frontend
npm install
npm start
```

Default frontend URL: `http://localhost:3000`

## 5) Start Local Backend

```bash
cd packages/lambda/src
python local_http_server.py --port 3001 --graph-file unified_diabetes_graph.json
```

Default backend URL: `http://localhost:3001`

## 6) Quick Smoke Check

From repository root:

```bash
npm run smoke
```

This command validates key project files and environment examples are present.

## 7) Build and Synthesize Infrastructure

```bash
cd packages/infrastructure
npm install
npm run build

# from repo root
npm run synth
```

## 8) Troubleshooting

- If Lambda scripts cannot read env values, verify `.env` and `packages/lambda/.env` both exist.
- If frontend cannot reach backend, ensure backend is running on port 3001.
- If AWS/CDK commands fail, verify AWS credentials and region in local env.
