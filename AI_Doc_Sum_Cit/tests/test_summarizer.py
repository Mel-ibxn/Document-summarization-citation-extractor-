import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from summarizer import Summarizer

class TestSummarizer(unittest.TestCase):
    def setUp(self):
        self.summarizer = Summarizer()

    def test_summarization_basic(self):
        text = (
            "The Supreme Court of India is the topmost judicial body in the country. "
            "It was established under the Constitution of India and has the power of judicial review. "
            "The court consists of the Chief Justice and 33 other judges. It has original, appellate, "
            "and advisory jurisdictions. It is one of the most powerful courts in the world."
        )
        summary = self.summarizer.summarize(text, length_mode="short")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(text))

if __name__ == "__main__":
    unittest.main()
