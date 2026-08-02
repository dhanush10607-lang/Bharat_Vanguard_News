"""
Bharat Vanguard News (BVN) — The Guardian API Collector
Fetches articles from The Guardian Open Platform (free: 5,000 calls/day).
Sign up at: https://open-platform.theguardian.com/access/

Advantages over RSS:
- Full article text available
- Structured metadata (section, tags, byline)
- Clean JSON response (no HTML parsing needed)
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config import settings
from shared.database import AsyncSessionLocal
from shared.models import Article, Publisher, ArticleStatus
from shared.utils.hashing import hash_url
from shared.utils.date_utils import parse_date
from shared.utils.text_utils import clean_text

logger = logging.getLogger("collector.guardian")

GUARDIAN_API_BASE = "https://content.guardianapis.com"

# Categories to collect and their Guardian section mapping
GUARDIAN_SECTIONS = {
    "world":        "world",
    "technology":   "technology",
    "business":     "business",
    "science":      "science",
    "environment":  "environment",
    "health":       "health",
    "politics":     "politics",
    "sport":        "sport",
    "culture":      "culture",
    "education":    "education",
}


class GuardianCollector:
    """Collects from The Guardian Open Platform API."""

    PUBLISHER_SLUG = "the-guardian"
    PUBLISHER_CONFIG = {
        "name": "The Guardian",
        "website": "https://www.theguardian.com",
        "country": "UK",
        "language": "en",
        "reputation_score": 0.88,
    }

    def __init__(self):
        self.api_key = settings.guardian_api_key
        if not self.api_key:
            logger.warning("GUARDIAN_API_KEY not set — Guardian collector disabled")

    async def get_or_create_publisher(self, db: AsyncSession) -> Optional[Publisher]:
        result = await db.execute(
            select(Publisher).where(Publisher.slug == self.PUBLISHER_SLUG)
        )
        publisher = result.scalar_one_or_none()

        if not publisher:
            publisher = Publisher(
                slug=self.PUBLISHER_SLUG,
                **self.PUBLISHER_CONFIG,
            )
            db.add(publisher)
            await db.flush()

        return publisher

    async def fetch_section(
        self, client: httpx.AsyncClient, section: str, page: int = 1
    ) -> Optional[dict]:
        """Fetch articles for a Guardian section."""
        params = {
            "api-key": self.api_key,
            "section": section,
            "show-fields": "trailText,byline,thumbnail,wordcount",
            "page-size": 20,
            "page": page,
            "order-by": "newest",
        }
        try:
            response = await client.get(f"{GUARDIAN_API_BASE}/search", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Guardian API error for section {section}: {e}")
            return None

    async def run(self) -> dict:
        """Collect from all Guardian sections."""
        if not self.api_key:
            return {"skipped": True, "reason": "no_api_key"}

        stats = {"found": 0, "new": 0, "duplicate": 0}

        async with httpx.AsyncClient(timeout=30) as client:
            async with AsyncSessionLocal() as db:
                publisher = await self.get_or_create_publisher(db)

                for category, section in GUARDIAN_SECTIONS.items():
                    data = await self.fetch_section(client, section)
                    if not data or data.get("response", {}).get("status") != "ok":
                        continue

                    results = data["response"].get("results", [])
                    stats["found"] += len(results)

                    for item in results:
                        url = item.get("webUrl", "")
                        if not url:
                            continue

                        url_hash = hash_url(url)
                        # Check duplicate
                        exists = await db.execute(
                            select(Article.article_id).where(Article.url_hash == url_hash).limit(1)
                        )
                        if exists.scalar_one_or_none():
                            stats["duplicate"] += 1
                            continue

                        fields = item.get("fields", {})
                        title = item.get("webTitle", "")
                        description = clean_text(fields.get("trailText", ""))
                        published_time = parse_date(item.get("webPublicationDate"))

                        article = Article(
                            title=title[:1000],
                            slug=url_hash[:12],
                            description=description,
                            url=url,
                            url_hash=url_hash,
                            image_url=fields.get("thumbnail"),
                            author=fields.get("byline"),
                            category=category,
                            language="en",
                            country="Global",
                            published_time=published_time,
                            publisher_id=publisher.publisher_id,
                            status=ArticleStatus.RAW,
                        )
                        db.add(article)
                        stats["new"] += 1

                    await asyncio.sleep(1)  # Polite delay

                await db.commit()

        logger.info(f"Guardian collection: {stats}")
        return stats


async def main():
    logging.basicConfig(level=logging.INFO)
    collector = GuardianCollector()
    await collector.run()


if __name__ == "__main__":
    asyncio.run(main())
