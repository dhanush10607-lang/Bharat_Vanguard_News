"""
TruthLens AI — Entities Model
Named entities extracted from articles: people, companies, countries, etc.
"""
import uuid
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from shared.database import Base
import enum


class EntityType(str, enum.Enum):
    PERSON = "person"
    COMPANY = "company"
    COUNTRY = "country"
    ORGANIZATION = "organization"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    CURRENCY = "currency"
    EVENT_TYPE = "event_type"
    OTHER = "other"


class Entity(Base):
    __tablename__ = "entities"

    entity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False, index=True)
    slug = Column(String(550), unique=True, index=True)
    type = Column(Enum(EntityType), nullable=False, index=True)
    aliases = Column(JSONB, default=list)           # ["alternative names", "abbreviations"]
    description = Column(Text)
    country = Column(String(100), index=True)
    wikidata_id = Column(String(50))                # For future Wikidata linking
    article_count = Column(Integer, default=0)      # Cached count, updated periodically
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    article_mentions = relationship("ArticleEntity", back_populates="entity")

    def __repr__(self) -> str:
        return f"<Entity name={self.name!r} type={self.type!r}>"


class ArticleEntity(Base):
    """Junction table: Article ↔ Entity (many-to-many with metadata)"""
    __tablename__ = "article_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.entity_id"), nullable=False, index=True)
    mention_count = Column(Integer, default=1)
    relevance_score = Column(Float, default=0.5)    # 0.0–1.0; higher = more central to article

    # Relationships
    article = relationship("Article", back_populates="entities")
    entity = relationship("Entity", back_populates="article_mentions")

    def __repr__(self) -> str:
        return f"<ArticleEntity article={self.article_id} entity={self.entity_id} count={self.mention_count}>"
