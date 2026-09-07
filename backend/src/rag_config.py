"""RAG Configuration - COMPONENT 2

Following official patterns from:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/retrieval-augmented-generation/rag_qna_with_bq_and_featurestore.ipynb
"""

from .config import Config

# BigQuery Configuration
BIGQUERY_DATASET = "filmfund_rag"  # FILMFUND-specific dataset
BIGQUERY_TABLE = "scripts_embeddings"  # Table for script embeddings
BIGQUERY_LOCATION = Config.GOOGLE_LOCATION  # us-central1

# Embedding Configuration
EMBEDDING_MODEL = "text-embedding-005"  # OFFICIAL: Must use this model

# LLM Configuration
LLM_MODEL = "gemini-2.5-flash"  # Our model

# Document Chunking Configuration
CHUNK_SIZE = 1000  # OFFICIAL: Chunk size from notebook
CHUNK_OVERLAP = 50  # OFFICIAL: Overlap from notebook
CHUNK_SEPARATORS = ["\n\n", "\n", ".", "!", "?", ",", " ", ""]  # OFFICIAL

# Project Configuration
PROJECT_ID = Config.GOOGLE_PROJECT_ID
LOCATION = Config.GOOGLE_LOCATION

# Feature Store Configuration
FEATURE_STORE_ONLINE_STORE_ID = "filmfund_online_store"
FEATURE_VIEW_ID = "scripts_feature_view"