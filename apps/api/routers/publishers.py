"""Bharat Vanguard News (BVN) — Publishers Router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.database import get_db
from shared.models import Publisher

router = APIRouter()

@router.get("/")
async def list_publishers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Publisher).where(Publisher.active.isnot(False)).order_by(Publisher.name))
    publishers = result.scalars().all()
    return [{"publisher_id": str(p.publisher_id), "name": p.name, "slug": p.slug,
             "country": p.country, "website": p.website, "is_official": p.is_official,
             "reputation_score": p.reputation_score, "logo_url": p.logo_url} for p in publishers]

@router.get("/{slug}")
async def get_publisher(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Publisher).where(Publisher.slug == slug))
    publisher = result.scalar_one_or_none()
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return {"publisher_id": str(publisher.publisher_id), "name": publisher.name,
            "slug": publisher.slug, "website": publisher.website, "country": publisher.country,
            "reputation_score": publisher.reputation_score, "is_official": publisher.is_official}
