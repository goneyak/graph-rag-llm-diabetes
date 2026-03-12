#!/usr/bin/env python3
"""
Unified Graph Builder for Diabetes Knowledge Graph

This script processes both the diabetes care chunks and the drug information,
extracts nodes and relationships, creates a unified graph, and dumps it to a file.
"""

import os
import json
import glob
import re
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class UnifiedGraphBuilder:
    def __init__(self, chunks_dir, drug_file):
        """
        Initialize the Unified Graph Builder
        
        Args:
            chunks_dir (str): Directory containing the processed chunk JSON files
            drug_file (str): Path to the drug information JSON file
        """
        self.chunks_dir = chunks_dir
        self.drug_file = drug_file
        
        # Initialize graph
        self.graph = nx.DiGraph()
        
        # Entity type mapping for better categorization
        self.entity_type_mapping = {
            'Diseases': 'Disease',
            'Medication Name': 'Medication',
            'Non-Medication Treatment': 'Treatment',
            'Clinical Manifestations': 'Symptom',
            'Examination Methods': 'ExaminationMethod',
            'Examination Indicators': 'ExaminationIndicator',
            'Medication Dosage': 'MedicationAttribute',
            'Medication Frequency': 'MedicationAttribute',
            'Medication Methods': 'MedicationAttribute',
            'Disease Staging and Classification': 'DiseaseAttribute',
            'Pathogenesis': 'DiseaseAttribute',
            'Cause': 'DiseaseAttribute',
            'Severity': 'SymptomAttribute',
            'Duration': 'TimeAttribute',
            'Location': 'AnatomicalLocation',
            'Surgery': 'Procedure',
            'Adverse Reactions': 'AdverseEffect',
            'Examination Indicator Values': 'LabValue'
        }
        
        # Define semantic relationships between entity types
        self.semantic_relationships = {
            ('Treatment', 'Disease'): 'TREATS',
            ('Medication', 'Disease'): 'TREATS',
            ('Disease', 'Symptom'): 'CAUSES',
            ('ExaminationMethod', 'Disease'): 'DIAGNOSES',
            ('Procedure', 'Disease'): 'TREATS',
            ('Disease', 'DiseaseAttribute'): 'HAS_ATTRIBUTE',
            ('Medication', 'MedicationAttribute'): 'HAS_ATTRIBUTE',
            ('Symptom', 'SymptomAttribute'): 'HAS_ATTRIBUTE',
            ('Disease', 'AdverseEffect'): 'CAUSES',
            ('Medication', 'AdverseEffect'): 'CAUSES',
            ('ExaminationIndicator', 'LabValue'): 'HAS_VALUE',
            ('Disease', 'AnatomicalLocation'): 'AFFECTS',
            ('Symptom', 'AnatomicalLocation'): 'OCCURS_AT'
        }
        
        # Drug relationship mapping
        self.drug_relationship_mapping = {
            'Mechanism': 'HAS_MECHANISM',
            'Indication': 'INDICATED_FOR',
            'Contraindication': 'CONTRAINDICATED_FOR',
            'Interaction': 'INTERACTS_WITH',
            'Warning': 'HAS_WARNING',
            'Population': 'USED_IN_POPULATION',
            'PregnancyGuidance': 'HAS_PREGNANCY_GUIDANCE',
            'AdverseEffect': 'HAS_ADVERSE_EFFECT'
        }
    
    def load_chunks(self):
        """Load all chunk files from the specified directory"""
        chunk_files = glob.glob(os.path.join(self.chunks_dir, "*.json"))
        chunks = []
        
        for file_path in chunk_files:
            try:
                with open(file_path, 'r') as f:
                    chunk_data = json.load(f)
                    chunk_id = os.path.basename(file_path).replace('.json', '')
                    chunk_data['chunk_id'] = chunk_id
                    chunks.append(chunk_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(chunks)} chunks")
        return chunks
    
    def load_drug_data(self):
        """Load drug data from the specified file"""
        try:
            with open(self.drug_file, 'r') as f:
                drug_data = json.load(f)
            print(f"Loaded drug data with {len(drug_data)} entries")
            return drug_data
        except Exception as e:
            print(f"Error loading drug data: {e}")
            return []
    
    def process_chunks(self, chunks):
        """Process chunks and add nodes and edges to the graph"""
        # Track document sources
        documents = {}
        
        # Process each chunk
        for chunk in chunks:
            chunk_id = chunk.get('chunk_id', '')
            if not chunk_id:
                continue
            
            # Add chunk node
            self.graph.add_node(chunk_id, 
                               type='Chunk', 
                               text=chunk.get('text', ''),
                               intent=chunk.get('intent', []))
            
            # Add document node if not exists
            source = chunk.get('source', '')
            if source:
                doc_id = source.split('.')[0]
                if doc_id not in documents:
                    documents[doc_id] = source
                    self.graph.add_node(doc_id, 
                                       type='Document', 
                                       source=source,
                                       title=f"Document {doc_id}")
                
                # Add edge from document to chunk
                self.graph.add_edge(doc_id, chunk_id, 
                                   type='CONTAINS', 
                                   weight=1.0)
            
            # Process entities
            entities = chunk.get('entities', {})
            for entity_category, entity_list in entities.items():
                if entity_category in self.entity_type_mapping and entity_list:
                    entity_type = self.entity_type_mapping[entity_category]
                    
                    for entity_name in entity_list:
                        if not entity_name:
                            continue
                        
                        # Create a unique ID for the entity
                        entity_id = self._normalize_entity_id(entity_name, entity_type)
                        
                        # Add entity node if not exists
                        if not self.graph.has_node(entity_id):
                            self.graph.add_node(entity_id, 
                                               type=entity_type, 
                                               name=entity_name,
                                               category=entity_category)
                        
                        # Add edge from chunk to entity
                        self.graph.add_edge(chunk_id, entity_id, 
                                           type='MENTIONS', 
                                           weight=1.0)
        
        # Create semantic edges between entities based on co-occurrence in chunks
        self._create_semantic_edges()
    
    def process_drug_data(self, drug_data):
        """Process drug data and add nodes and edges to the graph"""
        for drug_entry in drug_data:
            # Get drug name
            drug_name = drug_entry.get('drug_name', '')
            if not drug_name:
                continue
            
            # Create drug node
            drug_id = self._normalize_entity_id(drug_name, 'Drug')
            self.graph.add_node(drug_id, 
                               type='Drug', 
                               name=drug_name)
            
            # Process each relationship type
            for rel_type, edge_type in self.drug_relationship_mapping.items():
                if rel_type in drug_entry:
                    for item in drug_entry[rel_type]:
                        item_id = item.get('id', '')
                        item_label = item.get('label', '')
                        
                        if item_id and item_label:
                            # Add node for the item
                            self.graph.add_node(item_id, 
                                               type=rel_type, 
                                               label=item_label)
                            
                            # Add edge from drug to item
                            self.graph.add_edge(drug_id, item_id, 
                                               type=edge_type, 
                                               weight=1.0)
    
    def _create_semantic_edges(self):
        """Create semantic edges between entities based on co-occurrence in chunks"""
        # Find all chunks
        chunks = [n for n, attrs in self.graph.nodes(data=True) if attrs.get('type') == 'Chunk']
        
        # For each chunk, find entities mentioned and create semantic edges
        for chunk_id in chunks:
            # Get entities mentioned in this chunk
            entities = [n for n in self.graph.successors(chunk_id) 
                       if self.graph.nodes[n].get('type') != 'Document']
            
            # Create semantic edges between entities
            for i, entity_id1 in enumerate(entities):
                entity1_type = self.graph.nodes[entity_id1].get('type', '')
                
                for entity_id2 in entities[i+1:]:
                    entity2_type = self.graph.nodes[entity_id2].get('type', '')
                    
                    # Check if there's a defined semantic relationship
                    rel_type = None
                    if (entity1_type, entity2_type) in self.semantic_relationships:
                        rel_type = self.semantic_relationships[(entity1_type, entity2_type)]
                        source_id, target_id = entity_id1, entity_id2
                    elif (entity2_type, entity1_type) in self.semantic_relationships:
                        rel_type = self.semantic_relationships[(entity2_type, entity1_type)]
                        source_id, target_id = entity_id2, entity_id1
                    
                    if rel_type:
                        # Add semantic edge
                        self.graph.add_edge(source_id, target_id, 
                                           type=rel_type, 
                                           weight=1.0,
                                           source_chunk=chunk_id)
                    else:
                        # For entities without a defined relationship, create a generic RELATED_TO edge
                        # Only if they're different types to avoid too many edges
                        if entity1_type != entity2_type:
                            self.graph.add_edge(entity_id1, entity_id2, 
                                               type='RELATED_TO', 
                                               weight=0.5,
                                               source_chunk=chunk_id)
    
    def _normalize_entity_id(self, entity_name, entity_type):
        """Create a normalized ID for an entity"""
        # Remove special characters and spaces, convert to lowercase
        normalized = re.sub(r'[^a-zA-Z0-9]', '_', entity_name.lower())
        # Truncate if too long
        if len(normalized) > 50:
            normalized = normalized[:50]
        # Add entity type as prefix
        return f"{entity_type.lower()}_{normalized}"
    
    def build_graph(self):
        """Build the complete graph"""
        # Load data
        chunks = self.load_chunks()
        drug_data = self.load_drug_data()
        
        # Process data
        self.process_chunks(chunks)
        self.process_drug_data(drug_data)
        
        return self.graph
    
    def save_graph(self, output_file):
        """Save the graph to a file"""
        # Convert graph to a serializable format
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        # Add nodes
        for node_id, attrs in self.graph.nodes(data=True):
            node_data = {'id': node_id}
            node_data.update(attrs)
            graph_data['nodes'].append(node_data)
        
        # Add edges
        for source, target, attrs in self.graph.edges(data=True):
            edge_data = {
                'source': source,
                'target': target
            }
            edge_data.update(attrs)
            graph_data['edges'].append(edge_data)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"Saved graph to {output_file}")
    
    def generate_statistics(self):
        """Generate statistics about the graph"""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': defaultdict(int),
            'edge_types': defaultdict(int)
        }
        
        # Count node types
        for _, attrs in self.graph.nodes(data=True):
            node_type = attrs.get('type', 'Unknown')
            stats['node_types'][node_type] += 1
        
        # Count edge types
        for _, _, attrs in self.graph.edges(data=True):
            edge_type = attrs.get('type', 'Unknown')
            stats['edge_types'][edge_type] += 1
        
        return stats
    
    def visualize_graph(self, output_file=None, max_nodes=100):
        """Visualize the graph (limited to max_nodes for readability)"""
        if self.graph.number_of_nodes() > max_nodes:
            print(f"Graph has {self.graph.number_of_nodes()} nodes, showing a sample of {max_nodes} nodes")
            # Create a subgraph with a sample of nodes
            nodes = list(self.graph.nodes())[:max_nodes]
            subgraph = self.graph.subgraph(nodes)
        else:
            subgraph = self.graph
        
        plt.figure(figsize=(14, 10))
        
        # Define node colors based on type
        node_colors = []
        for node in subgraph.nodes():
            node_type = subgraph.nodes[node].get('type', '')
            if node_type == 'Document':
                node_colors.append('lightblue')
            elif node_type == 'Chunk':
                node_colors.append('lightgreen')
            elif node_type == 'Disease':
                node_colors.append('salmon')
            elif node_type in ['Treatment', 'Medication', 'Drug']:
                node_colors.append('orange')
            elif node_type == 'Symptom':
                node_colors.append('yellow')
            elif node_type == 'AdverseEffect':
                node_colors.append('red')
            elif node_type == 'Mechanism':
                node_colors.append('purple')
            elif node_type == 'Indication':
                node_colors.append('cyan')
            else:
                node_colors.append('lightgray')
        
        # Create layout
        pos = nx.spring_layout(subgraph, seed=42)
        
        # Draw nodes
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=500, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(subgraph, pos, width=1.5, alpha=0.7)
        
        # Draw labels
        node_labels = {}
        for node in subgraph.nodes():
            if 'name' in subgraph.nodes[node]:
                node_labels[node] = subgraph.nodes[node]['name']
            elif 'label' in subgraph.nodes[node]:
                # Truncate long labels
                label = subgraph.nodes[node]['label']
                if len(label) > 20:
                    label = label[:20] + '...'
                node_labels[node] = label
            else:
                node_labels[node] = node
        
        nx.draw_networkx_labels(subgraph, pos, labels=node_labels, font_size=8)
        
        plt.title("Unified Diabetes Knowledge Graph")
        plt.axis('off')
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        plt.show()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Paths to data
    chunks_dir = "datasets/chunks/diabetes_care"
    drug_file = "datasets/diatetic_structured_with_ids.json"
    
    # Create the graph builder
    builder = UnifiedGraphBuilder(chunks_dir, drug_file)
    
    # Build the graph
    graph = builder.build_graph()
    
    # Generate statistics
    stats = builder.generate_statistics()
    
    # Print statistics
    print("\nGraph Statistics:")
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Total edges: {stats['total_edges']}")
    
    print("\nNode Types:")
    for node_type, count in sorted(stats['node_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"- {node_type}: {count}")
    
    print("\nEdge Types:")
    for edge_type, count in sorted(stats['edge_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"- {edge_type}: {count}")
    
    # Save the graph to a file
    builder.save_graph(os.path.normpath(os.path.join(base_dir, '..', 'examples', 'unified_diabetes_graph.json')))
    
    # Visualize the graph
    builder.visualize_graph(os.path.normpath(os.path.join(base_dir, '..', 'assets', 'unified_diabetes_graph.png')))


if __name__ == "__main__":
    main()
