import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from neptune_graph_builder import NeptuneGraphBuilder

def load_graph_data(json_file):
    """Load graph data from JSON file"""
    with open(json_file, 'r') as f:
        return json.load(f)

def create_networkx_graph(graph_data):
    """Create a NetworkX graph from the graph data"""
    G = nx.Graph()
    
    # Add document nodes
    for node in graph_data['document_nodes']:
        G.add_node(node['id'], label=node['title'], type='Document')
    
    # Add chunk nodes
    for node in graph_data['chunk_nodes']:
        G.add_node(node['id'], label=f"Chunk: {node['id']}", type='Chunk')
    
    # Add entity nodes
    for node in graph_data['entity_nodes']:
        G.add_node(node['id'], label=node['name'], type=node['type'])
    
    # Add edges
    for edge in graph_data['edges']:
        source_id, edge_type, target_id, props = edge
        G.add_edge(source_id, target_id, label=edge_type, **props)
    
    return G

def visualize_graph(G, title, output_file=None):
    """Visualize the graph using NetworkX and Matplotlib"""
    plt.figure(figsize=(14, 10))
    
    # Define node colors based on type
    node_colors = []
    for node in G.nodes():
        node_type = G.nodes[node].get('type', '')
        if node_type == 'Document':
            node_colors.append('lightblue')
        elif node_type == 'Chunk':
            node_colors.append('lightgreen')
        elif node_type == 'Disease':
            node_colors.append('salmon')
        elif node_type == 'Treatment' or node_type == 'Medication':
            node_colors.append('orange')
        elif node_type == 'Symptom':
            node_colors.append('yellow')
        else:
            node_colors.append('lightgray')
    
    # Define edge colors based on type
    edge_colors = []
    for u, v, data in G.edges(data=True):
        edge_type = data.get('label', '')
        if edge_type == 'CONTAINS':
            edge_colors.append('blue')
        elif edge_type == 'MENTIONS':
            edge_colors.append('green')
        elif edge_type == 'TREATS':
            edge_colors.append('red')
        elif edge_type == 'CAUSES':
            edge_colors.append('purple')
        elif edge_type == 'DIAGNOSES':
            edge_colors.append('brown')
        else:
            edge_colors.append('gray')
    
    # Create layout
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=1.5, alpha=0.7)
    
    # Draw labels
    node_labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
    
    # Draw edge labels for semantic relationships only
    edge_labels = {(u, v): data.get('label', '') for u, v, data in G.edges(data=True) 
                  if data.get('label', '') not in ['CONTAINS', 'MENTIONS']}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    plt.title(title)
    plt.axis('off')
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    plt.show()

def visualize_subgraph_by_type(G, central_type, title, output_file=None):
    """Visualize a subgraph centered around nodes of a specific type"""
    # Get all nodes of the specified type
    central_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type', '') == central_type]
    
    if not central_nodes:
        print(f"No nodes of type '{central_type}' found in the graph.")
        return
    
    # Create a subgraph with these nodes and their neighbors
    subgraph_nodes = set(central_nodes)
    for node in central_nodes:
        subgraph_nodes.update(G.neighbors(node))
    
    subgraph = G.subgraph(subgraph_nodes)
    
    # Visualize the subgraph
    visualize_graph(subgraph, title, output_file)

def main():
    # Check if the graph data file exists, if not, run the graph builder
    if not os.path.exists('neptune_graph_data.json'):
        print("Graph data file not found. Running graph builder...")
        builder = NeptuneGraphBuilder("datasets/chunks/diabetes_care")
        builder.build_graph()
    
    # Load the graph data
    graph_data = load_graph_data('neptune_graph_data.json')
    
    # Create a NetworkX graph
    G = create_networkx_graph(graph_data)
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Visualize the full graph
    visualize_graph(G, "Diabetes Knowledge Graph", "diabetes_knowledge_graph.png")
    
    # Visualize subgraphs centered around specific entity types
    visualize_subgraph_by_type(G, 'Disease', "Disease-Centered Subgraph", "disease_subgraph.png")
    visualize_subgraph_by_type(G, 'Treatment', "Treatment-Centered Subgraph", "treatment_subgraph.png")
    
    print("Visualization complete. Check the output PNG files.")

if __name__ == "__main__":
    main()
