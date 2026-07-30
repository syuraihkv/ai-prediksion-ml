"""
AI Prediction API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging

from src.schemas import PredictionRequest, PredictionResponse
from src.services.prediction_service import prediction_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def get_prediction(request: PredictionRequest):
    """Get AI prediction for an asset."""
    try:
        asset = request.asset.upper()
        
        # Use prediction service to generate prediction
        result = prediction_service.predict(asset)
        
        return PredictionResponse(
            asset=result['asset'],
            prediction=result['prediction'],
            confidence=result['confidence'],
            probability_up=result['probability_up'],
            probability_down=result['probability_down'],
            model_used=result['model_used'],
            features=result['features'],
            timestamp=datetime.utcnow(),
            is_ml_backed=result['is_ml_backed']
        )
        
    except ValueError as e:
        logger.error(f"Value error in prediction: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
