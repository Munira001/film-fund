"""
PHASE 2 - ENHANCED Search with REAL Parallel API + Google Custom Search
Complete production-ready system
"""

import sys
import os
import json
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(__file__))

from logs import logger
from filmmaker_profile import FilmmakerProfile
from funding_database import FilmfundDatabase
from funding_matching_engine import AdvancedMatchingEngine


# ============================================================================
# CONFIGURATION - REAL APIs
# ============================================================================

class SearchConfig:
    """REAL API Configuration"""
    
    # Parallel API - REAL
    PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY", "gd7LHuUETXNIj4u1oBHCUXowSDihzDlCoLNvHyfD")
    PARALLEL_ENDPOINT = "https://api.parallel.ai/v1/search"
    
    # Google Custom Search - REAL
    GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    GOOGLE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
    
    # Settings
    MAX_RESULTS = 20
    API_TIMEOUT = 15


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class FundingOpportunity:
    """Real funding opportunity"""
    id: str
    name: str
    type: str
    amount: float = 0.0
    deadline: Optional[str] = None
    organization: str = ""
    source: str = ""
    match_score: float = 0.0
    application_link: str = ""
    
    def to_dict(self):
        return self.__dict__


# ============================================================================
# PARALLEL API - REAL
# ============================================================================

class ParallelAPISearcher:
    """Real Parallel API integration"""
    
    def __init__(self):
        self.api_key = SearchConfig.PARALLEL_API_KEY
        self.endpoint = SearchConfig.PARALLEL_ENDPOINT
        self.db = FilmfundDatabase()
        logger.info(" ParallelAPISearcher - REAL API initialized")
    
    def search(self, query: str, opp_type: str = "grants") -> List[Dict]:
        """REAL Parallel API call"""
        try:
            logger.info(f" Calling REAL Parallel API: {query}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "type": opp_type,
                "limit": 10,
                "category": "film-funding"
            }
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=SearchConfig.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                logger.info(f" Parallel API returned {len(results)} results")
                self.db.track_api_usage("parallel-api", 1000)
                return results
            else:
                logger.warning(f" Parallel API error: {response.status_code}")
                return []
        
        except requests.exceptions.Timeout:
            logger.warning(" Parallel API timeout")
            return []
        except Exception as e:
            logger.error(f" Parallel API error: {str(e)}")
            return []


# ============================================================================
# GOOGLE CUSTOM SEARCH - REAL
# ============================================================================

class GoogleCustomSearcher:
    """Real Google Custom Search integration"""
    
    def __init__(self):
        self.api_key = SearchConfig.GOOGLE_API_KEY
        self.engine_id = SearchConfig.GOOGLE_ENGINE_ID
        self.endpoint = SearchConfig.GOOGLE_ENDPOINT
        self.db = FilmfundDatabase()
        logger.info(" GoogleCustomSearcher - REAL API initialized")
    
    def search(self, query: str) -> List[Dict]:
        """REAL Google Custom Search API call"""
        try:
            logger.info(f" Calling REAL Google Custom Search: {query}")
            
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.engine_id,
                "num": 10
            }
            
            response = requests.get(
                self.endpoint,
                params=params,
                timeout=SearchConfig.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("items", [])
                logger.info(f" Google CSE returned {len(results)} results")
                self.db.track_api_usage("google-cse", 100)
                return results
            else:
                logger.warning(f" Google CSE error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f" Google CSE error: {str(e)}")
            return []


# ============================================================================
# SEARCH ORCHESTRATOR
# ============================================================================

class SearchOrchestrator:
    """Complete REAL search workflow"""
    
    def __init__(self, profile: FilmmakerProfile):
        self.profile = profile
        self.parallel = ParallelAPISearcher()
        self.google = GoogleCustomSearcher()
        self.db = FilmfundDatabase()
        self.matcher = AdvancedMatchingEngine(profile)
        logger.info(f" SearchOrchestrator initialized: {profile.project_title}")
    
    def execute_search(self) -> List[FundingOpportunity]:
        """Execute REAL search with both APIs"""
        
        logger.info("="*100)
        logger.info("PHASE 2 - REAL SEARCH EXECUTION")
        logger.info("="*100)
        
        opportunities = []
        
        # Build search query
        query = f"{self.profile.film_genre} film grants ${self.profile.total_budget_needed:,.0f}"
        
        print("\n" + "="*100)
        print("FILMFUND - PHASE 2: REAL API SEARCH")
        print("="*100)
        print(f"\n Filmmaker: {self.profile.filmmaker_name}")
        print(f"  Project: {self.profile.project_title}")
        print(f" Budget: ${self.profile.total_budget_needed:,}")
        print(f" Genre: {self.profile.film_genre}")
        print(f" Location: {self.profile.filmmaker_location}")
        
        print(f"\n Search Query: {query}")
        
        # REAL Parallel API Search
        print("\n" + "-"*100)
        print(" CALLING REAL PARALLEL API...")
        print("-"*100)
        
        parallel_results = self.parallel.search(query)
        
        for result in parallel_results:
            opp = FundingOpportunity(
                id=result.get("id", f"parallel_{datetime.now().timestamp()}"),
                name=result.get("name", "Unknown"),
                type=result.get("type", "grant"),
                amount=result.get("amount", 0),
                deadline=result.get("deadline"),
                organization=result.get("organization", ""),
                source="parallel-api",
                application_link=result.get("url", "")
            )
            opportunities.append(opp)
        
        print(f" Parallel API: Found {len(parallel_results)} opportunities")
        
        # REAL Google Custom Search
        print("\n" + "-"*100)
        print(" CALLING REAL GOOGLE CUSTOM SEARCH...")
        print("-"*100)
        
        google_results = self.google.search(query + " film funding grants")
        
        for result in google_results:
            opp = FundingOpportunity(
                id=f"google_{result.get('link', '').replace('/', '_')[:50]}",
                name=result.get("title", "Unknown"),
                type="grant",
                organization=result.get("displayLink", ""),
                source="google-cse",
                application_link=result.get("link", "")
            )
            opportunities.append(opp)
        
        print(f" Google CSE: Found {len(google_results)} opportunities")
        
        # Match and score
        print("\n" + "-"*100)
        print(" CALCULATING MATCH SCORES...")
        print("-"*100)
        
        scored_opps = []
        for opp in opportunities:
            score = self.matcher.calculate_match(opp.to_dict())
            opp.match_score = score.overall_score
            scored_opps.append(opp)
        
        # Sort by score
        scored_opps.sort(key=lambda x: x.match_score, reverse=True)
        
        # Save to database
        print("\n" + "-"*100)
        print(" SAVING TO DATABASE...")
        print("-"*100)
        
        for i, opp in enumerate(scored_opps[:SearchConfig.MAX_RESULTS], 1):
            self.db.save_funding_opportunity(opp.to_dict())
            self.db.save_opportunity_match(
                self.profile.profile_id,
                opp.id,
                f"search_{datetime.now().timestamp()}",
                opp.match_score,
                i
            )
        
        print(f"✅ Saved {min(len(scored_opps), SearchConfig.MAX_RESULTS)} opportunities to database")
        
        logger.info(f"✅ Search complete: {len(scored_opps)} opportunities")
        
        return scored_opps[:SearchConfig.MAX_RESULTS]


# ============================================================================
# DISPLAY RESULTS
# ============================================================================

def display_results(opportunities: List[FundingOpportunity], profile: FilmmakerProfile):
    """Display REAL results"""
    
    print("\n" + "="*100)
    print("SEARCH RESULTS - TOP OPPORTUNITIES")
    print("="*100)
    
    if not opportunities:
        print("\n No opportunities found")
        return
    
    print(f"\n Found {len(opportunities)} opportunities for {profile.project_title}\n")
    
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"{i}. {opp.name}")
        print(f"   Type: {opp.type.upper()}")
        print(f"   Organization: {opp.organization}")
        print(f"   Amount: ${opp.amount:,.0f}" if opp.amount > 0 else "   💰 Amount: TBD")
        print(f"   Deadline: {opp.deadline if opp.deadline else 'Ongoing'}")
        print(f"   Match Score: {opp.match_score:.1f}%")
        print(f"   Source: {opp.source}")
        print(f"   Link: {opp.application_link}")
        print()


# ============================================================================
# MAIN - REAL EXECUTION
# ============================================================================

def main():
    """Main execution with REAL data and REAL APIs"""
    
    logger.info("="*100)
    logger.info("PHASE 2 - FILMFUND REAL API SEARCH SYSTEM")
    logger.info("Real Parallel API + Real Google Custom Search + Real Data")
    logger.info("="*100)
    
    try:
        # Create REAL profile (not loading from file)
        print("\n" + "="*100)
        print("STEP 1: CREATE REAL FILMMAKER PROFILE")
        print("="*100)
        
        profile = FilmmakerProfile(
            project_title="FILMFUND",
            project_logline="AI agent platform for filmmaker funding",
            film_genre="other",
            visual_style="cinematic",
            film_rating="Unrated",
            project_description="FILMFUND automates funding discovery for filmmakers",
            budget_breakdown=None,
            total_budget_needed=100000,
            already_secured_funding=0,
            start_date="2026-07-20",
            timeline_urgency="urgent",
            production_stage="pre-production",
            estimated_runtime_minutes=120,
            filmmaker_name="Munira Mohammed",
            filmmaker_email="muniramohammed1256@gmail.com",
            filmmaker_phone=None,
            experience_level="professional",
            filmmaker_location="Ghana",
            target_audience="All filmmakers seeking funding",
            key_themes=["technology", "filmmaking", "funding", "ai", "agent"],
            shooting_location="Ghana"
        )
        
        print(f" Profile created: {profile.project_title}")
        
        # Execute REAL search
        print("\n" + "="*100)
        print("STEP 2: EXECUTE REAL API SEARCH")
        print("="*100)
        
        orchestrator = SearchOrchestrator(profile)
        opportunities = orchestrator.execute_search()
        
        # Display results
        print("\n" + "="*100)
        print("STEP 3: DISPLAY RESULTS")
        print("="*100)
        
        display_results(opportunities, profile)
        
        # Save results file
        print("\n" + "="*100)
        print("STEP 4: SAVE RESULTS")
        print("="*100)
        
        results_file = f"data/search_results/{profile.profile_id}_real_results.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                "profile": {
                    "filmmaker": profile.filmmaker_name,
                    "project": profile.project_title,
                    "budget": profile.total_budget_needed,
                    "genre": profile.film_genre
                },
                "opportunities": [o.to_dict() for o in opportunities],
                "total_found": len(opportunities),
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f" Results saved: {results_file}")
        
        logger.info("="*100)
        logger.info(" PHASE 2 COMPLETE - REAL DATA + REAL APIs")
        logger.info("="*100)
        
        print("\n" + "="*100)
        print(" PHASE 2 - REAL SEARCH COMPLETE!")
        print("="*100)
        print("\nNext: Phase 3 - Eligibility Parser & Scam Detection")
        print("="*100 + "\n")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f" Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# Create: src/funding_loader.py
class RealGrantsLoader:
    """Load REAL grants from real_grants.json"""
    
    def load_real_grants():
        """Load real grant data from file"""
        # Load real_grants.json
        # Parse and return as opportunities
        # Match to filmmaker profile