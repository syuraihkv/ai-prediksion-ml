"""
Database connection and initialization
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
import logging

from src.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Create async session
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class Prediction(Base):
    """Prediction model for storing AI predictions."""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String, index=True)
    prediction = Column(String)  # BUY, SELL, HOLD
    confidence = Column(Float)
    probability_up = Column(Float)
    probability_down = Column(Float)
    model_used = Column(String)
    features = Column(Text)  # JSON string of features
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_correct = Column(Boolean, nullable=True)  # Updated later when actual result known


class ModelPerformance(Base):
    """Model performance tracking."""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String, index=True)
    model_name = Column(String, index=True)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class MarketData(Base):
    """Cached market data."""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String, index=True)
    price = Column(Float)
    change_24h = Column(Float)
    volume_24h = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def get_db():
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
