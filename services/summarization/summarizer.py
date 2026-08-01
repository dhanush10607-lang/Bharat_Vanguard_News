"""
TruthLens AI — AI Summarizer
Generates multi-level summaries for articles using HuggingFace Transformers.
"""
import logging
from transformers import pipeline
import nltk

# Ensure punkt is downloaded for sentence splitting
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
# For newer nltk versions punkt_tab might be needed
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

from nltk.tokenize import sent_tokenize

logger = logging.getLogger("nlp.summarizer")

class Summarizer:
    def __init__(self):
        logger.info("Loading Summarization model (facebook/bart-large-cnn)...")
        # device=-1 for CPU
        self.pipeline = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1
        )
        logger.info("Summarization model loaded.")

    def summarize_article(self, text: str) -> dict:
        """
        Generates 3 levels of summary:
        - short (1 sentence)
        - medium (3-5 sentences)
        - bullets (list of points)
        
        Optimized for CPU: Runs one generation pass (medium length),
        then uses NLTK sentence tokenization to derive short and bullet versions.
        """
        if not text or len(text.split()) < 50:
            # Too short to summarize meaningfully
            return {
                "short": text,
                "medium": text,
                "bullets": [text] if text else []
            }
            
        try:
            # Truncate text to fit BART's context window (roughly 1024 tokens ~ 4000 chars)
            safe_text = text[:4000]
            
            # Generate medium summary (target 130 max length for a good paragraph)
            result = self.pipeline(safe_text, max_length=150, min_length=40, do_sample=False)
            medium_text = result[0]["summary_text"].strip()
            
            # Tokenize into sentences
            sentences = sent_tokenize(medium_text)
            
            # Derive short summary (first sentence)
            short_text = sentences[0] if sentences else medium_text
            
            # Derive bullets (each sentence is a bullet)
            bullets = [s for s in sentences if s.strip()]
            
            return {
                "short": short_text,
                "medium": medium_text,
                "bullets": bullets
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {
                "short": "",
                "medium": "",
                "bullets": []
            }

    def summarize_event(self, texts: list[str]) -> dict:
        """
        Summarizes a cluster of related articles (an Event).
        Combines the texts (or their summaries) up to the model's context limit,
        and generates a single unified summary.
        """
        if not texts:
            return {"short": "", "medium": "", "bullets": []}
            
        # Combine texts with some delimiter, truncating each to roughly balance them
        # Target total context around 4000 chars for BART
        budget_per_text = max(500, 4000 // len(texts))
        combined_text = " \n ".join([t[:budget_per_text] for t in texts if t])
        
        # We can just reuse the article summarization logic since it handles 
        # the same input/output format and tokenization constraints.
        return self.summarize_article(combined_text)

# Singleton
_summarizer = None

def get_summarizer() -> Summarizer:
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer()
    return _summarizer
