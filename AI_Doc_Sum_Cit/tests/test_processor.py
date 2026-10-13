import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()

    def test_cleaning(self):
        messy_text = "  Hello   World  \n\n\n  New Paragraph  "
        expected = "Hello World\n\nNew Paragraph"
        cleaned = self.processor.clean_text(messy_text)
        self.assertEqual(cleaned, expected)

    def test_txt_extraction(self):
        content = "This is a test file content."
        file_bytes = content.encode('utf-8')
        extracted = self.processor.extract_text(file_bytes, "test.txt")
        self.assertEqual(extracted, content)

if __name__ == "__main__":
    unittest.main()
