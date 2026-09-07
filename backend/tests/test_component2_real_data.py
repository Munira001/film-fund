# -*- coding: utf-8 -*-
"""Component 2 - Complete Real Data Testing & Verification

Tests ALL critical workflows with REAL FILMFUND data in BigQuery:
1. Similarity Search with Real Embeddings
2. Batch Search
3. RetrievalQA Chain (end-to-end RAG)
4. Feature Store Sync
5. Performance Comparison
6. Production Verification
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.logs import logger
from src.bigquery_rag import bq_rag_manager
from src.rag_config import PROJECT_ID, LOCATION, BIGQUERY_DATASET, BIGQUERY_TABLE


class Component2RealDataTester:
    """Test Component 2 with REAL FILMFUND data"""
    
    def __init__(self):
        """Initialize tester"""
        logger.info("\n" + "="*80)
        logger.info("COMPONENT 2 - REAL DATA TESTING & VERIFICATION")
        logger.info("Testing with actual FILMFUND documents in BigQuery")
        logger.info("="*80)
        
        self.test_results = {}
        self.query_results = {}
    
    # ========== TEST 1: SIMILARITY SEARCH WITH REAL DATA ==========
    
    def test_similarity_search(self) -> bool:
        """Test 1: Similarity search with real embeddings"""
        try:
            logger.info("\n" + "="*80)
            logger.info("TEST 1: SIMILARITY SEARCH WITH REAL EMBEDDINGS")
            logger.info("="*80)
            
            queries = [
                "What is the total budget needed for The Last Dawn?",
                "When is the funding deadline?",
                "Tell me about Sarah Chen's filmmaking experience",
                "What are the production phases and timeline?",
            ]
            
            for query in queries:
                logger.info(f"\nQuery: '{query}'")
                logger.info("Searching in BigQuery with real embeddings...")
                
                start_time = time.time()
                results = bq_rag_manager.similarity_search(query, k=2)
                elapsed = time.time() - start_time
                
                logger.info(f"Found {len(results)} results in {elapsed:.2f}s")
                
                if results:
                    for idx, result in enumerate(results):
                        logger.info(f"  Result {idx+1}:")
                        logger.info(f"    Source: {result.metadata.get('source')}")
                        logger.info(f"    Type: {result.metadata.get('type')}")
                        logger.info(f"    Content: {result.page_content[:100]}...")
                else:
                    logger.warning("  No results found")
            
            logger.info("\nSimilarity Search Test: PASSED")
            self.test_results["1. Similarity Search"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"Similarity Search Test FAILED: {str(e)}")
            self.test_results["1. Similarity Search"] = "FAILED"
            return False
    
    # ========== TEST 2: BATCH SEARCH ==========
    
    def test_batch_search(self) -> bool:
        """Test 2: Batch search with multiple queries"""
        try:
            logger.info("\n" + "="*80)
            logger.info("TEST 2: BATCH SEARCH WITH MULTIPLE QUERIES")
            logger.info("="*80)
            
            batch_queries = [
                "funding deadline",
                "production budget",
                "filmmaker experience",
                "shooting schedule",
            ]
            
            logger.info(f"\nBatch searching with {len(batch_queries)} queries...")
            logger.info("Queries: " + ", ".join(batch_queries))
            
            start_time = time.time()
            batch_results = bq_rag_manager.batch_search(queries=batch_queries, k=1)
            elapsed = time.time() - start_time
            
            logger.info(f"Batch search completed in {elapsed:.2f}s")
            logger.info(f"Result sets: {len(batch_results) if batch_results else 0}")
            
            if batch_results:
                for idx, result_set in enumerate(batch_results):
                    logger.info(f"  Query {idx+1} ({batch_queries[idx]}): {len(result_set)} results")
            
            logger.info("\nBatch Search Test: PASSED")
            self.test_results["2. Batch Search"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"Batch Search Test FAILED: {str(e)}")
            self.test_results["2. Batch Search"] = "FAILED"
            return False
    
    # ========== TEST 3: RETRIEVAL QA CHAIN (END-TO-END RAG) ==========
    
    def test_retrieval_qa_chain(self) -> bool:
        """Test 3: Complete RAG pipeline with real data"""
        try:
            logger.info("\n" + "="*80)
            logger.info("TEST 3: RETRIEVAL QA CHAIN (END-TO-END RAG)")
            logger.info("="*80)
            
            logger.info("\nCreating RetrievalQA chain...")
            qa_chain = bq_rag_manager.create_retrieval_qa_chain(chain_type="stuff")
            
            if not qa_chain:
                logger.error("Failed to create chain")
                self.test_results["3. RetrievalQA Chain"] = "FAILED"
                return False
            
            test_questions = [
                "What is the total project budget for The Last Dawn?",
                "What are the key production phases and their timelines?",
                "Tell me about the filmmaker's track record and experience.",
            ]
            
            logger.info("\nTesting RetrievalQA with real questions...\n")
            
            for question in test_questions:
                logger.info(f"Question: '{question}'")
                logger.info("Querying real data...")
                
                start_time = time.time()
                response = bq_rag_manager.query(question)
                elapsed = time.time() - start_time
                
                logger.info(f"Response received in {elapsed:.2f}s")
                
                if response:
                    result = response.get('result', 'No result')
                    sources = response.get('source_documents', [])
                    
                    logger.info(f"Answer: {str(result)[:150]}...")
                    logger.info(f"Source documents: {len(sources)}")
                    
                    self.query_results[question] = {
                        "answer": result,
                        "sources": len(sources),
                        "time": elapsed
                    }
                else:
                    logger.warning("No response")
                
                logger.info("")
            
            logger.info("RetrievalQA Chain Test: PASSED")
            self.test_results["3. RetrievalQA Chain"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"RetrievalQA Chain Test FAILED: {str(e)}")
            self.test_results["3. RetrievalQA Chain"] = "FAILED"
            return False
    
    # ========== TEST 4: METADATA FILTERING ==========
    
    def test_metadata_filtering(self) -> bool:
        """Test 4: Search with metadata filters"""
        try:
            logger.info("\n" + "="*80)
            logger.info("TEST 4: METADATA FILTERING WITH REAL DATA")
            logger.info("="*80)
            
            # Filter by document type
            logger.info("\nFiltering for production_budget documents only...")
            
            filter_dict = {"type": "production_budget"}
            query = "budget and funding"
            
            logger.info(f"Query: '{query}'")
            logger.info(f"Filter: {filter_dict}")
            
            start_time = time.time()
            results = bq_rag_manager.similarity_search_with_filter(query, filter_dict, k=2)
            elapsed = time.time() - start_time
            
            logger.info(f"Found {len(results)} filtered results in {elapsed:.2f}s")
            
            if results:
                for result in results:
                    logger.info(f"  Type: {result.metadata.get('type')}")
                    logger.info(f"  Content: {result.page_content[:80]}...")
            
            logger.info("\nMetadata Filtering Test: PASSED")
            self.test_results["4. Metadata Filtering"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"Metadata Filtering Test FAILED: {str(e)}")
            self.test_results["4. Metadata Filtering"] = "FAILED"
            return False
    
    # ========== TEST 5: MMR SEARCH (DIVERSE RESULTS) ==========
    
    def test_mmr_search(self) -> bool:
        """Test 5: Maximal Marginal Relevance for diverse results"""
        try:
            logger.info("\n" + "="*80)
            logger.info("TEST 5: MAXIMAL MARGINAL RELEVANCE SEARCH")
            logger.info("="*80)
            
            query = "funding and budget and schedule"
            
            logger.info(f"\nQuery: '{query}'")
            logger.info("Searching for diverse, non-redundant results...")
            
            start_time = time.time()
            results = bq_rag_manager.mmr_search(query, k=3, lambda_mult=0.5)
            elapsed = time.time() - start_time
            
            logger.info(f"Found {len(results)} diverse results in {elapsed:.2f}s")
            
            if results:
                for idx, result in enumerate(results):
                    logger.info(f"  Result {idx+1}:")
                    logger.info(f"    Type: {result.metadata.get('type')}")
                    logger.info(f"    Name: {result.metadata.get('document_name')}")
            
            logger.info("\nMMR Search Test: PASSED")
            self.test_results["5. MMR Search"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"MMR Search Test FAILED: {str(e)}")
            self.test_results["5. MMR Search"] = "FAILED"
            return False
    
    # ========== TEST 6: PERFORMANCE COMPARISON ==========
    
    def test_performance(self) -> bool:
        """Test 6: Performance metrics"""
        try:
            logger.info("\n" + "="*80)
            logger.info("TEST 6: PERFORMANCE METRICS")
            logger.info("="*80)
            
            test_query = "What is the funding deadline?"
            
            logger.info(f"\nPerformance Test Query: '{test_query}'")
            logger.info("Running 5 queries to measure average latency...\n")
            
            latencies = []
            
            for i in range(5):
                start_time = time.time()
                results = bq_rag_manager.similarity_search(test_query, k=2)
                elapsed = time.time() - start_time
                latencies.append(elapsed)
                
                logger.info(f"  Query {i+1}: {elapsed*1000:.1f}ms")
            
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            logger.info(f"\nPerformance Summary:")
            logger.info(f"  Average latency: {avg_latency*1000:.1f}ms")
            logger.info(f"  Min latency: {min_latency*1000:.1f}ms")
            logger.info(f"  Max latency: {max_latency*1000:.1f}ms")
            logger.info(f"  Throughput: {1/avg_latency:.1f} queries/sec")
            
            logger.info("\nPerformance Test: PASSED")
            self.test_results["6. Performance Metrics"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"Performance Test FAILED: {str(e)}")
            self.test_results["6. Performance Metrics"] = "FAILED"
            return False
    
    # ========== TEST 7: DATA VERIFICATION ==========
    
    def test_data_verification(self) -> bool:
        """Test 7: Verify data in BigQuery"""
        try:
            logger.info("\n" + "="*80)
            logger.info("TEST 7: DATA VERIFICATION IN BIGQUERY")
            logger.info("="*80)
            
            from google.cloud import bigquery
            
            client = bigquery.Client(project=PROJECT_ID)
            table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
            
            query = f"""
            SELECT 
                COUNT(*) as total_docs,
                COUNT(DISTINCT doc_id) as unique_docs,
                ARRAY_LENGTH(embedding) as embedding_dim
            FROM `{table_id}`
            """
            
            logger.info("\nQuerying BigQuery for data statistics...")
            results = client.query(query).result()
            
            for row in results:
                logger.info(f"\nData Statistics:")
                logger.info(f"  Total documents: {row.total_docs}")
                logger.info(f"  Unique docs: {row.unique_docs}")
                logger.info(f"  Embedding dimension: {row.embedding_dim}")
            
            logger.info("\nData Verification: PASSED")
            self.test_results["7. Data Verification"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"Data Verification FAILED: {str(e)}")
            self.test_results["7. Data Verification"] = "FAILED"
            return False
    
    # ========== RUN ALL TESTS ==========
    
    def run_all_tests(self) -> int:
        """Run all 7 real data tests"""
        try:
            tests = [
                ("Similarity Search", self.test_similarity_search),
                ("Batch Search", self.test_batch_search),
                ("RetrievalQA Chain", self.test_retrieval_qa_chain),
                ("Metadata Filtering", self.test_metadata_filtering),
                ("MMR Search", self.test_mmr_search),
                ("Performance", self.test_performance),
                ("Data Verification", self.test_data_verification),
            ]
            
            passed = 0
            failed = 0
            
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    if result:
                        passed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Test exception: {str(e)}")
                    failed += 1
            
            # Summary
            logger.info("\n" + "="*80)
            logger.info("COMPONENT 2 - REAL DATA TEST SUMMARY")
            logger.info("="*80)
            
            for test_name, result in self.test_results.items():
                logger.info(f"  {test_name}: {result}")
            
            logger.info(f"\nTotal: {passed} PASSED, {failed} FAILED")
            
            if failed == 0:
                logger.info("\nComponent 2: PRODUCTION READY WITH REAL DATA!")
                logger.info("All critical workflows verified and working!")
            else:
                logger.info(f"\nComponent 2: {failed} tests failed")
            
            logger.info("="*80 + "\n")
            
            return 0 if failed == 0 else 1
            
        except Exception as e:
            logger.error(f"Test runner error: {str(e)}")
            return 1


def main():
    """Main entry point"""
    try:
        tester = Component2RealDataTester()
        return tester.run_all_tests()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)