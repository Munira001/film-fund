"""
PHASE 2 - Real Eligibility Parser
Uses REAL grant requirements from 25+ verified programs
"""

import json
import os
from dataclasses import dataclass
from typing import List, Dict, Optional
from logs import logger


@dataclass
class EligibilityMatch:
    grant_name: str
    site: str
    match_score: float
    reasons: List[str]
    conflicts: List[str]


class RealEligibilityParser:
    
    def __init__(self):
        logger.info("RealEligibilityParser initialized with REAL grant data")
        self.grants_file = "data/real_grant_requirements.json"
        self.grants = self._load_real_grants()
    
    def _load_real_grants(self) -> List[Dict]:
        try:
            if os.path.exists(self.grants_file):
                with open(self.grants_file, 'r') as f:
                    data = json.load(f)
                    all_grants = []
                    for site_data in data.get('grants', []):
                        for program in site_data.get('programs', []):
                            program['site'] = site_data.get('site')
                            program['site_url'] = site_data.get('url')
                            all_grants.append(program)
                    logger.info(f"Loaded {len(all_grants)} REAL grants from file")
                    return all_grants
            else:
                logger.warning(f"Real grants file not found: {self.grants_file}")
                return []
        except Exception as e:
            logger.error(f"Error loading real grants: {str(e)}")
            return []
    
    def match_filmmaker_to_grants(self, filmmaker_profile: dict) -> List[EligibilityMatch]:
        matches = []
        
        for grant in self.grants:
            score = 0
            reasons = []
            conflicts = []
            
            budget = filmmaker_profile.get('total_budget_needed', 0)
            if grant['budget_min'] and budget < grant['budget_min']:
                conflicts.append(f"Budget below minimum ${grant['budget_min']:,.0f}")
            elif grant['budget_max'] == 0:
                score += 15
                reasons.append("Budget flexible or not specified")
            else:
                score += 15
                reasons.append("Budget within range")
            
            if grant['budget_max'] and grant['budget_max'] > 0 and budget > grant['budget_max']:
                conflicts.append(f"Budget exceeds maximum ${grant['budget_max']:,.0f}")
            elif grant['budget_max'] > 0:
                score += 15
                reasons.append("Budget feasible")
            
            filmmaker_exp = filmmaker_profile.get('experience_level', 'some')
            exp_levels = ['first-time', 'some', 'experienced', 'professional']
            filmmaker_exp_index = exp_levels.index(filmmaker_exp) if filmmaker_exp in exp_levels else 1
            grant_exp_index = exp_levels.index(grant['experience_level']) if grant['experience_level'] in exp_levels else 1
            
            if filmmaker_exp_index >= grant_exp_index or grant['experience_level'] == 'any':
                score += 20
                reasons.append(f"Experience level matches: {grant['experience_level']}")
            else:
                conflicts.append(f"Requires {grant['experience_level']} experience, you have {filmmaker_exp}")
            
            filmmaker_genre = filmmaker_profile.get('film_genre', 'other').lower()
            if 'all' in grant['genres'] or filmmaker_genre in grant['genres']:
                score += 20
                reasons.append(f"Genre eligible: {', '.join(grant['genres'][:3])}")
            else:
                conflicts.append(f"Genre {filmmaker_genre} not in eligible genres")
            
            filmmaker_stage = filmmaker_profile.get('production_stage', 'pre-production').lower()
            if 'any' in grant['project_stages'] or filmmaker_stage in grant['project_stages']:
                score += 15
                reasons.append(f"Project stage eligible")
            else:
                conflicts.append(f"Stage {filmmaker_stage} not eligible")
            
            if grant.get('portfolio_required') and not filmmaker_profile.get('has_portfolio', False):
                conflicts.append("Portfolio required but not available")
                score -= 10
            elif not grant.get('portfolio_required'):
                score += 5
                reasons.append("No portfolio required")
            
            if grant.get('application_fee'):
                conflicts.append("Application fee required")
            else:
                score += 5
                reasons.append("No application fee")
            
            final_score = max(0, min(100, score))
            
            match = EligibilityMatch(
                grant_name=grant.get('name', 'Unknown'),
                site=grant.get('site', 'Unknown'),
                match_score=final_score,
                reasons=reasons,
                conflicts=conflicts
            )
            
            matches.append(match)
        
        matches.sort(key=lambda x: x.match_score, reverse=True)
        logger.info(f"Matched {len(matches)} grants to filmmaker")
        
        return matches