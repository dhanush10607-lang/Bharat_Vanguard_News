"""
TruthLens AI — Article Embeddings Model
Stores vector embeddings for semantic similarity search and duplicate detection.
Requires: pgvector PostgreSQL extension (enabled in Supabase free tier).
"""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from shared.database import Base

# Embedding dimension from sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIM = 384


class ArticleEmbedding(Base):
    __tablename__ = "article_embeddings"

    embedding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), unique=True, nullable=False, index=True)
    model_name = Column(String(100), default="sentence-transformers/all-MiniLM-L6-v2")
    vector = Column(Vector(EMBEDDING_DIM), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("Article", back_populates="embedding")

    def __repr__(self) -> str:
        return f"<ArticleEmbedding article={self.article_id} dim={EMBEDDING_DIM}>"
