"""
PHASE 2 - COMPLETE SEARCH
Real Parallel API + Real Google CSE + Real Researched Grants
"""

import sys
import os
import json
from datetime import datetime
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(__file__))

from logs import logger
from filmmaker_profile import FilmmakerProfile
from funding_database import FilmfundDatabase
from funding_matching_engine import AdvancedMatchingEngine
from funding_google_loader import GoogleSearchLoader
from funding_real_grants_loader import RealGrantsLoader
from parallel_api import ParallelAPISearcher


@dataclass
class FundingOpportunity:
    """Funding opportunity"""
    id: str
    name: str
    type: str
    amount: float = 0.0
    deadline: str = None
    organization: str = ""
    source: str = ""
    match_score: float = 0.0
    application_link: str = ""
    
    def to_dict(self):
        return self.__dict__


class CompleteSearchOrchestrator:
    """Search from ALL sources - Real data only"""
    
    def __init__(self, profile: FilmmakerProfile):
        self.profile = profile
        self.parallel = ParallelAPISearcher()
        self.google = GoogleSearchLoader()
        self.real_grants = RealGrantsLoader()
        self.db = FilmfundDatabase()
        self.matcher = AdvancedMatchingEngine(profile)
        logger.info(" CompleteSearchOrchestrator initialized")
    
    def execute_complete_search(self) -> List[FundingOpportunity]:
        """Execute search from ALL REAL sources"""
        
        logger.info("="*100)
        logger.info("PHASE 2 - COMPLETE SEARCH (ALL REAL SOURCES)")
        logger.info("="*100)
        
        opportunities = []
        
        print("\n" + "="*100)
        print("FILMFUND - PHASE 2: COMPLETE REAL DATA SEARCH")
        print("="*100)
        print(f"\n Filmmaker: {self.profile.filmmaker_name}")
        print(f"  Project: {self.profile.project_title}")
        print(f" Budget: ${self.profile.total_budget_needed:,}")
        
        # SOURCE 1: REAL GRANTS (Researched)
        print("\n" + "-"*100)
        print("SOURCE 1: REAL RESEARCHED GRANTS")
        print("-"*100)
        
        real_grants = self.real_grants.load_grants()
        for grant in real_grants:
            opp = FundingOpportunity(
                id=grant.get("id"),
                name=grant.get("name"),
                type="grant",
                amount=grant.get("amount", 0),
                deadline=grant.get("deadline"),
                organization=grant.get("organization"),
                source="real-researched",
                application_link=grant.get("application_link")
            )
            opportunities.append(opp)
        
        print(f" Loaded {len(real_grants)} REAL researched grants")
        
        # SOURCE 2: PARALLEL API
        print("\n" + "-"*100)
        print("SOURCE 2: PARALLEL API")
        print("-"*100)
        
        query = f"{self.profile.film_genre} film grants ${self.profile.total_budget_needed:,}"
        try:
            parallel_results = self.parallel.search({
                "search_queries": [query]
            })
            
            for result in parallel_results:
                opp = FundingOpportunity(
                    id=result.get("id", f"parallel_{datetime.now().timestamp()}"),
                    name=result.get("name", "Unknown"),
                    type="grant",
                    amount=result.get("amount", 0),
                    deadline=result.get("deadline"),
                    organization=result.get("organization", ""),
                    source="parallel-api",
                    application_link=result.get("url", "")
                )
                opportunities.append(opp)
            
            print(f" Parallel API: Found {len(parallel_results)} opportunities")
        except Exception as e:
            logger.warning(f" Parallel API error: {str(e)}")
        
        # SOURCE 3: GOOGLE CUSTOM SEARCH
        print("\n" + "-"*100)
        print("SOURCE 3: GOOGLE CUSTOM SEARCH")
        print("-"*100)
        
        try:
            google_results = self.google.search_multiple_queries()
            
            for result in google_results:
                # Only add if we have real data
                if result.get("application_link"):
                    opp = FundingOpportunity(
                        id=result.get("id"),
                        name=result.get("name"),
                        type="grant",
                        amount=0,  # Google CSE doesn't always have amounts
                        organization=result.get("organization"),
                        source="google-cse",
                        application_link=result.get("application_link")
                    )
                    opportunities.append(opp)
            
            print(f" Google CSE: Found {len(google_results)} opportunities")
        except Exception as e:
            logger.warning(f"⚠️ Google CSE error: {str(e)}")
        
        # DEDUPLICATION
        print("\n" + "-"*100)
        print("DEDUPLICATION & MATCHING")
        print("-"*100)
        
        # Remove duplicates
        unique_opps = {}
        for opp in opportunities:
            key = (opp.name.lower(), opp.organization.lower())
            if key not in unique_opps:
                unique_opps[key] = opp
        
        opportunities = list(unique_opps.values())
        print(f" After dedup: {len(opportunities)} unique opportunities")
        
        # MATCH & SCORE
        print("\n" + "-"*100)
        print("CALCULATING MATCH SCORES")
        print("-"*100)
        
        scored_opps = []
        for opp in opportunities:
            score = self.matcher.calculate_match(opp.to_dict())
            opp.match_score = score.overall_score
            scored_opps.append(opp)
        
        # Sort by score
        scored_opps.sort(key=lambda x: x.match_score, reverse=True)
        
        # SAVE TO DATABASE
        print("\n" + "-"*100)
        print("SAVING TO DATABASE")
        print("-"*100)
        
        for i, opp in enumerate(scored_opps[:50], 1):
            self.db.save_funding_opportunity(opp.to_dict())
            self.db.save_opportunity_match(
                self.profile.profile_id,
                opp.id,
                f"search_{datetime.now().timestamp()}",
                opp.match_score,
                i
            )
        
        print(f" Saved {min(len(scored_opps), 50)} to database")
        
        logger.info(" COMPLETE SEARCH FINISHED")
        return scored_opps[:50]


def display_results(opportunities: List[FundingOpportunity]):
    """Display all REAL opportunities"""
    
    print("\n" + "="*100)
    print("REAL FUNDING OPPORTUNITIES - TOP MATCHES")
    print("="*100)
    
    if not opportunities:
        print("\n No opportunities found")
        return
    
    print(f"\n Found {len(opportunities)} REAL opportunities\n")
    
    for i, opp in enumerate(opportunities[:15], 1):
        print(f"{i}. {opp.name}")
        print(f"    Organization: {opp.organization}")
        print(f"    Amount: ${opp.amount:,.0f}" if opp.amount > 0 else "   💰 Amount: Contact for details")
        print(f"    Deadline: {opp.deadline if opp.deadline else 'Rolling'}")
        print(f"    Match: {opp.match_score:.1f}%")
        print(f"    Source: {opp.source}")
        print(f"    {opp.application_link}\n")


def main():
    """Main execution"""
    
    try:
        # Create profile
        profile = FilmmakerProfile(
            project_title="FILMFUND",
            project_logline="AI agent for filmmaker funding",
            film_genre="other",
            visual_style="cinematic",
            film_rating="Unrated",
            project_description="FILMFUND automates funding discovery",
            total_budget_needed=100000,
            start_date="2026-07-20",
            filmmaker_name="Munira Mohammed",
            filmmaker_email="muniramohammed1256@gmail.com",
            experience_level="professional",
            filmmaker_location="Ghana"
        )
        
        print(f" Profile: {profile.project_title}")
        
        # Execute search
        orchestrator = CompleteSearchOrchestrator(profile)
        opportunities = orchestrator.execute_complete_search()
        
        # Display
        display_results(opportunities)
        
        print("\n" + "="*100)
        print(" PHASE 2 COMPLETE - ALL REAL DATA + ALL REAL APIs")
        print("="*100)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f" Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()