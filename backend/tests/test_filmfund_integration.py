"""Integration test - Full FILMFUND workflow with REAL data"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from filmfund import FilmFund
from models import Filmmaker
from logs import logger

def test_filmfund_integration():
    """Test FILMFUND end-to-end with REAL Parallel API"""
    
    logger.info("="*70)
    logger.info("INTEGRATION TEST - PHASE 3 COMPLETE VERIFICATION")
    logger.info("="*70)
    
    try:
        # Validate config
        Config.validate()
        logger.info("Config validated successfully")
        
        # Create test filmmaker profile
        filmmaker = Filmmaker(
            budget_min=500000,
            budget_max=1500000,
            genre="sci-fi",
            experience="some",
            timeline="6months",
            location="California"
        )
        
        logger.info(f"\nTest Filmmaker: {filmmaker.genre} film, ${filmmaker.budget_min:,} - ${filmmaker.budget_max:,}")
        
        # Initialize agent
        logger.info("\nInitializing FILMFUND Agent...")
        agent = FilmFund()
        logger.info("Agent initialized successfully")
        
        # Phase 2: Search REAL data
        logger.info("\nPhase 2: Searching REAL grants from Parallel API...")
        grants = agent.searcher.search_grants(filmmaker)
        logger.info(f"Phase 2 Result: Found {len(grants)} opportunities")
        
        # Phase 3: Filter
        logger.info("\nPhase 3: Filtering scams...")
        verified = agent.filter_and_verify(grants)
        logger.info(f"Phase 3 Result: {len(verified)} verified")
        
        # Phase 4: Rank
        logger.info("\nPhase 4: Ranking opportunities...")
        ranked = agent.rank_opportunities(verified, filmmaker)
        logger.info(f"Phase 4 Result: Top {len(ranked)} ranked")
        
        # Phase 5: Format
        logger.info("\nPhase 5: Formatting response...")
        response = agent.format_response(ranked, filmmaker.budget_max)
        logger.info("Phase 5 Result: Response formatted")
        
        logger.info("\n" + "="*70)
        logger.info("INTEGRATION TEST PASSED - PHASE 3 COMPLETE!")
        logger.info("="*70)
        
        print("\n" + response)
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_filmfund_integration()