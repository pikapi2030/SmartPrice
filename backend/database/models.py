from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.database.connection import Base

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class CachedResult(Base):
    __tablename__ = "cached_results"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, unique=True, index=True)
    amazon_data = Column(Text)  # JSON string of raw Amazon results
    flipkart_data = Column(Text)  # JSON string of raw Flipkart results
    created_at = Column(DateTime, default=datetime.utcnow)
