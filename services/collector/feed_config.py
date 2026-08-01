"""
TruthLens AI — RSS Feed Configuration
All 25 verified free RSS feeds, organized by publisher and category.
No API keys required for any of these feeds.

To add a new feed:
1. Add an entry to PUBLISHERS list
2. The RSS collector will automatically pick it up on next run
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FeedSource:
    """Represents a single RSS feed URL from a publisher."""
    publisher_slug: str
    category: str
    url: str
    country: str = "Global"
    language: str = "en"


@dataclass
class PublisherConfig:
    """Configuration for a news publisher."""
    slug: str
    name: str
    website: str
    country: str
    language: str = "en"
    is_official: bool = False
    reputation_score: float = 0.75
    logo_url: str = ""
    feeds: list[FeedSource] = field(default_factory=list)


# ============================================================
#  VERIFIED FREE RSS FEEDS
#  Last verified: 2026-07-31
# ============================================================

PUBLISHERS: list[PublisherConfig] = [

    # --------------------------------------------------------
    # BBC NEWS — Highly reputable, multiple categories
    # --------------------------------------------------------
    PublisherConfig(
        slug="bbc-news",
        name="BBC News",
        website="https://www.bbc.com/news",
        country="UK",
        reputation_score=0.92,
        logo_url="https://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif",
        feeds=[
            FeedSource("bbc-news", "world",       "http://feeds.bbci.co.uk/news/world/rss.xml",        "Global"),
            FeedSource("bbc-news", "technology",   "http://feeds.bbci.co.uk/news/technology/rss.xml",   "Global"),
            FeedSource("bbc-news", "business",     "http://feeds.bbci.co.uk/news/business/rss.xml",     "Global"),
            FeedSource("bbc-news", "science",      "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "Global"),
            FeedSource("bbc-news", "health",       "http://feeds.bbci.co.uk/news/health/rss.xml",       "Global"),
            FeedSource("bbc-news", "entertainment","http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "Global"),
        ],
    ),

    # --------------------------------------------------------
    # AL JAZEERA — Strong international coverage
    # --------------------------------------------------------
    PublisherConfig(
        slug="al-jazeera",
        name="Al Jazeera",
        website="https://www.aljazeera.com",
        country="Qatar",
        reputation_score=0.80,
        feeds=[
            FeedSource("al-jazeera", "world", "https://www.aljazeera.com/xml/rss/all.xml", "Global"),
        ],
    ),

    # --------------------------------------------------------
    # TECHCRUNCH — Best tech startup coverage
    # --------------------------------------------------------
    PublisherConfig(
        slug="techcrunch",
        name="TechCrunch",
        website="https://techcrunch.com",
        country="US",
        reputation_score=0.82,
        feeds=[
            FeedSource("techcrunch", "technology", "https://techcrunch.com/feed/", "US"),
            FeedSource("techcrunch", "ai",         "https://techcrunch.com/category/artificial-intelligence/feed/", "US"),
            FeedSource("techcrunch", "startups",   "https://techcrunch.com/category/startups/feed/", "US"),
        ],
    ),

    # --------------------------------------------------------
    # ARS TECHNICA — Deep technical analysis
    # --------------------------------------------------------
    PublisherConfig(
        slug="ars-technica",
        name="Ars Technica",
        website="https://arstechnica.com",
        country="US",
        reputation_score=0.85,
        feeds=[
            FeedSource("ars-technica", "technology", "https://feeds.arstechnica.com/arstechnica/index", "US"),
        ],
    ),

    # --------------------------------------------------------
    # THE VERGE — Tech consumer coverage
    # --------------------------------------------------------
    PublisherConfig(
        slug="the-verge",
        name="The Verge",
        website="https://www.theverge.com",
        country="US",
        reputation_score=0.80,
        feeds=[
            FeedSource("the-verge", "technology", "https://www.theverge.com/rss/index.xml", "US"),
            FeedSource("the-verge", "ai",         "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "US"),
        ],
    ),

    # --------------------------------------------------------
    # MIT TECHNOLOGY REVIEW — Research-grade AI/Tech
    # --------------------------------------------------------
    PublisherConfig(
        slug="mit-tech-review",
        name="MIT Technology Review",
        website="https://www.technologyreview.com",
        country="US",
        reputation_score=0.90,
        feeds=[
            FeedSource("mit-tech-review", "ai",         "https://www.technologyreview.com/feed/", "US"),
            FeedSource("mit-tech-review", "technology", "https://www.technologyreview.com/feed/", "US"),
        ],
    ),

    # --------------------------------------------------------
    # WIRED — Tech culture and policy
    # --------------------------------------------------------
    PublisherConfig(
        slug="wired",
        name="Wired",
        website="https://www.wired.com",
        country="US",
        reputation_score=0.82,
        feeds=[
            FeedSource("wired", "technology", "https://www.wired.com/feed/rss", "US"),
        ],
    ),

    # --------------------------------------------------------
    # THE HINDU — India's leading newspaper
    # --------------------------------------------------------
    PublisherConfig(
        slug="the-hindu",
        name="The Hindu",
        website="https://www.thehindu.com",
        country="India",
        reputation_score=0.88,
        feeds=[
            FeedSource("the-hindu", "india",   "https://www.thehindu.com/news/national/feeder/default.rss",       "India"),
            FeedSource("the-hindu", "world",   "https://www.thehindu.com/news/international/feeder/default.rss",  "India"),
            FeedSource("the-hindu", "business","https://www.thehindu.com/business/feeder/default.rss",            "India"),
            FeedSource("the-hindu", "science", "https://www.thehindu.com/sci-tech/science/feeder/default.rss",    "India"),
        ],
    ),

    # --------------------------------------------------------
    # NDTV — Major Indian news network
    # --------------------------------------------------------
    PublisherConfig(
        slug="ndtv",
        name="NDTV",
        website="https://www.ndtv.com",
        country="India",
        reputation_score=0.78,
        feeds=[
            FeedSource("ndtv", "india", "https://feeds.feedburner.com/ndtvnews-top-stories", "India"),
        ],
    ),

    # --------------------------------------------------------
    # HINDUSTAN TIMES — Leading Indian daily
    # --------------------------------------------------------
    PublisherConfig(
        slug="hindustan-times",
        name="Hindustan Times",
        website="https://www.hindustantimes.com",
        country="India",
        reputation_score=0.78,
        feeds=[
            FeedSource("hindustan-times", "india", "https://www.hindustantimes.com/rss/topnews/rssfeed.xml", "India"),
        ],
    ),

    # --------------------------------------------------------
    # NASA — Official government science source
    # --------------------------------------------------------
    PublisherConfig(
        slug="nasa",
        name="NASA",
        website="https://www.nasa.gov",
        country="US",
        is_official=True,
        reputation_score=0.98,
        feeds=[
            FeedSource("nasa", "science", "https://www.nasa.gov/rss/dyn/breaking_news.rss", "US"),
        ],
    ),

    # --------------------------------------------------------
    # WHO — Official global health authority
    # --------------------------------------------------------
    PublisherConfig(
        slug="who",
        name="World Health Organization",
        website="https://www.who.int",
        country="Global",
        is_official=True,
        reputation_score=0.97,
        feeds=[
            FeedSource("who", "health", "https://www.who.int/rss-feeds/news-releases.xml", "Global"),
        ],
    ),

    # --------------------------------------------------------
    # SCIENCE DAILY — Aggregated science research
    # --------------------------------------------------------
    PublisherConfig(
        slug="science-daily",
        name="ScienceDaily",
        website="https://www.sciencedaily.com",
        country="US",
        reputation_score=0.83,
        feeds=[
            FeedSource("science-daily", "science", "https://www.sciencedaily.com/rss/all.xml", "Global"),
        ],
    ),

    # --------------------------------------------------------
    # NATURE — Premier scientific journal
    # --------------------------------------------------------
    PublisherConfig(
        slug="nature",
        name="Nature",
        website="https://www.nature.com",
        country="UK",
        reputation_score=0.97,
        feeds=[
            FeedSource("nature", "science", "https://www.nature.com/nature.rss", "Global"),
        ],
    ),

    # --------------------------------------------------------
    # HACKER NEWS — Tech community frontpage
    # --------------------------------------------------------
    PublisherConfig(
        slug="hacker-news",
        name="Hacker News",
        website="https://news.ycombinator.com",
        country="US",
        reputation_score=0.72,
        feeds=[
            FeedSource("hacker-news", "technology", "https://hnrss.org/frontpage", "US"),
        ],
    ),

    # --------------------------------------------------------
    # REUTERS — via Google News (no official public RSS)
    # --------------------------------------------------------
    PublisherConfig(
        slug="reuters",
        name="Reuters",
        website="https://www.reuters.com",
        country="Global",
        reputation_score=0.93,
        feeds=[
            FeedSource("reuters", "world",    "https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en", "Global"),
            FeedSource("reuters", "business", "https://news.google.com/rss/search?q=site:reuters.com+business&hl=en-US&gl=US&ceid=US:en", "Global"),
        ],
    ),

    # --------------------------------------------------------
    # AP NEWS — via Google News
    # --------------------------------------------------------
    PublisherConfig(
        slug="ap-news",
        name="AP News",
        website="https://apnews.com",
        country="US",
        reputation_score=0.92,
        feeds=[
            FeedSource("ap-news", "world", "https://news.google.com/rss/search?q=site:apnews.com&hl=en-US&gl=US&ceid=US:en", "Global"),
        ],
    ),

]

# ============================================================
#  TOPIC CATEGORIES (for classification)
# ============================================================
CATEGORIES = [
    "world",
    "technology",
    "ai",
    "business",
    "finance",
    "science",
    "health",
    "sports",
    "entertainment",
    "politics",
    "environment",
    "india",
    "startups",
    "education",
]

# ============================================================
#  TARGET COUNTRIES (for geographic tagging)
# ============================================================
COUNTRIES = [
    "Global",
    "India",
    "United States",
    "United Kingdom",
    "China",
    "Russia",
    "Germany",
    "France",
    "Japan",
    "Australia",
    "Canada",
    "Brazil",
    "Pakistan",
    "Bangladesh",
    "Sri Lanka",
]

# Build lookup dicts for fast access
PUBLISHER_BY_SLUG: dict[str, PublisherConfig] = {p.slug: p for p in PUBLISHERS}
ALL_FEEDS: list[FeedSource] = [f for p in PUBLISHERS for f in p.feeds]
