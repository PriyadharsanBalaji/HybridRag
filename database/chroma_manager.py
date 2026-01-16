"""
ChromaDB Vector Store Manager - NO FILTERING VERSION
Free, embedded vector database
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger
from config import settings
from src.embeddings import embedding_manager


class ChromaManager:
    """Manage ChromaDB vector store operations"""
    
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIR
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        
        logger.info(f"Initializing ChromaDB at {self.persist_directory}")
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized. Collection: {self.collection_name}")
            logger.info(f"Current document count: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """Add documents to vector store"""
        try:
            logger.info(f"Generating embeddings for {len(documents)} documents")
            embeddings = embedding_manager.embed_texts(documents)
            
            logger.info(f"Adding {len(documents)} documents to ChromaDB")
            
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            # Verify addition
            new_count = self.collection.count()
            logger.info(f"✅ Added {len(documents)} documents. Total now: {new_count}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def query(
        self,
        query_text: str,
        n_results: int = None,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Query vector store with similarity search - RETURNS ALL RESULTS"""
        try:
            n_results = n_results or settings.TOP_K_VECTOR_RESULTS
            
            logger.info(f"🔍 Querying: '{query_text[:50]}...' (requesting {n_results} results)")
            
            # Check if collection is empty
            count = self.collection.count()
            if count == 0:
                logger.warning("❌ ChromaDB collection is empty!")
                return {'results': [], 'count': 0}
            
            logger.info(f"📊 Collection has {count} documents")
            
            # Generate query embedding
            query_embedding = embedding_manager.embed_text(query_text)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, count),
                where=where,
                where_document=where_document,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format ALL results (no filtering)
            formatted_results = []
            if results.get('documents') and results['documents'][0]:
                for idx in range(len(results['documents'][0])):
                    distance = results['distances'][0][idx]
                    similarity = 1 - distance
                    
                    result_data = {
                        'content': results['documents'][0][idx],
                        'metadata': results['metadatas'][0][idx],
                        'similarity': similarity,
                        'distance': distance,
                        'source': 'vector_store'
                    }
                    
                    formatted_results.append(result_data)
                    
                    logger.info(
                        f"  ✅ Result {idx+1}: "
                        f"similarity={similarity:.3f}, "
                        f"content_preview={results['documents'][0][idx][:50]}..."
                    )
            
            logger.info(f"✅ Returning {len(formatted_results)} results (NO FILTERING)")
            
            return {
                'results': formatted_results,
                'count': len(formatted_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Error querying ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return {'results': [], 'count': 0}
    
    def delete_by_source(self, source: str) -> bool:
        """Delete all documents from a specific source"""
        try:
            self.collection.delete(
                where={"source": source}
            )
            logger.info(f"Deleted documents from source: {source}")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def reset(self) -> bool:
        """Reset the entire collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB collection reset successfully")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False


# Global ChromaDB manager instance
chroma_manager = ChromaManager()
