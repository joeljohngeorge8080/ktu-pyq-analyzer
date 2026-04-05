from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.base import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    year = Column(Integer, nullable=False)
    exam_type = Column(String(50), nullable=True)  # e.g. "Regular", "Supplementary"
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf / image
    page_count = Column(Integer, default=1)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="papers")
    questions = relationship("Question", back_populates="paper", cascade="all, delete-orphan")
