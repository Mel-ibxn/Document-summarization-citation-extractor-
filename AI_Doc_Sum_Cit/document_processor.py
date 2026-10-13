import re
import io
import pdfplumber
from docx import Document

class DocumentProcessor:
    """
    Handles extraction of text from various document formats (PDF, DOCX, TXT)
    and applies cleaning logic.
    """

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """
        Takes file bytes and filename, determines file type, and extracts text.
        """
        extension = filename.lower().split('.')[-1]
        
        if extension == 'pdf':
            return self._extract_from_pdf(file_bytes)
        elif extension == 'docx':
            return self._extract_from_docx(file_bytes)
        elif extension in ['txt', 'md']:
            return self._extract_from_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extracts text from PDF using pdfplumber."""
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _extract_from_docx(self, file_bytes: bytes) -> str:
        """Extracts text from DOCX using python-docx."""
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([para.text for para in doc.paragraphs])

    def _extract_from_txt(self, file_bytes: bytes) -> str:
        """Extracts text from TXT using UTF-8 encoding."""
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            return file_bytes.decode('latin-1')

    def clean_text(self, text: str) -> str:
        """
        Cleans the extracted text by:
        - Removing extra whitespaces and newlines.
        - Stripping leading/trailing whitespace.
        - Basic cleanup of messy characters.
        """
        if not text:
            return ""

        # Replace multiple spaces with a single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Replace 3 or more newlines with 2 newlines (keep paragraph structure but remove excess)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace from each line and from the whole text
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Final strip
        text = text.strip()
        
        return text

    def process(self, file_bytes: bytes, filename: str) -> str:
        """Convenience method to extract and clean text in one go."""
        raw_text = self.extract_text(file_bytes, filename)
        return self.clean_text(raw_text)

if __name__ == "__main__":
    # Example usage / basic smoke test
    processor = DocumentProcessor()
    sample_text = "   This is a   test. \n\n\n Messy   text here.   "
    cleaned = processor.clean_text(sample_text)
    print(f"Cleaned: '{cleaned}'")
