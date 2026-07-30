"""
Model comparison and performance API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import logging

from src.schemas import ModelComparisonResponse, ModelPerformanceResponse
from src.services.prediction_service import prediction_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/compare/{asset}", response_model=ModelComparisonResponse)
async def compare_models(asset: str):
    """Compare all trained models for an asset."""
    try:
        asset = asset.upper()
        
        # Get model info from prediction service
        models_info = prediction_service.get_model_info(asset)
        
        if not models_info:
            raise HTTPException(
                status_code=404,
                detail=f"No trained models found for {asset}"
            )
        
        # Convert to format expected by frontend
        models_data = []
        for model_info in models_info:
            # In production, load actual performance metrics from database
            # For now, use placeholder values
            models_data.append({
                "name": model_info['name'],
                "type": model_info['name'],  # Simplified - in production get from model
                "accuracy": 0.52,
                "precision": 0.53,
                "recall": 0.52,
                "f1_score": 0.52,
                "roc_auc": 0.53
            })
        
        # Select best model based on accuracy (in production, use actual metrics)
        best_model = max(models_data, key=lambda x: x['accuracy'])['name']
        
        return ModelComparisonResponse(
            asset=asset,
            models=models_data,
            best_model=best_model,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_models():
    """List all available trained models."""
    try:
        from src.config import settings
        from pathlib import Path
        
        models_dir = Path(settings.MODELS_DIR)
        all_models = list(models_dir.glob("*.joblib"))
        
        models_by_asset = {}
        for model_file in all_models:
            parts = model_file.stem.split("_")
            if len(parts) >= 2:
                asset = parts[0]
                model_name = "_".join(parts[1:])
                
                if asset not in models_by_asset:
                    models_by_asset[asset] = []
                
                models_by_asset[asset].append(model_name)
        
        return {
            "total_models": len(all_models),
            "models_by_asset": models_by_asset
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{asset}/{model_name}", response_model=ModelPerformanceResponse)
async def get_model_performance(asset: str, model_name: str):
    """Get performance metrics for a specific model."""
    try:
        asset = asset.upper()
        
        # In production, load from database
        # For now, return placeholder data
        return ModelPerformanceResponse(
            asset=asset,
            model_name=model_name,
            accuracy=0.52,
            precision=0.53,
            recall=0.52,
            f1_score=0.52,
            roc_auc=0.53,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
