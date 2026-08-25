"""
Bharat Vanguard News (BVN) — RSS Collector
Fetches articles from all configured RSS feeds and stores them in PostgreSQL.

Features:
- Async HTTP fetching (httpx)
- SHA256 URL hashing for duplicate detection (no DB hit needed)
- Rate limiting with configurable delays
- Retry logic with exponential backoff
- Structured logging
- Tracks collection runs in DB for health monitoring
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional
import feedparser
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config import settings
from shared.database import AsyncSessionLocal
from shared.models import Article, Publisher, ArticleStatus, CollectionRun
from shared.utils.hashing import hash_url
from shared.utils.date_utils import parse_date, utc_now
from shared.utils.text_utils import clean_text, truncate, remove_html_tags
from services.collector.feed_config import PUBLISHERS, PublisherConfig, FeedSource

logger = logging.getLogger("collector.rss")


class RSSCollector:
    """
    Collects articles from RSS feeds for all configured publishers.
    """

    def __init__(self):
        self.session: Optional[httpx.AsyncClient] = None
        self.stats = {"total": 0, "new": 0, "duplicate": 0, "failed": 0}

    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=settings.parser_timeout_seconds,
            follow_redirects=True,
            headers={
                "User-Agent": "BharatVanguardNews/1.0 (news aggregator)",
            },
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    async def fetch_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse an RSS feed URL with retry logic."""
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            logger.debug(f"Fetched {url}: {len(feed.entries)} entries")
            return feed
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP {e.response.status_code} for {url}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise

    async def get_or_create_publisher(
        self, db: AsyncSession, config: PublisherConfig
    ) -> Publisher:
        """Get existing publisher or create a new one from config."""
        result = await db.execute(
            select(Publisher).where(Publisher.slug == config.slug)
        )
        publisher = result.scalar_one_or_none()

        if not publisher:
            publisher = Publisher(
                name=config.name,
                slug=config.slug,
                website=config.website,
                country=config.country,
                language=config.language,
                is_official=config.is_official,
                reputation_score=config.reputation_score,
                logo_url=config.logo_url,
                rss_feeds=[{"url": f.url, "category": f.category} for f in config.feeds],
            )
            db.add(publisher)
            await db.commit()
            logger.info(f"Created publisher: {config.name}")

        return publisher

    async def article_exists(self, db: AsyncSession, url_hash: str) -> bool:
        """Fast duplicate check using the SHA256 URL hash."""
        result = await db.execute(
            select(Article.article_id).where(Article.url_hash == url_hash).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def parse_entry(self, entry: dict, feed: FeedSource, publisher_id) -> Optional[dict]:
        """
        Extract article data from a feedparser entry.
        Returns None if entry is invalid.
        """
        url = entry.get("link", "").strip()
        if not url:
            return None

        title = entry.get("title", "").strip()
        if not title:
            return None

        # Get description/summary
        description = ""
        if "summary" in entry:
            description = clean_text(remove_html_tags(entry.summary))
        elif "description" in entry:
            description = clean_text(remove_html_tags(entry.description))

        # Clean up Hacker News metadata commonly found in description
        import re
        description = re.sub(r'Article URL:.*', '', description, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up Nature publication metadata (e.g., "Nature, Published online: ... doi: ...")
        description = re.sub(r'Nature, Published online: [^;]+; doi:[^\s]+', '', description, flags=re.IGNORECASE)
        
        description = description.strip()

        # Truncate description to avoid storing huge raw HTML snippets
        description = truncate(description, max_length=500)

        # Content (Full Article text if available in RSS)
        content = ""
        if "content" in entry and entry.content:
            content_val = entry.content[0].get("value", "")
            content = clean_text(remove_html_tags(content_val))
            
        if not content:
            content = description  # Fallback if full content isn't in feed

        # If content is just the description or very short, extract the actual web page!
        if content == description or len(content.split()) < 100:
            try:
                import httpx
                import trafilatura
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(url, follow_redirects=True)
                    if resp.status_code == 200:
                        extracted = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
                        if extracted and len(extracted.split()) > 50:
                            content = extracted
            except Exception as e:
                import logging
                logging.getLogger("collector.rss").debug(f"Failed to extract full text from URL {url}: {e}")

        # Generate content hash for deduplication
        import hashlib
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest() if content else None

        # Parse published date
        published_str = entry.get("published", "") or entry.get("updated", "")
        published_time = parse_date(published_str) or utc_now()

        # Extract image URL (prioritize high-res)
        image_url = None
        
        # 1. Try media_content (sort by width to get largest)
        if "media_content" in entry and entry.media_content:
            try:
                images = sorted(entry.media_content, key=lambda x: int(x.get("width", 0)), reverse=True)
                image_url = images[0].get("url")
            except Exception:
                image_url = entry.media_content[0].get("url")
                
        # 2. Try enclosures
        if not image_url and "links" in entry:
            for link in entry.links:
                if link.get("type", "").startswith("image/") and link.get("href"):
                    image_url = link.href
                    break

        # 3. Extract from raw HTML BEFORE stripping tags
        raw_desc = entry.get("summary", "") or entry.get("description", "")
        if not image_url and raw_desc:
            import re
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_desc, re.IGNORECASE)
            if img_match:
                image_url = img_match.group(1)

        # 4. Fallback to thumbnail
        if not image_url and "media_thumbnail" in entry and entry.media_thumbnail:
            image_url = entry.media_thumbnail[0].get("url")
            
        # 5. Automatically upscale Google/Blogger/Medium thumbnails
        if image_url:
            import re
            # Replaces things like =s150-c or =w200 with =s1200 (high-res) for Google-hosted images
            image_url = re.sub(r'=[swh]\d+(-[a-z]+)*$', '=s1200', image_url)

        # Extract author
        author = entry.get("author", "")

        url_hash = hash_url(url)
        # Use a short hash for the slug to keep URLs clean and unique
        slug = url_hash[:12]

        return {
            "title": title[:1000],
            "slug": slug,
            "description": description,
            "content": content,
            "content_hash": content_hash,
            "is_paywalled": False,
            "url": url[:2000],
            "url_hash": url_hash,
            "image_url": image_url,
            "author": author[:500] if author else None,
            "category": feed.category,
            "country": feed.country,
            "language": feed.language,
            "published_time": published_time,
            "publisher_id": publisher_id,
            "status": ArticleStatus.RAW,
        }

    async def process_feed(
        self, db: AsyncSession, publisher: Publisher, feed: FeedSource, seen_url_hashes: set
    ) -> dict:
        """Process a single RSS feed and store new articles."""
        stats = {"found": 0, "new": 0, "duplicate": 0, "failed": 0}

        parsed_feed = await self.fetch_feed(feed.url)
        if not parsed_feed or not parsed_feed.entries:
            logger.warning(f"Empty or failed feed: {feed.url}")
            return stats

        for entry in parsed_feed.entries[: settings.max_articles_per_run]:
            stats["found"] += 1

            try:
                article_data = await self.parse_entry(entry, feed, publisher.publisher_id)
                if not article_data:
                    stats["failed"] += 1
                    continue

                url_hash = article_data["url_hash"]
                
                # Duplicate check (in memory first, then DB)
                if url_hash in seen_url_hashes or await self.article_exists(db, url_hash):
                    stats["duplicate"] += 1
                    continue

                seen_url_hashes.add(url_hash)

                # Store new article
                article = Article(**article_data)
                db.add(article)
                stats["new"] += 1
                logger.debug(f"New article: {article_data['title'][:60]}")

                # Polite delay
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Failed to process entry: {e}")
                stats["failed"] += 1

        await db.flush()
        return stats

    async def run_all(self) -> dict:
        """
        Run collection for all configured publishers and feeds.
        Returns aggregate stats.
        """
        total_stats = {"total_feeds": 0, "total_found": 0, "total_new": 0, "total_duplicate": 0}
        run_start = utc_now()

        async with AsyncSessionLocal() as db:
            seen_url_hashes = set()
            for pub_config in PUBLISHERS:
                publisher = await self.get_or_create_publisher(db, pub_config)

                for feed in pub_config.feeds:
                    total_stats["total_feeds"] += 1
                    logger.info(f"Processing: {pub_config.name} / {feed.category}")

                    # Record collection run
                    run = CollectionRun(
                        publisher_id=publisher.publisher_id,
                        source_type="rss",
                        started_at=run_start,
                        status="running",
                    )
                    db.add(run)
                    await db.commit()

                    try:
                        stats = await self.process_feed(db, publisher, feed, seen_url_hashes)
                        run.articles_found = str(stats["found"])
                        run.articles_new = str(stats["new"])
                        run.articles_duplicate = str(stats["duplicate"])
                        run.status = "success"
                        run.finished_at = utc_now()
                        await db.commit()

                        total_stats["total_found"] += stats["found"]
                        total_stats["total_new"] += stats["new"]
                        total_stats["total_duplicate"] += stats["duplicate"]

                    except Exception as e:
                        await db.rollback()
                        run = await db.get(CollectionRun, run.run_id)
                        if run:
                            run.status = "FAILED"
                            run.error_message = str(e)
                            run.finished_at = utc_now()
                            await db.commit()
                        logger.error(f"Feed failed: {feed.url} — {e}")

                    # Polite delay between publishers
                    await asyncio.sleep(settings.request_delay_seconds)

            await db.commit()

        logger.info(
            f"Collection complete: {total_stats['total_new']} new articles "
            f"({total_stats['total_duplicate']} duplicates skipped)"
        )
        return total_stats


async def main():
    """Entry point for running the collector standalone."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    )

    # How often to fetch new articles (in seconds)
    POLL_INTERVAL_SECONDS = 10 * 60  # Every 10 minutes

    logger.info(f"Starting Bharat Vanguard News (BVN) RSS Collector (polling every {POLL_INTERVAL_SECONDS // 60} minutes)...")

    while True:
        async with RSSCollector() as collector:
            stats = await collector.run_all()
            logger.info(f"Collection complete. New: {stats['total_new']}, Duplicates skipped: {stats['total_duplicate']}")
        logger.info(f"Sleeping {POLL_INTERVAL_SECONDS // 60} minutes before next collection...")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
