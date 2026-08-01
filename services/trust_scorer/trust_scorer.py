"""
Bharat Vanguard News (BVN) — Trust Scorer
Evaluates articles and events to generate transparency and confidence scores.
"""
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.models import Article, Event, TrustSignal, Publisher

logger = logging.getLogger("trust.scorer")

class TrustScorer:
    def __init__(self):
        pass

    async def score_article(self, db: AsyncSession, article: Article, event: Event = None) -> TrustSignal:
        """
        Generates or updates a TrustSignal for the given article.
        If the article belongs to an Event, the event's data (like article_count) 
        boosts the independent sources and cross-confirmation metrics.
        """
        # Fetch publisher details if not loaded
        publisher = article.publisher
        if not publisher:
            pub_res = await db.execute(select(Publisher).where(Publisher.publisher_id == article.publisher_id))
            publisher = pub_res.scalar_one()

        # Calculate freshness
        now = datetime.now(timezone.utc)
        published_time = article.published_time or article.collected_time
        if published_time:
            # ensure published_time is timezone-aware
            if published_time.tzinfo is None:
                published_time = published_time.replace(tzinfo=timezone.utc)
            delta = now - published_time
            freshness_hours = delta.total_seconds() / 3600.0
        else:
            freshness_hours = 24.0 # default if unknown

        # Check existing trust signal
        existing_res = await db.execute(
            select(TrustSignal).where(TrustSignal.article_id == article.article_id)
        )
        trust_signal = existing_res.scalar_one_or_none()

        if not trust_signal:
            trust_signal = TrustSignal(article_id=article.article_id)
            db.add(trust_signal)

        # Update metrics
        trust_signal.official_source = publisher.is_official
        trust_signal.publisher_reputation = publisher.reputation_score or 0.5
        trust_signal.freshness_hours = max(0.0, freshness_hours)

        # Event-based metrics (Cross-confirmation)
        if event:
            trust_signal.event_id = event.event_id
            trust_signal.independent_sources = event.article_count
            trust_signal.cross_confirmation = event.article_count > 1
        else:
            trust_signal.independent_sources = 1
            trust_signal.cross_confirmation = False

        # Compute the composite score
        trust_signal.compute_confidence()
        
        logger.info(f"Generated trust score {trust_signal.confidence_score:.2f} for article {article.article_id}")
        return trust_signal

# Singleton
_scorer = None

def get_trust_scorer() -> TrustScorer:
    global _scorer
    if _scorer is None:
        _scorer = TrustScorer()
    return _scorer
