"""
TruthLens AI — Users & Auth Models
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from shared.database import Base
import enum


class UserRole(str, enum.Enum):
    READER = "reader"
    JOURNALIST = "journalist"
    RESEARCHER = "researcher"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, index=True)
    display_name = Column(String(255))
    password_hash = Column(Text, nullable=True)          # Nullable — OAuth users have no password
    role = Column(Enum(UserRole), default=UserRole.READER)

    # OAuth provider info (e.g. Google)
    oauth_provider = Column(String(50))                  # "google" | None (email/password)
    oauth_provider_id = Column(String(255), index=True)  # Google sub ID
    avatar_url = Column(String(500))                     # Profile picture from Google

    # Preferences stored as JSON
    preferences = Column(JSONB, default=dict)
    # Example: {"categories": ["technology", "science"], "countries": ["India", "US"]}

    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    bookmarks = relationship("UserBookmark", back_populates="user", lazy="select")
    history = relationship("UserHistory", back_populates="user", lazy="select")

    def __repr__(self) -> str:
        return f"<User email={self.email!r} role={self.role!r}>"


class UserBookmark(Base):
    __tablename__ = "user_bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.event_id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookmarks")


class UserHistory(Base):
    __tablename__ = "user_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), server_default=func.now())
    read_pct = Column(String(5), default="0")    # % of article read (0–100)

    user = relationship("User", back_populates="history")


class SystemLog(Base):
    """Structured log entries for monitoring and debugging."""
    __tablename__ = "system_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service = Column(String(100), index=True)     # "collector", "nlp", "api"
    level = Column(String(20), index=True)        # "info", "warning", "error"
    message = Column(Text, nullable=False)
    log_metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class CollectionRun(Base):
    """Tracks each RSS/API collection run for health monitoring."""
    __tablename__ = "collection_runs"

    run_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publisher_id = Column(UUID(as_uuid=True), ForeignKey("publishers.publisher_id"), index=True)
    source_type = Column(String(50))      # "rss", "guardian_api", "currents_api"
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    articles_found = Column(String(20), default="0")
    articles_new = Column(String(20), default="0")
    articles_duplicate = Column(String(20), default="0")
    status = Column(String(20), default="running")  # running | success | failed
    error_message = Column(Text)

    def __repr__(self) -> str:
        return f"<CollectionRun publisher={self.publisher_id} status={self.status!r}>"
