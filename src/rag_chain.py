"""
RAG Chain Orchestration
Combines retrieval and generation
"""

import time
from typing import Dict, Any, Optional, List  # ADDED List here
from loguru import logger
from src.hybrid_retriever import hybrid_retriever
from src.llm_manager import llm_manager
from utils.metrics import metrics_tracker, QueryMetrics
from datetime import datetime


class RAGChain:
    """Orchestrate the complete RAG pipeline"""
    
    def __init__(self):
        self.retriever = hybrid_retriever
        self.llm = llm_manager
        logger.info("RAGChain initialized")
    
    def query(
        self,
        user_query: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute complete RAG pipeline
        1. Retrieve relevant context
        2. Generate response
        3. Track metrics
        """
        try:
            start_time = time.time()
            
            # Step 1: Retrieve context
            logger.info(f"Processing query: {user_query[:100]}...")
            retrieval_start = time.time()
            
            retrieval_results = self.retriever.retrieve(user_query)
            retrieval_time = time.time() - retrieval_start
            
            # Step 2: Build context
            context = self.retriever.build_context(retrieval_results)
            
            if not context:
                return {
                    'answer': "I couldn't find relevant information to answer your question. Please try rephrasing or upload relevant documents.",
                    'sources': [],
                    'retrieval_results': retrieval_results,
                    'metrics': {}
                }
            
            # Step 3: Generate response
            generation_start = time.time()
            
            if system_prompt is None:
                system_prompt = """You are a helpful AI assistant that answers questions based on provided context.
                
Instructions:
- Answer based ONLY on the provided context
- Be concise and accurate
- If the context doesn't contain the answer, say so clearly
- Cite sources when possible
- Use a professional but friendly tone
"""
            
            answer = self.llm.generate_response(
                query=user_query,
                context=context,
                system_prompt=system_prompt
            )
            
            generation_time = time.time() - generation_start
            total_time = time.time() - start_time
            
            # Step 4: Prepare sources
            sources = self._format_sources(retrieval_results)
            
            # Step 5: Track metrics
            metrics = QueryMetrics(
                query=user_query,
                timestamp=datetime.now(),
                retrieval_time=retrieval_time,
                generation_time=generation_time,
                total_time=total_time,
                vector_results=len(retrieval_results.get('vector_results', [])),
                graph_results=len(retrieval_results.get('graph_results', [])),
                total_tokens=len(context.split())
            )
            metrics_tracker.record_query(metrics)
            
            return {
                'answer': answer,
                'sources': sources,
                'retrieval_results': retrieval_results,
                'metrics': {
                    'retrieval_time': retrieval_time,
                    'generation_time': generation_time,
                    'total_time': total_time,
                    'vector_results': len(retrieval_results.get('vector_results', [])),
                    'graph_results': len(retrieval_results.get('graph_results', []))
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RAG chain: {e}")
            return {
                'answer': f"An error occurred: {str(e)}",
                'sources': [],
                'retrieval_results': {},
                'metrics': {}
            }
    
    def _format_sources(self, retrieval_results: Dict) -> List[Dict[str, Any]]:
        """Format sources for display"""
        sources = []
        
        # Vector search sources
        for result in retrieval_results.get('vector_results', []):
            metadata = result.get('metadata', {})
            sources.append({
                'type': 'Vector Search',
                'file': metadata.get('source', 'Unknown'),
                'page': metadata.get('page', 'N/A'),
                'similarity': f"{result.get('similarity', 0):.2%}",
                'content': result.get('content', '')[:200] + '...'
            })
        
        # Graph sources
        for result in retrieval_results.get('graph_results', []):
            sources.append({
                'type': 'Knowledge Graph',
                'entity': result.get('entity', 'Unknown'),
                'label': result.get('label', 'Unknown'),
                'neighbors': ', '.join(result.get('neighbors', [])[:3]),
                'content': f"Entity: {result.get('entity', '')}"
            })
        
        return sources


# Global RAG chain instance
rag_chain = RAGChain()
