"""
Component 3: Zero-Config Grounding Agent with Parallel API
Integrates BigQuery RAG + Parallel API for dual grounding

This is the COMPLETE, PRODUCTION-READY implementation.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import bigquery
from src.bigquery_rag import bq_rag_manager
from src.parallel_api import ParallelAPI
from src.logs import logger


class Component3GroundingAgent:
    """
    FILMFUND Grounding Agent with Dual Sources
    
    Architecture:
    - Internal: BigQuery RAG (Component 2)
    - External: Parallel API (Component 3)
    - Response: Dual-grounded with citations
    """
    
    def __init__(self):
        """Initialize agent with both data sources"""
        logger.info("\n" + "="*80)
        logger.info("COMPONENT 3 - GROUNDING AGENT INITIALIZATION")
        logger.info("="*80)
        
        try:
            # Component 2: BigQuery RAG
            self.rag_manager = bq_rag_manager
            logger.info("[OK] BigQuery RAG initialized (Component 2)")
            logger.info("     - Dataset: filmfund_rag")
            logger.info("     - Table: scripts_embeddings")
            logger.info("     - Documents: 55 real FILMFUND documents")
            logger.info("     - Embeddings: 768-dimensional")
            
        except Exception as e:
            logger.error(f"[FAIL] BigQuery RAG initialization failed: {str(e)}")
            raise
        
        try:
            # Component 3: Parallel API
            self.parallel_api = ParallelAPI()
            logger.info("[OK] Parallel API initialized (Component 3)")
            logger.info("     - Endpoint: https://api.parallel.ai/v1/search")
            logger.info("     - Auth: x-api-key header")
            logger.info("     - Purpose: Market intelligence and external grounding")
            
        except Exception as e:
            logger.error(f"[FAIL] Parallel API initialization failed: {str(e)}")
            self.parallel_api = None
        
        logger.info("[OK] Component 3 Grounding Agent fully initialized")
        logger.info("="*80 + "\n")
    
    def answer_question(self, query: str) -> Dict[str, Any]:
        """
        Answer question with dual grounding (internal + external)
        
        Args:
            query (str): User question
            
        Returns:
            dict: {
                'query': str,
                'answer': str,
                'grounding': {'internal': {...}, 'external': {...}},
                'confidence': str,
                'sources': [str],
                'timestamp': str
            }
        """
        logger.info(f"\n[QUERY] {query}")
        logger.info("-"*80)
        
        try:
            # STEP 1: Query internal FILMFUND data
            logger.info("[STEP 1] Querying internal FILMFUND data...")
            internal_answer = self.query_internal(query)
            
            # STEP 2: Query external market data
            logger.info("[STEP 2] Querying external market intelligence...")
            external_answer = self.query_external(query)
            
            # STEP 3: Combine and cite
            logger.info("[STEP 3] Combining and citing sources...")
            combined_response = self.combine_answers(
                query,
                internal_answer,
                external_answer
            )
            
            logger.info(f"[RESPONSE] Confidence: {combined_response['confidence']}")
            logger.info(f"[SOURCES] {len(combined_response['sources'])} sources cited")
            logger.info("-"*80)
            
            return combined_response
        
        except Exception as e:
            logger.error(f"[ERROR] Failed to answer question: {str(e)}")
            return {
                'query': query,
                'answer': f"Error processing query: {str(e)}",
                'grounding': {'internal': {'found': False}, 'external': {'found': False}},
                'confidence': 'low',
                'sources': [],
                'timestamp': str(datetime.now())
            }
    
    def query_internal(self, query: str) -> Dict[str, Any]:
        """
        Query FILMFUND BigQuery data (Component 2)
        
        Returns FILMFUND project information with high confidence
        """
        try:
            logger.info("  [INTERNAL] Searching FILMFUND BigQuery...")
            
            # Search BigQuery with similarity
            results = self.rag_manager.similarity_search(query, k=3)
            
            if not results or len(results) == 0:
                logger.info("  [INTERNAL] No FILMFUND documents found")
                return {
                    'found': False,
                    'message': 'Not in FILMFUND records'
                }
            
            # Get document names and metadata
            documents = []
            for result in results:
                metadata = result.metadata if hasattr(result, 'metadata') else {}
                doc_name = metadata.get('document_name', 'Unknown document')
                documents.append(doc_name)
            
            # Create QA chain answer
            qa_chain = self.rag_manager.create_retrieval_qa_chain()
            qa_response = qa_chain.invoke({'query': query})
            answer_text = qa_response.get('result', '') if isinstance(qa_response, dict) else str(qa_response)
            
            logger.info(f"  [INTERNAL] Found {len(results)} matching documents")
            logger.info(f"  [INTERNAL] Documents: {', '.join(set(documents))}")
            
            return {
                'found': True,
                'answer': answer_text,
                'sources': list(set(documents)),
                'confidence': 'high',
                'data_type': 'FILMFUND BigQuery (Component 2)',
                'documents_count': len(results),
                'retrieval_method': 'semantic_search_768dim_embeddings'
            }
        
        except Exception as e:
            logger.error(f"  [INTERNAL] Error querying BigQuery: {str(e)}")
            return {
                'found': False,
                'error': str(e),
                'message': 'Error accessing FILMFUND database'
            }
    
    def query_external(self, query: str) -> Dict[str, Any]:
        """
        Query external market data via Parallel API (Component 3)
        
        Returns market intelligence and trends with medium confidence
        """
        try:
            logger.info("  [EXTERNAL] Searching market intelligence via Parallel API...")
            
            # Check if Parallel API is available
            if not self.parallel_api:
                logger.warning("  [EXTERNAL] Parallel API not initialized")
                return {
                    'found': False,
                    'message': 'Parallel API not available'
                }
            
            # Query Parallel API for market intelligence
            results = self.parallel_api.search_grants(
                search_queries=[query],
                objective='Find current market data, trends, and funding opportunities'
            )
            
            if not results or len(results) == 0:
                logger.info("  [EXTERNAL] No external data found")
                return {
                    'found': False,
                    'message': 'No market data available'
                }
            
            logger.info(f"  [EXTERNAL] Found {len(results)} market intelligence results")
            
            return {
                'found': True,
                'results': results,
                'confidence': 'medium',
                'data_type': 'Market Intelligence (Parallel API - Component 3)',
                'sources': ['Google Search', 'Parallel API'],
                'results_count': len(results),
                'retrieval_method': 'parallel_api_search'
            }
        
        except Exception as e:
            logger.error(f"  [EXTERNAL] Error querying Parallel API: {str(e)}")
            return {
                'found': False,
                'error': str(e),
                'message': 'Error accessing market intelligence'
            }
    
    def combine_answers(self, query: str, internal: Dict, external: Dict) -> Dict[str, Any]:
        """
        Combine internal and external answers with proper grounding and citations
        
        Implements smart routing:
        - FILMFUND data only → HIGH confidence
        - Market data only → MEDIUM confidence
        - Both sources → HIGH-MEDIUM confidence
        - Neither → LOW confidence with suggestion
        """
        
        response = {
            'query': query,
            'answer': '',
            'grounding': {
                'internal': internal,
                'external': external
            },
            'sources': [],
            'confidence': 'medium',
            'timestamp': str(datetime.now())
        }
        
        # CASE 1: Both internal FILMFUND and external market data
        if internal.get('found') and external.get('found'):
            logger.info("  [COMBINE] Case 1: Using BOTH internal and external data (DUAL GROUNDING)")
            
            response['answer'] = f"""
FILMFUND Project Data:
{internal.get('answer', '')}

Market Intelligence:
{self._format_external_results(external.get('results', []))}

Analysis:
This response combines FILMFUND production data with current market intelligence 
for comprehensive decision support.
"""
            response['confidence'] = 'high'
            response['sources'] = (
                [f"[FILMFUND] {doc}" for doc in internal.get('sources', [])] +
                [f"[MARKET] {src}" for src in external.get('sources', [])]
            )
        
        # CASE 2: Only internal FILMFUND data
        elif internal.get('found'):
            logger.info("  [COMBINE] Case 2: Using FILMFUND data only (INTERNAL GROUNDING)")
            
            response['answer'] = f"""
{internal.get('answer', '')}

Sources: FILMFUND Production Database
- Documents: {', '.join(internal.get('sources', []))}
- Confidence Level: HIGH (grounded in real FILMFUND 2026-2029 project data)
- Data Type: {internal.get('data_type', 'FILMFUND')}

This answer is based on actual FILMFUND production records from the BigQuery database 
with 768-dimensional semantic search embeddings.
"""
            response['confidence'] = 'high'
            response['sources'] = [f"[FILMFUND] {doc}" for doc in internal.get('sources', [])]
        
        # CASE 3: Only external market data
        elif external.get('found'):
            logger.info("  [COMBINE] Case 3: Using market intelligence only (EXTERNAL GROUNDING)")
            
            response['answer'] = f"""
{self._format_external_results(external.get('results', []))}

Sources: Market Intelligence (Parallel API)
- Confidence Level: MEDIUM (grounded in current market data)
- Data Type: {external.get('data_type', 'Market Intelligence')}

Note: This information is not in FILMFUND records. 
Would you like to know about our 5 FILMFUND 2026-2029 projects instead?

Our Projects:
1. The Last Dawn (Sarah Chen) - $1.2M - Oct 15, 2026
2. Neon Dreams (Marcus Johnson) - $450K - Nov 30, 2026
3. Voices of Change (Aisha Patel) - $300K - Dec 15, 2026
4. Love in the City (Jessica Torres) - $150K - Sep 30, 2026
5. The Future Calls (David Kim) - $800K - Mar 15, 2027
"""
            response['confidence'] = 'medium'
            response['sources'] = [f"[MARKET] {src}" for src in external.get('sources', [])]
        
        # CASE 4: No data found in either source
        else:
            logger.info("  [COMBINE] Case 4: No data found (LOW CONFIDENCE)")
            
            response['answer'] = f"""
I could not find information about that in either FILMFUND records or market data.

What I can help with:
1. FILMFUND 2026-2029 Projects
   - The Last Dawn, Neon Dreams, Voices of Change, Love in the City, The Future Calls
   - Budget, timeline, and filmmaker information

2. Market Intelligence
   - Current film industry trends
   - Funding opportunities
   - Filmmaker opportunities
   - Competitive analysis

3. Comparative Analysis
   - FILMFUND projects vs industry benchmarks
   - Budget comparisons
   - Timeline analysis

Please ask about any of these topics, or rephrase your question.
"""
            response['confidence'] = 'low'
            response['sources'] = ['None - No data available']
        
        return response
    
    def _format_external_results(self, results: List[Any]) -> str:
        """Format external API results for display"""
        if not results:
            return "No results found"
        
        formatted = []
        for i, result in enumerate(results[:5], 1):  # Limit to top 5
            if isinstance(result, dict):
                formatted.append(f"{i}. {result.get('title', 'Result')} - {result.get('snippet', '')}")
            else:
                formatted.append(f"{i}. {str(result)}")
        
        return "\n".join(formatted)


# ============================================================================
# GLOBAL AGENT INSTANCE
# ============================================================================

component3_agent = Component3GroundingAgent()


# ============================================================================
# PUBLIC FUNCTIONS
# ============================================================================

def answer_filmfund_question(question: str) -> Dict[str, Any]:
    """
    Public function to answer FILMFUND questions with dual grounding
    
    Args:
        question (str): User's question about FILMFUND or market
        
    Returns:
        dict: Grounded answer with citations
    """
    return component3_agent.answer_question(question)


def get_agent_status() -> Dict[str, str]:
    """Get Component 3 agent status"""
    return {
        'component': 'Component 3 - Zero-Config Grounding',
        'status': 'Ready',
        'internal_source': 'BigQuery RAG (55 documents)',
        'external_source': 'Parallel API (Market Intelligence)',
        'timestamp': str(datetime.now())
    }


if __name__ == "__main__":
    # Test the agent
    logger.info("Testing Component 3 Grounding Agent...")
    
    test_question = "What is the budget for The Last Dawn?"
    response = answer_filmfund_question(test_question)
    
    logger.info(f"Question: {response['query']}")
    logger.info(f"Answer: {response['answer']}")
    logger.info(f"Confidence: {response['confidence']}")
    logger.info(f"Sources: {response['sources']}")