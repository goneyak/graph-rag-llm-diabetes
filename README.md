# Graph-RAG for Evidence-Based Diabetes Care

An interactive Graph-RAG system for precision diabetes care that combines ADA clinical practice guidelines and FDA drug label data into a queryable medical knowledge graph. The goal is to produce evidence-backed answers that are traceable to structured biomedical relationships rather than flat text retrieval alone.

## Why This Project

Traditional diabetes care relies heavily on population-level guidance, while real clinical decisions depend on relationships across diagnoses, medications, lab values, contraindications, adverse effects, and treatment pathways. Standard RAG pipelines flatten that structure into text chunks and make it harder to inspect why a recommendation was produced.

This project addresses that gap by:

- integrating guideline and drug-label knowledge into a unified graph
- extracting clinical intents and entities from user queries
- retrieving relevant subgraphs instead of only nearby text
- generating answers with supporting graph context and provenance

## Key Results

- Average accuracy above the MRCP Endocrinology and Diabetes passing threshold on a sample-question benchmark reported in the project poster and final report
- Knowledge graph built from curated diabetes sources with 5,488 nodes and 39,929 edges
- Interactive UI for question answering plus graph-based evidence tracing

## System Overview

The system is organized as a modular Graph-RAG pipeline:

1. Data ingestion from ADA guideline PDFs and FDA or DailyMed drug-label data
2. Intent detection and entity extraction over clinical text and user questions
3. Knowledge-graph construction with typed nodes and semantically labeled edges
4. Subgraph retrieval for context selection
5. LLM-based response generation grounded in retrieved graph evidence
6. Frontend visualization of answers, entities, and graph structure

## Architecture

This repository uses a monorepo layout, but the primary product is a diabetes Graph-RAG application rather than a generic AWS template.

- `packages/frontend`: React interface for chat and graph visualization
- `packages/infrastructure`: AWS CDK stacks for deployment and cloud resources
- `packages/lambda`: Python backend logic for graph processing, local serving, and chat orchestration
- `datasets`: diabetes guideline assets, annotation resources, and structured data
- `docs`: project poster and final report

At a high level, the deployed system combines:

- React for the user-facing chat and graph UI
- AWS CDK for infrastructure definition
- Lambda and API Gateway for backend orchestration
- Amazon Neptune for graph storage and retrieval
- LLM-based intent extraction and answer generation

## Repository Structure

```text
.
├── datasets/
│   ├── diabetes_care/              # ADA guideline PDFs
│   ├── 0521_new_format/            # Structured chunk outputs
│   ├── diatetic_structured_with_ids.json
│   ├── Annotation_Guidelines_English.md
│   └── README.md
├── docs/
│   ├── team178poster.pdf
│   └── team178report.pdf
├── packages/
│   ├── frontend/                   # React UI
│   ├── infrastructure/             # AWS CDK stacks
│   └── lambda/
│       └── src/                    # Python graph and chat logic
├── package.json
└── tsconfig.json
```

## Data Assets

The repository currently combines two main knowledge sources:

- ADA diabetes care guideline documents processed into structured chunk-level assets
- diabetes-related drug-label information transformed into structured graph entities

The resulting graph includes node types such as disease, treatment, medication, symptom, examination method, indication, contraindication, interaction, and warning.

## Getting Started

For a full reproducible setup flow, see `docs/setup.md`.

### Prerequisites

- Node.js 18+
- npm
- Python 3.9+
- AWS credentials and service configuration if you plan to deploy cloud infrastructure

### Install Dependencies

```bash
npm install
pip install -r packages/lambda/src/requirements.txt
```

### Start the Frontend

```bash
cd packages/frontend
npm install
npm start
```

### Run the Local Backend Server

```bash
cd packages/lambda/src
python local_http_server.py --port 3001 --graph-file unified_diabetes_graph.json
```

### Build Infrastructure Code

```bash
cd packages/infrastructure
npm install
npm run build
```

### Synthesize CDK

```bash
npm run synth
```

Note: Deployment and environment-variable setup still need cleanup. This repository contains working project code, but some packaging and configuration surfaces remain prototype-level.

### Quick Smoke Check

```bash
npm run smoke
```

## Research Basis

The current README is aligned with the materials in:

- `docs/team178report.pdf`
- `docs/team178poster.pdf`

Those documents describe the project motivation, architecture, benchmark framing, and reported outcomes.

## Limitations

- This is a research prototype, not a clinical decision-support tool for real-world prescribing
- Some repository metadata and package naming still reflect earlier template scaffolding
- Setup and deployment documentation are not yet fully standardized
- Evaluation is still limited compared with the level of validation expected for production medical software

## Roadmap

- clean up remaining template-era naming and UI labels
- align package metadata, README, and frontend branding
- improve setup documentation and environment configuration
- separate research artifacts from deployment-oriented code more cleanly
- expand evaluation documentation and demo assets

## Acknowledgments

Team 178: Jad Mokdad, Mehul Goenka, Huu Khue Pham, Sriya Shabadu, Goyeun Yun
