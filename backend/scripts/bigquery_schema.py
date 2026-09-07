"""Fix BigQuery schema - add id column for Vertex AI Search"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from google.cloud import bigquery
from src.logs import logger

def fix_schema():
    """Add id column to scripts_embeddings table"""
    
    client = bigquery.Client(project='filmfund-505222')
    table_id = 'filmfund-505222.filmfund_rag.scripts_embeddings'
    
    logger.info("="*80)
    logger.info("FIXING BIGQUERY SCHEMA")
    logger.info("="*80)
    
    try:
        # STEP 1: Add id column
        logger.info("\n[STEP 1] Adding id column...")
        query1 = f"ALTER TABLE `{table_id}` ADD COLUMN id STRING NOT NULL"
        job1 = client.query(query1)
        job1.result()
        logger.info("[OK] id column added")
        
    except Exception as e:
        if "already exists" in str(e):
            logger.info("[OK] id column already exists")
        else:
            logger.error(f"[ERROR] Failed to add column: {str(e)}")
            return False
    
    try:
        # STEP 2: Populate id column with doc_id values
        logger.info("\n[STEP 2] Populating id column...")
        query2 = f"UPDATE `{table_id}` SET id = doc_id WHERE id IS NULL"
        job2 = client.query(query2)
        job2.result()
        logger.info("[OK] id column populated")
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to populate column: {str(e)}")
        return False
    
    # STEP 3: Verify
    logger.info("\n[STEP 3] Verifying schema...")
    table = client.get_table(table_id)
    
    logger.info("\nColumns in table:")
    for field in table.schema:
        logger.info(f"  - {field.name} ({field.field_type}) [Required: {field.mode == 'REQUIRED'}]")
    
    logger.info("\n" + "="*80)
    logger.info("[SUCCESS] Schema fixed! id column is now present")
    logger.info("="*80)
    
    return True

if __name__ == "__main__":
    fix_schema()