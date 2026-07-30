"""
Health check endpoint
"""

from fastapi import APIRouter
from src.schemas import HealthResponse
from src.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Check database connection (simplified)
    db_status = "connected"  # In production, actually check connection
    
    # Check if models are loaded
    from pathlib import Path
    models_dir = Path(settings.MODELS_DIR)
    models_loaded = models_dir.exists() and len(list(models_dir.glob("*.joblib"))) > 0
    
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        database=db_status,
        models_loaded=models_loaded
    )
