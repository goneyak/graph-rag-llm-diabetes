# Setup Guide

This guide covers local setup for the Graph-RAG diabetes prototype monorepo.

## 1. Prerequisites

- Node.js 18+
- npm 9+
- Python 3.10+
- AWS CLI configured (for deploy only)

## 2. Initialize Environment Files

```bash
cp .env.example .env
cp packages/infrastructure/.env.example packages/infrastructure/.env
cp packages/lambda/.env.example packages/lambda/.env
cp packages/frontend/.env.example packages/frontend/.env
```

Set at minimum:

- `AWS_ACCOUNT_ID` in `.env`
- `GEMINI_API_KEY` in `packages/lambda/.env`

## 3. Install Dependencies

```bash
npm install
cd packages/lambda/src && pip install -r requirements.txt
```

## 4. Local Development Flow

1. Install root dependencies.
2. Install Python requirements for Lambda.
3. Set environment variables.
4. Run local Lambda server: `npm run lambda:test`.
5. Run frontend: `npm run frontend:start`.
6. Verify backend health: `http://localhost:3001/health`.

## 5. Build Frontend

```bash
npm run frontend:build
```

## 6. Optional CDK Deploy

```bash
npm run deploy
```

Or deploy by stack:

```bash
npm run deploy:frontend
npm run deploy:backend
npm run deploy:chatapi
```

## 7. Useful Commands

```bash
npm run smoke
npm run lambda:test
cd packages/lambda && npm run local:test:json
```
