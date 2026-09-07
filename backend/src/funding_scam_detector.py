"""
PHASE 2 - Scam Detector
Detect fraudulent funding opportunities
"""

from dataclasses import dataclass
from typing import List, Dict
from logs import logger


@dataclass
class ScamAnalysis:
    is_scam: bool
    risk_level: str
    confidence: float
    red_flags: List[str]
    warnings: List[str]
    safety_score: float


class ScamDetector:
    
    def __init__(self):
        logger.info("ScamDetector initialized")
        
        self.scam_patterns = [
            'pay to apply',
            'application fee',
            'processing fee',
            'upfront payment',
            'guaranteed funding',
            'guaranteed approval',
            'wire transfer',
            'money back guarantee',
            'act now',
            'limited time',
            'fast cash',
            'no credit check',
            'easy money',
            'exclusive opportunity',
            'secret money',
            'hidden grants',
            'untapped funds',
            'unclaimed money',
            'free government money',
            'free grant money',
            'no strings attached',
            'too good to be true'
        ]
        
        self.legitimate_keywords = [
            'foundation',
            'institute',
            'university',
            'nonprofit',
            'government',
            'arts council',
            'endowment',
            'established',
            'official',
            'registered',
            'accredited'
        ]
        
        self.suspicious_domains = [
            '.tk',
            '.ml',
            '.ga',
            '.cf',
            'bit.ly',
            'tinyurl',
            'short.link'
        ]
    
    def analyze(self, opportunity: dict) -> ScamAnalysis:
        
        logger.info(f"Analyzing: {opportunity.get('name', 'Unknown')}")
        
        red_flags = []
        warnings = []
        risk_score = 0
        
        name = opportunity.get('name', '').lower()
        description = opportunity.get('description', '').lower()
        org = opportunity.get('organization', '').lower()
        link = opportunity.get('application_link', '').lower()
        eligibility = opportunity.get('eligibility_requirements', '').lower()
        
        combined_text = f"{name} {description} {org} {eligibility}".lower()
        
        for pattern in self.scam_patterns:
            if pattern in combined_text:
                red_flags.append(f"Scam pattern: '{pattern}'")
                risk_score += 15
        
        legitimate_found = False
        for keyword in self.legitimate_keywords:
            if keyword in combined_text:
                legitimate_found = True
                break
        
        if not legitimate_found:
            warnings.append("Organization not identified as legitimate")
            risk_score += 10
        
        if not link or link.strip() == '':
            red_flags.append("No application link provided")
            risk_score += 25
        
        for domain in self.suspicious_domains:
            if domain in link:
                red_flags.append(f"Suspicious domain: {domain}")
                risk_score += 20
        
        if 'http://' in link and 'https' not in link:
            warnings.append("Non-secure HTTP connection")
            risk_score += 10
        
        if 'contact' not in combined_text and 'email' not in combined_text:
            warnings.append("No contact information provided")
            risk_score += 5
        
        risk_score = min(100, risk_score)
        
        is_scam = risk_score > 50
        risk_level = 'high' if risk_score > 70 else 'medium' if risk_score > 40 else 'low'
        confidence = min(1.0, (len(red_flags) * 0.2 + len(warnings) * 0.1) / 10)
        safety_score = 100 - risk_score
        
        return ScamAnalysis(
            is_scam=is_scam,
            risk_level=risk_level,
            confidence=confidence,
            red_flags=red_flags,
            warnings=warnings,
            safety_score=safety_score
        )