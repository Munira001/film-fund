"""Gemini Multimodal Client Setup

Following official pattern from:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/intro_multimodal_use_cases.ipynb

Proper Gemini client with enterprise configuration.
"""

import os
from typing import Optional
from google import genai
from google.genai.types import GenerateContentConfig
from .config import Config
from .logs import logger

class GeminiClient:
    """
    Gemini Multimodal Client with official setup
    
    Capabilities:
    - Enterprise client initialization
    - Proper project/location configuration
    - Model selection (Gemini 2.5 Flash for multimodal)
    - Content configuration with all parameters
    - Context caching support
    """
    
    # Official model - supports multimodal
    MODEL_ID = "gemini-2.5-flash"
    
    def __init__(self):
        """Initialize Gemini client with enterprise settings"""
        try:
            logger.info("Initializing Gemini Multimodal Client")
            
            # Get project configuration
            self.project_id = Config.GOOGLE_PROJECT_ID
            self.location = Config.GOOGLE_LOCATION
            
            if not self.project_id:
                logger.error("GOOGLE_PROJECT_ID not configured in .env")
                raise ValueError("Missing GOOGLE_PROJECT_ID")
            
            # Initialize enterprise client (OFFICIAL PATTERN)
            self.client = genai.Client(
                enterprise=True,
                project=self.project_id,
                location=self.location
            )
            
            logger.info(f"Gemini client initialized: {self.project_id}")
            logger.info(f"Location: {self.location}")
            logger.info(f"Model: {self.MODEL_ID}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise
    
    def create_generation_config(self,
                                temperature: float = 0.7,
                                max_output_tokens: int = 2048,
                                audio_timestamp: bool = False,
                                top_p: float = 0.9,
                                top_k: int = 40) -> GenerateContentConfig:
        """
        Create proper GenerateContentConfig with ALL parameters
        
        audio_timestamp=True enables filmmaker urgency detection
        
        Args:
            temperature: Randomness (0-1, lower = more deterministic)
            max_output_tokens: Maximum response length
            audio_timestamp: Enables timestamp extraction
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Properly configured GenerateContentConfig
        """
        try:
            config = GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=top_p,
                top_k=top_k,
                audio_timestamp=audio_timestamp,
                candidate_count=1
            )
            
            logger.info(f"Config created: temp={temperature}, tokens={max_output_tokens}, audio_ts={audio_timestamp}")
            return config
            
        except Exception as e:
            logger.error(f"Config creation error: {str(e)}")
            raise
    
    def generate_content(self,
                        contents,
                        config: Optional[GenerateContentConfig] = None) -> str:
        """
        Generate content using Gemini multimodal
        
        Args:
            contents: List of content parts (text, images, video, audio)
            config: GenerateContentConfig
            
        Returns:
            Generated text response
        """
        try:
            if config is None:
                config = self.create_generation_config()
            
            logger.info("Calling Gemini API for content generation")
            
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=contents,
                config=config
            )
            
            logger.info("Content generation successful")
            return response.text
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            raise
    
    def create_cache(self, prompt: str, ttl: str = "3600s"):
        """
        Create content cache for large prompts
        
        Args:
            prompt: Large prompt to cache
            ttl: Time to live for cache
            
        Returns:
            Cache object
        """
        try:
            from google.genai.types import CreateCachedContentConfig
            
            logger.info(f"Creating content cache (TTL: {ttl})")
            
            cached_content = self.client.caches.create(
                model=self.MODEL_ID,
                config=CreateCachedContentConfig(
                    contents=prompt,
                    ttl=ttl,
                ),
            )
            
            logger.info(f"Cache created: {cached_content.name}")
            return cached_content
            
        except Exception as e:
            logger.error(f"Cache creation error: {str(e)}")
            raise
    
    def generate_with_cache(self,
                           question: str,
                           cached_content,
                           config: Optional[GenerateContentConfig] = None) -> str:
        """
        Generate content using cached context
        
        Args:
            question: Question to ask
            cached_content: Previously cached content
            config: GenerateContentConfig
            
        Returns:
            Generated response
        """
        try:
            if config is None:
                config = self.create_generation_config()
            
            logger.info("Calling Gemini API with cached content")
            
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=question,
                config=GenerateContentConfig(
                    cached_content=cached_content.name,
                    **config.__dict__
                ),
            )
            
            logger.info("Content generation with cache successful")
            return response.text
            
        except Exception as e:
            logger.error(f"Cached generation error: {str(e)}")
            raise

# Global instance
gemini_client = GeminiClient()