"""
Bharat Vanguard News (BVN) — Articles Router
Provides paginated, filtered article listing and single article retrieval.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from pydantic import BaseModel
from datetime import datetime

from shared.database import get_db
from shared.models import Article, Publisher, AISummary, TrustSignal, ArticleStatus

router = APIRouter()


# ============================================================
#  RESPONSE SCHEMAS
# ============================================================

class PublisherBrief(BaseModel):
    publisher_id: UUID
    name: str
    slug: str
    country: Optional[str]
    logo_url: Optional[str]
    reputation_score: Optional[float]

    class Config:
        from_attributes = True


class ArticleListItem(BaseModel):
    article_id: UUID
    title: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    category: Optional[str]
    country: Optional[str]
    language: Optional[str]
    published_time: Optional[datetime]
    collected_time: Optional[datetime]
    reading_time_min: Optional[int]
    word_count: Optional[int]
    publisher: Optional[PublisherBrief]
    confidence_score: Optional[float] = None
    likes_count: int = 0

    class Config:
        from_attributes = True


class ArticleDetail(ArticleListItem):
    content: Optional[str]
    author: Optional[str]
    url: str
    sentiment: Optional[str]
    summary_short: Optional[str] = None
    summary_medium: Optional[str] = None
    summary_bullets: Optional[list] = None
    keywords: Optional[list] = None


class PaginatedArticles(BaseModel):
    items: list[ArticleListItem]
    total: int
    page: int
    page_size: int
    has_next: bool


# ============================================================
#  ENDPOINTS
# ============================================================

@router.get("/", response_model=PaginatedArticles)
async def list_articles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    country: Optional[str] = Query(None, description="Filter by country"),
    language: Optional[str] = Query(None, description="Filter by language code"),
    publisher_slug: Optional[str] = Query(None, description="Filter by publisher slug"),
    status: Optional[str] = Query("published", description="Article status filter"),
    sort_by: str = Query("published_time", description="Sort by 'published_time' or 'likes'"),
    db: AsyncSession = Depends(get_db),
):
    """
    List articles with optional filters.
    Returns paginated results ordered by published_time DESC.
    """
    # Build filters
    filters = []

    if status:
        try:
            filters.append(Article.status == ArticleStatus(status))
        except ValueError:
            pass

    if category:
        filters.append(Article.category == category.lower())

    if country:
        filters.append(Article.country.ilike(f"%{country}%"))

    if language:
        filters.append(Article.language == language.lower())

    if publisher_slug:
        publisher_result = await db.execute(
            select(Publisher).where(Publisher.slug == publisher_slug)
        )
        publisher = publisher_result.scalar_one_or_none()
        if publisher:
            filters.append(Article.publisher_id == publisher.publisher_id)

    # Count total
    count_query = select(func.count()).select_from(Article)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    offset = (page - 1) * page_size
    query = (
        select(Article, Publisher)
        .join(Publisher, Article.publisher_id == Publisher.publisher_id)
        .offset(offset)
        .limit(page_size)
    )
    
    if sort_by == "likes":
        query = query.order_by(Article.likes_count.desc().nulls_last(), desc(Article.published_time))
    else:
        query = query.order_by(desc(Article.published_time))
    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    rows = result.all()

    items = []
    for article, publisher in rows:
        item = ArticleListItem(
            article_id=article.article_id,
            title=article.title,
            slug=article.slug,
            description=article.description,
            image_url=article.image_url,
            category=article.category,
            country=article.country,
            language=article.language,
            published_time=article.published_time,
            collected_time=article.collected_time,
            reading_time_min=article.reading_time_min,
            word_count=article.word_count,
            publisher=PublisherBrief(
                publisher_id=publisher.publisher_id,
                name=publisher.name,
                slug=publisher.slug,
                country=publisher.country,
                logo_url=publisher.logo_url,
                reputation_score=publisher.reputation_score,
            ),
            likes_count=article.likes_count or 0
        )
        items.append(item)

    return PaginatedArticles(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )


@router.get("/{slug}", response_model=ArticleDetail)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Get a single article by slug with full content, AI summary, and trust signals.
    """
    result = await db.execute(
        select(Article, Publisher)
        .join(Publisher, Article.publisher_id == Publisher.publisher_id)
        .where(Article.slug == slug)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Article not found")

    article, publisher = row

    # Load AI summary (if available)
    summary_result = await db.execute(
        select(AISummary).where(AISummary.article_id == article.article_id)
    )
    ai_summary = summary_result.scalar_one_or_none()

    # Load trust signal
    trust_result = await db.execute(
        select(TrustSignal).where(TrustSignal.article_id == article.article_id)
    )
    trust = trust_result.scalar_one_or_none()

    return ArticleDetail(
        article_id=article.article_id,
        title=article.title,
        slug=article.slug,
        description=article.description,
        content=article.content,
        image_url=article.image_url,
        author=article.author,
        category=article.category,
        country=article.country,
        language=article.language,
        published_time=article.published_time,
        collected_time=article.collected_time,
        reading_time_min=article.reading_time_min,
        word_count=article.word_count,
        url=article.url,
        sentiment=article.sentiment if article.sentiment else None,
        publisher=PublisherBrief(
            publisher_id=publisher.publisher_id,
            name=publisher.name,
            slug=publisher.slug,
            country=publisher.country,
            logo_url=publisher.logo_url,
            reputation_score=publisher.reputation_score,
        ),
        confidence_score=trust.confidence_score if trust else None,
        summary_short=ai_summary.summary_short if ai_summary else None,
        summary_medium=ai_summary.summary_medium if ai_summary else None,
        summary_bullets=ai_summary.summary_bullets if ai_summary else None,
        keywords=ai_summary.keywords if ai_summary else None,
    )


@router.get("/latest/breaking", response_model=list[ArticleListItem])
async def get_breaking_news(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest breaking news articles (most recently published)."""
    result = await db.execute(
        select(Article, Publisher)
        .join(Publisher)
        .where(Article.status == ArticleStatus.PUBLISHED)
        .order_by(desc(Article.published_time))
        .limit(limit)
    )
    rows = result.all()

    return [
        ArticleListItem(
            article_id=a.article_id,
            title=a.title,
            slug=a.slug,
            description=a.description,
            image_url=a.image_url,
            category=a.category,
            country=a.country,
            language=a.language,
            published_time=a.published_time,
            collected_time=a.collected_time,
            reading_time_min=a.reading_time_min,
            word_count=a.word_count,
            publisher=PublisherBrief(
                publisher_id=p.publisher_id,
                name=p.name,
                slug=p.slug,
                country=p.country,
                logo_url=p.logo_url,
                reputation_score=p.reputation_score,
            ),
        )
        for a, p in rows
    ]
