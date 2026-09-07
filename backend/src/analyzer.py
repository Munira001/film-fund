"""Analysis and ranking - Phases 3 & 4"""

from logs import logger
from models import Grant, Filmmaker


class GrantAnalyzer:
    """Analyzes and ranks grants"""
    
    SCAM_KEYWORDS = [
        "pay to apply",
        "guaranteed funding",
        "processing fee",
        "upfront payment",
        "guarantee",
        "assured",
        "wire transfer",
        "money back"
    ]
    
    @staticmethod
    def is_scam(grant: Grant) -> bool:
        """Detect scam grants - Phase 3"""
        try:
            text = (grant.name + " " + grant.eligibility).lower()
            is_scam = any(keyword in text for keyword in GrantAnalyzer.SCAM_KEYWORDS)
            
            if is_scam:
                logger.warning(f"Potential scam detected: {grant.name}")
            
            return is_scam
            
        except Exception as e:
            logger.error(f"Scam detection error: {str(e)}")
            return False
    
    @staticmethod
    def calculate_fit_score(grant: Grant, filmmaker: Filmmaker) -> float:
        """Calculate how well grant matches filmmaker - Phase 4"""
        try:
            score = 0.0
            
            # Budget match (40%)
            if grant.amount >= filmmaker.budget_min and grant.amount <= filmmaker.budget_max:
                score += 40.0
            elif grant.amount >= filmmaker.budget_min * 0.75:
                score += 20.0
            
            # Genre match (30%)
            if filmmaker.genre.lower() in grant.eligibility.lower():
                score += 30.0
            
            # Timeline (20%)
            score += 20.0
            
            # Experience match (10%)
            if filmmaker.experience.lower() in grant.eligibility.lower():
                score += 10.0
            
            return min(score, 100.0)  # Cap at 100%
            
        except Exception as e:
            logger.error(f"Score calculation error: {str(e)}")
            return 0.0
    
    @staticmethod
    def rank_grants(grants: list, filmmaker: Filmmaker) -> list:
        """Rank grants by relevance - Phase 4"""
        try:
            ranked = []
            scams_removed = 0
            
            for grant in grants:
                # Handle both Grant objects and dicts
                if isinstance(grant, dict):
                    try:
                        grant = Grant(**grant)
                    except Exception as e:
                        logger.warning(f"Could not convert dict to Grant: {str(e)}")
                        continue
                
                # Filter scams
                if GrantAnalyzer.is_scam(grant):
                    scams_removed += 1
                    continue
                
                # Calculate score
                score = GrantAnalyzer.calculate_fit_score(grant, filmmaker)
                grant.fit_score = score
                
                if score > 0:
                    ranked.append(grant)
            
            # Sort by score
            ranked.sort(key=lambda g: g.fit_score, reverse=True)
            
            logger.info(f"Ranked {len(ranked)} grants (removed {scams_removed} scams)")
            return ranked[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Ranking error: {str(e)}")
            return []