"""
Bharat Vanguard News (BVN) — Hashing Utilities
SHA256 hashing for URL and content deduplication.
"""
import hashlib


def hash_url(url: str) -> str:
    """
    Create a SHA256 hash of a URL for fast duplicate detection.
    Normalized before hashing (strip trailing slash, lowercase scheme+host).

    Example:
        hash_url("https://BBC.com/news/article/") == hash_url("https://bbc.com/news/article")
    """
    if not url:
        return ""
    normalized = _normalize_url(url)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def hash_content(content: str) -> str:
    """
    Create a SHA256 hash of article content for detecting near-identical articles.
    Strips whitespace before hashing.
    """
    if not content:
        return ""
    normalized = " ".join(content.split())  # normalize whitespace
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalize_url(url: str) -> str:
    """Normalize a URL for consistent hashing."""
    url = url.strip().lower()
    # Remove trailing slash
    if url.endswith("/"):
        url = url[:-1]
    # Remove common tracking parameters (utm_*, fbclid, etc.)
    if "?" in url:
        base, params = url.split("?", 1)
        filtered = "&".join(
            p for p in params.split("&")
            if not p.startswith(("utm_", "fbclid", "gclid", "ref=", "source="))
        )
        url = f"{base}?{filtered}" if filtered else base
    return url
