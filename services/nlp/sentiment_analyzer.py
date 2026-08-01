"""
Bharat Vanguard News (BVN) — Sentiment Analyzer
Sentiment analysis using HuggingFace Transformers (cardiffnlp/twitter-roberta-base-sentiment-latest)
"""
import logging
from transformers import pipeline

logger = logging.getLogger("nlp.sentiment")

class SentimentAnalyzer:
    def __init__(self):
        logger.info("Loading Sentiment model (cardiffnlp/twitter-roberta-base-sentiment-latest)...")
        self.analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
            max_length=512,
            truncation=True,
            device=-1
        )
        logger.info("Sentiment model loaded.")

    def analyze(self, text: str) -> dict:
        """
        Analyzes the sentiment of the text.
        Returns a dictionary with the sentiment (positive, neutral, negative) and confidence score.
        """
        if not text or not text.strip():
            return {"sentiment": "neutral", "score": 0.0}
            
        try:
            # Model output: [{'label': 'positive', 'score': 0.85}]
            result = self.analyzer(text)[0]
            label = result["label"].lower()
            score = result["score"]
            
            return {
                "sentiment": label,
                "score": score
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"sentiment": "neutral", "score": 0.0}

# Singleton
_analyzer = None

def get_sentiment_analyzer() -> SentimentAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer
