import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from citation_extractor import CitationExtractor

class TestCitationExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = CitationExtractor()

    def test_citation_extraction(self):
        sample_text = """
        The Petitioner in Suresh v. Union of India argued that Section 21 of the Constitution of India 
        was violated. Reference was made to Section 300 of the Indian Penal Code. 
        The High Court of Delhi observed that the case was similar to Amit vs. State of Haryana. 
        The judgment cited (1995) and 2022 SCC. 
        The Supreme Court finally decided the matter.
        """
        results = self.extractor.extract_all(sample_text)
        
        self.assertIn("Suresh v. Union of India", results["cases"])
        self.assertIn("Section 21", results["sections"])
        self.assertIn("Indian Penal Code", results["acts"])
        self.assertIn("(1995)", results["years"])
        self.assertIn("Supreme Court", results["courts"])

if __name__ == "__main__":
    unittest.main()
