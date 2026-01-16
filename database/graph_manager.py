"""
Knowledge Graph Manager using NetworkX
Free, in-memory graph database
"""

from typing import List, Dict, Any, Tuple, Set
import networkx as nx
from collections import defaultdict
from loguru import logger
from config import settings
from src.entity_extractor import entity_extractor


class GraphManager:
    """Manage knowledge graph using NetworkX"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph
        self.entity_index = defaultdict(list)  # Entity -> Document mapping
        logger.info("Knowledge Graph initialized with NetworkX")
    
    def add_document_entities(
        self,
        document: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Extract entities and add to graph"""
        try:
            # Extract entities
            entities = entity_extractor.extract_entities(document)
            
            # Extract relationships
            relationships = entity_extractor.extract_relationships(document)
            
            # Add entities as nodes
            for entity in entities:
                entity_text = entity['text'].lower().strip()
                entity_label = entity['label']
                
                if entity_text not in self.graph:
                    self.graph.add_node(
                        entity_text,
                        label=entity_label,
                        type='entity',
                        documents=[]
                    )
                
                # Add document reference
                self.graph.nodes[entity_text]['documents'].append({
                    'source': metadata.get('source', 'unknown'),
                    'chunk_id': metadata.get('chunk_id', 'unknown')
                })
                
                # Update entity index
                self.entity_index[entity_text].append(metadata.get('chunk_id'))
            
            # Add relationships as edges
            for subject, relation, obj in relationships:
                subject = subject.lower().strip()
                obj = obj.lower().strip()
                
                if subject and obj:
                    if subject not in self.graph:
                        self.graph.add_node(subject, type='entity')
                    if obj not in self.graph:
                        self.graph.add_node(obj, type='entity')
                    
                    self.graph.add_edge(
                        subject,
                        obj,
                        relation=relation,
                        source=metadata.get('source', 'unknown')
                    )
            
            logger.info(f"Added {len(entities)} entities and {len(relationships)} relationships")
            return True
            
        except Exception as e:
            logger.error(f"Error adding entities to graph: {e}")
            return False
    
    def query_graph(
        self,
        query: str,
        max_results: int = None
    ) -> Dict[str, Any]:
        """Query graph for relevant entities and relationships"""
        try:
            max_results = max_results or settings.TOP_K_GRAPH_RESULTS
            
            # Extract entities from query
            query_entities = entity_extractor.extract_entities(query)
            
            results = []
            
            for entity in query_entities:
                entity_text = entity['text'].lower().strip()
                
                if entity_text in self.graph:
                    # Get node information
                    node_data = self.graph.nodes[entity_text]
                    
                    # Get neighbors (connected entities)
                    neighbors = list(self.graph.neighbors(entity_text))
                    predecessors = list(self.graph.predecessors(entity_text))
                    
                    # Get related documents
                    related_docs = node_data.get('documents', [])
                    
                    results.append({
                        'entity': entity_text,
                        'label': node_data.get('label', 'UNKNOWN'),
                        'neighbors': neighbors[:5],  # Top 5 neighbors
                        'predecessors': predecessors[:5],
                        'documents': related_docs,
                        'source': 'knowledge_graph'
                    })
            
            logger.info(f"Graph query returned {len(results)} entity matches")
            
            return {
                'results': results[:max_results],
                'count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error querying graph: {e}")
            return {'results': [], 'count': 0}
    
    def get_related_entities(
        self,
        entity: str,
        max_depth: int = None
    ) -> List[str]:
        """Get entities related to given entity within max_depth"""
        max_depth = max_depth or settings.MAX_GRAPH_DEPTH
        entity = entity.lower().strip()
        
        if entity not in self.graph:
            return []
        
        try:
            # BFS to find related entities
            related = set()
            visited = set()
            queue = [(entity, 0)]
            
            while queue:
                current, depth = queue.pop(0)
                
                if depth > max_depth or current in visited:
                    continue
                
                visited.add(current)
                related.add(current)
                
                # Add neighbors
                for neighbor in self.graph.neighbors(current):
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))
                
                # Add predecessors
                for predecessor in self.graph.predecessors(current):
                    if predecessor not in visited:
                        queue.append((predecessor, depth + 1))
            
            return list(related)
            
        except Exception as e:
            logger.error(f"Error getting related entities: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        try:
            return {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
                "avg_degree": sum(dict(self.graph.degree()).values()) / max(self.graph.number_of_nodes(), 1),
                "is_directed": self.graph.is_directed()
            }
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            return {}
    
    def get_graph_data(self) -> Dict[str, Any]:
        """Get graph data for visualization"""
        try:
            nodes = []
            edges = []
            
            for node in self.graph.nodes():
                nodes.append({
                    'id': node,
                    'label': node,
                    'type': self.graph.nodes[node].get('label', 'UNKNOWN')
                })
            
            for source, target in self.graph.edges():
                edge_data = self.graph[source][target]
                edges.append({
                    'source': source,
                    'target': target,
                    'relation': edge_data.get('relation', 'related_to')
                })
            
            return {
                'nodes': nodes,
                'edges': edges
            }
            
        except Exception as e:
            logger.error(f"Error getting graph data: {e}")
            return {'nodes': [], 'edges': []}
    
    def reset(self) -> bool:
        """Reset the graph"""
        try:
            self.graph.clear()
            self.entity_index.clear()
            logger.info("Knowledge graph reset successfully")
            return True
        except Exception as e:
            logger.error(f"Error resetting graph: {e}")
            return False


# Global graph manager instance
graph_manager = GraphManager()
