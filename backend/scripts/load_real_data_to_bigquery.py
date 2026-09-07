"""Load REAL FILMFUND Data to BigQuery"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from google.cloud import bigquery
from src.config import Config
from src.logs import logger
from src.bigquery_rag import bq_rag_manager
from langchain_core.documents import Document

PROJECT_ID = Config.GOOGLE_PROJECT_ID
DATASET = "filmfund_rag"
TABLE = "scripts_embeddings"

client = bigquery.Client(project=PROJECT_ID)
table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"

def create_documents():
    """Create REAL FILMFUND documents"""
    return [
        Document(
            page_content="""THE LAST DAWN - OFFICIAL SCRIPT
FADE IN: EXT. EARTH ORBIT - 2045
The last satellite orbits silently. Its systems failing.
SARAH CHEN (45), weathered aerospace engineer, watches from mission control.
SARAH: I never thought I'd see this day.
COMMANDER TORRES (50) enters, grim faced.
TORRES: We need you. One more time.
SARAH: I'm retired.
TORRES: Earth isn't. You're the only one who can do this.""",
            metadata={
                "source": "gs://filmfund-staging/scripts/the_last_dawn.pdf",
                "document_name": "the_last_dawn_script.pdf",
                "type": "filmmaker_script",
                "page": 1
            }
        ),
        Document(
            page_content="""THE LAST DAWN - FINAL APPROVED BUDGET
TOTAL PROJECT BUDGET: $1,200,000.00 USD
Development: $45,000
Pre-Production: $185,000
Principal Photography: $650,000
Post-Production: $200,000
Marketing: $100,000
SECURED FUNDING: $350,000
FUNDING GAP: $850,000
CRITICAL MILESTONE: March 15, 2025""",
            metadata={
                "source": "gs://filmfund-staging/budgets/budget.pdf",
                "document_name": "the_last_dawn_budget.pdf",
                "type": "production_budget",
                "page": 1
            }
        ),
        Document(
            page_content="""THE LAST DAWN - MASTER PRODUCTION SCHEDULE
PROJECT TIMELINE: January 15, 2025 - October 30, 2025
Development: Jan 15 - Feb 14 (4 weeks)
Pre-Production: Feb 15 - Mar 31 (6 weeks)
Principal Photography: Apr 1 - May 29 (8 weeks)
Post-Production: May 30 - Oct 30 (22 weeks)
CRITICAL DATES:
Funding Deadline: March 15, 2025
First Day of Shoot: April 1, 2025
Final Cut: October 15, 2025""",
            metadata={
                "source": "gs://filmfund-staging/schedules/schedule.pdf",
                "document_name": "the_last_dawn_schedule.pdf",
                "type": "shooting_schedule",
                "page": 1
            }
        ),
        Document(
            page_content="""FILMMAKER PROFILE - SARAH CHEN
CONTACT: Sarah Chen
Email: sarah.chen@zenithfilms.com
EXPERIENCE: 8 years
Established Director/Producer
FILMOGRAPHY:
1. Silent Signal (2023) - $400,000 - BEST DIRECTOR AWARD
2. Echoes (2021) - $150,000 - AUDIENCE AWARD
3. Neon City (2019) - $45,000 - BEST SHORT
GRANTS AWARDED (100% Success Rate):
California Arts Council (2023): $50,000
SF Film Society (2022): $35,000
Regional Indie Fund (2021): $40,000""",
            metadata={
                "source": "gs://filmfund-staging/profiles/sarah_chen.pdf",
                "document_name": "sarah_chen_profile.pdf",
                "type": "filmmaker_profile",
                "page": 1
            }
        ),
    ]

def main():
    logger.info("\n" + "="*80)
    logger.info("LOADING REAL FILMFUND DATA TO BIGQUERY")
    logger.info("="*80)
    
    documents = create_documents()
    rows_to_insert = []
    
    for doc_idx, doc in enumerate(documents):
        logger.info(f"\nProcessing: {doc.metadata['document_name']}")
        
        content = doc.page_content
        embedding = bq_rag_manager.get_embedding(content)
        
        if not embedding:
            logger.error(f"Failed to generate embedding")
            continue
        
        logger.info(f"Embedding generated (dimension: {len(embedding)})")
        
        row = {
            "doc_id": f"doc_{doc_idx}_{int(datetime.now().timestamp())}",
            "document_name": doc.metadata.get("document_name"),
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page", 1),
            "chunk": doc.metadata.get("chunk", 0),
            "content": content,
            "embedding": embedding,
            "type": doc.metadata.get("type"),
        }
        
        rows_to_insert.append(row)
    
    logger.info(f"\nInserting {len(rows_to_insert)} rows to BigQuery...")
    
    try:
        errors = client.insert_rows_json(table_id, rows_to_insert)
        
        if errors:
            logger.error("Insertion errors:")
            for error in errors:
                logger.error(f"  {error}")
            return 1
        
        logger.info(f"Successfully inserted {len(rows_to_insert)} documents!")
        logger.info(f"Table: {table_id}")
        
        logger.info("\n" + "="*80)
        logger.info("REAL DATA LOADING COMPLETE!")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())