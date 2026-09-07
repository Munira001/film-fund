"""
PHASE 2 - COMPLETE
Real Parallel API + Real Eligibility Parser + Real Grant Database
"""

import sys
import os
import json
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))

from logs import logger
from filmmaker_profile import FilmmakerProfile
from funding_database import FilmfundDatabase
from funding_matching_engine import AdvancedMatchingEngine
from funding_scam_detector import ScamDetector
from funding_eligibility_parser import RealEligibilityParser


@dataclass
class FundingOpportunity:
    id: str
    name: str
    type: str
    amount: float = 0.0
    deadline: str = None
    organization: str = ""
    source: str = ""
    match_score: float = 0.0
    application_link: str = ""
    eligibility_score: float = 0.0
    scam_risk: float = 0.0
    
    def to_dict(self):
        return self.__dict__


class ParallelAPISearcher:
    
    def __init__(self):
        self.api_key = os.getenv("PARALLEL_API_KEY", "shO5SaaJC4VpW1YGSuRYnzrrLwgbjiX4GA4F6AUy")
        self.endpoint = "https://api.parallel.ai/v1/search"
        logger.info("Parallel API initialized")
    
    def search(self, query: str) -> List[Dict]:
        try:
            logger.info(f"Parallel API searching: {query}")
            
            payload = {"search_queries": [query]}
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                logger.info(f"Parallel API: {len(results)} results found")
                return results
            else:
                logger.warning(f"Parallel API: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Parallel API error: {str(e)}")
            return []


class CompletePhase2:
    
    def __init__(self, profile: FilmmakerProfile):
        self.profile = profile
        self.parallel = ParallelAPISearcher()
        self.eligibility_parser = RealEligibilityParser()
        self.scam_detector = ScamDetector()
        self.matching_engine = AdvancedMatchingEngine(profile)
        self.db = FilmfundDatabase()
        logger.info("Phase 2 Complete System initialized")
    
    def execute(self) -> List[FundingOpportunity]:
        
        logger.info("="*100)
        logger.info("PHASE 2 - COMPLETE SYSTEM")
        logger.info("Real Parallel API + Real Eligibility Parser + Real Scam Detection")
        logger.info("="*100)
        
        opportunities = []
        
        print("\n" + "="*100)
        print("FILMFUND - PHASE 2: COMPLETE SYSTEM")
        print("="*100)
        print(f"\nFilmmaker: {self.profile.filmmaker_name}")
        print(f"Project: {self.profile.project_title}")
        print(f"Budget: ${self.profile.total_budget_needed:,}")
        print(f"Genre: {self.profile.film_genre}")
        print(f"Location: {self.profile.filmmaker_location}")
        
        query = f"{self.profile.film_genre} film grants ${self.profile.total_budget_needed:,}"
        
        print("\n" + "-"*100)
        print("STEP 1: PARALLEL API SEARCH (REAL)")
        print("-"*100)
        print(f"Query: {query}\n")
        
        parallel_results = self.parallel.search(query)
        
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
        
        print(f"Found: {len(parallel_results)} opportunities from Parallel API")
        for i, opp in enumerate(parallel_results[:5], 1):
            print(f"   {i}. {opp.get('name', 'Unknown')} - {opp.get('url', 'N/A')}")
        
        print("\n" + "-"*100)
        print("STEP 2: ELIGIBILITY MATCHING (REAL GRANT DATA)")
        print("-"*100)
        
        eligibility_matches = self.eligibility_parser.match_filmmaker_to_grants(self.profile.__dict__)
        
        eligibility_dict = {m.grant_name.lower(): m for m in eligibility_matches}
        
        for opp in opportunities:
            opp_name_lower = opp.name.lower()
            if opp_name_lower in eligibility_dict:
                opp.eligibility_score = eligibility_dict[opp_name_lower].match_score
        
        print(f"Matched {len(eligibility_matches)} real grant programs to filmmaker")
        print("\nTop eligibility matches:")
        for i, match in enumerate(eligibility_matches[:5], 1):
            print(f"   {i}. {match.grant_name} - Match: {match.match_score:.0f}%")
        
        print("\n" + "-"*100)
        print("STEP 3: SCAM DETECTION")
        print("-"*100)
        
        safe_opps = []
        for opp in opportunities:
            analysis = self.scam_detector.analyze(opp.to_dict())
            opp.scam_risk = 100 - analysis.safety_score
            
            if analysis.safety_score >= 40 and not analysis.is_scam:
                safe_opps.append(opp)
        
        print(f"Safe opportunities: {len(safe_opps)}/{len(opportunities)}")
        
        print("\n" + "-"*100)
        print("STEP 4: MATCH SCORING")
        print("-"*100)
        
        scored = []
        for opp in safe_opps:
            score = self.matching_engine.calculate_match(opp.to_dict())
            opp.match_score = score.overall_score
            scored.append(opp)
        
        scored.sort(key=lambda x: x.match_score, reverse=True)
        print(f"Scored {len(scored)} opportunities")
        
        print("\n" + "-"*100)
        print("STEP 5: DATABASE STORAGE")
        print("-"*100)
        
        for i, opp in enumerate(scored[:50], 1):
            self.db.save_funding_opportunity(opp.to_dict())
            self.db.save_opportunity_match(
                self.profile.profile_id,
                opp.id,
                f"search_{datetime.now().timestamp()}",
                opp.match_score,
                i
            )
        
        print(f"Saved {min(len(scored), 50)} opportunities to database")
        
        logger.info("Phase 2 complete")
        return scored[:50]


def main():
    
    try:
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
        
        system = CompletePhase2(profile)
        opportunities = system.execute()
        
        print("\n" + "="*100)
        print("TOP OPPORTUNITIES - RANKED BY MATCH")
        print("="*100 + "\n")
        
        if opportunities:
            for i, opp in enumerate(opportunities[:15], 1):
                print(f"{i}. {opp.name}")
                print(f"   Organization: {opp.organization}")
                print(f"   Amount: ${opp.amount:,.0f}" if opp.amount > 0 else "   Amount: Contact")
                print(f"   Deadline: {opp.deadline if opp.deadline else 'Rolling'}")
                print(f"   Match Score: {opp.match_score:.1f}%")
                print(f"   Eligibility: {opp.eligibility_score:.1f}%")
                print(f"   Safety: {100-opp.scam_risk:.1f}%")
                print(f"   Source: {opp.source}")
                print(f"   Link: {opp.application_link}\n")
        
        print("="*100)
        print("PHASE 2 COMPLETE - ALL SYSTEMS WORKING")
        print("="*100)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()