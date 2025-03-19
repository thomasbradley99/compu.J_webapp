from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    
    # Classification results
    predicted_category = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    category_scores = Column(JSON, nullable=False)  # Store scores for all categories
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Optional fields
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    
    # Add these new fields
    token_count = Column(Integer, nullable=True)
    num_chunks = Column(Integer, nullable=True) 