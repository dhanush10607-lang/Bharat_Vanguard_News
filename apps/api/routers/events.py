"""
Bharat Vanguard News (BVN) — Events Router (Full Implementation)
Provides endpoints for Event groups (multi-source story clusters).
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from pydantic import BaseModel
from datetime import datetime

from shared.database import get_db
from shared.models import Event, EventArticle, Article, Publisher, TrustSignal

router = APIRouter()


# ============================================================
#  RESPONSE SCHEMAS
# ============================================================

class PublisherBrief(BaseModel):
    publisher_id: UUID
    name: str
    slug: str
    country: Optional[str] = None
    logo_url: Optional[str] = None
    reputation_score: Optional[float] = None
    class Config:
        from_attributes = True


class ArticleInEvent(BaseModel):
    article_id: UUID
    title: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    published_time: Optional[datetime] = None
    reading_time_min: Optional[int] = None
    sentiment: Optional[str] = None
    similarity_score: float = 1.0
    is_primary: bool = False
    publisher: Optional[PublisherBrief] = None
    confidence_score: Optional[float] = None
    class Config:
        from_attributes = True


class EventListItem(BaseModel):
    event_id: UUID
    title: str
    slug: str
    summary_short: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    article_count: int
    confidence_score: Optional[float] = None
    sentiment: Optional[str] = None
    breaking: bool = False
    trending: bool = False
    first_seen: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    class Config:
        from_attributes = True


class EventDetail(EventListItem):
    summary_medium: Optional[str] = None
    summary_bullets: Optional[list] = None
    keywords: Optional[list] = None
    importance_score: Optional[float] = None
    articles: list[ArticleInEvent] = []


class PaginatedEvents(BaseModel):
    items: list[EventListItem]
    total: int
    page: int
    page_size: int
    has_next: bool


# ============================================================
#  HELPERS
# ============================================================

def _event_to_item(e: Event) -> EventListItem:
    return EventListItem(
        event_id=e.event_id,
        title=e.title,
        slug=e.slug,
        summary_short=e.summary_short,
        category=e.category,
        country=e.country,
        article_count=e.article_count,
        confidence_score=e.confidence_score,
        sentiment=e.sentiment.value if e.sentiment else None,
        breaking=e.breaking,
        trending=e.trending,
        first_seen=e.first_seen,
        last_updated=e.last_updated,
    )


# ============================================================
#  ENDPOINTS
# ============================================================

@router.get("/", response_model=PaginatedEvents)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    breaking: Optional[bool] = Query(None),
    trending: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List events (grouped stories), newest first."""
    filters = []
    if category:
        filters.append(Event.category == category.lower())
    if country:
        filters.append(Event.country.ilike(f"%{country}%"))
    if breaking is not None:
        filters.append(Event.breaking == breaking)
    if trending is not None:
        filters.append(Event.trending == trending)

    # Total count
    count_q = select(func.count()).select_from(Event)
    if filters:
        count_q = count_q.where(and_(*filters))
    total_res = await db.execute(count_q)
    total = total_res.scalar() or 0

    # Fetch page
    query = (
        select(Event)
        .order_by(desc(Event.last_updated))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    events = result.scalars().all()

    return PaginatedEvents(
        items=[_event_to_item(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(((page - 1) * page_size) + page_size) < total,
    )


@router.get("/trending", response_model=list[EventListItem])
async def get_trending_events(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get top trending events (most articles + recent)."""
    result = await db.execute(
        select(Event)
        .order_by(desc(Event.article_count), desc(Event.last_updated))
        .limit(limit)
    )
    events = result.scalars().all()
    return [_event_to_item(e) for e in events]


@router.get("/breaking", response_model=list[EventListItem])
async def get_breaking_events(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Get breaking events (flagged as breaking or most recent with 2+ sources)."""
    result = await db.execute(
        select(Event)
        .where(Event.article_count >= 2)
        .order_by(desc(Event.first_seen))
        .limit(limit)
    )
    events = result.scalars().all()
    return [_event_to_item(e) for e in events]


@router.get("/{slug}", response_model=EventDetail)
async def get_event(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Get a full Event with all linked articles from different publishers.
    """
    event_res = await db.execute(select(Event).where(Event.slug == slug))
    event = event_res.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Fetch linked articles with publisher info + trust signals
    links_res = await db.execute(
        select(EventArticle, Article, Publisher, TrustSignal)
        .join(Article, Article.article_id == EventArticle.article_id)
        .join(Publisher, Publisher.publisher_id == Article.publisher_id)
        .outerjoin(TrustSignal, TrustSignal.article_id == Article.article_id)
        .where(EventArticle.event_id == event.event_id)
        .order_by(desc(EventArticle.is_primary), desc(Article.published_time))
    )
    link_rows = links_res.all()

    articles = [
        ArticleInEvent(
            article_id=a.article_id,
            title=a.title,
            slug=a.slug,
            description=a.description,
            image_url=a.image_url,
            published_time=a.published_time,
            reading_time_min=a.reading_time_min,
            sentiment=a.sentiment.value if a.sentiment else None,
            similarity_score=ea.similarity_score,
            is_primary=ea.is_primary,
            confidence_score=ts.confidence_score if ts else None,
            publisher=PublisherBrief(
                publisher_id=p.publisher_id,
                name=p.name,
                slug=p.slug,
                country=p.country,
                logo_url=p.logo_url,
                reputation_score=p.reputation_score,
            ),
        )
        for ea, a, p, ts in link_rows
    ]

    return EventDetail(
        event_id=event.event_id,
        title=event.title,
        slug=event.slug,
        summary_short=event.summary_short,
        summary_medium=event.summary_medium,
        summary_bullets=event.summary_bullets,
        keywords=event.keywords,
        category=event.category,
        country=event.country,
        article_count=event.article_count,
        confidence_score=event.confidence_score,
        importance_score=event.importance_score,
        sentiment=event.sentiment.value if event.sentiment else None,
        breaking=event.breaking,
        trending=event.trending,
        first_seen=event.first_seen,
        last_updated=event.last_updated,
        articles=articles,
    )
