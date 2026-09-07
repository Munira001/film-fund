"""Document Extraction Module - COMPONENT 1 (COMPLETE)

Following exact patterns from:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/document-processing/document_processing.ipynb

Implements ALL 9 capabilities:
1. Document Classification
2. Entity Extraction
3. Chaining (Classify → Extract)
4. Question Answering
5. Summarization
6. Table Extraction
7. Page Extraction
8. Translation
9. Comparison
"""

from enum import Enum
from typing import Optional, List
from google.genai.types import GenerateContentConfig, Part

from .gemini_client import gemini_client
from .document_models import (
    FilmmakerScript,
    BudgetDocument,
    ProductionSchedule,
    FilmmakerProfile,
)
from .logs import logger


# ========== DOCUMENT CLASSIFICATION (ENUM) ==========

class DocumentType(Enum):
    """Document type classification for FILMFUND documents"""
    
    FILMMAKER_SCRIPT = "filmmaker_script"
    PRODUCTION_BUDGET = "production_budget"
    SHOOTING_SCHEDULE = "shooting_schedule"
    FILMMAKER_PROFILE = "filmmaker_profile"
    UNKNOWN = "unknown"


# ========== MIME TYPES ==========

PDF_MIME_TYPE = "application/pdf"
JSON_MIME_TYPE = "application/json"
ENUM_MIME_TYPE = "text/x.enum"


# ========== SYSTEM INSTRUCTIONS ==========

CLASSIFICATION_SYSTEM_INSTRUCTION = """You are a document classification specialist. 
Given a document, your task is to find which category the document belongs to from the 
document categories provided in the schema.

Focus on:
- Document title and headers
- Key content indicators
- Specific fields present in document
- Overall structure and purpose

Return ONLY the most appropriate category."""


EXTRACTION_SYSTEM_INSTRUCTION = """You are a document entity extraction specialist. 
Given a document, your task is to extract the text value of the entities provided in the schema.

Rules:
- The values must only include text found in the document
- Do not normalize any entity values
- Extract all available fields
- If a field is not found in document, leave as None
- Be precise and accurate with all monetary values and dates"""


QA_SYSTEM_INSTRUCTION = """You are a question answering specialist. Given a question and a context, 
your task is to provide the answer to the question based on the context provided. 

Instructions:
- Give the answer first, followed by an explanation
- Base your answer ONLY on information in the document
- If the answer is not in the document, state that clearly
- Be precise and specific"""


SUMMARIZATION_SYSTEM_INSTRUCTION = """You are a professional document summarization specialist. 
Given a document, your task is to provide a detailed summary of the content of the document.

Rules:
- If it includes images, provide descriptions of the images
- If it includes tables, extract all elements of the tables
- If it includes graphs, explain the findings in the graphs
- Do not include any numbers that are not mentioned in the document
- Focus on the most important information
- Be comprehensive but concise"""


TABLE_EXTRACTION_SYSTEM_INSTRUCTION = """You are a table extraction specialist.
Your task is to extract table information from the document and return it as HTML code.

Rules:
- Extract ALL tables found in the document
- Format as proper HTML table structure
- Include headers if present
- Preserve data accuracy
- If no tables found, indicate that clearly"""


PAGE_EXTRACTION_SYSTEM_INSTRUCTION = """You are a document page analyzer specialist.
Given a document and a question, your task is to identify which pages contain information 
related to the question.

Rules:
- Use the document as your only source of information
- Return page numbers as a list of integers
- When in doubt, include the page
- Be thorough in finding relevant pages
- Consider chart legends and colors as indicators"""


TRANSLATION_SYSTEM_INSTRUCTION = """You are a professional document translator. 
Provide accurate translations maintaining the original meaning and structure."""


COMPARISON_SYSTEM_INSTRUCTION = """You are a document comparison specialist. 
Compare and contrast the documents provided, highlighting similarities, differences, and changes between them."""


# ========== CAPABILITY 1: DOCUMENT CLASSIFICATION ==========

class DocumentClassifier:
    """Classify document type using Gemini"""
    
    def __init__(self):
        """Initialize classifier"""
        logger.info("Initializing DocumentClassifier")
        self.model = "gemini-2.5-flash"
    
    def classify_from_bytes(self, pdf_bytes: bytes) -> DocumentType:
        """Classify document from PDF bytes (local file)"""
        try:
            logger.info("Classifying document from bytes...")
            
            pdf_part = Part.from_bytes(
                data=pdf_bytes,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    "Classify the following document.",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=CLASSIFICATION_SYSTEM_INSTRUCTION,
                    response_schema=DocumentType,
                    response_mime_type=ENUM_MIME_TYPE,
                ),
            )
            
            document_type = response.parsed
            logger.info(f" Document classified as: {document_type.value}")
            
            return document_type
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return DocumentType.UNKNOWN
    
    def classify_from_uri(self, gcs_uri: str) -> DocumentType:
        """Classify document from Cloud Storage URI"""
        try:
            logger.info(f"Classifying document from URI: {gcs_uri}")
            
            pdf_part = Part.from_uri(
                file_uri=gcs_uri,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    "Classify the following document.",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=CLASSIFICATION_SYSTEM_INSTRUCTION,
                    response_schema=DocumentType,
                    response_mime_type=ENUM_MIME_TYPE,
                ),
            )
            
            document_type = response.parsed
            logger.info(f" Document classified as: {document_type.value}")
            
            return document_type
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return DocumentType.UNKNOWN


# ========== CAPABILITY 2: ENTITY EXTRACTION ==========

class DocumentExtractor:
    """Extract structured data from classified documents"""
    
    def __init__(self):
        """Initialize extractor"""
        logger.info("Initializing DocumentExtractor")
        self.model = "gemini-2.5-flash"
        
        self.type_to_schema = {
            DocumentType.FILMMAKER_SCRIPT: FilmmakerScript,
            DocumentType.PRODUCTION_BUDGET: BudgetDocument,
            DocumentType.SHOOTING_SCHEDULE: ProductionSchedule,
            DocumentType.FILMMAKER_PROFILE: FilmmakerProfile,
        }
    
    def extract_from_bytes(self, pdf_bytes: bytes, doc_type: DocumentType):
        """Extract entities from PDF bytes"""
        try:
            logger.info(f"Extracting entities from bytes ({doc_type.value})...")
            
            schema = self.type_to_schema.get(doc_type)
            if not schema:
                logger.error(f"No schema for document type: {doc_type.value}")
                return None
            
            pdf_part = Part.from_bytes(
                data=pdf_bytes,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    f"Extract entities from this {doc_type.value} document.",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=EXTRACTION_SYSTEM_INSTRUCTION,
                    response_schema=schema,
                    response_mime_type=JSON_MIME_TYPE,
                ),
            )
            
            extracted_data = response.parsed
            logger.info(f"✅ Extraction successful")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            return None
    
    def extract_from_uri(self, gcs_uri: str, doc_type: DocumentType):
        """Extract entities from Cloud Storage PDF"""
        try:
            logger.info(f"Extracting entities from URI ({doc_type.value})...")
            
            schema = self.type_to_schema.get(doc_type)
            if not schema:
                logger.error(f"No schema for document type: {doc_type.value}")
                return None
            
            pdf_part = Part.from_uri(
                file_uri=gcs_uri,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    f"Extract entities from this {doc_type.value} document.",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=EXTRACTION_SYSTEM_INSTRUCTION,
                    response_schema=schema,
                    response_mime_type=JSON_MIME_TYPE,
                ),
            )
            
            extracted_data = response.parsed
            logger.info(f" Extraction successful")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            return None


# ========== CAPABILITY 3: CHAINING ==========

class DocumentProcessor:
    """Complete document processing pipeline (Classify → Extract)"""
    
    def __init__(self):
        """Initialize processor"""
        logger.info("Initializing DocumentProcessor")
        self.classifier = DocumentClassifier()
        self.extractor = DocumentExtractor()
    
    def process_from_bytes(self, pdf_bytes: bytes) -> dict:
        """Process document: Classify → Extract"""
        try:
            logger.info("\n" + "="*70)
            logger.info("DOCUMENT PROCESSING PIPELINE")
            logger.info("="*70)
            
            logger.info("\nSTEP 1: Classifying document...")
            document_type = self.classifier.classify_from_bytes(pdf_bytes)
            
            if document_type == DocumentType.UNKNOWN:
                logger.warning(" Document type unknown")
                return {
                    "classification": "unknown",
                    "extracted_data": None,
                    "error": "Document type could not be determined"
                }
            
            logger.info(f"\nSTEP 2: Extracting entities ({document_type.value})...")
            extracted_data = self.extractor.extract_from_bytes(pdf_bytes, document_type)
            
            logger.info("\n" + "="*70)
            logger.info("PROCESSING COMPLETE")
            logger.info("="*70)
            
            return {
                "classification": document_type.value,
                "extracted_data": extracted_data,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return {
                "classification": None,
                "extracted_data": None,
                "error": str(e)
            }
    
    def process_from_uri(self, gcs_uri: str) -> dict:
        """Process document from Cloud Storage"""
        try:
            logger.info("\n" + "="*70)
            logger.info("DOCUMENT PROCESSING (Cloud Storage)")
            logger.info("="*70)
            
            logger.info("\nSTEP 1: Classifying document...")
            document_type = self.classifier.classify_from_uri(gcs_uri)
            
            if document_type == DocumentType.UNKNOWN:
                logger.warning(" Document type unknown")
                return {
                    "classification": "unknown",
                    "extracted_data": None,
                    "error": "Document type could not be determined"
                }
            
            logger.info(f"\nSTEP 2: Extracting entities ({document_type.value})...")
            extracted_data = self.extractor.extract_from_uri(gcs_uri, document_type)
            
            logger.info("\n" + "="*70)
            logger.info("PROCESSING COMPLETE")
            logger.info("="*70)
            
            return {
                "classification": document_type.value,
                "extracted_data": extracted_data,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return {
                "classification": None,
                "extracted_data": None,
                "error": str(e)
            }


# ========== CAPABILITY 4: QUESTION ANSWERING ==========

class DocumentQA:
    """Answer questions about documents"""
    
    def __init__(self):
        """Initialize Q&A"""
        logger.info("Initializing DocumentQA")
        self.model = "gemini-2.5-flash"
    
    def answer_from_bytes(self, pdf_bytes: bytes, question: str) -> str:
        """Answer question about PDF from bytes"""
        try:
            logger.info(f"Answering question: {question}")
            
            pdf_part = Part.from_bytes(
                data=pdf_bytes,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    question,
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=QA_SYSTEM_INSTRUCTION,
                ),
            )
            
            answer = response.text
            logger.info(f" Question answered")
            
            return answer
            
        except Exception as e:
            logger.error(f"Q&A error: {str(e)}")
            return None
    
    def answer_from_uri(self, gcs_uri: str, question: str) -> str:
        """Answer question about PDF from Cloud Storage"""
        try:
            logger.info(f"Answering question: {question}")
            
            pdf_part = Part.from_uri(
                file_uri=gcs_uri,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    question,
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=QA_SYSTEM_INSTRUCTION,
                ),
            )
            
            answer = response.text
            logger.info(f"✅ Question answered")
            
            return answer
            
        except Exception as e:
            logger.error(f"Q&A error: {str(e)}")
            return None


# ========== CAPABILITY 5: SUMMARIZATION ==========

class DocumentSummarizer:
    """Summarize document content"""
    
    def __init__(self):
        """Initialize summarizer"""
        logger.info("Initializing DocumentSummarizer")
        self.model = "gemini-2.5-flash"
    
    def summarize_from_bytes(self, pdf_bytes: bytes) -> str:
        """Summarize PDF from bytes"""
        try:
            logger.info("Summarizing document from bytes...")
            
            pdf_part = Part.from_bytes(
                data=pdf_bytes,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    "Summarize the following document.",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=SUMMARIZATION_SYSTEM_INSTRUCTION,
                ),
            )
            
            summary = response.text
            logger.info(f" Summarization successful")
            
            return summary
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return None
    
    def summarize_from_uri(self, gcs_uri: str) -> str:
        """Summarize PDF from Cloud Storage"""
        try:
            logger.info("Summarizing document from URI...")
            
            pdf_part = Part.from_uri(
                file_uri=gcs_uri,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    "Summarize the following document.",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=SUMMARIZATION_SYSTEM_INSTRUCTION,
                ),
            )
            
            summary = response.text
            logger.info(f" Summarization successful")
            
            return summary
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return None


# ========== CAPABILITY 6: TABLE EXTRACTION ==========

class TableExtractor:
    """Extract tables from documents"""
    
    def __init__(self):
        """Initialize table extractor"""
        logger.info("Initializing TableExtractor")
        self.model = "gemini-2.5-flash"
    
    def extract_from_bytes(self, pdf_bytes: bytes) -> str:
        """Extract tables from PDF bytes as HTML"""
        try:
            logger.info("Extracting tables from bytes...")
            
            pdf_part = Part.from_bytes(
                data=pdf_bytes,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    "What is the HTML code of all tables in this document?",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=TABLE_EXTRACTION_SYSTEM_INSTRUCTION,
                ),
            )
            
            table_html = response.text
            logger.info(f" Table extraction successful")
            
            return table_html
            
        except Exception as e:
            logger.error(f"Table extraction error: {str(e)}")
            return None
    
    def extract_from_uri(self, gcs_uri: str) -> str:
        """Extract tables from PDF in Cloud Storage as HTML"""
        try:
            logger.info("Extracting tables from URI...")
            
            pdf_part = Part.from_uri(
                file_uri=gcs_uri,
                mime_type=PDF_MIME_TYPE
            )
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    "What is the HTML code of all tables in this document?",
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=TABLE_EXTRACTION_SYSTEM_INSTRUCTION,
                ),
            )
            
            table_html = response.text
            logger.info(f" Table extraction successful")
            
            return table_html
            
        except Exception as e:
            logger.error(f"Table extraction error: {str(e)}")
            return None


# ========== CAPABILITY 7: PAGE EXTRACTION ==========

class PageExtractor:
    """Extract relevant pages from documents"""
    
    def __init__(self):
        """Initialize page extractor"""
        logger.info("Initializing PageExtractor")
        self.model = "gemini-2.5-flash"
    
    def find_pages_from_bytes(self, pdf_bytes: bytes, question: str) -> List[int]:
        """Find pages relevant to a question from PDF bytes"""
        try:
            logger.info(f"Finding relevant pages: {question}")
            
            pdf_part = Part.from_bytes(
                data=pdf_bytes,
                mime_type=PDF_MIME_TYPE
            )
            
            prompt = f"""Return the numbers of all pages that contain information related to: {question}
Return as a list of integers, e.g. [1, 2, 3]"""
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    pdf_part,
                    prompt
                ],
                config=GenerateContentConfig(
                    response_mime_type=JSON_MIME_TYPE,
                    response_schema=list[int],
                ),
            )
            
            pages = response.parsed
            logger.info(f" Found relevant pages: {pages}")
            
            return pages
            
        except Exception as e:
            logger.error(f"Page extraction error: {str(e)}")
            return []
    
    def find_pages_from_uri(self, gcs_uri: str, question: str) -> List[int]:
        """Find pages relevant to a question from PDF in Cloud Storage"""
        try:
            logger.info(f"Finding relevant pages: {question}")
            
            pdf_part = Part.from_uri(
                file_uri=gcs_uri,
                mime_type=PDF_MIME_TYPE
            )
            
            prompt = f"""Return the numbers of all pages that contain information related to: {question}
Return as a list of integers, e.g. [1, 2, 3]"""
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    pdf_part,
                    prompt
                ],
                config=GenerateContentConfig(
                    response_mime_type=JSON_MIME_TYPE,
                    response_schema=list[int],
                ),
            )
            
            pages = response.parsed
            logger.info(f" Found relevant pages: {pages}")
            
            return pages
            
        except Exception as e:
            logger.error(f"Page extraction error: {str(e)}")
            return []


# ========== CAPABILITY 8: TRANSLATION ==========

class DocumentTranslator:
    """Translate document content"""
    
    def __init__(self):
        """Initialize translator"""
        logger.info("Initializing DocumentTranslator")
        self.model = "gemini-2.5-flash"
    
    def translate_from_bytes(self, pdf_bytes: bytes, target_languages: list) -> str:
        """Translate document from PDF bytes"""
        try:
            languages_str = " and ".join(target_languages)
            logger.info(f"Translating into: {languages_str}")
            
            pdf_part = Part.from_bytes(
                data=pdf_bytes,
                mime_type=PDF_MIME_TYPE
            )
            
            prompt = f"Translate the content into {languages_str}. Label each section with the target language."
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    prompt,
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=TRANSLATION_SYSTEM_INSTRUCTION,
                ),
            )
            
            translation = response.text
            logger.info(f" Translation successful")
            
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None
    
    def translate_from_uri(self, gcs_uri: str, target_languages: list) -> str:
        """Translate document from Cloud Storage PDF"""
        try:
            languages_str = " and ".join(target_languages)
            logger.info(f"Translating into: {languages_str}")
            
            pdf_part = Part.from_uri(
                file_uri=gcs_uri,
                mime_type=PDF_MIME_TYPE
            )
            
            prompt = f"Translate the content into {languages_str}. Label each section with the target language."
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=[
                    prompt,
                    pdf_part
                ],
                config=GenerateContentConfig(
                    system_instruction=TRANSLATION_SYSTEM_INSTRUCTION,
                ),
            )
            
            translation = response.text
            logger.info(f"✅ Translation successful")
            
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None


# ========== CAPABILITY 9: COMPARISON ==========

class DocumentComparator:
    """Compare multiple documents"""
    
    def __init__(self):
        """Initialize comparator"""
        logger.info("Initializing DocumentComparator")
        self.model = "gemini-2.5-flash"
    
    def compare_from_bytes(self, pdf_bytes_list: list, question: str) -> str:
        """Compare multiple documents from bytes"""
        try:
            logger.info(f"Comparing {len(pdf_bytes_list)} documents...")
            
            if len(pdf_bytes_list) < 2:
                logger.error("Need at least 2 documents")
                return None
            
            pdf_parts = []
            for pdf_bytes in pdf_bytes_list:
                pdf_part = Part.from_bytes(
                    data=pdf_bytes,
                    mime_type=PDF_MIME_TYPE
                )
                pdf_parts.append(pdf_part)
            
            contents = [question] + pdf_parts
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=GenerateContentConfig(
                    system_instruction=COMPARISON_SYSTEM_INSTRUCTION,
                ),
            )
            
            comparison = response.text
            logger.info(f" Comparison successful")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Comparison error: {str(e)}")
            return None
    
    def compare_from_uri(self, gcs_uri_list: list, question: str) -> str:
        """Compare multiple documents from Cloud Storage"""
        try:
            logger.info(f"Comparing {len(gcs_uri_list)} documents...")
            
            if len(gcs_uri_list) < 2:
                logger.error("Need at least 2 documents")
                return None
            
            pdf_parts = []
            for gcs_uri in gcs_uri_list:
                pdf_part = Part.from_uri(
                    file_uri=gcs_uri,
                    mime_type=PDF_MIME_TYPE
                )
                pdf_parts.append(pdf_part)
            
            contents = [question] + pdf_parts
            
            response = gemini_client.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=GenerateContentConfig(
                    system_instruction=COMPARISON_SYSTEM_INSTRUCTION,
                ),
            )
            
            comparison = response.text
            logger.info(f" Comparison successful")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Comparison error: {str(e)}")
            return None


# ========== GLOBAL INSTANCES ==========

document_processor = DocumentProcessor()
classifier = DocumentClassifier()
extractor = DocumentExtractor()
qa = DocumentQA()
summarizer = DocumentSummarizer()
table_extractor = TableExtractor()
page_extractor = PageExtractor()
translator = DocumentTranslator()
comparator = DocumentComparator()