"""
Bharat Vanguard News (BVN) — Analytics Router (Full)
Returns pre-aggregated analytics data for dashboards, trending topics,
entity spotlight, volume charts, and sentiment breakdowns.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

from shared.database import get_db
from shared.models import Article, Entity, ArticleEntity, Publisher, ArticleStatus, Event
from fastapi_cache.decorator import cache

router = APIRouter()


# ============================================================
#  RESPONSE SCHEMAS
# ============================================================

class TrendingEntity(BaseModel):
    entity_id: str
    name: str
    type: str
    mention_count: int
    country: Optional[str] = None


class CategoryStat(BaseModel):
    category: str
    article_count: int
    percentage: float


class PublisherStat(BaseModel):
    publisher_name: str
    publisher_slug: str
    article_count: int
    country: Optional[str] = None
    reputation_score: Optional[float] = None
    logo_url: Optional[str] = None


class SentimentStat(BaseModel):
    sentiment: str
    count: int
    percentage: float


class VolumePoint(BaseModel):
    date: str          # ISO date "YYYY-MM-DD"
    count: int


class AnalyticsSummary(BaseModel):
    total_articles: int
    total_publishers: int
    total_events: int
    articles_today: int
    articles_this_week: int
    top_categories: list[CategoryStat]
    top_publishers: list[PublisherStat]
    trending_entities: list[TrendingEntity]
    sentiment_breakdown: list[SentimentStat]


# ============================================================
#  ENDPOINTS
# ============================================================

@router.get("/summary", response_model=AnalyticsSummary)
@cache(expire=300)
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """Get platform-wide analytics summary for the dashboard."""
    now = datetime.now(timezone.utc)
    today = now - timedelta(hours=24)
    this_week = now - timedelta(days=7)

    # ── Total counts ──
    total_result = await db.execute(
        select(func.count()).select_from(Article)
        .where(Article.status == ArticleStatus.PUBLISHED)
    )
    total_articles = total_result.scalar() or 0

    total_pub_result = await db.execute(
        select(func.count()).select_from(Publisher).where(Publisher.active.isnot(False))
    )
    total_publishers = total_pub_result.scalar() or 0

    total_event_result = await db.execute(select(func.count()).select_from(Event))
    total_events = total_event_result.scalar() or 0

    # ── Volume ──
    today_result = await db.execute(
        select(func.count()).select_from(Article)
        .where(Article.collected_time >= today)
    )
    articles_today = today_result.scalar() or 0

    week_result = await db.execute(
        select(func.count()).select_from(Article)
        .where(Article.collected_time >= this_week)
    )
    articles_this_week = week_result.scalar() or 0

    # ── Top categories ──
    cat_result = await db.execute(
        select(Article.category, func.count().label("cnt"))
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            Article.category.isnot(None),
        )
        .group_by(Article.category)
        .order_by(desc("cnt"))
        .limit(10)
    )
    cat_rows = cat_result.all()
    cat_total = sum(r.cnt for r in cat_rows) or 1
    top_categories = [
        CategoryStat(
            category=r.category,
            article_count=r.cnt,
            percentage=round((r.cnt / cat_total) * 100, 1),
        )
        for r in cat_rows
    ]

    # ── Top publishers ──
    pub_result = await db.execute(
        select(
            Publisher.name,
            Publisher.slug,
            Publisher.country,
            Publisher.reputation_score,
            Publisher.logo_url,
            func.count(Article.article_id).label("cnt"),
        )
        .join(Article, Article.publisher_id == Publisher.publisher_id)
        .where(Article.status == ArticleStatus.PUBLISHED)
        .group_by(Publisher.publisher_id)
        .order_by(desc("cnt"))
        .limit(10)
    )
    pub_rows = pub_result.all()
    top_publishers = [
        PublisherStat(
            publisher_name=r.name,
            publisher_slug=r.slug,
            article_count=r.cnt,
            country=r.country,
            reputation_score=r.reputation_score,
            logo_url=r.logo_url,
        )
        for r in pub_rows
    ]

    # ── Trending entities (most mentioned in last 7 days) ──
    ent_result = await db.execute(
        select(
            Entity.entity_id,
            Entity.name,
            Entity.type,
            Entity.country,
            func.sum(ArticleEntity.mention_count).label("mentions"),
        )
        .join(ArticleEntity, ArticleEntity.entity_id == Entity.entity_id)
        .join(Article, Article.article_id == ArticleEntity.article_id)
        .where(
            Article.published_time >= this_week,
            Article.status == ArticleStatus.PUBLISHED,
        )
        .group_by(Entity.entity_id)
        .order_by(desc("mentions"))
        .limit(15)
    )
    ent_rows = ent_result.all()
    trending_entities = [
        TrendingEntity(
            entity_id=str(r.entity_id),
            name=r.name,
            type=r.type,
            mention_count=int(r.mentions or 0),
            country=r.country,
        )
        for r in ent_rows
    ]

    # ── Sentiment breakdown ──
    sent_result = await db.execute(
        select(Article.sentiment, func.count().label("cnt"))
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            Article.sentiment.isnot(None),
        )
        .group_by(Article.sentiment)
        .order_by(desc("cnt"))
    )
    sent_rows = sent_result.all()
    sent_total = sum(r.cnt for r in sent_rows) or 1
    sentiment_breakdown = [
        SentimentStat(
            sentiment=r.sentiment.value if hasattr(r.sentiment, "value") else str(r.sentiment),
            count=r.cnt,
            percentage=round((r.cnt / sent_total) * 100, 1),
        )
        for r in sent_rows
    ]

    return AnalyticsSummary(
        total_articles=total_articles,
        total_publishers=total_publishers,
        total_events=total_events,
        articles_today=articles_today,
        articles_this_week=articles_this_week,
        top_categories=top_categories,
        top_publishers=top_publishers,
        trending_entities=trending_entities,
        sentiment_breakdown=sentiment_breakdown,
    )


@router.get("/categories", response_model=list[CategoryStat])
@cache(expire=300)
async def get_category_stats(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Article counts by category over the specified number of days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(Article.category, func.count().label("cnt"))
        .where(
            Article.published_time >= since,
            Article.category.isnot(None),
            Article.status == ArticleStatus.PUBLISHED,
        )
        .group_by(Article.category)
        .order_by(desc("cnt"))
    )
    rows = result.all()
    total = sum(r.cnt for r in rows) or 1
    return [
        CategoryStat(category=r.category, article_count=r.cnt, percentage=round(r.cnt / total * 100, 1))
        for r in rows
    ]


@router.get("/countries")
@cache(expire=300)
async def get_country_stats(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Article counts by country over the specified number of days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(Article.country, func.count().label("count"))
        .where(
            Article.published_time >= since,
            Article.country.isnot(None),
            Article.country != "Global",
            Article.status == ArticleStatus.PUBLISHED,
        )
        .group_by(Article.country)
        .order_by(desc("count"))
        .limit(30)
    )
    rows = result.all()
    return [{"country": r.country, "count": r.count} for r in rows]


@router.get("/volume", response_model=list[VolumePoint])
@cache(expire=300)
async def get_article_volume(
    days: int = Query(30, ge=1, le=90),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Daily article volume over the last N days.
    Returns a time-series list suitable for charting.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    filters = [
        Article.published_time >= since,
        Article.status == ArticleStatus.PUBLISHED,
    ]
    if category:
        filters.append(Article.category == category.lower())

    result = await db.execute(
        select(
            func.date_trunc("day", Article.published_time).label("day"),
            func.count().label("count"),
        )
        .where(and_(*filters))
        .group_by("day")
        .order_by("day")
    )
    rows = result.all()
    return [
        VolumePoint(date=r.day.strftime("%Y-%m-%d"), count=r.count)
        for r in rows
        if r.day
    ]


@router.get("/sentiment", response_model=list[SentimentStat])
@cache(expire=300)
async def get_sentiment_breakdown(
    days: int = Query(7, ge=1, le=30),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Sentiment breakdown over the last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    filters = [
        Article.published_time >= since,
        Article.status == ArticleStatus.PUBLISHED,
        Article.sentiment.isnot(None),
    ]
    if category:
        filters.append(Article.category == category.lower())

    result = await db.execute(
        select(Article.sentiment, func.count().label("cnt"))
        .where(and_(*filters))
        .group_by(Article.sentiment)
        .order_by(desc("cnt"))
    )
    rows = result.all()
    total = sum(r.cnt for r in rows) or 1
    return [
        SentimentStat(
            sentiment=r.sentiment.value if hasattr(r.sentiment, "value") else str(r.sentiment),
            count=r.cnt,
            percentage=round(r.cnt / total * 100, 1),
        )
        for r in rows
    ]


@router.get("/trending-entities", response_model=list[TrendingEntity])
@cache(expire=300)
async def get_trending_entities(
    days: int = Query(7, ge=1, le=30),
    entity_type: Optional[str] = Query(None, description="Filter: person, organization, location"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Entities (people, orgs, places) most mentioned in the last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    filters = [
        Article.published_time >= since,
        Article.status == ArticleStatus.PUBLISHED,
    ]

    query = (
        select(
            Entity.entity_id,
            Entity.name,
            Entity.type,
            Entity.country,
            func.sum(ArticleEntity.mention_count).label("mentions"),
        )
        .join(ArticleEntity, ArticleEntity.entity_id == Entity.entity_id)
        .join(Article, Article.article_id == ArticleEntity.article_id)
        .where(and_(*filters))
        .group_by(Entity.entity_id)
        .order_by(desc("mentions"))
        .limit(limit)
    )

    if entity_type:
        query = query.where(Entity.type == entity_type)

    result = await db.execute(query)
    rows = result.all()
    return [
        TrendingEntity(
            entity_id=str(r.entity_id),
            name=r.name,
            type=r.type,
            mention_count=int(r.mentions or 0),
            country=r.country,
        )
        for r in rows
    ]
