import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base

class Magazine(Base):
    __tablename__ = "magazines"

    magazine_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)
    pdf_url = Column(String(1024), nullable=False)
    cover_image_url = Column(String(1024), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
