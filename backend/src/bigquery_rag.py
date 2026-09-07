"""BigQuery RAG Implementation - COMPONENT 2 (Phase 1)

Following official patterns from:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/retrieval-augmented-generation/rag_qna_with_bq_and_featurestore.ipynb

Capabilities:
1. Load and ingest PDF documents
2. Split documents into chunks
3. Create embeddings
4. Store in BigQueryVectorStore
5. Perform similarity search
6. Run RetrievalQA chain
7. Batch search
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_community import BigQueryVectorStore
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from langchain_core.documents import Document
from langchain_classic.chains import RetrievalQA

from .logs import logger
from .rag_config import (
    PROJECT_ID,
    LOCATION,
    BIGQUERY_DATASET,
    BIGQUERY_TABLE,
    EMBEDDING_MODEL,
    LLM_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
)


class BigQueryRAGManager:
    """Manage RAG with BigQueryVectorStore for prototyping"""
    
    def __init__(self):
        """Initialize BigQuery RAG Manager"""
        try:
            logger.info("Initializing BigQueryRAGManager")
            
            # Initialize embedding model (OFFICIAL PATTERN)
            logger.info(f"Initializing VertexAIEmbeddings: {EMBEDDING_MODEL}")
            self.embedding_model = VertexAIEmbeddings(
                model_name=EMBEDDING_MODEL,
                project=PROJECT_ID,
                location=LOCATION
            )
            
            # Initialize LLM (OFFICIAL PATTERN)
            logger.info(f"Initializing VertexAI LLM: {LLM_MODEL}")
            self.llm = VertexAI(
                model_name=LLM_MODEL,
                project=PROJECT_ID,
                location=LOCATION
            )
            
            # Initialize BigQueryVectorStore (OFFICIAL PATTERN)
            logger.info(f"Initializing BigQueryVectorStore")
            logger.info(f"  Dataset: {BIGQUERY_DATASET}")
            logger.info(f"  Table: {BIGQUERY_TABLE}")
            logger.info(f"  Location: {LOCATION}")
            
            self.bq_store = BigQueryVectorStore(
                project_id=PROJECT_ID,
                location=LOCATION,
                dataset_name=BIGQUERY_DATASET,
                table_name=BIGQUERY_TABLE,
                embedding=self.embedding_model,
            )
            
            # Initialize text splitter (OFFICIAL PATTERN)
            logger.info("Initializing RecursiveCharacterTextSplitter")
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=CHUNK_SEPARATORS,
            )
            
            logger.info("BigQueryRAGManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize BigQueryRAGManager: {str(e)}")
            raise
    
    # ========== CAPABILITY 1: PDF INGESTION ==========
    
    def load_pdf_documents(self, pdf_path: str) -> List[Document]:
        """Load PDF documents (OFFICIAL PATTERN)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of loaded documents
        """
        try:
            logger.info(f"Loading PDF: {pdf_path}")
            
            # Verify file exists
            if not Path(pdf_path).exists():
                logger.error(f"PDF not found: {pdf_path}")
                return []
            
            # Load PDF (OFFICIAL PATTERN)
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            logger.info(f"Loaded {len(documents)} documents from PDF")
            
            return documents
            
        except Exception as e:
            logger.error(f"PDF loading error: {str(e)}")
            return []
    
    # ========== CAPABILITY 2: METADATA ENRICHMENT ==========
    
    def add_document_metadata(self, documents: List[Document], 
                             doc_name: Optional[str] = None) -> List[Document]:
        """Add source and document name to metadata (OFFICIAL PATTERN)
        
        Args:
            documents: List of documents
            doc_name: Document name (optional)
            
        Returns:
            Documents with enriched metadata
        """
        try:
            logger.info(f"Adding metadata to {len(documents)} documents")
            
            for idx, document in enumerate(documents):
                doc_md = document.metadata
                
                # Extract document name from source
                source_path = doc_md.get("source", "unknown")
                document_name = doc_name or Path(source_path).name
                
                # Update metadata (OFFICIAL PATTERN)
                document.metadata = {
                    "source": source_path,
                    "document_name": document_name,
                    "page": doc_md.get("page", 0)
                }
            
            logger.info("Metadata enrichment complete")
            return documents
            
        except Exception as e:
            logger.error(f"Metadata enrichment error: {str(e)}")
            return document
    
    # ========== CAPABILITY 3: DOCUMENT CHUNKING ==========
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks (OFFICIAL PATTERN)
        
        Args:
            documents: List of documents
            
        Returns:
            List of chunked documents
        """
        try:
            logger.info(f"Chunking {len(documents)} documents")
            logger.info(f"  Chunk size: {CHUNK_SIZE}")
            logger.info(f"  Chunk overlap: {CHUNK_OVERLAP}")
            
            # Split documents (OFFICIAL PATTERN)
            doc_splits = self.text_splitter.split_documents(documents)
            
            # Add chunk number to metadata (OFFICIAL PATTERN)
            for idx, split in enumerate(doc_splits):
                split.metadata["chunk"] = idx
            
            logger.info(f"Created {len(doc_splits)} chunks")
            
            return doc_splits
            
        except Exception as e:
            logger.error(f"Document chunking error: {str(e)}")
            return []
    
    # ========== CAPABILITY 4: STORE DOCUMENTS ==========
    
    def add_documents_to_store(self, documents: List[Document]) -> List[str]:
        """Add documents to BigQueryVectorStore (OFFICIAL PATTERN)
        
        Args:
            documents: List of documents to add
            
        Returns:
            List of document IDs
        """
        try:
            logger.info(f"Adding {len(documents)} documents to BigQueryVectorStore")
            
            # Add documents (OFFICIAL PATTERN)
            doc_ids = self.bq_store.add_documents(documents)
            
            logger.info(f"Successfully added {len(doc_ids)} documents")
            logger.info(f"Document IDs: {doc_ids[:5]}...")  # Show first 5
            
            return doc_ids
            
        except Exception as e:
            logger.error(f"Document storage error: {str(e)}")
            return []
    
    # ========== CAPABILITY 5: SIMILARITY SEARCH ==========
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents (OFFICIAL PATTERN)
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of similar documents
        """
        try:
            logger.info(f"Similarity search: '{query}' (k={k})")
            
            # Search (OFFICIAL PATTERN)
            results = self.bq_store.similarity_search(query, k=k)
            
            logger.info(f"Found {len(results)} similar documents")
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity search error: {str(e)}")
            return []
    
    # ========== CAPABILITY 6: BATCH SEARCH ==========
    
    def batch_search(self, queries: List[str] = None, 
                    embeddings: List[list] = None, 
                    k: int = 4) -> List[List[Document]]:
        """Batch search (OFFICIAL PATTERN)
        
        Args:
            queries: List of queries OR
            embeddings: List of pre-computed embeddings
            k: Number of results per query
            
        Returns:
            List of document lists
        """
        try:
            if queries:
                logger.info(f"Batch search with {len(queries)} queries")
            elif embeddings:
                logger.info(f"Batch search with {len(embeddings)} embeddings")
            
            # Batch search (OFFICIAL PATTERN)
            results = self.bq_store.batch_search(
                embeddings=embeddings,
                queries=queries,
                k=k
            )
            
            logger.info(f"Batch search complete: {len(results)} result sets")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch search error: {str(e)}")
            return []
    
    # ========== CAPABILITY 7: RETRIEVAL QA CHAIN ==========
    
    def create_retrieval_qa_chain(self, chain_type: str = "stuff"):
        """Create RetrievalQA chain (OFFICIAL PATTERN)
        
        Args:
            chain_type: Type of chain (stuff, map_reduce, etc.)
            
        Returns:
            RetrievalQA chain object
        """
        try:
            logger.info(f"Creating RetrievalQA chain (type={chain_type})")
            
            # Create retriever (OFFICIAL PATTERN)
            retriever = self.bq_store.as_retriever()
            
            # Create chain (OFFICIAL PATTERN)
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type=chain_type,
                retriever=retriever,
                return_source_documents=True
            )
            
            logger.info("RetrievalQA chain created successfully")
            
            return qa_chain
            
        except Exception as e:
            logger.error(f"Chain creation error: {str(e)}")
            return None
    
    # ========== CAPABILITY 8: INVOKE CHAIN ==========
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query using RetrievalQA chain
        
        Args:
            question: User question
            
        Returns:
            Dict with result and source documents
        """
        try:
            logger.info(f"Querying: '{question}'")
            
            # Create chain if not exists
            if not hasattr(self, 'qa_chain') or self.qa_chain is None:
                self.qa_chain = self.create_retrieval_qa_chain()
            
            # Invoke chain (OFFICIAL PATTERN)
            response = self.qa_chain.invoke(question)
            
            logger.info("Query complete")
            
            return response
            
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            return {
                "result": f"Error: {str(e)}",
                "source_documents": []
            }
    
    # ========== CAPABILITY 9: METADATA FILTERING ==========
    
    def similarity_search_with_filter(self, query: str, 
                                     filter_dict: Optional[Dict] = None,
                                     k: int = 4) -> List[Document]:
        """Search with metadata filtering
        
        Args:
            query: Search query
            filter_dict: Metadata filter
            k: Number of results
            
        Returns:
            Filtered results
        """
        try:
            logger.info(f"Similarity search with filter: '{query}'")
            logger.info(f"Filter: {filter_dict}")
            
            # Search with filter (OFFICIAL PATTERN)
            results = self.bq_store.similarity_search(
                query, 
                k=k,
                filter=filter_dict
            )
            
            logger.info(f"Found {len(results)} filtered results")
            
            return results
            
        except Exception as e:
            logger.error(f"Filtered search error: {str(e)}")
            return []
    
    # ========== CAPABILITY 10: VECTOR SEARCH ==========
    
    def get_embedding(self, text: str) -> list:
        """Get embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            logger.info("Generating embedding")
            
            embedding = self.embedding_model.embed_query(text)
            
            logger.info(f"Embedding generated (dim={len(embedding)})")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            return []
    
    def similarity_search_by_vector(self, embedding: list, 
                                   k: int = 4) -> List[Document]:
        """Search by vector (OFFICIAL PATTERN)
        
        Args:
            embedding: Embedding vector
            k: Number of results
            
        Returns:
            Similar documents
        """
        try:
            logger.info(f"Vector similarity search (k={k})")
            
            results = self.bq_store.similarity_search_by_vector(embedding, k=k)
            
            logger.info(f"Found {len(results)} similar documents")
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []
    
    # ========== UTILITY: GET/DELETE DOCUMENTS ==========
    
    def get_documents(self, doc_ids: List[str]) -> List[Document]:
        """Retrieve documents by ID
        
        Args:
            doc_ids: List of document IDs
            
        Returns:
            List of documents
        """
        try:
            logger.info(f"Retrieving {len(doc_ids)} documents")
            
            docs = self.bq_store.get_documents(ids=doc_ids)
            
            logger.info(f"Retrieved {len(docs)} documents")
            
            return docs
            
        except Exception as e:
            logger.error(f"Document retrieval error: {str(e)}")
            return []
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """Delete documents by ID
        
        Args:
            doc_ids: List of document IDs
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Deleting {len(doc_ids)} documents")
            
            self.bq_store.delete(ids=doc_ids)
            
            logger.info("Documents deleted successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Document deletion error: {str(e)}")
            return False
    
    # ========== UTILITY: MAXIMAL MARGINAL RELEVANCE ==========
    
    def mmr_search(self, query: str, k: int = 4, 
                   lambda_mult: float = 0.5) -> List[Document]:
        """Maximal Marginal Relevance search (OFFICIAL PATTERN)
        
        Reduces redundancy in results
        
        Args:
            query: Search query
            k: Number of results
            lambda_mult: Diversity parameter (0=max diversity, 1=max relevance)
            
        Returns:
            Diverse results
        """
        try:
            logger.info(f"MMR search: '{query}' (k={k}, lambda={lambda_mult})")
            
            retriever = self.bq_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": k,
                    "lambda_mult": lambda_mult
                }
            )
            
            results = retriever.get_relevant_documents(query)
            
            logger.info(f"Found {len(results)} diverse results")
            
            return results
            
        except Exception as e:
            logger.error(f"MMR search error: {str(e)}")
            return []


# Global instance
bq_rag_manager = BigQueryRAGManager()