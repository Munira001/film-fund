"""
Operational Metrics
Monitor agent performance and decisions
"""

import time
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentMetrics:
    
    def __init__(self):
        self.metrics = {
            "searches": 0,
            "matches": 0,
            "errors": 0,
            "total_time": 0,
            "api_calls": [],
            "decisions": []
        }
        logger.info("AgentMetrics initialized")
    
    def log_search(self, query: str, results_count: int, duration: float):
        """Log search operation"""
        self.metrics["searches"] += 1
        self.metrics["total_time"] += duration
        
        self.metrics["api_calls"].append({
            "type": "search",
            "query": query,
            "results": results_count,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Search: {query} - {results_count} results in {duration:.2f}s")
    
    def log_match(self, filmmaker: str, opportunity: str, score: float):
        """Log matching decision"""
        self.metrics["matches"] += 1
        
        self.metrics["decisions"].append({
            "type": "match",
            "filmmaker": filmmaker,
            "opportunity": opportunity,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Match: {filmmaker} -> {opportunity} ({score:.0f}%)")
    
    def log_error(self, error_type: str, message: str):
        """Log error"""
        self.metrics["errors"] += 1
        
        self.metrics["api_calls"].append({
            "type": "error",
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.error(f"{error_type}: {message}")
    
    def get_summary(self) -> dict:
        """Get metrics summary"""
        return {
            "total_searches": self.metrics["searches"],
            "total_matches": self.metrics["matches"],
            "total_errors": self.metrics["errors"],
            "total_time": self.metrics["total_time"],
            "api_calls_count": len(self.metrics["api_calls"]),
            "decisions_count": len(self.metrics["decisions"])
        }
    
    def save_report(self, filepath: str):
        """Save metrics report"""
        report = {
            "summary": self.get_summary(),
            "api_calls": self.metrics["api_calls"][-100:],
            "decisions": self.metrics["decisions"][-100:]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Metrics saved to {filepath}")