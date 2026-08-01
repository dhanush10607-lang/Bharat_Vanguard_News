"""
TruthLens AI — Language Detector
Detects the primary language of an article.
"""
import logging
from langdetect import detect, detect_langs, LangDetectException

logger = logging.getLogger("nlp.language")

def detect_language(text: str) -> str:
    """
    Detects language of the provided text.
    Returns ISO 639-1 language code (e.g. 'en', 'es').
    Falls back to 'unknown' if detection fails.
    """
    if not text or not text.strip():
        return "unknown"
    
    try:
        # Get the top detected language
        lang = detect(text)
        return lang
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return "unknown"

def detect_languages_with_confidence(text: str) -> list[dict]:
    """
    Detects languages with confidence scores.
    Returns a list of dicts: [{'lang': 'en', 'score': 0.99}, ...]
    """
    if not text or not text.strip():
        return []
        
    try:
        langs = detect_langs(text)
        return [{"lang": l.lang, "score": l.prob} for l in langs]
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return []
