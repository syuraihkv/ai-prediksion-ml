"""
Model comparison and performance API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import logging
import joblib
from pathlib import Path

from src.schemas import ModelComparisonResponse, ModelPerformanceResponse
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/compare/{asset}", response_model=ModelComparisonResponse)
async def compare_models(asset: str):
    """Compare all trained models for an asset."""
    try:
        asset = asset.upper()
        
        # Load models for the asset
        models_dir = Path(settings.MODELS_DIR)
        asset_models = list(models_dir.glob(f"{asset}_*.joblib"))
        
        if not asset_models:
            raise HTTPException(
                status_code=404,
                detail=f"No trained models found for {asset}"
            )
        
        # Load all models and get their info
        models_info = []
        for model_file in asset_models:
            model_name = model_file.stem.replace(f"{asset}_", "")
            try:
                model = joblib.load(model_file)
                
                # Get model metrics (simplified - in production, load from database)
                models_info.append({
                    "name": model_name,
                    "type": model.__class__.__name__,
                    "accuracy": 0.52,  # Placeholder - in production, load from database
                    "precision": 0.53,
                    "recall": 0.52,
                    "f1_score": 0.52,
                    "roc_auc": 0.53
                })
                logger.info(f"Loaded model: {model_name}")
            except Exception as e:
                logger.error(f"Error loading model {model_name}: {e}")
        
        if not models_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to load any models"
            )
        
        # Select best model based on accuracy
        best_model = max(models_info, key=lambda x: x['accuracy'])['name']
        
        return ModelComparisonResponse(
            asset=asset,
            models=models_info,
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
