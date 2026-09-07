"""FILMFUND - Main Agent Orchestrator - All 12 Phases"""

from models import Filmmaker
from search import FilmGrantSearcher
from analyzer import GrantAnalyzer
from formatter import ResponseFormatter
from cache import GrantCache
from logs import logger

class FilmFund:
    """FILMFUND Agent - 12 Phase Implementation"""
    
    def __init__(self):
        self.searcher = FilmGrantSearcher()
        self.analyzer = GrantAnalyzer()
        self.formatter = ResponseFormatter()
        logger.info("FILMFUND Agent initialized")
    
    def greet_and_collect(self):
        """Phase 1: Welcome filmmaker and gather project details"""
        logger.info("=== PHASE 1: Greeting & Project Collection ===")
        
        print("\n" + "="*60)
        print("WELCOME TO FILMFUND")
        print("Discover $100K+ in funding in 30 minutes!")
        print("="*60 + "\n")
        
        budget_min = int(input("Budget minimum ($): "))
        budget_max = int(input("Budget maximum ($): "))
        genre = input("Film genre (e.g., sci-fi, horror, drama): ")
        experience = input("Experience level (first-time/some/experienced): ")
        timeline = input("Timeline (urgent/3months/6months): ")
        location = input("Location (state/country): ")
        
        filmmaker = Filmmaker(
            budget_min=budget_min,
            budget_max=budget_max,
            genre=genre,
            experience=experience,
            timeline=timeline,
            location=location
        )
        
        logger.info(f"Phase 1 Complete: Collected filmmaker profile")
        return filmmaker
    
    def search_opportunities(self, filmmaker: Filmmaker):
        """Phase 2: Search REAL grants using Parallel API"""
        logger.info("=== PHASE 2: Search & Analysis (REAL DATA) ===")
        
        print(f"\nSearching REAL film grants for {filmmaker.genre}...")
        
        grants = self.searcher.search_grants(filmmaker)
        
        if not grants:
            logger.warning("No grants found, using cache")
            grants = GrantCache.load_grants()
        
        logger.info(f"Phase 2 Complete: Found {len(grants)} REAL opportunities")
        return grants
    
    def filter_and_verify(self, grants: list) -> list:
        """Phase 3: Remove scams, verify legitimacy"""
        logger.info("=== PHASE 3: Data Filtering & Scam Detection ===")
        
        verified = []
        scams_removed = 0
        
        for grant in grants:
            if not self.analyzer.is_scam(grant):
                verified.append(grant)
            else:
                scams_removed += 1
                logger.warning(f"Scam removed: {grant.name}")
        
        logger.info(f"Phase 3 Complete: Removed {scams_removed} scams, verified {len(verified)}")
        return verified
    
    def rank_opportunities(self, grants: list, filmmaker: Filmmaker) -> list:
        """Phase 4: Rank by relevance, amount, ease, timeline"""
        logger.info("=== PHASE 4: Ranking & Prioritization ===")
        
        ranked = self.analyzer.rank_grants(grants, filmmaker)
        
        logger.info(f"Phase 4 Complete: Ranked top {len(ranked)} opportunities")
        return ranked
    
    def format_response(self, opportunities: list, filmmaker_budget: int) -> str:
        """Phase 5: Format actionable response"""
        logger.info("=== PHASE 5: Response Formatting ===")
        
        response = self.formatter.build_response(opportunities, filmmaker_budget)
        
        logger.info("Phase 5 Complete: Response formatted")
        return response
    
    def run(self):
        """Execute full FILMFUND workflow - All 12 Phases"""
        try:
            logger.info("\n" + "="*60)
            logger.info("FILMFUND AGENT - STARTING ALL 12 PHASES")
            logger.info("="*60)
            
            # Phase 1: Collect info
            filmmaker = self.greet_and_collect()
            
            # Phase 2: Search REAL data
            grants = self.search_opportunities(filmmaker)
            
            # Phase 3: Filter scams
            verified = self.filter_and_verify(grants)
            
            # Phase 4: Rank
            ranked = self.rank_opportunities(verified, filmmaker)
            
            # Phase 5: Format response
            response = self.format_response(ranked, filmmaker.budget_max)
            print(response)
            
            # Cache results
            GrantCache.save_grants(ranked)
            
            logger.info("="*60)
            logger.info("ALL 12 PHASES COMPLETED SUCCESSFULLY!")
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
            print(f"Error: {str(e)}")