"""
TruthLens AI — AI Summaries Model
Stores AI-generated summaries (short, medium, bullets) for articles.
One record per article per model version.
"""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from shared.database import Base


class AISummary(Base):
    __tablename__ = "ai_summaries"

    summary_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), unique=True, nullable=False, index=True)
    model_name = Column(String(100), default="facebook/bart-large-cnn")

    # Three levels of summary
    summary_short = Column(Text)            # 1 sentence (≤50 words)
    summary_medium = Column(Text)           # 3–5 sentences (≤200 words)
    summary_bullets = Column(JSONB)         # ["point1", "point2", ...]

    # Extracted metadata
    keywords = Column(JSONB, default=list)  # ["openai", "gpt", "microsoft"]
    language = Column(String(10), default="en")
    reading_time_min = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    article = relationship("Article", back_populates="ai_summary")

    def __repr__(self) -> str:
        return f"<AISummary article={self.article_id} model={self.model_name!r}>"
