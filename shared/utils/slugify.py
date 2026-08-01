"""
TruthLens AI — Slug Generator
Creates URL-safe slugs from article titles.
"""
import re
import unicodedata
from slugify import slugify as _slugify


def make_slug(text: str, max_length: int = 100) -> str:
    """
    Generate a clean URL slug from any text string.

    Examples:
        "Apple launches new AI chip!" → "apple-launches-new-ai-chip"
        "Modi's speech on India's economy" → "modis-speech-on-indias-economy"
    """
    if not text:
        return ""

    slug = _slugify(
        text,
        max_length=max_length,
        word_boundary=True,
        separator="-",
        lowercase=True,
    )

    return slug


def make_unique_slug(text: str, existing_slugs: set[str], max_length: int = 100) -> str:
    """
    Generate a slug guaranteed to not conflict with existing slugs.
    Appends a numeric suffix if needed: "title-2", "title-3", etc.
    """
    base = make_slug(text, max_length=max_length - 5)  # leave room for suffix
    slug = base

    counter = 2
    while slug in existing_slugs:
        slug = f"{base}-{counter}"
        counter += 1

    return slug
