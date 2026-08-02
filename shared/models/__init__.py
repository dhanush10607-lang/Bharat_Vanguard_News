"""
TruthLens AI — Models Package
Import all models here so SQLAlchemy can register them with the metadata.
"""
from shared.models.publishers import Publisher
from shared.models.articles import Article, ArticleStatus
from shared.models.events import Event, EventArticle, EventSentiment
from shared.models.entities import Entity, ArticleEntity, EntityType
from shared.models.ai_summaries import AISummary
from shared.models.trust_signals import TrustSignal
from shared.models.embeddings import ArticleEmbedding
from shared.models.users import User, UserBookmark, UserHistory, UserRole, SystemLog, CollectionRun
from shared.models.magazines import Magazine

__all__ = [
    "Publisher",
    "Article", "ArticleStatus", "SentimentLabel",
    "Event", "EventArticle", "EventSentiment",
    "Entity", "ArticleEntity", "EntityType",
    "AISummary",
    "TrustSignal",
    "ArticleEmbedding",
    "User", "UserBookmark", "UserHistory", "UserRole",
    "SystemLog", "CollectionRun",
    "Magazine",
]
