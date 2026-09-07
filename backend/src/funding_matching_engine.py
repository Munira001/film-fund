"""
ADVANCED MATCHING ENGINE - Phase 2 Core Feature
Intelligent matching between filmmaker profiles and funding opportunities

Official References:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/retrieval-augmented-generation/rag_qna_with_bq_and_featurestore.ipynb
https://python.langchain.com/docs/modules/retrievers/
"""

import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from logs import logger
from filmmaker_profile import FilmmakerProfile


# ============================================================================
# MATCHING SCORE DATA MODEL
# ============================================================================

@dataclass
class MatchScore:
    """Complete matching analysis"""
    
    overall_score: float  # 0-100
    confidence: float  # 0-1.0
    budget_score: float  # 0-100
    genre_score: float  # 0-100
    experience_score: float  # 0-100
    timeline_score: float  # 0-100
    location_score: float  # 0-100
    scam_risk: float  # 0-1.0 (probability it's a scam)
    red_flags: List[str] = None
    reasoning: str = ""
    
    def __post_init__(self):
        if self.red_flags is None:
            self.red_flags = []


# ============================================================================
# PART 1: ADVANCED MATCHING ENGINE
# ============================================================================

class AdvancedMatchingEngine:
    """
    Intelligent matching between filmmaker and opportunities
    Uses multi-factor weighted algorithm
    """
    
    # Weighting factors (must sum to 1.0)
    WEIGHTS = {
        "budget": 0.30,        # Budget match most important
        "genre": 0.25,         # Genre match
        "experience": 0.20,    # Experience requirements
        "timeline": 0.15,      # Deadline alignment
        "location": 0.10       # Geographic restrictions
    }
    
    def __init__(self, profile: FilmmakerProfile):
        """Initialize with filmmaker profile"""
        self.profile = profile
        logger.info(f"AdvancedMatchingEngine initialized for: {profile.project_title}")
    
    def calculate_match(self, opportunity: Dict) -> MatchScore:
        """
        Calculate comprehensive match score
        Returns detailed analysis with confidence and risk factors
        """
        
        # Calculate individual scores
        budget_score = self._score_budget(opportunity)
        genre_score = self._score_genre(opportunity)
        experience_score = self._score_experience(opportunity)
        timeline_score = self._score_timeline(opportunity)
        location_score = self._score_location(opportunity)
        
        # Calculate weighted overall score
        overall_score = (
            budget_score * self.WEIGHTS["budget"] +
            genre_score * self.WEIGHTS["genre"] +
            experience_score * self.WEIGHTS["experience"] +
            timeline_score * self.WEIGHTS["timeline"] +
            location_score * self.WEIGHTS["location"]
        )
        
        # Calculate confidence (how sure are we about this match?)
        confidence = self._calculate_confidence(opportunity)
        
        # Detect scam risk
        scam_risk, red_flags = self._assess_scam_risk(opportunity)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            budget_score, genre_score, experience_score, 
            timeline_score, location_score, red_flags
        )
        
        score = MatchScore(
            overall_score=min(overall_score, 100.0),
            confidence=confidence,
            budget_score=budget_score,
            genre_score=genre_score,
            experience_score=experience_score,
            timeline_score=timeline_score,
            location_score=location_score,
            scam_risk=scam_risk,
            red_flags=red_flags,
            reasoning=reasoning
        )
        
        return score
    
    def _score_budget(self, opportunity: Dict) -> float:
        """Score budget compatibility (0-100)"""
        
        opp_amount = opportunity.get("amount", 0)
        filmmaker_budget = self.profile.total_budget_needed
        
        if opp_amount <= 0:
            return 50.0  # Unknown amount
        
        # Perfect match
        if opp_amount == filmmaker_budget:
            return 100.0
        
        # Within 10%
        if abs(opp_amount - filmmaker_budget) / filmmaker_budget < 0.10:
            return 95.0
        
        # Within 25%
        if abs(opp_amount - filmmaker_budget) / filmmaker_budget < 0.25:
            return 85.0
        
        # Within 50%
        if abs(opp_amount - filmmaker_budget) / filmmaker_budget < 0.50:
            return 70.0
        
        # Within double/half
        if filmmaker_budget * 0.5 <= opp_amount <= filmmaker_budget * 2:
            return 50.0
        
        # Too different
        return 20.0
    
    def _score_genre(self, opportunity: Dict) -> float:
        """Score genre compatibility (0-100)"""
        
        opp_genres = opportunity.get("genre_focus", [])
        filmmaker_genre = self.profile.film_genre.lower()
        
        if not opp_genres:
            return 60.0  # Unknown genre focus
        
        opp_genres = [g.lower() for g in opp_genres]
        
        # Exact match
        if filmmaker_genre in opp_genres:
            return 100.0
        
        # Related genres
        genre_relationships = {
            "drama": ["indie", "experimental", "short-film"],
            "documentary": ["indie", "experimental"],
            "sci-fi": ["action", "indie"],
            "comedy": ["indie", "short-film"],
            "animation": ["experimental", "short-film"],
            "other": ["all", "any", "all genres"],
            "indie": ["all", "any", "all genres"]
        }
        
        if filmmaker_genre in genre_relationships:
            related = genre_relationships[filmmaker_genre]
            if any(g in opp_genres for g in related):
                return 80.0
        
        # Generic support
        if any(g in opp_genres for g in ["all", "any", "all genres", "other"]):
            return 70.0
        
        # No match
        return 30.0
    
    def _score_experience(self, opportunity: Dict) -> float:
        """Score experience requirement compatibility (0-100)"""
        
        opp_exp = opportunity.get("experience_required", "").lower()
        filmmaker_exp = self.profile.experience_level.lower()
        
        if not opp_exp or "all" in opp_exp:
            return 100.0  # Accepts all levels
        
        # Perfect match
        if filmmaker_exp in opp_exp or opp_exp in filmmaker_exp:
            return 100.0
        
        # First-time filmmaker
        if filmmaker_exp == "first-time":
            if "first" in opp_exp or "beginner" in opp_exp or "emerging" in opp_exp:
                return 100.0
            else:
                return 40.0  # Prefers experienced
        
        # Experienced filmmaker
        if filmmaker_exp in ["experienced", "professional"]:
            if "experienced" in opp_exp or "professional" in opp_exp:
                return 100.0
            else:
                return 80.0  # Can still apply
        
        return 70.0
    
    def _score_timeline(self, opportunity: Dict) -> float:
        """Score deadline alignment with project timeline (0-100)"""
        
        deadline = opportunity.get("deadline")
        
        if not deadline:
            return 70.0  # Ongoing opportunity
        
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
            project_start = datetime.strptime(self.profile.start_date, "%Y-%m-%d")
            now = datetime.now()
            
            days_until_deadline = (deadline_date - now).days
            days_until_start = (project_start - now).days
            
            # Deadline is 6-12 months before start (IDEAL)
            if 180 <= days_until_deadline <= 365:
                return 100.0
            
            # Deadline is 3-6 months before (GOOD)
            if 90 <= days_until_deadline < 180:
                return 85.0
            
            # Deadline is 1-3 months before (ACCEPTABLE)
            if 30 <= days_until_deadline < 90:
                return 70.0
            
            # Deadline is very soon (RISKY)
            if 0 <= days_until_deadline < 30:
                return 40.0
            
            # Deadline has passed
            if days_until_deadline < 0:
                return 0.0
            
            # Too far in future
            if days_until_deadline > 365:
                return 50.0
                
        except Exception as e:
            logger.warning(f"Could not parse timeline: {str(e)}")
            return 60.0
        
        return 60.0
    
    def _score_location(self, opportunity: Dict) -> float:
        """Score location compatibility (0-100)"""
        
        restrictions = opportunity.get("location_restrictions", [])
        filmmaker_location = self.profile.filmmaker_location.lower()
        
        if not restrictions:
            return 100.0  # No restrictions
        
        for restriction in restrictions:
            if filmmaker_location in restriction.lower() or restriction.lower() in filmmaker_location:
                return 100.0
        
        # Has restrictions but doesn't match
        return 30.0
    
    def _calculate_confidence(self, opportunity: Dict) -> float:
        """
        Calculate confidence in match score (0-1.0)
        Based on data completeness
        """
        
        confidence = 0.5  # Base confidence
        
        # Add confidence for complete fields
        if opportunity.get("amount") and opportunity.get("amount") > 0:
            confidence += 0.15
        
        if opportunity.get("deadline"):
            confidence += 0.15
        
        if opportunity.get("eligibility_requirements"):
            confidence += 0.10
        
        if opportunity.get("genre_focus"):
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def _assess_scam_risk(self, opportunity: Dict) -> Tuple[float, List[str]]:
        """
        Assess probability opportunity is a scam
        Returns: (risk_score 0-1.0, list of red flags)
        """
        
        red_flags = []
        risk_score = 0.0
        
        name = opportunity.get("name", "").lower()
        description = opportunity.get("description", "").lower()
        eligibility = opportunity.get("eligibility_requirements", "").lower()
        text = f"{name} {description} {eligibility}"
        
        # Red flag patterns
        scam_patterns = [
            ("pay to apply", 0.4),
            ("application fee", 0.3),
            ("processing fee", 0.4),
            ("upfront payment", 0.5),
            ("guaranteed funding", 0.5),
            ("guaranteed approval", 0.4),
            ("wire transfer", 0.4),
            ("money back guarantee", 0.3),
            ("too good to be true", 0.3),
            ("act now", 0.2),
            ("limited time", 0.2)
        ]
        
        for pattern, risk in scam_patterns:
            if pattern in text:
                red_flags.append(f"Flagged: '{pattern}'")
                risk_score += risk
        
        # Missing legitimate organization
        if not opportunity.get("organization"):
            red_flags.append("No organization name")
            risk_score += 0.1
        
        # Missing application link
        if not opportunity.get("application_link"):
            red_flags.append("No application link")
            risk_score += 0.1
        
        # Suspiciously high amount
        if opportunity.get("amount") and opportunity.get("amount") > 10000000:
            red_flags.append("Unusually high amount")
            risk_score += 0.1
        
        return min(risk_score, 1.0), red_flags
    
    def _generate_reasoning(self, budget_score: float, genre_score: float,
                           experience_score: float, timeline_score: float,
                           location_score: float, red_flags: List[str]) -> str:
        """Generate human-readable reasoning for match"""
        
        reasoning = "Match analysis: "
        
        # Budget
        if budget_score >= 85:
            reasoning += "Budget is excellent fit. "
        elif budget_score >= 70:
            reasoning += "Budget is reasonable fit. "
        elif budget_score >= 50:
            reasoning += "Budget is partial match. "
        else:
            reasoning += "Budget may not align. "
        
        # Genre
        if genre_score >= 85:
            reasoning += "Genre is preferred. "
        elif genre_score >= 70:
            reasoning += "Genre is acceptable. "
        else:
            reasoning += "Genre may have restrictions. "
        
        # Experience
        if experience_score >= 80:
            reasoning += "Experience level matches. "
        elif experience_score >= 50:
            reasoning += "Experience level may work. "
        else:
            reasoning += "Experience level may be barrier. "
        
        # Timeline
        if timeline_score >= 85:
            reasoning += "Timeline is ideal. "
        elif timeline_score >= 70:
            reasoning += "Timeline is manageable. "
        elif timeline_score >= 40:
            reasoning += "Timeline is tight. "
        else:
            reasoning += "Timeline is problem. "
        
        # Red flags
        if red_flags:
            reasoning += f"⚠️ {len(red_flags)} concerns: {', '.join(red_flags[:2])}"
        else:
            reasoning += "✅ No red flags detected."
        
        return reasoning


# ============================================================================
# TESTING
# ============================================================================

def test_matching():
    """Test matching engine"""
    
    logger.info("Testing Advanced Matching Engine...")
    
    # Create test profile
    profile = FilmmakerProfile(
        project_title="Test Film",
        project_logline="Test logline",
        film_genre="drama",
        visual_style="cinematic",
        film_rating="PG-13",
        project_description="Test description",
        total_budget_needed=100000,
        start_date="2026-12-01",
        filmmaker_name="Test",
        filmmaker_email="test@test.com",
        experience_level="experienced",
        filmmaker_location="California"
    )
    
    # Create test opportunity
    test_opp = {
        "name": "Film Arts Foundation Grant",
        "amount": 95000,
        "deadline": "2026-11-15",
        "genre_focus": ["drama", "indie"],
        "experience_required": "experienced",
        "location_restrictions": ["California", "West Coast"],
        "eligibility_requirements": "Independent drama films",
        "organization": "Film Arts Foundation",
        "application_link": "https://filmarts.org/apply"
    }
    
    # Test matching
    engine = AdvancedMatchingEngine(profile)
    score = engine.calculate_match(test_opp)
    
    print("\n" + "="*80)
    print("MATCHING ENGINE TEST RESULTS")
    print("="*80)
    print(f"\nOpportunity: {test_opp['name']}")
    print(f"Overall Score: {score.overall_score:.1f}/100")
    print(f"Confidence: {score.confidence:.0%}")
    print(f"Scam Risk: {score.scam_risk:.0%}")
    print(f"\nScores:")
    print(f"  Budget: {score.budget_score:.1f}/100")
    print(f"  Genre: {score.genre_score:.1f}/100")
    print(f"  Experience: {score.experience_score:.1f}/100")
    print(f"  Timeline: {score.timeline_score:.1f}/100")
    print(f"  Location: {score.location_score:.1f}/100")
    print(f"\nReasoning: {score.reasoning}")
    
    if score.red_flags:
        print(f"\nRed Flags:")
        for flag in score.red_flags:
            print(f"  - {flag}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_matching()