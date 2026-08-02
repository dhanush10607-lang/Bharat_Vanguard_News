"""
Bharat Vanguard News (BVN) — Database Seed Script
Populates the publishers table with trusted news sources.
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from shared.database import AsyncSessionLocal
from shared.models import Publisher

PUBLISHERS = [
    {
        "name": "Reuters",
        "slug": "reuters",
        "homepage_url": "https://www.reuters.com",
        "feed_url": "https://www.reutersagency.com/feed/",
        "country": "United States",
        "reputation_score": 0.95,
        "is_active": True,
    },
    {
        "name": "Associated Press",
        "slug": "ap",
        "homepage_url": "https://apnews.com",
        "feed_url": "https://rsshub.app/apnews/topics/world-news",
        "country": "United States",
        "reputation_score": 0.95,
        "is_active": True,
    },
    {
        "name": "BBC News",
        "slug": "bbc",
        "homepage_url": "https://www.bbc.com/news",
        "feed_url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "country": "United Kingdom",
        "reputation_score": 0.90,
        "is_active": True,
    },
    {
        "name": "The Guardian",
        "slug": "the-guardian",
        "homepage_url": "https://www.theguardian.com",
        "feed_url": "https://www.theguardian.com/world/rss",
        "country": "United Kingdom",
        "reputation_score": 0.85,
        "is_active": True,
    },
    {
        "name": "The Hindu",
        "slug": "the-hindu",
        "homepage_url": "https://www.thehindu.com",
        "feed_url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "country": "India",
        "reputation_score": 0.85,
        "is_active": True,
    },
    {
        "name": "NPR",
        "slug": "npr",
        "homepage_url": "https://www.npr.org",
        "feed_url": "https://feeds.npr.org/1001/rss.xml",
        "country": "United States",
        "reputation_score": 0.90,
        "is_active": True,
    },
    {
        "name": "Al Jazeera",
        "slug": "al-jazeera",
        "homepage_url": "https://www.aljazeera.com",
        "feed_url": "https://www.aljazeera.com/xml/rss/all.xml",
        "country": "Qatar",
        "reputation_score": 0.85,
        "is_active": True,
    },
    {
        "name": "The New York Times",
        "slug": "nyt",
        "homepage_url": "https://www.nytimes.com",
        "feed_url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "country": "United States",
        "reputation_score": 0.90,
        "is_active": True,
    },
    {
        "name": "CNN",
        "slug": "cnn",
        "homepage_url": "https://edition.cnn.com",
        "feed_url": "http://rss.cnn.com/rss/edition_world.rss",
        "country": "United States",
        "reputation_score": 0.80,
        "is_active": True,
    },
    {
        "name": "Times of India",
        "slug": "toi",
        "homepage_url": "https://timesofindia.indiatimes.com",
        "feed_url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        "country": "India",
        "reputation_score": 0.80,
        "is_active": True,
    },
    {
        "name": "TechCrunch",
        "slug": "techcrunch",
        "homepage_url": "https://techcrunch.com",
        "feed_url": "https://techcrunch.com/feed/",
        "country": "United States",
        "reputation_score": 0.85,
        "is_active": True,
    },
    {
        "name": "The Verge",
        "slug": "the-verge",
        "homepage_url": "https://www.theverge.com",
        "feed_url": "https://www.theverge.com/rss/index.xml",
        "country": "United States",
        "reputation_score": 0.85,
        "is_active": True,
    }
]

async def seed_publishers():
    async with AsyncSessionLocal() as db:
        for pub_data in PUBLISHERS:
            # Check if exists
            result = await db.execute(
                select(Publisher).where(Publisher.slug == pub_data["slug"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                print(f"Adding publisher: {pub_data['name']}")
                mapped_data = {
                    "name": pub_data["name"],
                    "slug": pub_data["slug"],
                    "website": pub_data.get("homepage_url"),
                    "rss_feeds": [{"url": pub_data["feed_url"], "category": "General"}],
                    "country": pub_data.get("country"),
                    "reputation_score": pub_data.get("reputation_score", 0.5),
                    "active": pub_data.get("is_active", True)
                }
                pub = Publisher(**mapped_data)
                db.add(pub)
            else:
                print(f"Already exists: {pub_data['name']}")
        
        await db.commit()
        print("Done seeding publishers!")

if __name__ == "__main__":
    asyncio.run(seed_publishers())
