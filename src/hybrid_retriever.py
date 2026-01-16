"""
Hybrid Retriever combining Vector Search and Knowledge Graph
"""

from typing import List, Dict, Any
from loguru import logger
from config import settings
from src.vector_store import vector_store
from src.knowledge_graph import knowledge_graph


class HybridRetriever:
    """Combine vector search and knowledge graph retrieval"""
    
    def __init__(self):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        logger.info("HybridRetriever initialized")
    
    def retrieve(self, query: str) -> Dict[str, Any]:
        """
        Retrieve relevant information using both methods
        Returns combined results with sources
        """
        try:
            # Vector search
            logger.info("Performing vector search...")
            vector_results = self.vector_store.search(
                query,
                top_k=settings.TOP_K_VECTOR_RESULTS
            )
            
            # Knowledge graph search
            graph_results = []
            if settings.ENABLE_KNOWLEDGE_GRAPH:
                logger.info("Performing knowledge graph search...")
                graph_results = self.knowledge_graph.search(
                    query,
                    top_k=settings.TOP_K_GRAPH_RESULTS
                )
            
            # Combine and rank results
            combined_results = self._combine_results(vector_results, graph_results)
            
            logger.info(
                f"Retrieved {len(vector_results)} vector results, "
                f"{len(graph_results)} graph results"
            )
            
            return {
                'vector_results': vector_results,
                'graph_results': graph_results,
                'combined_results': combined_results,
                'total_results': len(combined_results)
            }
            
        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {e}")
            return {
                'vector_results': [],
                'graph_results': [],
                'combined_results': [],
                'total_results': 0
            }
    
    def _combine_results(
        self,
        vector_results: List[Dict],
        graph_results: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Combine and deduplicate results from both sources"""
        combined = []
        seen_content = set()
        
        # Add vector results
        for result in vector_results:
            content = result.get('content', '')
            if content and content not in seen_content:
                combined.append({
                    'content': content,
                    'metadata': result.get('metadata', {}),
                    'score': result.get('similarity', 0.0),
                    'source_type': 'vector_search'
                })
                seen_content.add(content)
        
        # Add graph results (entity information)
        for result in graph_results:
            entity = result.get('entity', '')
            if entity:
                # Create informative text from graph data
                content = self._format_graph_result(result)
                if content and content not in seen_content:
                    combined.append({
                        'content': content,
                        'metadata': {'entity': entity, 'label': result.get('label')},
                        'score': 0.8,  # Fixed score for graph results
                        'source_type': 'knowledge_graph'
                    })
                    seen_content.add(content)
        
        # Sort by score (descending)
        combined.sort(key=lambda x: x['score'], reverse=True)
        
        return combined
    
    def _format_graph_result(self, result: Dict) -> str:
        """Format graph result into readable text"""
        entity = result.get('entity', '')
        label = result.get('label', '')
        neighbors = result.get('neighbors', [])
        
        text_parts = [f"Entity: {entity} (Type: {label})"]
        
        if neighbors:
            text_parts.append(f"Related entities: {', '.join(neighbors[:5])}")
        
        return " | ".join(text_parts)
    
    def build_context(self, retrieval_results: Dict[str, Any], max_length: int = 3000) -> str:
        """Build context string from retrieval results"""
        combined = retrieval_results.get('combined_results', [])
        
        context_parts = []
        current_length = 0
        
        for idx, result in enumerate(combined, 1):
            content = result.get('content', '')
            source_type = result.get('source_type', 'unknown')
            
            section = f"[Source {idx} - {source_type}]\n{content}\n"
            section_length = len(section)
            
            if current_length + section_length > max_length:
                break
            
            context_parts.append(section)
            current_length += section_length
        
        return "\n".join(context_parts)


# Global hybrid retriever instance
hybrid_retriever = HybridRetriever()
