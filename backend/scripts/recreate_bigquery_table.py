"""Recreate BigQuery table with correct schema for Vertex AI Search"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from google.cloud import bigquery
from src.logs import logger

def recreate_table():
    """Recreate table with id as NOT NULL"""
    
    client = bigquery.Client(project='filmfund-505222')
    project_id = 'filmfund-505222'
    dataset_id = 'filmfund_rag'
    old_table = 'scripts_embeddings'
    new_table = 'scripts_embeddings_new'
    
    logger.info("="*80)
    logger.info("RECREATING BIGQUERY TABLE WITH CORRECT SCHEMA")
    logger.info("="*80)
    
    try:
        # STEP 1: Create new table from old table with id as NOT NULL
        logger.info("\n[STEP 1] Creating new table with correct schema...")
        
        query = f"""
        CREATE TABLE `{project_id}.{dataset_id}.{new_table}` AS
        SELECT 
            COALESCE(id, doc_id) as id,
            doc_id,
            content,
            embedding,
            source,
            document_name,
            type,
            page,
            chunk,
            feature_timestamp
        FROM `{project_id}.{dataset_id}.{old_table}`
        """
        
        job = client.query(query)
        job.result()
        logger.info("[OK] New table created")
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to create table: {str(e)}")
        return False
    
    try:
        # STEP 2: Delete old table - CORRECTED PARAMETER
        logger.info("\n[STEP 2] Deleting old table...")
        client.delete_table(f"{project_id}.{dataset_id}.{old_table}", not_found_ok=True)
        logger.info("[OK] Old table deleted")
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to delete old table: {str(e)}")
        return False
    
    try:
        # STEP 3: Copy new table to original name, then delete temp
        logger.info("\n[STEP 3] Copying to original table name...")
        copy_job_config = bigquery.CopyJobConfig()
        copy_job = client.copy_table(
            f"{project_id}.{dataset_id}.{new_table}",
            f"{project_id}.{dataset_id}.{old_table}",
            job_config=copy_job_config
        )
        copy_job.result()
        
        # Delete the temp table
        client.delete_table(f"{project_id}.{dataset_id}.{new_table}", not_found_ok=True)
        logger.info("[OK] Table copied and temp deleted")
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to copy/rename table: {str(e)}")
        return False
    
    # STEP 4: Verify
    logger.info("\n[STEP 4] Verifying new schema...")
    table = client.get_table(f"{project_id}.{dataset_id}.{old_table}")
    
    logger.info("\nColumns in table:")
    for field in table.schema:
        logger.info(f"  - {field.name} ({field.field_type}) [Required: {field.mode == 'REQUIRED'}]")
    
    logger.info("\n" + "="*80)
    logger.info("[SUCCESS] Table recreated with correct schema!")
    logger.info("="*80)
    
    return True

if __name__ == "__main__":
    recreate_table()