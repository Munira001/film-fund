"""
Agent Decision Framework
REAL reasoning - GLOBAL + USA searches
"""

import logging

logger = logging.getLogger(__name__)


class AgentReasoning:
    
    def __init__(self):
        logger.info("Agent Reasoning Engine initialized")
    
    def decide_search_strategy(self, filmmaker: dict) -> list:
        """Generate MORE GLOBAL search queries - USA + International"""
        
        genre = filmmaker.get('film_genre', 'other')
        budget = filmmaker.get('total_budget_needed', 0)
        experience = filmmaker.get('experience_level', 'some')
        
        queries = []
        
        # USA Specific
        queries.append(f"USA film grants")
        queries.append(f"American film funding")
        queries.append(f"US filmmaker grants 2026")
        
        # Global/International
        queries.append(f"international film grants")
        queries.append(f"global filmmaker funding")
        queries.append(f"worldwide film financing")
        
        # Genre + Funding
        queries.append(f"{genre} film funding worldwide")
        queries.append(f"{genre} filmmaker grants USA")
        
        # Budget-based
        queries.append(f"film grants ${budget}")
        queries.append(f"film funding ${budget} international")
        
        # Experience-based
        if experience in ['first-time', 'some']:
            queries.append(f"emerging filmmaker grants USA")
            queries.append(f"emerging filmmaker grants global")
        
        if experience in ['professional', 'experienced']:
            queries.append(f"professional filmmaker funding USA")
            queries.append(f"professional filmmaker funding international")
        
        # Specific fund types (USA + Global)
        queries.append(f"film grants foundations USA")
        queries.append(f"film grants foundations international")
        queries.append(f"arts grants filmmaking USA")
        queries.append(f"arts grants filmmaking global")
        queries.append(f"film fellowships USA")
        queries.append(f"film fellowships international")
        queries.append(f"film competitions with funding USA")
        queries.append(f"film competitions with funding global")
        queries.append(f"independent film funding USA")
        queries.append(f"independent film funding international")
        
        logger.info(f"Generated {len(queries)} USA + GLOBAL search queries")
        return queries
    
    def decide_priority(self, opportunity: dict, filmmaker: dict) -> dict:
        """REAL priority based on actual opportunity data"""
        
        factors = {
            "budget_fit": self._real_budget_fit(opportunity, filmmaker),
            "eligibility_match": self._real_eligibility_match(opportunity, filmmaker),
            "application_effort": self._real_effort_score(opportunity)
        }
        
        overall = sum(factors.values()) / len(factors)
        factors["overall_priority"] = overall
        
        logger.info(f"Priority factors: {factors}")
        return factors
    
    def should_apply(self, score: float, priority: dict) -> bool:
        """REAL decision based on actual scores"""
        
        if score >= 70 and priority["overall_priority"] >= 0.7:
            decision = True
        elif score >= 60 and priority["overall_priority"] >= 0.8:
            decision = True
        else:
            decision = False
        
        logger.info(f"Apply decision: {decision}")
        return decision
    
    def _real_budget_fit(self, opportunity: dict, filmmaker: dict) -> float:
        """REAL budget fit from actual data"""
        budget = filmmaker.get('total_budget_needed', 0)
        opp_min = opportunity.get('budget_min', 0)
        opp_max = opportunity.get('budget_max', 999999)
        
        if opp_min <= budget <= opp_max:
            return 1.0
        if budget * 0.8 <= opp_max and budget * 1.2 >= opp_min:
            return 0.7
        return 0.4
    
    def _real_eligibility_match(self, opportunity: dict, filmmaker: dict) -> float:
        """REAL eligibility from actual data"""
        
        score = 0.5
        
        genres = opportunity.get('genres', ['all'])
        filmmaker_genre = filmmaker.get('film_genre', 'other')
        
        if 'all' in genres or filmmaker_genre in genres:
            score += 0.2
        
        return min(1.0, score)
    
    def _real_effort_score(self, opportunity: dict) -> float:
        """REAL effort from actual data"""
        
        score = 0.5
        
        if not opportunity.get('application_fee'):
            score += 0.3
        
        return min(1.0, score)