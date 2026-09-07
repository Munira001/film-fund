import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """Central configuration for FILMFUND"""
    
    # Parallel API
    PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
    
    # Google Search
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
    GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    # Google Cloud
    GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
    GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION")
    
    # Validation
    @classmethod
    def validate(cls):
        """Check all required keys are set"""
        required = [
            cls.PARALLEL_API_KEY,
            cls.GOOGLE_SEARCH_API_KEY,
            cls.GOOGLE_PROJECT_ID,
        ]
        
        if not all(required):
            raise ValueError("Missing required API keys in .env file")
        
        print("✅ All configuration loaded successfully")

if __name__ == "__main__":
    Config.validate()