"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request schema for AI prediction."""
    asset: str = Field(..., description="Asset symbol (e.g., BTC, XAU)")
    timeframe: Optional[str] = Field("1d", description="Timeframe for prediction")


class PredictionResponse(BaseModel):
    """Response schema for AI prediction."""
    asset: str
    prediction: str  # BUY, SELL, HOLD
    confidence: float
    probability_up: float
    probability_down: float
    model_used: str
    features: Dict[str, Any]
    timestamp: datetime
    is_ml_backed: bool


class MarketDataResponse(BaseModel):
    """Response schema for market data."""
    asset: str
    price: float
    change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime


class ModelComparisonResponse(BaseModel):
    """Response schema for model comparison."""
    asset: str
    models: List[Dict[str, Any]]
    best_model: str
    timestamp: datetime


class ModelPerformanceResponse(BaseModel):
    """Response schema for model performance."""
    asset: str
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float]
    timestamp: datetime


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    version: str
    database: str
    models_loaded: bool
