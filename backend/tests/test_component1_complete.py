"""Component 1 - Complete Testing Suite

Tests all 9 capabilities:
1. Classification
2. Entity Extraction
3. Chaining
4. Question Answering
5. Summarization
6. Table Extraction
7. Page Extraction
8. Translation
9. Comparison
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from document_extraction import (
    document_processor,
    classifier,
    extractor,
    qa,
    summarizer,
    table_extractor,
    page_extractor,
    translator,
    comparator,
    DocumentType
)
from logs import logger


class Component1Tester:
    """Test all Component 1 capabilities"""
    
    def __init__(self):
        """Initialize tester"""
        logger.info("="*70)
        logger.info("COMPONENT 1 - COMPLETE TESTING SUITE")
        logger.info("="*70)
        self.sample_dir = Path(__file__).parent / "sample_documents"
        self.test_results = {}
    
    # ========== HELPER METHODS ==========
    
    def load_pdf(self, filename: str) -> bytes:
        """Load PDF file as bytes"""
        pdf_path = self.sample_dir / filename
        if not pdf_path.exists():
            logger.error(f"❌ PDF not found: {pdf_path}")
            return None
        
        with open(pdf_path, 'rb') as f:
            return f.read()
    
    # ========== TEST 1: CLASSIFICATION ==========
    
    def test_classification(self) -> bool:
        """Test Capability 1: Document Classification"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 1: DOCUMENT CLASSIFICATION")
            logger.info("="*70)
            
            # Test with script PDF
            pdf_bytes = self.load_pdf("filmmaker_script.pdf")
            if not pdf_bytes:
                return False
            
            logger.info("\nClassifying: filmmaker_script.pdf")
            doc_type = classifier.classify_from_bytes(pdf_bytes)
            
            assert doc_type != DocumentType.UNKNOWN, "Should classify as known type"
            logger.info(f"✅ Classification Test PASSED")
            logger.info(f"   Identified as: {doc_type.value}")
            
            self.test_results["Classification"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Classification Test FAILED: {str(e)}")
            self.test_results["Classification"] = "FAILED"
            return False
    
    # ========== TEST 2: ENTITY EXTRACTION ==========
    
    def test_entity_extraction(self) -> bool:
        """Test Capability 2: Entity Extraction"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 2: ENTITY EXTRACTION")
            logger.info("="*70)
            
            # Test with script PDF
            pdf_bytes = self.load_pdf("filmmaker_script.pdf")
            if not pdf_bytes:
                return False
            
            logger.info("\nExtracting entities from: filmmaker_script.pdf")
            doc_type = classifier.classify_from_bytes(pdf_bytes)
            extracted_data = extractor.extract_from_bytes(pdf_bytes, doc_type)
            
            assert extracted_data is not None, "Should extract data"
            logger.info(f"✅ Entity Extraction Test PASSED")
            logger.info(f"   Extracted data type: {type(extracted_data).__name__}")
            
            self.test_results["Entity Extraction"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Entity Extraction Test FAILED: {str(e)}")
            self.test_results["Entity Extraction"] = "FAILED"
            return False
    
    # ========== TEST 3: CHAINING (Classify → Extract) ==========
    
    def test_chaining(self) -> bool:
        """Test Capability 3: Chaining Pattern"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 3: CHAINING (Classify → Extract)")
            logger.info("="*70)
            
            # Test chaining with budget PDF
            pdf_bytes = self.load_pdf("production_budget.pdf")
            if not pdf_bytes:
                return False
            
            logger.info("\nTesting chaining with: production_budget.pdf")
            result = document_processor.process_document_from_bytes(pdf_bytes)
            
            assert result["classification"] is not None, "Should classify"
            assert result["extracted_data"] is not None, "Should extract"
            assert result["error"] is None, "Should have no errors"
            
            logger.info(f"✅ Chaining Test PASSED")
            logger.info(f"   Classification: {result['classification']}")
            logger.info(f"   Data extracted: ✅")
            
            self.test_results["Chaining"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Chaining Test FAILED: {str(e)}")
            self.test_results["Chaining"] = "FAILED"
            return False
    
    # ========== TEST 4: QUESTION ANSWERING ==========
    
    def test_question_answering(self) -> bool:
        """Test Capability 4: Question Answering"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 4: QUESTION ANSWERING")
            logger.info("="*70)
            
            # Test Q&A with budget PDF
            pdf_bytes = self.load_pdf("production_budget.pdf")
            if not pdf_bytes:
                return False
            
            question = "What is the total project budget?"
            logger.info(f"\nAsking: '{question}'")
            
            answer = qa.answer_question_from_bytes(pdf_bytes, question)
            
            assert answer is not None, "Should provide answer"
            assert len(answer) > 0, "Answer should not be empty"
            
            logger.info(f"✅ Question Answering Test PASSED")
            logger.info(f"   Answer: {answer[:100]}...")
            
            self.test_results["Question Answering"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Question Answering Test FAILED: {str(e)}")
            self.test_results["Question Answering"] = "FAILED"
            return False
    
    # ========== TEST 5: SUMMARIZATION ==========
    
    def test_summarization(self) -> bool:
        """Test Capability 5: Summarization"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 5: SUMMARIZATION")
            logger.info("="*70)
            
            # Test summarization with script PDF
            pdf_bytes = self.load_pdf("filmmaker_script.pdf")
            if not pdf_bytes:
                return False
            
            logger.info("\nSummarizing: filmmaker_script.pdf")
            summary = summarizer.summarize_from_bytes(pdf_bytes)
            
            assert summary is not None, "Should provide summary"
            assert len(summary) > 0, "Summary should not be empty"
            
            logger.info(f"✅ Summarization Test PASSED")
            logger.info(f"   Summary: {summary[:100]}...")
            
            self.test_results["Summarization"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Summarization Test FAILED: {str(e)}")
            self.test_results["Summarization"] = "FAILED"
            return False
    
    # ========== TEST 6: TABLE EXTRACTION ==========
    
    def test_table_extraction(self) -> bool:
        """Test Capability 6: Table Extraction"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 6: TABLE EXTRACTION")
            logger.info("="*70)
            
            # Test table extraction with budget PDF
            pdf_bytes = self.load_pdf("production_budget.pdf")
            if not pdf_bytes:
                return False
            
            logger.info("\nExtracting tables from: production_budget.pdf")
            tables = table_extractor.extract_tables_from_bytes(pdf_bytes)
            
            assert tables is not None, "Should extract tables"
            
            logger.info(f"✅ Table Extraction Test PASSED")
            logger.info(f"   Tables found: {len(tables) if tables else 0}")
            
            self.test_results["Table Extraction"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Table Extraction Test FAILED: {str(e)}")
            self.test_results["Table Extraction"] = "FAILED"
            return False
    
    # ========== TEST 7: PAGE EXTRACTION ==========
    
    def test_page_extraction(self) -> bool:
        """Test Capability 7: Page Extraction"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 7: PAGE EXTRACTION")
            logger.info("="*70)
            
            # Test page extraction with schedule PDF
            pdf_bytes = self.load_pdf("shooting_schedule.pdf")
            if not pdf_bytes:
                return False
            
            question = "Which pages contain funding information?"
            logger.info(f"\nFinding pages for: '{question}'")
            
            pages = page_extractor.find_relevant_pages_from_bytes(pdf_bytes, question)
            
            assert pages is not None, "Should find pages"
            
            logger.info(f"✅ Page Extraction Test PASSED")
            logger.info(f"   Pages found: {pages}")
            
            self.test_results["Page Extraction"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Page Extraction Test FAILED: {str(e)}")
            self.test_results["Page Extraction"] = "FAILED"
            return False
    
    # ========== TEST 8: TRANSLATION ==========
    
    def test_translation(self) -> bool:
        """Test Capability 8: Translation"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 8: TRANSLATION")
            logger.info("="*70)
            
            # Test translation with profile PDF
            pdf_bytes = self.load_pdf("filmmaker_profile.pdf")
            if not pdf_bytes:
                return False
            
            logger.info("\nTranslating: filmmaker_profile.pdf into Spanish")
            translation = translator.translate_from_bytes(pdf_bytes, ["Spanish"])
            
            assert translation is not None, "Should provide translation"
            assert len(translation) > 0, "Translation should not be empty"
            
            logger.info(f"✅ Translation Test PASSED")
            logger.info(f"   Translation: {translation[:100]}...")
            
            self.test_results["Translation"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Translation Test FAILED: {str(e)}")
            self.test_results["Translation"] = "FAILED"
            return False
    
    # ========== TEST 9: COMPARISON ==========
    
    def test_comparison(self) -> bool:
        """Test Capability 9: Comparison"""
        try:
            logger.info("\n" + "="*70)
            logger.info("TEST 9: COMPARISON")
            logger.info("="*70)
            
            # Test comparison with script and budget
            pdf_bytes_1 = self.load_pdf("filmmaker_script.pdf")
            pdf_bytes_2 = self.load_pdf("production_budget.pdf")
            
            if not pdf_bytes_1 or not pdf_bytes_2:
                return False
            
            question = "Compare the project information between these two documents."
            logger.info(f"\nComparing two documents...")
            
            comparison = comparator.compare_two_documents_from_bytes(
                pdf_bytes_1, 
                pdf_bytes_2, 
                question
            )
            
            assert comparison is not None, "Should provide comparison"
            assert len(comparison) > 0, "Comparison should not be empty"
            
            logger.info(f"✅ Comparison Test PASSED")
            logger.info(f"   Comparison: {comparison[:100]}...")
            
            self.test_results["Comparison"] = "PASSED"
            return True
            
        except Exception as e:
            logger.error(f"❌ Comparison Test FAILED: {str(e)}")
            self.test_results["Comparison"] = "FAILED"
            return False
    
    # ========== RUN ALL TESTS ==========
    
    def run_all_tests(self) -> dict:
        """Run all 9 capability tests"""
        try:
            tests = [
                ("Classification", self.test_classification),
                ("Entity Extraction", self.test_entity_extraction),
                ("Chaining", self.test_chaining),
                ("Question Answering", self.test_question_answering),
                ("Summarization", self.test_summarization),
                ("Table Extraction", self.test_table_extraction),
                ("Page Extraction", self.test_page_extraction),
                ("Translation", self.test_translation),
                ("Comparison", self.test_comparison),
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
                    self.test_results[test_name] = "ERROR"
                    failed += 1
            
            # Print Summary
            logger.info("\n" + "="*70)
            logger.info("COMPONENT 1 - TEST SUMMARY")
            logger.info("="*70)
            
            for test_name, result in self.test_results.items():
                symbol = "✅" if result == "PASSED" else "❌"
                logger.info(f"{symbol} {test_name}: {result}")
            
            logger.info(f"\nTotal: {passed} PASSED, {failed} FAILED")
            
            if failed == 0:
                logger.info("\n🎉 ALL TESTS PASSED - COMPONENT 1 COMPLETE!")
            else:
                logger.info(f"\n⚠️ {failed} tests failed - Review above")
            
            logger.info("="*70 + "\n")
            
            return {
                "total": len(tests),
                "passed": passed,
                "failed": failed,
                "results": self.test_results
            }
            
        except Exception as e:
            logger.error(f"Test runner error: {str(e)}")
            return {}


def main():
    """Main entry point"""
    try:
        tester = Component1Tester()
        results = tester.run_all_tests()
        
        return 0 if results.get("failed", 1) == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)