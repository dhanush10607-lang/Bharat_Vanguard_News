from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any

from apps.api.deps import get_db
from shared.models.magazines import Magazine

router = APIRouter(tags=["Magazines"])

@router.get("/")
async def list_magazines(db: AsyncSession = Depends(get_db)):
    """Get all generated monthly magazines, sorted by newest first."""
    stmt = select(Magazine).order_by(Magazine.year.desc(), Magazine.month.desc())
    result = await db.execute(stmt)
    magazines = result.scalars().all()
    
    return {
        "items": [
            {
                "magazine_id": str(m.magazine_id),
                "title": m.title,
                "month": m.month,
                "year": m.year,
                "summary": m.summary,
                "pdf_url": m.pdf_url,
                "cover_image_url": m.cover_image_url,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in magazines
        ]
    }
