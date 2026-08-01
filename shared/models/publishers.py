"""
TruthLens AI — Publishers Model
Represents news publishers/sources (BBC, Reuters, The Hindu, etc.)
"""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from shared.database import Base


class Publisher(Base):
    __tablename__ = "publishers"

    publisher_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    website = Column(String(500))
    country = Column(String(100), index=True)
    language = Column(String(10), default="en")     # ISO 639-1
    rss_feeds = Column(JSONB, default=list)          # [{"url": "...", "category": "..."}]
    api_endpoint = Column(String(500))
    is_official = Column(Boolean, default=False)     # Government/official org?
    reputation_score = Column(Float, default=0.7)   # 0.0–1.0
    logo_url = Column(String(500))
    description = Column(Text)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    articles = relationship("Article", back_populates="publisher", lazy="select")

    def __repr__(self) -> str:
        return f"<Publisher name={self.name!r} country={self.country!r}>"
