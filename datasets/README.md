# Unified Diabetes Knowledge Graph

This project provides tools to extract nodes and edges from multiple data sources related to diabetes care and prepare them for indexing in an Amazon Neptune graph database. The implementation focuses on creating semantically relevant relationships between different node types.

## Overview

The solution extracts nodes and relationships from two main data sources:

1. **Diabetes Care Chunks**: Processed text chunks with extracted entities and intents
2. **Drug Information**: Structured data about drugs, including mechanisms, indications, contraindications, etc.

The solution creates a unified graph with the following node types:

1. **Document Nodes**: Representing source documents
2. **Chunk Nodes**: Representing text chunks from documents
3. **Entity Nodes**: Representing medical entities extracted from chunks, categorized into types like:
   - Disease
   - Treatment
   - Medication
   - Symptom
   - ExaminationMethod
   - And many others
4. **Drug Nodes**: Representing drugs from the structured drug data
5. **Drug-Related Nodes**: Representing drug mechanisms, indications, contraindications, etc.

The solution also creates semantically meaningful edges between these nodes:

1. **Basic Edges**:
   - `CONTAINS`: Document → Chunk
   - `MENTIONS`: Chunk → Entity

2. **Semantic Edges** (based on co-occurrence and entity types):
   - `TREATS`: Treatment/Medication → Disease
   - `CAUSES`: Disease → Symptom
   - `DIAGNOSES`: ExaminationMethod → Disease
   - `HAS_ATTRIBUTE`: Entity → Attribute
   - `AFFECTS`: Disease → AnatomicalLocation
   - And others based on entity type relationships

3. **Drug-Related Edges**:
   - `HAS_MECHANISM`: Drug → Mechanism
   - `INDICATED_FOR`: Drug → Indication
   - `CONTRAINDICATED_FOR`: Drug → Contraindication
   - `INTERACTS_WITH`: Drug → Interaction
   - `HAS_WARNING`: Drug → Warning
   - `USED_IN_POPULATION`: Drug → Population
   - `HAS_PREGNANCY_GUIDANCE`: Drug → PregnancyGuidance
   - `HAS_ADVERSE_EFFECT`: Drug → AdverseEffect

## Files

- `unified_graph_builder.py`: Main class for building a unified graph from multiple data sources
- `graph_to_neptune.py`: Script to convert the unified graph to Neptune-compatible Gremlin queries
- `neptune_query_examples.py`: Example queries for the Neptune database
- `visualize_graph.py`: Script to visualize the generated graph using NetworkX and Matplotlib
- `run_graph_builder.py`: Script to run the graph builder and display statistics
- `neptune_gremlin_queries.txt`: Generated Gremlin queries for Neptune insertion (created when running the scripts)
- `unified_diabetes_graph.json`: The unified graph data (created when running the scripts)

## Usage

### Building the Unified Graph

To build the unified graph from both data sources:

```bash
python unified_graph_builder.py
```

This will:
1. Load and process the diabetes care chunks
2. Load and process the drug information
3. Create a unified graph with nodes and edges from both sources
4. Save the graph to `unified_diabetes_graph.json`
5. Generate statistics about the graph
6. Create a visualization of the graph

### Converting the Graph to Neptune Gremlin Queries

To convert the unified graph to Neptune-compatible Gremlin queries:

```bash
python graph_to_neptune.py --input unified_diabetes_graph.json --output neptune_gremlin_queries.txt --bucket your-s3-bucket
```

This will:
1. Load the unified graph from `unified_diabetes_graph.json`
2. Generate Gremlin queries for Neptune insertion
3. Save the queries to `neptune_gremlin_queries.txt`
4. Generate a Neptune Loader manifest file
5. Generate Neptune Loader commands for reference

### Visualizing the Graph

To visualize the graph:

```bash
python visualize_graph.py
```

This will:
1. Create visualizations of the full graph and subgraphs
2. Save the visualizations as PNG files

## Graph Schema

### Node Labels

- `Document`: Source documents
- `Chunk`: Text chunks from documents
- Entity types:
  - `Disease`
  - `Treatment`
  - `Medication`
  - `Symptom`
  - `ExaminationMethod`
  - `ExaminationIndicator`
  - `MedicationAttribute`
  - `DiseaseAttribute`
  - `SymptomAttribute`
  - `TimeAttribute`
  - `AnatomicalLocation`
  - `Procedure`
  - `AdverseEffect`
  - `LabValue`
- Drug-related types:
  - `Drug`
  - `Mechanism`
  - `Indication`
  - `Contraindication`
  - `Interaction`
  - `Warning`
  - `Population`
  - `PregnancyGuidance`
  - `AdverseEffect`

### Edge Labels

- Basic edges:
  - `CONTAINS`: Document contains Chunk
  - `MENTIONS`: Chunk mentions Entity
- Semantic edges:
  - `TREATS`: Treatment/Medication treats Disease
  - `CAUSES`: Disease causes Symptom/AdverseEffect
  - `DIAGNOSES`: ExaminationMethod diagnoses Disease
  - `HAS_ATTRIBUTE`: Entity has Attribute
  - `HAS_VALUE`: Indicator has Value
  - `AFFECTS`: Disease affects AnatomicalLocation
  - `OCCURS_AT`: Symptom occurs at AnatomicalLocation
  - `RELATED_TO`: Generic relationship between entities
- Drug-related edges:
  - `HAS_MECHANISM`: Drug has Mechanism
  - `INDICATED_FOR`: Drug is indicated for Indication
  - `CONTRAINDICATED_FOR`: Drug is contraindicated for Contraindication
  - `INTERACTS_WITH`: Drug interacts with Interaction
  - `HAS_WARNING`: Drug has Warning
  - `USED_IN_POPULATION`: Drug is used in Population
  - `HAS_PREGNANCY_GUIDANCE`: Drug has PregnancyGuidance
  - `HAS_ADVERSE_EFFECT`: Drug has AdverseEffect

## Neptune Integration

The generated Gremlin queries can be used to insert the nodes and edges into an Amazon Neptune database. The queries are saved in the `neptune_gremlin_queries.txt` file.

### Using the Neptune Loader

The `graph_to_neptune.py` script generates the necessary files and commands for using the Neptune Loader:

1. Upload the Gremlin queries file and manifest to S3:
```bash
aws s3 cp neptune_gremlin_queries.txt s3://<your-bucket>/
aws s3 cp neptune-manifest.json s3://<your-bucket>/
```

2. Start the Neptune Loader job:
```bash
curl -X POST \
    -H 'Content-Type: application/json' \
    https://<your-neptune-endpoint>:8182/loader \
    -d '{
        "source" : "s3://<your-bucket>/neptune-manifest.json",
        "format" : "csv",
        "iamRoleArn" : "arn:aws:iam::<account-id>:role/<role-name>",
        "region" : "us-east-1",
        "failOnError" : "FALSE"
    }'
```

3. Check the status of the loader job:
```bash
curl -G https://<your-neptune-endpoint>:8182/loader/<load-id>
```

### Using a Gremlin Client

You can also execute the queries directly using a Gremlin client:

```python
from gremlin_python.driver import client

# Connect to Neptune
neptune_client = client.Client('wss://<neptune-endpoint>:8182/gremlin', 'g')

# Execute the queries
with open('neptune_gremlin_queries.txt', 'r') as f:
    for query in f:
        if query.strip():
            neptune_client.submit(query.strip())
```

## Extending the Solution

To extend this solution:

1. **Add more entity types**: Update the `entity_type_mapping` dictionary in `UnifiedGraphBuilder`
2. **Define new semantic relationships**: Update the `semantic_relationships` dictionary
3. **Add new drug relationship types**: Update the `drug_relationship_mapping` dictionary
4. **Enhance edge properties**: Modify the edge creation methods to add more properties to edges
5. **Add more data sources**: Create new methods to process additional data sources

## Requirements

- Python 3.6+
- NetworkX
- Matplotlib
- (Optional) gremlinpython for Neptune integration
