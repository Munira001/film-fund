"""
Real Google Custom Search Integration
Get real funding opportunities from Google Search
"""

import requests
import json
import os
from typing import List, Dict
from logs import logger

class GoogleSearchLoader:
    """Load REAL data from Google Custom Search"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "d490fa5f925574ef1")
        self.endpoint = "https://www.googleapis.com/customsearch/v1"
        logger.info("GoogleSearchLoader initialized")
    
    def search_film_grants(self, query: str = "film grants", num: int = 10) -> List[Dict]:
        """
        REAL Google Custom Search for film grants
        Returns REAL opportunities from Google results
        """
        try:
            logger.info(f"🔍 Google CSE: Searching '{query}'")
            
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.engine_id,
                "num": num,
                "gl": "us",
                "lr": "lang_en"
            }
            
            response = requests.get(self.endpoint, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                logger.info(f" Google CSE: Found {len(items)} results")
                
                # Convert to opportunity format
                opportunities = []
                for item in items:
                    opp = {
                        "id": f"google_{item['link'].replace('/', '_')[:40]}",
                        "name": item.get("title", "Unknown"),
                        "description": item.get("snippet", ""),
                        "organization": item.get("displayLink", ""),
                        "application_link": item["link"],
                        "source": "google-cse",
                        "type": "grant"
                    }
                    opportunities.append(opp)
                
                return opportunities
            else:
                logger.warning(f" Google CSE error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f" Google CSE error: {str(e)}")
            return []
    
    def search_multiple_queries(self) -> List[Dict]:
        """
        Search multiple queries to get comprehensive real data
        """
        all_results = []
        
        queries = [
            "film grants for independent filmmakers",
            "documentary film funding",
            "short film grants",
            "low budget film grants",
            "emerging filmmaker grants",
            "film production funding"
        ]
        
        for query in queries:
            logger.info(f"Searching: {query}")
            results = self.search_film_grants(query, num=5)
            all_results.extend(results)
            print(f"   Found {len(results)} results for '{query}'")
        
        # Remove duplicates
        unique = {opp["application_link"]: opp for opp in all_results}
        logger.info(f" Total unique opportunities: {len(unique)}")
        
        return list(unique.values())