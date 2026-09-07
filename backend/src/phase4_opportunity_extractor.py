"""
Phase 4 - Opportunity Data Extraction
Extract REAL data from Parallel API results
Fixed to match ACTUAL Parallel API structure
"""

import logging
import re

logger = logging.getLogger(__name__)


class OpportunityExtractor:
    """Extract structured data from Parallel API results"""
    
    @staticmethod
    def extract_name(opportunity: dict) -> str:
        """Extract opportunity name - use 'title' field"""
        
        # Parallel API uses 'title' field
        if opportunity.get('title'):
            return opportunity['title']
        
        # Fallback to other fields
        if opportunity.get('name'):
            return opportunity['name']
        
        # Extract from URL
        url = opportunity.get('url', '')
        if url:
            parts = url.split('/')
            if len(parts) > 2:
                domain = parts[2].replace('www.', '').split('.')[0]
                return f"{domain.title()} Opportunity"
        
        return 'Film Funding Opportunity'
    
    @staticmethod
    def extract_budget_from_text(text: str) -> str:
        """Extract budget amounts from excerpts text"""
        
        if not text:
            return "Amount Varies"
        
        # Look for dollar amounts: $10,000 to $100,000
        dollar_pattern = r'\$[\d,]+'
        matches = re.findall(dollar_pattern, text)
        
        if matches:
            # Return first two matches (min and max)
            if len(matches) >= 2:
                return f"{matches[0]} - {matches[1]}"
            else:
                return f"Up to {matches[0]}"
        
        # Look for "between" amounts
        between_pattern = r'between\s+\$[\d,]+\s+and\s+\$[\d,]+'
        between_match = re.search(between_pattern, text)
        if between_match:
            return between_match.group(0).replace('between ', '')
        
        return "Amount Varies"
    
    @staticmethod
    def extract_deadline_from_text(text: str) -> str:
        """Extract deadline from excerpts text"""
        
        if not text:
            return "Rolling/Ongoing"
        
        text_lower = text.lower()
        
        # Look for date patterns
        month_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}(?:,?\s+\d{4})?'
        date_match = re.search(month_pattern, text)
        
        if date_match:
            return date_match.group(0).title()
        
        # Look for "rolling" or "ongoing"
        if 'rolling' in text_lower:
            return "Rolling Deadline"
        
        if 'ongoing' in text_lower or 'open' in text_lower:
            return "Ongoing/Rolling"
        
        return "Check website"
    
    @staticmethod
    def extract_url(opportunity: dict) -> str:
        """Extract working URL"""
        
        if opportunity.get('url'):
            return opportunity['url']
        
        return 'N/A'
    
    @staticmethod
    def extract_excerpt(opportunity: dict) -> str:
        """Extract text excerpt"""
        
        excerpts = opportunity.get('excerpts', [])
        
        if excerpts and len(excerpts) > 0:
            # Return first excerpt, truncated
            excerpt = excerpts[0][:200]
            return excerpt + "..." if len(excerpts[0]) > 200 else excerpt
        
        return "No details available"
    
    @staticmethod
    def extract_opportunity(opportunity: dict) -> dict:
        """Extract all REAL data from Parallel API result"""
        
        name = OpportunityExtractor.extract_name(opportunity)
        excerpt = OpportunityExtractor.extract_excerpt(opportunity)
        
        # Extract budget and deadline from text
        budget = OpportunityExtractor.extract_budget_from_text(excerpt)
        deadline = OpportunityExtractor.extract_deadline_from_text(excerpt)
        
        extracted = {
            "name": name,
            "url": OpportunityExtractor.extract_url(opportunity),
            "budget": budget,
            "deadline": deadline,
            "excerpt": excerpt,
            "raw_data": opportunity
        }
        
        logger.info(f"Extracted: {name}")
        return extracted