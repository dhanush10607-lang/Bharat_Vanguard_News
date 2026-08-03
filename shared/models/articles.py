"""
TruthLens AI — Articles Model
Core model representing individual news articles collected from publishers.
"""
import uuid
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.database import Base
import enum


class ArticleStatus(str, enum.Enum):
    RAW = "RAW"               # Just collected, no processing
    PARSED = "PARSED"         # HTML cleaned, content extracted
    PROCESSED = "PROCESSED"   # NLP pipeline complete
    PUBLISHED = "PUBLISHED"   # Visible on website
    FAILED = "FAILED"         # Processing failed





class Article(Base):
    __tablename__ = "articles"

    article_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publisher_id = Column(UUID(as_uuid=True), ForeignKey("publishers.publisher_id"), nullable=False, index=True)

    # Content
    title = Column(String(1000), nullable=False)
    slug = Column(String(1100), unique=True, index=True)
    description = Column(Text)                          # Short excerpt / meta description
    content = Column(Text)                              # Full article text
    url = Column(String(2000), unique=True, nullable=False)
    url_hash = Column(String(64), unique=True, index=True)       # SHA256(url) for fast dedup
    content_hash = Column(String(64), index=True)                # SHA256(content) for dedup
    image_url = Column(String(2000))
    author = Column(String(500))

    # Classification
    language = Column(String(10), default="en", index=True)
    category = Column(String(100), index=True)
    country = Column(String(100), index=True)
    sentiment = Column(String(20), index=True)

    # Timestamps
    published_time = Column(DateTime(timezone=True), index=True)
    collected_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Processing
    status = Column(
        Enum(ArticleStatus),
        default=ArticleStatus.RAW,
        index=True
    )
    word_count = Column(Integer)
    reading_time_min = Column(Integer)                  # Estimated reading time in minutes
    is_paywalled = Column(Boolean, default=False)
    likes_count = Column(Integer, default=0, index=True)

    # Relationships
    publisher = relationship("Publisher", back_populates="articles")
    entities = relationship("ArticleEntity", back_populates="article", lazy="select")
    ai_summary = relationship("AISummary", back_populates="article", uselist=False)
    trust_signal = relationship("TrustSignal", back_populates="article", uselist=False)
    embedding = relationship("ArticleEmbedding", back_populates="article", uselist=False)
    event_links = relationship("EventArticle", back_populates="article")

    def __repr__(self) -> str:
        return f"<Article title={self.title[:50]!r} status={self.status!r}>"
