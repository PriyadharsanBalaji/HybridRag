"""
Graph Visualizations
"""

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from typing import Dict, Any, List


def render_knowledge_graph(graph_data: Dict[str, Any]):
    """Render interactive knowledge graph"""
    nodes_data = graph_data.get('nodes', [])
    edges_data = graph_data.get('edges', [])
    
    if not nodes_data:
        st.info("No graph data available yet. Upload documents to build the knowledge graph.")
        return
    
    # Limit to top 50 nodes for performance
    nodes_data = nodes_data[:50]
    
    # Color mapping for entity types
    color_map = {
        'PERSON': '#FF6B6B',
        'ORG': '#4ECDC4',
        'GPE': '#45B7D1',
        'LOC': '#96CEB4',
        'PRODUCT': '#FFEAA7',
        'EVENT': '#DFE6E9',
        'DATE': '#74B9FF',
        'UNKNOWN': '#B2BEC3'
    }
    
    # Create nodes
    nodes = []
    for node_data in nodes_data:
        entity_type = node_data.get('type', 'UNKNOWN')
        nodes.append(
            Node(
                id=node_data['id'],
                label=node_data['label'][:30],  # Truncate long labels
                size=20,
                color=color_map.get(entity_type, '#B2BEC3'),
                title=f"{node_data['label']} ({entity_type})"
            )
        )
    
    # Create edges
    edges = []
    node_ids = {node.id for node in nodes}
    for edge_data in edges_data:
        if edge_data['source'] in node_ids and edge_data['target'] in node_ids:
            edges.append(
                Edge(
                    source=edge_data['source'],
                    target=edge_data['target'],
                    label=edge_data.get('relation', '')[:20],
                    color='#95A5A6'
                )
            )
    
    # Graph configuration
    config = Config(
        width=800,
        height=600,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7B731",
        collapsible=False,
        node={'labelProperty': 'label'},
        link={'labelProperty': 'label', 'renderLabel': True}
    )
    
    # Render graph
    if nodes:
        return_value = agraph(nodes=nodes, edges=edges, config=config)
