# -*- coding: utf-8 -*-
"""Complete Test Suite for Document Extraction - COMPONENT 1
Following exact patterns from:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/document-processing/document_processing.ipynb

Tests ALL 9 Capabilities:
1. Document Classification
2. Entity Extraction
3. Chaining (Classify → Extract)
4. Question Answering
5. Summarization
6. Table Extraction
7. Page Extraction
8. Translation
9. Comparison

Uses REAL PDFs and REAL Gemini API calls.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.document_extraction import (
    classifier,
    extractor,
    qa,
    summarizer,
    table_extractor,
    page_extractor,
    translator,
    comparator,
    document_processor,
    DocumentType
)
from src.logs import logger


class DocumentExtractionTestSuite:
    """Complete test suite for all 9 document extraction capabilities"""
    
    def __init__(self):
        """Initialize test suite"""
        logger.info("\n" + "="*80)
        logger.info("DOCUMENT EXTRACTION - COMPLETE TEST SUITE")
        logger.info("Testing all 9 capabilities with REAL PDFs and REAL Gemini API")
        logger.info("="*80)
        
        self.sample_dir = Path(__file__).parent / "sample_documents"
        self.test_results = {}
        self.pdfs = {}
        
        # Verify sample directory exists
        if not self.sample_dir.exists():
            logger.error(f" Sample documents directory not found: {self.sample_dir}")
            logger.error("Run: python tests/create_test_pdfs.py")
            sys.exit(1)
    
    # ========== HELPER METHODS ==========
    
    def load_all_pdfs(self) -> bool:
        """Load all PDF files needed for testing"""
        try:
            logger.info("\n" + "="*80)
            logger.info("LOADING PDF FILES")
            logger.info("="*80)
            
            pdf_files = {
                "script": "filmmaker_script.pdf",
                "budget": "production_budget.pdf",
                "schedule": "shooting_schedule.pdf",
                "profile": "filmmaker_profile.pdf"
            }
            
            all_loaded = True
            for key, filename in pdf_files.items():
                pdf_path = self.sample_dir / filename
                
                if not pdf_path.exists():
                    logger.error(f" Missing PDF: {filename}")
                    all_loaded = False
                    continue
                
                try:
                    with open(pdf_path, 'rb') as f:
                        self.pdfs[key] = f.read()
                    logger.info(f"✅ Loaded: {filename} ({len(self.pdfs[key])} bytes)")
                except Exception as e:
                    logger.error(f" Failed to load {filename}: {str(e)}")
                    all_loaded = False
            
            if not all_loaded:
                logger.error(" Not all PDFs loaded. Run: python tests/create_test_pdfs.py")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f" PDF loading error: {str(e)}")
            return False
    
    # ========== CAPABILITY 1: CLASSIFICATION ==========
    
    def test_capability_1_classification(self) -> bool:
        """Test Capability 1: Document Classification"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 1: DOCUMENT CLASSIFICATION")
            logger.info("="*80)
            
            if "script" not in self.pdfs:
                logger.error(" Script PDF not loaded")
                return False
            
            logger.info("\n Testing classification with: filmmaker_script.pdf")
            logger.info("Sending to Gemini API...")
            
            doc_type = classifier.classify_from_bytes(self.pdfs["script"])
            
            logger.info(f"\n Classification Result:")
            logger.info(f"   Document Type: {doc_type.value}")
            logger.info(f"   Expected: filmmaker_script")
            
            if doc_type == DocumentType.UNKNOWN:
                logger.error(" Failed to classify document")
                self.test_results["1. Classification"] = "FAILED"
                return False
            
            self.test_results["1. Classification"] = "PASSED"
            logger.info(" Classification Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Classification Test FAILED: {str(e)}")
            self.test_results["1. Classification"] = "FAILED"
            return False
    
    # ========== CAPABILITY 2: ENTITY EXTRACTION ==========
    
    def test_capability_2_entity_extraction(self) -> bool:
        """Test Capability 2: Entity Extraction"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 2: ENTITY EXTRACTION")
            logger.info("="*80)
            
            if "script" not in self.pdfs:
                logger.error(" Script PDF not loaded")
                return False
            
            logger.info("\n Testing entity extraction with: filmmaker_script.pdf")
            logger.info("Step 1: Classifying document...")
            
            doc_type = classifier.classify_from_bytes(self.pdfs["script"])
            
            logger.info(f"   Classification: {doc_type.value}")
            logger.info("Step 2: Extracting entities...")
            logger.info("Sending to Gemini API...")
            
            extracted_data = extractor.extract_from_bytes(self.pdfs["script"], doc_type)
            
            if extracted_data is None:
                logger.error(" Failed to extract entities")
                self.test_results["2. Entity Extraction"] = "FAILED"
                return False
            
            logger.info(f"\n Extraction Result:")
            logger.info(f"   Data Type: {type(extracted_data).__name__}")
            logger.info(f"   Project Title: {getattr(extracted_data, 'project_title', 'N/A')}")
            logger.info(f"   Genre: {getattr(extracted_data, 'genre', 'N/A')}")
            logger.info(f"   Urgency: {getattr(extracted_data, 'urgency_level', 'N/A')}")
            
            self.test_results["2. Entity Extraction"] = "PASSED"
            logger.info("✅ Entity Extraction Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Entity Extraction Test FAILED: {str(e)}")
            self.test_results["2. Entity Extraction"] = "FAILED"
            return False
    
    # ========== CAPABILITY 3: CHAINING ==========
    
    def test_capability_3_chaining(self) -> bool:
        """Test Capability 3: Chaining (Classify → Extract)"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 3: CHAINING (Classify → Extract)")
            logger.info("="*80)
            
            if "budget" not in self.pdfs:
                logger.error(" Budget PDF not loaded")
                return False
            
            logger.info("\n Testing chaining with: production_budget.pdf")
            logger.info("Process: Classify document → Then extract entities")
            logger.info("Sending to Gemini API...")
            
            result = document_processor.process_from_bytes(self.pdfs["budget"])
            
            if result["error"] is not None:
                logger.error(f" Processing failed: {result['error']}")
                self.test_results["3. Chaining"] = "FAILED"
                return False
            
            logger.info(f"\n Chaining Result:")
            logger.info(f"   Classification: {result['classification']}")
            logger.info(f"   Data Extracted: {'Yes' if result['extracted_data'] else 'No'}")
            logger.info(f"   Total Budget: ${getattr(result['extracted_data'], 'total_budget', 'N/A'):,}")
            
            self.test_results["3. Chaining"] = "PASSED"
            logger.info("✅ Chaining Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Chaining Test FAILED: {str(e)}")
            self.test_results["3. Chaining"] = "FAILED"
            return False
    
    # ========== CAPABILITY 4: QUESTION ANSWERING ==========
    
    def test_capability_4_question_answering(self) -> bool:
        """Test Capability 4: Question Answering"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 4: QUESTION ANSWERING")
            logger.info("="*80)
            
            if "budget" not in self.pdfs:
                logger.error(" Budget PDF not loaded")
                return False
            
            question = "What is the total project budget and funding gap?"
            logger.info(f"\n Testing Q&A with: production_budget.pdf")
            logger.info(f"Question: '{question}'")
            logger.info("Sending to Gemini API...")
            
            answer = qa.answer_from_bytes(self.pdfs["budget"], question)
            
            if answer is None or len(answer) == 0:
                logger.error(" Failed to get answer")
                self.test_results["4. Question Answering"] = "FAILED"
                return False
            
            logger.info(f"\n Q&A Result:")
            logger.info(f"   Answer: {answer[:150]}...")
            
            self.test_results["4. Question Answering"] = "PASSED"
            logger.info(" Question Answering Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Question Answering Test FAILED: {str(e)}")
            self.test_results["4. Question Answering"] = "FAILED"
            return False
    
    # ========== CAPABILITY 5: SUMMARIZATION ==========
    
    def test_capability_5_summarization(self) -> bool:
        """Test Capability 5: Summarization"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 5: SUMMARIZATION")
            logger.info("="*80)
            
            if "script" not in self.pdfs:
                logger.error(" Script PDF not loaded")
                return False
            
            logger.info("\n Testing summarization with: filmmaker_script.pdf")
            logger.info("Sending to Gemini API...")
            
            summary = summarizer.summarize_from_bytes(self.pdfs["script"])
            
            if summary is None or len(summary) == 0:
                logger.error(" Failed to generate summary")
                self.test_results["5. Summarization"] = "FAILED"
                return False
            
            logger.info(f"\n Summarization Result:")
            logger.info(f"   Summary: {summary[:150]}...")
            
            self.test_results["5. Summarization"] = "PASSED"
            logger.info(" Summarization Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Summarization Test FAILED: {str(e)}")
            self.test_results["5. Summarization"] = "FAILED"
            return False
    
    # ========== CAPABILITY 6: TABLE EXTRACTION ==========
    
    def test_capability_6_table_extraction(self) -> bool:
        """Test Capability 6: Table Extraction"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 6: TABLE EXTRACTION")
            logger.info("="*80)
            
            if "budget" not in self.pdfs:
                logger.error(" Budget PDF not loaded")
                return False
            
            logger.info("\n Testing table extraction with: production_budget.pdf")
            logger.info("Sending to Gemini API...")
            
            tables = table_extractor.extract_from_bytes(self.pdfs["budget"])
            
            if tables is None:
                logger.error(" Failed to extract tables")
                self.test_results["6. Table Extraction"] = "FAILED"
                return False
            
            logger.info(f"\n Table Extraction Result:")
            logger.info(f"   Tables found: {len(tables) if tables else 0}")
            logger.info(f"   Content length: {len(tables)} characters")
            
            self.test_results["6. Table Extraction"] = "PASSED"
            logger.info(" Table Extraction Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Table Extraction Test FAILED: {str(e)}")
            self.test_results["6. Table Extraction"] = "FAILED"
            return False
    
    # ========== CAPABILITY 7: PAGE EXTRACTION ==========
    
    def test_capability_7_page_extraction(self) -> bool:
        """Test Capability 7: Page Extraction"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 7: PAGE EXTRACTION")
            logger.info("="*80)
            
            if "schedule" not in self.pdfs:
                logger.error(" Schedule PDF not loaded")
                return False
            
            question = "Which pages contain funding deadline information?"
            logger.info("\n Testing page extraction with: shooting_schedule.pdf")
            logger.info(f"Question: '{question}'")
            logger.info("Sending to Gemini API...")
            
            pages = page_extractor.find_pages_from_bytes(self.pdfs["schedule"], question)
            
            if pages is None:
                logger.error(" Failed to extract page numbers")
                self.test_results["7. Page Extraction"] = "FAILED"
                return False
            
            logger.info(f"\ Page Extraction Result:")
            logger.info(f"   Pages found: {pages}")
            
            self.test_results["7. Page Extraction"] = "PASSED"
            logger.info(" Page Extraction Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Page Extraction Test FAILED: {str(e)}")
            self.test_results["7. Page Extraction"] = "FAILED"
            return False
    
    # ========== CAPABILITY 8: TRANSLATION ==========
    
    def test_capability_8_translation(self) -> bool:
        """Test Capability 8: Translation"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 8: TRANSLATION")
            logger.info("="*80)
            
            if "profile" not in self.pdfs:
                logger.error(" Profile PDF not loaded")
                return False
            
            target_languages = ["Spanish"]
            logger.info("\n Testing translation with: filmmaker_profile.pdf")
            logger.info(f"Target languages: {target_languages}")
            logger.info("Sending to Gemini API...")
            
            translation = translator.translate_from_bytes(self.pdfs["profile"], target_languages)
            
            if translation is None or len(translation) == 0:
                logger.error(" Failed to translate document")
                self.test_results["8. Translation"] = "FAILED"
                return False
            
            logger.info(f"\n Translation Result:")
            logger.info(f"   Translation: {translation[:150]}...")
            
            self.test_results["8. Translation"] = "PASSED"
            logger.info(" Translation Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f" Translation Test FAILED: {str(e)}")
            self.test_results["8. Translation"] = "FAILED"
            return False
    
    # ========== CAPABILITY 9: COMPARISON ==========
    
    def test_capability_9_comparison(self) -> bool:
        """Test Capability 9: Comparison"""
        try:
            logger.info("\n" + "="*80)
            logger.info("CAPABILITY 9: COMPARISON")
            logger.info("="*80)
            
            if "script" not in self.pdfs or "budget" not in self.pdfs:
                logger.error(" Required PDFs not loaded")
                return False
            
            question = "Compare the project information between the script and budget documents."
            logger.info("\n Testing comparison with:")
            logger.info("   Document 1: filmmaker_script.pdf")
            logger.info("   Document 2: production_budget.pdf")
            logger.info(f"Question: '{question}'")
            logger.info("Sending to Gemini API...")
            
            comparison = comparator.compare_from_bytes(
                [self.pdfs["script"], self.pdfs["budget"]],
                question
            )
            
            if comparison is None or len(comparison) == 0:
                logger.error(" Failed to compare documents")
                self.test_results["9. Comparison"] = "FAILED"
                return False
            
            logger.info(f"\n Comparison Result:")
            logger.info(f"   Comparison: {comparison[:150]}...")
            
            self.test_results["9. Comparison"] = "PASSED"
            logger.info(" Comparison Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Comparison Test FAILED: {str(e)}")
            self.test_results["9. Comparison"] = "FAILED"
            return False
    
    # ========== RUN ALL TESTS ==========
    
    def run_all_tests(self) -> int:
        """Run all 9 capability tests"""
        try:
            # Load PDFs first
            if not self.load_all_pdfs():
                return 1
            
            # Run all tests
            tests = [
                self.test_capability_1_classification,
                self.test_capability_2_entity_extraction,
                self.test_capability_3_chaining,
                self.test_capability_4_question_answering,
                self.test_capability_5_summarization,
                self.test_capability_6_table_extraction,
                self.test_capability_7_page_extraction,
                self.test_capability_8_translation,
                self.test_capability_9_comparison,
            ]
            
            passed = 0
            failed = 0
            
            for test_func in tests:
                try:
                    result = test_func()
                    if result:
                        passed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Test exception: {str(e)}")
                    failed += 1
            
            # Print Summary
            logger.info("\n" + "="*80)
            logger.info("FINAL TEST SUMMARY - COMPONENT 1 COMPLETE")
            logger.info("="*80)
            
            for test_name, result in self.test_results.items():
                symbol = "" if result == "PASSED" else ""
                logger.info(f"{symbol} {test_name}: {result}")
            
            logger.info(f"\n Total Results:")
            logger.info(f"    PASSED: {passed}")
            logger.info(f"    FAILED: {failed}")
            logger.info(f"    Success Rate: {(passed/(passed+failed)*100):.1f}%")
            
            if failed == 0:
                logger.info("\n ALL TESTS PASSED - COMPONENT 1 VERIFIED!")
                logger.info("Ready to move to COMPONENT 2 (RAG with BigQuery)")
            else:
                logger.info(f"\n {failed} tests failed - Review above for details")
            
            logger.info("="*80 + "\n")
            
            return 0 if failed == 0 else 1
            
        except Exception as e:
            logger.error(f" Test suite error: {str(e)}")
            return 1


def main():
    """Main entry point"""
    try:
        suite = DocumentExtractionTestSuite()
        return suite.run_all_tests()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
