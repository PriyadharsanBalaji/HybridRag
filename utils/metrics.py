"""Performance Metrics Tracking"""

import time
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger


@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    query: str
    timestamp: datetime
    retrieval_time: float
    generation_time: float
    total_time: float
    vector_results: int
    graph_results: int
    total_tokens: int


class MetricsTracker:
    """Track and analyze system performance"""
    
    def __init__(self):
        self.queries: List[QueryMetrics] = []
        self.total_queries = 0
        self.total_documents_processed = 0
        self.start_time = datetime.now()
    
    def record_query(self, metrics: QueryMetrics):
        """Record query metrics"""
        self.queries.append(metrics)
        self.total_queries += 1
        logger.info(f"Query processed in {metrics.total_time:.2f}s")
    
    def get_average_metrics(self) -> Dict:
        """Calculate average performance metrics"""
        if not self.queries:
            return {}
        
        return {
            "avg_retrieval_time": sum(q.retrieval_time for q in self.queries) / len(self.queries),
            "avg_generation_time": sum(q.generation_time for q in self.queries) / len(self.queries),
            "avg_total_time": sum(q.total_time for q in self.queries) / len(self.queries),
            "total_queries": self.total_queries,
            "total_documents": self.total_documents_processed
        }
    
    def get_summary(self) -> str:
        """Get formatted metrics summary"""
        if not self.queries:
            return "No queries processed yet"
        
        avg = self.get_average_metrics()
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return f"""
        📊 **System Metrics**
        - Total Queries: {self.total_queries}
        - Documents Processed: {self.total_documents_processed}
        - Avg Retrieval Time: {avg['avg_retrieval_time']:.2f}s
        - Avg Generation Time: {avg['avg_generation_time']:.2f}s
        - Avg Total Time: {avg['avg_total_time']:.2f}s
        - Uptime: {uptime/60:.1f} minutes
        """


# Global metrics tracker
metrics_tracker = MetricsTracker()
