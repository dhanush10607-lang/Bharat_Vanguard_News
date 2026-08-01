"""
TruthLens AI — Events Model
An Event groups multiple articles about the same real-world story.
E.g., "Apple launches M4 chip" may have 10 articles from different publishers.
"""
import uuid
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from shared.database import Base
import enum


class EventSentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class Event(Base):
    __tablename__ = "events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(1000), nullable=False)
    slug = Column(String(1100), unique=True, index=True)

    # Summaries (3 levels)
    summary_short = Column(Text)        # 1 sentence
    summary_medium = Column(Text)       # 3–5 sentences
    summary_bullets = Column(JSONB)     # ["point1", "point2", ...]

    # Classification
    category = Column(String(100), index=True)
    country = Column(String(100), index=True)
    keywords = Column(JSONB, default=list)   # ["openai", "gpt", "microsoft"]

    # Scoring
    importance_score = Column(Float, default=0.0)   # 0.0–1.0
    confidence_score = Column(Float, default=0.0)   # Transparency score 0.0–1.0
    sentiment = Column(Enum(EventSentiment))
    article_count = Column(Integer, default=1)

    # Status flags
    verified = Column(Boolean, default=False, index=True)
    trending = Column(Boolean, default=False, index=True)
    breaking = Column(Boolean, default=False, index=True)

    # Timestamps
    first_seen = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article_links = relationship("EventArticle", back_populates="event")
    trust_signals = relationship("TrustSignal", back_populates="event")

    def __repr__(self) -> str:
        return f"<Event title={self.title[:50]!r} articles={self.article_count}>"


class EventArticle(Base):
    """Junction table: Event ↔ Article (many-to-many)"""
    __tablename__ = "event_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.event_id"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), nullable=False, index=True)
    similarity_score = Column(Float, default=1.0)   # Cosine similarity to event centroid
    is_primary = Column(Boolean, default=False)      # The canonical "best" article for this event
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    event = relationship("Event", back_populates="article_links")
    article = relationship("Article", back_populates="event_links")

    def __repr__(self) -> str:
        return f"<EventArticle event={self.event_id} article={self.article_id} primary={self.is_primary}>"
