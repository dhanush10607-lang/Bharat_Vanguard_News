"""
TruthLens AI — Trust Signals Model
Stores explainable confidence/transparency signals for articles and events.
IMPORTANT: This is NOT a fact-check. It measures evidence strength, not truth.
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from shared.database import Base


class TrustSignal(Base):
    __tablename__ = "trust_signals"

    signal_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.article_id"), unique=True, nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.event_id"), index=True)  # nullable

    # Individual signals (inputs to composite score)
    official_source = Column(Boolean, default=False)        # Publisher is gov/official org
    independent_sources = Column(Integer, default=1)        # How many distinct publishers reported it
    publisher_reputation = Column(Float, default=0.5)       # Publisher's reputation score (0–1)
    cross_confirmation = Column(Boolean, default=False)     # Do sources agree on key facts?
    has_correction = Column(Boolean, default=False)         # Has a correction been issued?
    freshness_hours = Column(Float)                         # Hours since last update

    # Composite score (weighted formula)
    confidence_score = Column(Float, default=0.0, index=True)  # 0.0–1.0

    # Full breakdown stored as JSON for UI rendering
    # Example: {"official_source": 0.25, "independent_sources": 0.30, ...}
    signal_breakdown = Column(JSONB, default=dict)

    last_checked = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("Article", back_populates="trust_signal")
    event = relationship("Event", back_populates="trust_signals")

    def compute_confidence(self) -> float:
        """
        Compute composite confidence score from individual signals.
        Weights:
          - official_source:       0.25
          - independent_sources:   0.30  (capped at 10 sources = 1.0)
          - publisher_reputation:  0.20
          - cross_confirmation:    0.15
          - freshness:             0.10  (within 24h = 1.0; degrades over 7 days)
        """
        w_official = 0.25 * (1.0 if self.official_source else 0.0)
        w_sources = 0.30 * min(1.0, (self.independent_sources or 1) / 10)
        w_reputation = 0.20 * (self.publisher_reputation or 0.5)
        w_cross = 0.15 * (1.0 if self.cross_confirmation else 0.0)

        if self.freshness_hours is not None:
            if self.freshness_hours <= 24:
                freshness = 1.0
            elif self.freshness_hours <= 168:  # 7 days
                freshness = 1.0 - ((self.freshness_hours - 24) / 144)
            else:
                freshness = 0.1
        else:
            freshness = 0.5
        w_freshness = 0.10 * freshness

        score = w_official + w_sources + w_reputation + w_cross + w_freshness
        self.confidence_score = round(min(1.0, score), 3)
        self.signal_breakdown = {
            "official_source": round(w_official, 3),
            "independent_sources": round(w_sources, 3),
            "publisher_reputation": round(w_reputation, 3),
            "cross_confirmation": round(w_cross, 3),
            "freshness": round(w_freshness, 3),
        }
        return self.confidence_score

    def __repr__(self) -> str:
        return f"<TrustSignal article={self.article_id} confidence={self.confidence_score:.2f}>"
