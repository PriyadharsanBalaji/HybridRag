"""
Vector Store Operations Wrapper
"""

from typing import List, Dict, Any
from loguru import logger
from database.chroma_manager import chroma_manager
from src.document_processor import DocumentChunk


class VectorStore:
    """High-level vector store operations"""
    
    def __init__(self):
        self.manager = chroma_manager
        logger.info("VectorStore initialized")
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to vector store"""
        try:
            documents = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [chunk.chunk_id for chunk in chunks]
            
            return self.manager.add_documents(documents, metadatas, ids)
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")
            return False
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search vector store"""
        try:
            results = self.manager.query(query, n_results=top_k)
            return results.get('results', [])
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return self.manager.get_stats()
    
    def reset(self) -> bool:
        """Reset vector store"""
        return self.manager.reset()


# Global vector store instance
vector_store = VectorStore()
