"""
FastAPI Backend for AI Market Prediction System
Provides REST API endpoints for market data, AI predictions, and model comparison
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.database import init_db
from src.api import market, prediction, models, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting up FastAPI application...")
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down FastAPI application...")


# Create FastAPI app
app = FastAPI(
    title="AI Market Prediction API",
    description="REST API for AI-powered market prediction and analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["Prediction"])
app.include_router(models.router, prefix="/api/models", tags=["Models"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Market Prediction API",
        "version": "1.0.0",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
