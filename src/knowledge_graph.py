"""
Knowledge Graph Operations Wrapper
"""

from typing import List, Dict, Any
from loguru import logger
from database.graph_manager import graph_manager
from src.document_processor import DocumentChunk


class KnowledgeGraph:
    """High-level knowledge graph operations"""
    
    def __init__(self):
        self.manager = graph_manager
        logger.info("KnowledgeGraph initialized")
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to knowledge graph"""
        try:
            for chunk in chunks:
                self.manager.add_document_entities(
                    document=chunk.content,
                    metadata=chunk.metadata
                )
            return True
        except Exception as e:
            logger.error(f"Error adding chunks to knowledge graph: {e}")
            return False
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search knowledge graph"""
        try:
            results = self.manager.query_graph(query, max_results=top_k)
            return results.get('results', [])
        except Exception as e:
            logger.error(f"Error searching knowledge graph: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return self.manager.get_stats()
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """Get data for graph visualization"""
        return self.manager.get_graph_data()
    
    def reset(self) -> bool:
        """Reset knowledge graph"""
        return self.manager.reset()


# Global knowledge graph instance
knowledge_graph = KnowledgeGraph()
