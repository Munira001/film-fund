"""
Error Recovery
Handle errors with fallback and retry logic
"""

import logging
import time

logger = logging.getLogger(__name__)


class ErrorHandler:
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        logger.info(f"ErrorHandler initialized (max_retries={max_retries})")
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed: {str(e)}")
                    raise
    
    def fallback_strategy(self, primary_func, fallback_func, *args, **kwargs):
        """Try primary, fall back if fails"""
        
        try:
            logger.info("Attempting primary strategy...")
            return primary_func(*args, **kwargs)
        
        except Exception as e:
            logger.warning(f"Primary failed: {str(e)}. Using fallback...")
            try:
                return fallback_func(*args, **kwargs)
            except Exception as e2:
                logger.error(f"Fallback also failed: {str(e2)}")
                raise
    
    def graceful_degradation(self, data: dict, required_fields: list) -> bool:
        """Check if data is usable despite errors"""
        
        missing = [f for f in required_fields if f not in data]
        
        if not missing:
            return True
        elif len(missing) <= len(required_fields) // 2:
            logger.warning(f"Degraded mode: missing {missing}")
            return True
        else:
            logger.error(f"Too many missing fields: {missing}")
            return False