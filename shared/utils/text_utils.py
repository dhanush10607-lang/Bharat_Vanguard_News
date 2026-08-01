"""
Bharat Vanguard News (BVN) — Text Processing Utilities
"""
import re
import math
from typing import Optional


# Average reading speed (words per minute)
READING_SPEED_WPM = 238


def clean_text(text: Optional[str]) -> str:
    """
    Clean raw text extracted from articles.
    - Removes excessive whitespace and newlines
    - Removes null bytes
    - Strips leading/trailing whitespace
    """
    if not text:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple blank lines to single
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def count_words(text: str) -> int:
    """Count the number of words in a text string."""
    if not text:
        return 0
    return len(text.split())


def estimate_reading_time(text: str) -> int:
    """
    Estimate reading time in minutes.
    Returns minimum 1 minute.
    """
    words = count_words(text)
    minutes = math.ceil(words / READING_SPEED_WPM)
    return max(1, minutes)


def truncate(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to max_length characters, breaking at word boundary.
    """
    if not text or len(text) <= max_length:
        return text

    truncated = text[: max_length - len(suffix)]
    # Break at last space
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + suffix


def extract_first_sentence(text: str) -> str:
    """Extract the first sentence from a paragraph of text."""
    if not text:
        return ""

    # Split on sentence-ending punctuation
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return sentences[0] if sentences else text[:200]


def remove_html_tags(text: str) -> str:
    """Strip HTML tags from text (fallback if trafilatura misses some)."""
    clean = re.compile(r"<[^>]+>")
    return clean.sub("", text).strip()
