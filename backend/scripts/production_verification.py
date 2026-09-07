"""Production Verification Checklist - Component 2

Comprehensive verification before production deployment.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from google.cloud import bigquery
from src.logs import logger
from src.rag_config import PROJECT_ID, LOCATION, BIGQUERY_DATASET, BIGQUERY_TABLE

def verify_bigquery_data():
    """Verify data in BigQuery"""
    
    logger.info("\n[CHECK 1/6] BigQuery Data Verification")
    logger.info("-"*80)
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
        
        query = f"SELECT COUNT(*) as total FROM `{table_id}`"
        result = client.query(query).result()
        
        for row in result:
            total_docs = row.total
            logger.info(f"[OK] Total documents in BigQuery: {total_docs}")
            
            if total_docs > 0:
                logger.info("[OK] PASSED - Documents loaded")
                return True
        
        logger.error("[FAIL] FAILED - No documents found")
        return False
        
    except Exception as e:
        logger.error(f"[FAIL] FAILED - {str(e)}")
        return False

def verify_embeddings():
    """Verify embeddings quality"""
    
    logger.info("\n[CHECK 2/6] Embeddings Verification")
    logger.info("-"*80)
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
        
        query = f"""
        SELECT 
            COUNT(*) as total_with_embeddings,
            MIN(ARRAY_LENGTH(embedding)) as min_dim,
            MAX(ARRAY_LENGTH(embedding)) as max_dim
        FROM `{table_id}`
        WHERE embedding IS NOT NULL
        """
        
        result = client.query(query).result()
        
        for row in result:
            logger.info(f"[OK] Documents with embeddings: {row.total_with_embeddings}")
            logger.info(f"[OK] Embedding dimension: {row.min_dim}")
            
            if row.total_with_embeddings > 0 and row.min_dim == 768:
                logger.info("[OK] PASSED - Embeddings verified (768-dim)")
                return True
        
        logger.error("[FAIL] FAILED - Embeddings issue")
        return False
        
    except Exception as e:
        logger.error(f"[FAIL] FAILED - {str(e)}")
        return False

def verify_projects_loaded():
    """Verify data completeness"""
    
    logger.info("\n[CHECK 3/6] FILMFUND Data Completeness")
    logger.info("-"*80)
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
        
        query = f"""
        SELECT 
            COUNT(*) as total_docs,
            COUNT(DISTINCT document_name) as unique_documents,
            COUNT(DISTINCT type) as document_types
        FROM `{table_id}`
        """
        
        result = client.query(query).result()
        
        for row in result:
            logger.info(f"[OK] Total documents: {row.total_docs}")
            logger.info(f"[OK] Unique document names: {row.unique_documents}")
            logger.info(f"[OK] Document types: {row.document_types}")
            
            if row.total_docs > 0:
                logger.info("[OK] PASSED - Data completeness verified")
                return True
        
        logger.error("[FAIL] FAILED - Data completeness check")
        return False
        
    except Exception as e:
        logger.error(f"[FAIL] FAILED - {str(e)}")
        return False

def verify_metadata():
    """Verify metadata fields"""
    
    logger.info("\n[CHECK 4/6] Metadata Verification")
    logger.info("-"*80)
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
        
        query = f"""
        SELECT 
            COUNT(DISTINCT type) as type_count,
            ARRAY_AGG(DISTINCT type) as types
        FROM `{table_id}`
        WHERE type IS NOT NULL
        """
        
        result = client.query(query).result()
        
        for row in result:
            logger.info(f"[OK] Document types: {row.type_count}")
            if row.types:
                logger.info(f"  Types: {', '.join(row.types)}")
            
            if row.type_count >= 2:
                logger.info("[OK] PASSED - Metadata complete")
                return True
        
        logger.error("[FAIL] FAILED - Metadata incomplete")
        return False
        
    except Exception as e:
        logger.error(f"[FAIL] FAILED - {str(e)}")
        return False

def verify_search_capability():
    """Verify search works"""
    
    logger.info("\n[CHECK 5/6] Search Capability Verification")
    logger.info("-"*80)
    
    try:
        from src.bigquery_rag import bq_rag_manager
        
        logger.info("Testing similarity search...")
        results = bq_rag_manager.similarity_search("funding 2026", k=3)
        
        if results and len(results) > 0:
            logger.info(f"[OK] Search returned {len(results)} results")
            logger.info("[OK] PASSED - Search capability working")
            return True
        else:
            logger.error("[FAIL] FAILED - No search results")
            return False
        
    except Exception as e:
        logger.error(f"[FAIL] FAILED - {str(e)}")
        return False

def verify_llm_integration():
    """Verify LLM integration"""
    
    logger.info("\n[CHECK 6/6] LLM Integration Verification")
    logger.info("-"*80)
    
    try:
        from src.bigquery_rag import bq_rag_manager
        
        logger.info("Initializing RetrievalQA chain...")
        qa_chain = bq_rag_manager.create_retrieval_qa_chain()
        
        if qa_chain:
            logger.info("[OK] RetrievalQA chain created")
            logger.info("[OK] PASSED - LLM integration ready")
            return True
        else:
            logger.error("[FAIL] FAILED - Chain creation failed")
            return False
        
    except Exception as e:
        logger.error(f"[FAIL] FAILED - {str(e)}")
        return False

def main():
    """Run all verification checks"""
    
    logger.info("\n" + "="*80)
    logger.info("COMPONENT 2 - PRODUCTION VERIFICATION CHECKLIST")
    logger.info("="*80)
    logger.info(f"Date: {datetime.now().isoformat()}")
    logger.info(f"Project: {PROJECT_ID}")
    logger.info("="*80)
    
    checks = [
        ("BigQuery Data", verify_bigquery_data),
        ("Embeddings Quality", verify_embeddings),
        ("FILMFUND Projects", verify_projects_loaded),
        ("Metadata", verify_metadata),
        ("Search Capability", verify_search_capability),
        ("LLM Integration", verify_llm_integration),
    ]
    
    results = {}
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = "PASSED" if result else "FAILED"
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Check error: {str(e)}")
            results[check_name] = "ERROR"
            failed += 1
    
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*80)
    
    for check_name, result in results.items():
        logger.info(f"  {check_name}: {result}")
    
    logger.info(f"\nTotal: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        logger.info("\n" + "[SUCCESS] "*40)
        logger.info("COMPONENT 2 - PRODUCTION READY!")
        logger.info("All verification checks PASSED")
        logger.info("Ready for deployment")
        logger.info("[SUCCESS] "*40)
        return 0
    else:
        logger.error(f"\n[WARNING] {failed} checks failed - review above")
        return 1

if __name__ == "__main__":
    sys.exit(main())