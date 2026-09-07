"""Cache system for API failures"""

import json
import os
from logs import logger
from models import Grant

class GrantCache:
    """Cache grants locally as backup"""
    
    CACHE_FILE = "data/grants_cache.json"
    
    @staticmethod
    def save_grants(grants: list) -> None:
        """Save grants to cache"""
        try:
            os.makedirs("data", exist_ok=True)
            
            with open(GrantCache.CACHE_FILE, 'w') as f:
                json.dump([g.__dict__ for g in grants], f)
            
            logger.info(f"Cached {len(grants)} grants")
            
        except Exception as e:
            logger.error(f"Cache save failed: {str(e)}")
    
    @staticmethod
    def load_grants() -> list:
        """Load cached grants if API fails"""
        try:
            if not os.path.exists(GrantCache.CACHE_FILE):
                logger.warning("No cache file found")
                return []
            
            with open(GrantCache.CACHE_FILE, 'r') as f:
                data = json.load(f)
            
            # Convert dicts back to Grant objects
            grants = []
            for item in data:
                try:
                    grant = Grant(**item)
                    grants.append(grant)
                except Exception as e:
                    logger.warning(f"Could not load cached grant: {str(e)}")
            
            logger.info(f"Using cached {len(grants)} grants (API may be down)")
            return grants
            
        except Exception as e:
            logger.error(f"Cache load failed: {str(e)}")
            return []