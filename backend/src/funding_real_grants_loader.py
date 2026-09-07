"""
Load REAL researched grant data
Data manually verified from official grant websites
"""

import json
import os
from typing import List, Dict
from logs import logger


class RealGrantsLoader:
    """Load REAL grant data from researched JSON"""
    
    def __init__(self):
        self.file_path = "data/real_grants.json"
        logger.info(" RealGrantsLoader initialized")
    
    def load_grants(self) -> List[Dict]:
        """Load real grants from JSON file"""
        try:
            if not os.path.exists(self.file_path):
                logger.warning(f"Real grants file not found: {self.file_path}")
                return []
            
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            grants = data.get("grants", [])
            logger.info(f" Loaded {len(grants)} REAL grants from file")
            
            return grants
        
        except Exception as e:
            logger.error(f" Error loading real grants: {str(e)}")
            return []