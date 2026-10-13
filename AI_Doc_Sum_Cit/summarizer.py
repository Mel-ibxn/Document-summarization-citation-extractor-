import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List

class Summarizer:
    """
    Handles AI-powered text summarization using pre-trained models.
    Supports chunking for long documents and variable summary lengths.
    Uses AutoModelForSeq2SeqLM directly to avoid pipeline registry issues.
    """

    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        
        # Ranges for different length modes
        self.length_params = {
            "short": {"max_length": 60, "min_length": 20},
            "medium": {"max_length": 150, "min_length": 50},
            "long": {"max_length": 300, "min_length": 150}
        }

    def load_model(self):
        """Loads the model and tokenizer into memory."""
        if self.model is None:
            print(f"Loading model {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
            print("Model loaded successfully.")

    def _chunk_text(self, text: str, max_chunk_size: int = 800) -> List[str]:
        """
        Splits text into chunks of roughly max_chunk_size tokens.
        Simple word-based splitting as a fallback for robustness.
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += 1
            
            if current_length >= max_chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def summarize(self, text: str, length_mode: str = "medium") -> str:
        """
        Summarizes the input text. Handles long text by chunking.
        length_mode: 'short', 'medium', or 'long'
        """
        if not text or len(text.strip()) < 50:
            return text

        self.load_model()
        
        params = self.length_params.get(length_mode, self.length_params["medium"])
        
        # BART context window is 1024. Let's use 800 for safety.
        chunks = self._chunk_text(text, max_chunk_size=800)
        
        summaries = []
        for chunk in chunks:
            if len(chunk.split()) < 10: 
                continue
            
            # Tokenize and generate
            inputs = self.tokenizer(chunk, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
            
            summary_ids = self.model.generate(
                inputs["input_ids"], 
                max_length=params["max_length"], 
                min_length=params["min_length"], 
                length_penalty=2.0, 
                num_beams=4, 
                early_stopping=True
            )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(summary)
            
        # If we have multiple chunks, combine them. 
        # For very long docs, we might want to summarize the combined summary again, 
        # but for now, we just join them.
        return " ".join(summaries)

if __name__ == "__main__":
    # Basic smoke test (will trigger download on first run)
    s = Summarizer()
    sample = (
        "The Supreme Court of India is the supreme judicial authority of India and is the highest court of the Republic of India under the constitution. "
        "It is the most senior constitutional court, and has the power of judicial review. The Chief Justice of India is the head and chief judge of the Supreme Court, "
        "which consists of a maximum of 34 judges and has extensive powers in the form of original, appellate and advisory jurisdictions. "
        "It is regarded as the most powerful public institution in India. It safeguards fundamental rights of citizens and settles disputes between various government authorities as well as the central government vs state governments or state governments versus each other. "
        "As an advisory court, it hears matters which may specifically be referred to it by the President of India under the Constitution. "
        "The law declared by the Supreme Court becomes binding on all courts within India and also by the union and state governments. "
        "Per Article 141 of the Constitution, the law declared by the Supreme Court is to be binding on all courts within the territory of India."
    )
    
    print("Testing Summarizer...")
    result = s.summarize(sample, length_mode="short")
    print(f"\nSummary (Short):\n{result}")
