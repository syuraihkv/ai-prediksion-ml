"""
AI Prediction API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging
import joblib
from pathlib import Path
import numpy as np

from src.schemas import PredictionRequest, PredictionResponse
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def get_prediction(request: PredictionRequest):
    """Get AI prediction for an asset."""
    try:
        asset = request.asset.upper()
        
        # Load models for the asset
        models_dir = Path(settings.MODELS_DIR)
        asset_models = list(models_dir.glob(f"{asset}_*.joblib"))
        
        if not asset_models:
            raise HTTPException(
                status_code=404, 
                detail=f"No trained models found for {asset}"
            )
        
        # Load all models
        models = {}
        for model_file in asset_models:
            model_name = model_file.stem.replace(f"{asset}_", "")
            try:
                models[model_name] = joblib.load(model_file)
                logger.info(f"Loaded model: {model_name}")
            except Exception as e:
                logger.error(f"Error loading model {model_name}: {e}")
        
        if not models:
            raise HTTPException(
                status_code=500,
                detail="Failed to load any models"
            )
        
        # Generate features (simplified - in production, use real feature engineering)
        features = generate_sample_features(asset)
        
        # Get predictions from all models
        predictions = {}
        for model_name, model in models.items():
            try:
                pred = model.predict([features])[0]
                prob = model.predict_proba([features])[0] if hasattr(model, 'predict_proba') else None
                predictions[model_name] = {
                    'prediction': pred,
                    'probability': prob
                }
            except Exception as e:
                logger.error(f"Error predicting with {model_name}: {e}")
        
        # Aggregate predictions (ensemble)
        buy_votes = sum(1 for p in predictions.values() if p['prediction'] == 1)
        sell_votes = sum(1 for p in predictions.values() if p['prediction'] == 0)
        
        if buy_votes > sell_votes:
            final_prediction = "BUY"
            confidence = buy_votes / len(predictions)
        elif sell_votes > buy_votes:
            final_prediction = "SELL"
            confidence = sell_votes / len(predictions)
        else:
            final_prediction = "HOLD"
            confidence = 0.5
        
        # Calculate probabilities
        probability_up = confidence
        probability_down = 1 - confidence
        
        # Select best model (random for now, in production use performance metrics)
        best_model = list(models.keys())[0]
        
        return PredictionResponse(
            asset=asset,
            prediction=final_prediction,
            confidence=confidence,
            probability_up=probability_up,
            probability_down=probability_down,
            model_used=best_model,
            features=features,
            timestamp=datetime.utcnow(),
            is_ml_backed=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_sample_features(asset: str) -> Dict[str, float]:
    """Generate sample features for prediction (simplified)."""
    # In production, this would use real feature engineering
    np.random.seed(42)
    return {
        'rsi': np.random.uniform(30, 70),
        'macd': np.random.uniform(-1, 1),
        'volume_ratio': np.random.uniform(0.5, 2.0),
        'price_change_24h': np.random.uniform(-5, 5),
        'volatility': np.random.uniform(0.5, 3.0),
        'momentum': np.random.uniform(-2, 2),
        'trend_strength': np.random.uniform(0, 1),
    }
