"""Test Component 3 Grounding Agent"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.component3_grounding_agent import component3_agent
from src.logs import logger

def test_grounding_agent():
    """Test agent with various questions"""
    
    logger.info("="*80)
    logger.info("COMPONENT 3 - GROUNDING AGENT TEST")
    logger.info("="*80)
    
    test_questions = [
        "What is the budget for The Last Dawn?",
        "Tell me about Sarah Chen's filmmaking background",
        "What are the latest indie film trends?",
        "Compare The Last Dawn to other sci-fi projects",
        "How much funding is available for Love in the City?",
        "What is the market demand for documentary films?",
    ]
    
    passed = 0
    failed = 0
    
    for i, question in enumerate(test_questions, 1):
        logger.info(f"\n[TEST {i}] Question: {question}")
        logger.info("-"*80)
        
        try:
            response = component3_agent.answer_question(question)
            
            logger.info(f"Answer: {response['answer']}")
            logger.info(f"Confidence: {response['confidence']}")
            logger.info(f"Sources: {', '.join(response['sources'])}")
            logger.info(f"[OK] TEST {i} PASSED")
            passed += 1
        except Exception as e:
            logger.error(f"[FAIL] TEST {i} FAILED: {str(e)}")
            failed += 1
    
    logger.info("\n" + "="*80)
    logger.info(f"RESULTS: {passed} PASSED, {failed} FAILED")
    logger.info("="*80)
    
    if failed == 0:
        logger.info("\n[SUCCESS] COMPONENT 3 - PRODUCTION READY!")
    else:
        logger.error(f"\n[WARNING] {failed} tests failed")

if __name__ == "__main__":
    test_grounding_agent()