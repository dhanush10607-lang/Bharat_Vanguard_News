"""
TruthLens AI — Entities Router (Full Implementation)
Provides entity profile pages and article-entity relationships.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from pydantic import BaseModel
from datetime import datetime

from shared.database import get_db
from shared.models import Entity, ArticleEntity, Article, Publisher, ArticleStatus

router = APIRouter()


class EntityOut(BaseModel):
    entity_id: UUID
    name: str
    slug: str
    type: str
    country: Optional[str] = None
    description: Optional[str] = None
    article_count: int = 0
    class Config:
        from_attributes = True


class EntityArticle(BaseModel):
    article_id: UUID
    title: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    published_time: Optional[datetime] = None
    publisher_name: Optional[str] = None
    publisher_slug: Optional[str] = None
    mention_count: int = 1
    class Config:
        from_attributes = True


class EntityProfile(EntityOut):
    articles: list[EntityArticle] = []
    top_categories: list[dict] = []
    top_publishers: list[dict] = []


class PaginatedEntities(BaseModel):
    items: list[EntityOut]
    total: int
    page: int
    page_size: int
    has_next: bool


@router.get("/", response_model=PaginatedEntities)
async def list_entities(
    entity_type: Optional[str] = Query(None, description="person | organization | location | group"),
    q: Optional[str] = Query(None, description="Search entity name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List entities ordered by article count."""
    filters = []
    if entity_type:
        filters.append(Entity.type == entity_type)
    if q:
        filters.append(Entity.name.ilike(f"%{q}%"))

    count_q = select(func.count()).select_from(Entity)
    if filters:
        count_q = count_q.where(and_(*filters))
    total_res = await db.execute(count_q)
    total = total_res.scalar() or 0

    query = (
        select(Entity)
        .order_by(desc(Entity.article_count))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    entities = result.scalars().all()

    return PaginatedEntities(
        items=[EntityOut.model_validate(e) for e in entities],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(((page - 1) * page_size) + page_size) < total,
    )


@router.get("/{slug}", response_model=EntityProfile)
async def get_entity_profile(
    slug: str,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Full entity profile with linked articles, top categories, and top publishers."""
    entity_res = await db.execute(select(Entity).where(Entity.slug == slug))
    entity = entity_res.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Linked articles (most mentioned first)
    articles_res = await db.execute(
        select(Article, Publisher, ArticleEntity.mention_count)
        .join(ArticleEntity, ArticleEntity.article_id == Article.article_id)
        .join(Publisher, Publisher.publisher_id == Article.publisher_id)
        .where(
            ArticleEntity.entity_id == entity.entity_id,
            Article.status == ArticleStatus.PUBLISHED,
        )
        .order_by(desc(ArticleEntity.mention_count), desc(Article.published_time))
        .limit(limit)
    )
    article_rows = articles_res.all()

    articles = [
        EntityArticle(
            article_id=a.article_id,
            title=a.title,
            slug=a.slug,
            description=a.description,
            image_url=a.image_url,
            category=a.category,
            published_time=a.published_time,
            publisher_name=p.name,
            publisher_slug=p.slug,
            mention_count=mc,
        )
        for a, p, mc in article_rows
    ]

    # Top categories for this entity
    cat_res = await db.execute(
        select(Article.category, func.count().label("cnt"))
        .join(ArticleEntity, ArticleEntity.article_id == Article.article_id)
        .where(
            ArticleEntity.entity_id == entity.entity_id,
            Article.category.isnot(None),
        )
        .group_by(Article.category)
        .order_by(desc("cnt"))
        .limit(5)
    )
    top_categories = [{"category": r.category, "count": r.cnt} for r in cat_res.all()]

    # Top publishers for this entity
    pub_res = await db.execute(
        select(Publisher.name, Publisher.slug, func.count().label("cnt"))
        .join(Article, Article.publisher_id == Publisher.publisher_id)
        .join(ArticleEntity, ArticleEntity.article_id == Article.article_id)
        .where(ArticleEntity.entity_id == entity.entity_id)
        .group_by(Publisher.publisher_id)
        .order_by(desc("cnt"))
        .limit(5)
    )
    top_publishers = [{"name": r.name, "slug": r.slug, "count": r.cnt} for r in pub_res.all()]

    return EntityProfile(
        entity_id=entity.entity_id,
        name=entity.name,
        slug=entity.slug,
        type=entity.type,
        country=entity.country,
        description=entity.description,
        article_count=entity.article_count,
        articles=articles,
        top_categories=top_categories,
        top_publishers=top_publishers,
    )
