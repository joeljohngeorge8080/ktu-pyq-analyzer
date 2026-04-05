from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    module = Column(Integer, nullable=False)            # 1–5
    type = Column(String(20), nullable=False)           # short / long
    question_number = Column(String(20), nullable=True)
    image_path = Column(String(500), nullable=False)
    tags = Column(JSON, default=list)
    page_number = Column(Integer, default=1)
    crop_coords = Column(JSON, nullable=True)  # {x,y,w,h} for reference
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    paper = relationship("Paper", back_populates="questions")
