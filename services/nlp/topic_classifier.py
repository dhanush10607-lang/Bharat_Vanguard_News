"""
TruthLens AI — Topic Classifier
Zero-shot classification using HuggingFace Transformers (facebook/bart-large-mnli)
"""
import logging
from transformers import pipeline

logger = logging.getLogger("nlp.topics")

# Standard categories we want to map into
STANDARD_CATEGORIES = [
    "world", "technology", "ai", "business", "finance", 
    "science", "environment", "health", "politics", 
    "sports", "entertainment", "india"
]

class TopicClassifier:
    def __init__(self):
        logger.info("Loading Zero-Shot Classification model (facebook/bart-large-mnli)...")
        # device=-1 forces CPU which is safe for free tier/low RAM. Use device=0 for GPU.
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1
        )
        logger.info("Zero-Shot Classification model loaded.")

    def classify(self, text: str, candidate_labels: list[str] = None) -> dict:
        """
        Classifies the text into one of the candidate labels.
        Returns the top predicted category and its confidence score.
        """
        if not text or not text.strip():
            return {"category": "unknown", "score": 0.0}
            
        labels = candidate_labels if candidate_labels else STANDARD_CATEGORIES
        
        # Truncate text to avoid sequence length errors (BART handles up to 1024 tokens)
        # 3000 chars is usually safe
        safe_text = text[:3000]
        
        try:
            result = self.classifier(safe_text, labels)
            # result format: {'sequence': text, 'labels': ['world', ...], 'scores': [0.9, ...]}
            top_label = result["labels"][0]
            top_score = result["scores"][0]
            
            return {
                "category": top_label,
                "score": top_score,
                "all_scores": dict(zip(result["labels"], result["scores"]))
            }
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {"category": "unknown", "score": 0.0}

# Singleton
_classifier = None

def get_topic_classifier() -> TopicClassifier:
    global _classifier
    if _classifier is None:
        _classifier = TopicClassifier()
    return _classifier
