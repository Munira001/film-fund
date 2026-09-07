"""Data models for FILMFUND"""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Filmmaker:
    """Filmmaker profile"""
    budget_min: int
    budget_max: int
    genre: str
    experience: str  # first-time, some, experienced
    timeline: str    # urgent, 3months, 6months
    location: str    # state/country

@dataclass
class Grant:
    """Film grant opportunity"""
    name: str
    amount: int
    deadline: str
    eligibility: str
    organization: str
    link: str
    relevance_score: float = 0.0
    fit_score: float = 0.0

@dataclass
class Producer:
    """Production company"""
    name: str
    specialization: str  # genre focus
    budget_range: str
    past_films: List[str]
    contact_info: str

@dataclass
class FundingOpportunity:
    """Complete funding opportunity"""
    type: str  # grant, producer, crowdfunding
    name: str
    amount: int
    details: dict
    next_steps: str
    rank_score: float = 0.0