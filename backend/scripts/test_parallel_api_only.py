"""Test Parallel API integration in Component 3"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.component3_grounding_agent import component3_agent
from src.logs import logger

def test_parallel_api():
    """Test ONLY market questions (uses Parallel API)"""
    
    logger.info("="*80)
    logger.info("COMPONENT 3 - PARALLEL API TEST")
    logger.info("="*80)
    
    market_questions = [
        "What is the current market demand for indie films?",
        "What funding opportunities are available for filmmakers?",
        "What are the latest indie film trends?",
        "Tell me about current filmmaker opportunities",
    ]
    
    for question in market_questions:
        logger.info(f"\nQuestion: {question}")
        logger.info("-"*80)
        
        response = component3_agent.answer_question(question)
        
        # Check if Parallel API was used (external grounding)
        if response['grounding']['external']['found']:
            logger.info("[OK] PARALLEL API USED")
            logger.info(f"Results: {response['grounding']['external'].get('results_count')} items")
            logger.info(f"Source: {response['grounding']['external'].get('data_type')}")
        else:
            logger.info("[WARNING] Parallel API returned no results")
        
        logger.info(f"Answer: {response['answer']}")

if __name__ == "__main__":
    test_parallel_api()