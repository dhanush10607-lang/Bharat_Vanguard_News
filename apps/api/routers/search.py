"""
TruthLens AI — Search Router (Upgraded)
Dual-mode search:
  1. Semantic search via pgvector cosine similarity (requires embeddings from NLP worker)
  2. Full-text fallback using PostgreSQL ts_vector for freshly collected articles

Both modes are merged and re-ranked by a hybrid score.
No Elasticsearch needed — pgvector on Supabase handles it for free.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, and_
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from shared.database import get_db
from shared.models import Article, Publisher, ArticleEmbedding, TrustSignal, ArticleStatus

router = APIRouter()


class PublisherBrief(BaseModel):
    publisher_id: UUID
    name: str
    slug: str
    country: Optional[str] = None
    logo_url: Optional[str] = None
    reputation_score: Optional[float] = None
    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    article_id: UUID
    title: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    published_time: Optional[datetime] = None
    reading_time_min: Optional[int] = None
    word_count: Optional[int] = None
    sentiment: Optional[str] = None
    confidence_score: Optional[float] = None
    publisher: Optional[PublisherBrief] = None
    relevance_score: Optional[float] = None
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int
    page: int
    page_size: int
    has_next: bool
    search_mode: str   # "semantic" | "fulltext" | "hybrid"


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    semantic: bool = Query(True, description="Enable semantic (vector) search"),
    db: AsyncSession = Depends(get_db),
):
    """
    Hybrid search: semantic vector similarity + PostgreSQL full-text.
    Falls back gracefully to full-text only if embeddings are unavailable.
    """
    offset = (page - 1) * page_size
    search_mode = "fulltext"

    # ── Attempt semantic search ──────────────────────────────────
    semantic_article_ids: list[UUID] = []
    semantic_scores: dict[UUID, float] = {}

    if semantic:
        try:
            from services.nlp.embedder import get_embedder
            embedder = get_embedder()
            query_vector = embedder.generate_embedding(q)

            # Find nearest articles via pgvector cosine distance
            vec_query = (
                select(
                    ArticleEmbedding.article_id,
                    ArticleEmbedding.vector.cosine_distance(query_vector).label("distance"),
                )
                .where(ArticleEmbedding.vector.cosine_distance(query_vector) < 0.5)
                .order_by("distance")
                .limit(100)  # broad pool then re-rank
            )
            vec_result = await db.execute(vec_query)
            vec_rows = vec_result.all()

            for row in vec_rows:
                sim = 1.0 - float(row.distance)
                semantic_article_ids.append(row.article_id)
                semantic_scores[row.article_id] = sim

            if semantic_article_ids:
                search_mode = "hybrid"

        except Exception:
            pass  # Embedder not loaded yet — fall through to full-text

    # ── Full-text conditions ──────────────────────────────────────
    ft_conditions = [
        Article.status == ArticleStatus.PUBLISHED,
        or_(
            func.to_tsvector("english", Article.title).op("@@")(
                func.plainto_tsquery("english", q)
            ),
            Article.title.ilike(f"%{q}%"),
            Article.description.ilike(f"%{q}%"),
        ),
    ]

    if category:
        ft_conditions.append(Article.category == category.lower())
    if country:
        ft_conditions.append(Article.country.ilike(f"%{country}%"))
    if language:
        ft_conditions.append(Article.language == language.lower())

    # ── Merge pools ───────────────────────────────────────────────
    if semantic_article_ids:
        # Widen conditions to also accept semantic hits
        merged_conditions = [
            Article.status == ArticleStatus.PUBLISHED,
            or_(
                Article.article_id.in_(semantic_article_ids),
                and_(*ft_conditions[1:]),   # full-text match (skip status which is already in outer)
            ),
        ]
        if category:
            merged_conditions.append(Article.category == category.lower())
        if country:
            merged_conditions.append(Article.country.ilike(f"%{country}%"))
        if language:
            merged_conditions.append(Article.language == language.lower())
        conditions = merged_conditions
    else:
        conditions = ft_conditions

    # ── Count ─────────────────────────────────────────────────────
    count_result = await db.execute(
        select(func.count()).select_from(Article).where(and_(*conditions))
    )
    total = count_result.scalar() or 0

    # ── Ranked query ──────────────────────────────────────────────
    rank_expr = func.ts_rank(
        func.to_tsvector("english", Article.title + " " + func.coalesce(Article.description, "")),
        func.plainto_tsquery("english", q),
    ).label("ft_rank")

    query = (
        select(Article, Publisher, TrustSignal, rank_expr)
        .join(Publisher, Article.publisher_id == Publisher.publisher_id)
        .outerjoin(TrustSignal, TrustSignal.article_id == Article.article_id)
        .where(and_(*conditions))
        .order_by(desc(Article.published_time))
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    rows = result.all()

    results = []
    for article, publisher, trust, ft_rank in rows:
        # Hybrid score: 60% semantic (if available) + 40% full-text rank
        sem_score = semantic_scores.get(article.article_id, 0.0)
        ft_score = float(ft_rank) if ft_rank else 0.0
        hybrid_score = (0.6 * sem_score + 0.4 * ft_score) if sem_score else ft_score

        results.append(SearchResult(
            article_id=article.article_id,
            title=article.title,
            slug=article.slug,
            description=article.description,
            image_url=article.image_url,
            category=article.category,
            country=article.country,
            language=article.language,
            published_time=article.published_time,
            reading_time_min=article.reading_time_min,
            word_count=article.word_count,
            sentiment=article.sentiment.value if article.sentiment else None,
            confidence_score=trust.confidence_score if trust else None,
            publisher=PublisherBrief(
                publisher_id=publisher.publisher_id,
                name=publisher.name,
                slug=publisher.slug,
                country=publisher.country,
                logo_url=publisher.logo_url,
                reputation_score=publisher.reputation_score,
            ),
            relevance_score=round(hybrid_score, 4),
        ))

    # Re-sort by hybrid score descending
    results.sort(key=lambda r: r.relevance_score or 0, reverse=True)

    return SearchResponse(
        query=q,
        results=results,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
        search_mode=search_mode,
    )


@router.get("/suggest")
async def suggest(
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
):
    """Autocomplete suggestions using prefix match on article titles."""
    result = await db.execute(
        select(Article.title, Article.slug, Article.category)
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            Article.title.ilike(f"{q}%"),
        )
        .order_by(desc(Article.published_time))
        .limit(limit)
    )
    rows = result.all()
    return [{"title": r.title, "slug": r.slug, "category": r.category} for r in rows]
