"""
PHASE 4 - Define Real Functions as Tools
Official Google ADK Pattern
Functions for Gemini Agent to use
"""

import logging
from parallel_api import ParallelAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_funding_opportunities(query: str, budget: int) -> dict:
    """
    Search for REAL film funding opportunities using Parallel API
    
    Args:
        query (str): Search query (e.g., 'documentary film grants')
        budget (int): Filmmaker's budget in dollars (e.g., 100000)
    
    Returns:
        dict: Results with opportunities list
    """
    try:
        logger.info(f"Searching: {query} for budget ${budget}")
        
        api = ParallelAPI()
        results = api.search(query, limit=20)
        
        logger.info(f"Found {len(results)} opportunities")
        
        return {
            "success": True,
            "query": query,
            "budget": budget,
            "count": len(results),
            "opportunities": results[:10]
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def score_opportunity(opportunity: dict, filmmaker_profile: dict) -> dict:
    """
    Score an opportunity against filmmaker profile
    
    Args:
        opportunity (dict): Opportunity data
        filmmaker_profile (dict): Filmmaker profile data
    
    Returns:
        dict: Score and recommendation
    """
    try:
        score = 0
        factors = {}
        
        # Budget fit (30 points)
        budget = filmmaker_profile.get('total_budget_needed', 0)
        opp_budget = opportunity.get('budget', {})
        
        if isinstance(opp_budget, dict):
            min_amt = opp_budget.get('min', 0)
            max_amt = opp_budget.get('max', 999999)
            
            if min_amt <= budget <= max_amt:
                score += 30
                factors['budget_fit'] = 'Perfect fit'
            elif budget * 0.8 <= max_amt and budget * 1.2 >= min_amt:
                score += 20
                factors['budget_fit'] = 'Close fit'
            else:
                score += 5
                factors['budget_fit'] = 'Outside range'
        else:
            score += 15
            factors['budget_fit'] = 'Unknown range'
        
        # Genre match (25 points)
        genres = opportunity.get('genres', ['all'])
        filmmaker_genre = filmmaker_profile.get('film_genre', 'other')
        
        if 'all' in genres or filmmaker_genre in genres:
            score += 25
            factors['genre_match'] = 'Matches'
        else:
            score += 5
            factors['genre_match'] = 'No match'
        
        # Deadline (20 points)
        deadline = opportunity.get('deadline', 'Rolling')
        
        if 'rolling' in str(deadline).lower():
            score += 20
            factors['deadline'] = 'Rolling (always open)'
        elif deadline and deadline != 'unknown':
            score += 15
            factors['deadline'] = 'Has deadline'
        else:
            score += 5
            factors['deadline'] = 'Unknown'
        
        # Application fee (15 points)
        has_fee = opportunity.get('application_fee', False)
        
        if not has_fee:
            score += 15
            factors['application_fee'] = 'No fee'
        else:
            score += 5
            factors['application_fee'] = 'Has fee'
        
        # Experience level (10 points)
        experience = filmmaker_profile.get('experience_level', 'some')
        
        if experience in ['professional', 'experienced']:
            score += 10
            factors['experience'] = 'Professional level match'
        else:
            score += 5
            factors['experience'] = 'Emerging level match'
        
        final_score = min(100, max(0, score))
        
        return {
            "success": True,
            "opportunity_name": opportunity.get('name', 'Unknown'),
            "score": final_score,
            "factors": factors,
            "recommendation": "APPLY" if final_score >= 70 else "CONSIDER" if final_score >= 50 else "SKIP"
        }
    except Exception as e:
        logger.error(f"Scoring error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_filmmaker_profile(name: str, budget: int, genre: str, experience: str) -> dict:
    """
    Create or retrieve a filmmaker profile
    
    Args:
        name (str): Filmmaker name
        budget (int): Budget needed in dollars
        genre (str): Film genre
        experience (str): Experience level
    
    Returns:
        dict: Filmmaker profile
    """
    try:
        profile = {
            "filmmaker_name": name,
            "total_budget_needed": budget,
            "film_genre": genre,
            "experience_level": experience,
            "filmmaker_location": "Global"
        }
        
        logger.info(f"Created profile for {name}")
        
        return {
            "success": True,
            "profile": profile
        }
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }