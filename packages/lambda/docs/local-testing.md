# Lambda Local Testing

This document describes local development for the Lambda package after runtime and support assets were separated.

## Folder Layout

- `src/`: runtime Python handlers and support modules
- `examples/`: sample graph payloads used for local testing
- `docs/`: local testing and Neptune helper documents
- `assets/`: generated graph images
- `notebooks/`: research notebooks

## Start Local API Server

From the repository root:

```bash
npm run lambda:test
```

Equivalent direct command:

```bash
cd packages/lambda/src
python load_env.py python local_http_server.py --port 3001 --graph-file ../examples/unified_diabetes_graph.json
```

## Alternate Local Test Inputs

```bash
cd packages/lambda
npm run local:test:json
npm run local:test:sample
```

`local:test:json` uses `examples/sample-graph.json`.

`local:test:sample` uses `examples/sample-graph.csv`.

## Local Endpoints

- `GET /health`
- `GET /api/graph?limit=100`
- `POST /api/chat`
- `POST /api/graph/query`
- `POST /api/graph/upload`

## Environment Variables

Required in `packages/lambda/.env`:

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (optional, defaults to `gemini-1.5-pro`)
- `NEPTUNE_ENDPOINT`
- `NEPTUNE_PORT`

If `GEMINI_API_KEY` is missing, the chat endpoint returns `500` with `Server configuration error`.

## Notes

- This repository is a research and educational prototype.
- Responses should be interpreted as evidence-guided support output, not direct clinical deployment guidance.
