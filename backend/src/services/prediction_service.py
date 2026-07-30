"""
Prediction Service for FastAPI Backend
Handles ML model loading and prediction generation
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from src.config import settings

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for handling ML predictions."""
    
    def __init__(self):
        """Initialize prediction service."""
        self.models_dir = Path(settings.MODELS_DIR)
        self.models_cache: Dict[str, Any] = {}
        logger.info(f"PredictionService initialized with models directory: {self.models_dir}")
    
    def load_models_for_asset(self, asset: str) -> Dict[str, Any]:
        """
        Load all trained models for a specific asset.
        
        Args:
            asset: Asset symbol (e.g., BTC, XAU)
            
        Returns:
            Dictionary of model names to model objects
        """
        models = {}
        try:
            asset_upper = asset.upper()
            model_files = list(self.models_dir.glob(f"{asset_upper}_*.joblib"))
            
            if not model_files:
                logger.warning(f"No trained models found for {asset}")
                return models
            
            for model_file in model_files:
                try:
                    model_name = model_file.stem.replace(f"{asset_upper}_", "")
                    model = joblib.load(model_file)
                    models[model_name] = model
                    logger.info(f"Loaded model: {model_name} for {asset}")
                except Exception as e:
                    logger.error(f"Error loading model {model_file.stem}: {e}")
            
            return models
            
        except Exception as e:
            logger.error(f"Error loading models for {asset}: {e}")
            return {}
    
    def generate_features(self, asset: str) -> Dict[str, float]:
        """
        Generate features for prediction.
        In production, this would use real feature engineering.
        
        Args:
            asset: Asset symbol
            
        Returns:
            Dictionary of feature names to values
        """
        # In production, this would use real feature engineering from market data
        # For now, generate sample features for demonstration
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
    
    def predict(self, asset: str) -> Dict[str, Any]:
        """
        Generate prediction for an asset using ensemble of models.
        
        Args:
            asset: Asset symbol
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Load models for the asset
            models = self.load_models_for_asset(asset)
            
            if not models:
                raise ValueError(f"No trained models available for {asset}")
            
            # Generate features
            features = self.generate_features(asset)
            feature_vector = np.array([list(features.values())])
            
            # Get predictions from all models
            predictions = {}
            for model_name, model in models.items():
                try:
                    pred = model.predict(feature_vector)[0]
                    prob = model.predict_proba(feature_vector)[0] if hasattr(model, 'predict_proba') else None
                    predictions[model_name] = {
                        'prediction': int(pred),
                        'probability': prob.tolist() if prob is not None else None
                    }
                except Exception as e:
                    logger.error(f"Error predicting with {model_name}: {e}")
            
            # Ensemble prediction (majority vote)
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
            
            # Select best model (based on accuracy - in production, load from database)
            best_model = list(models.keys())[0]
            
            return {
                'asset': asset,
                'prediction': final_prediction,
                'confidence': confidence,
                'probability_up': probability_up,
                'probability_down': probability_down,
                'model_used': best_model,
                'features': features,
                'individual_predictions': predictions,
                'is_ml_backed': True
            }
            
        except Exception as e:
            logger.error(f"Error generating prediction for {asset}: {e}")
            raise
    
    def get_model_info(self, asset: str) -> List[Dict[str, Any]]:
        """
        Get information about available models for an asset.
        
        Args:
            asset: Asset symbol
            
        Returns:
            List of model information dictionaries
        """
        models_info = []
        try:
            asset_upper = asset.upper()
            model_files = list(self.models_dir.glob(f"{asset_upper}_*.joblib"))
            
            for model_file in model_files:
                model_name = model_file.stem.replace(f"{asset_upper}_", "")
                models_info.append({
                    'name': model_name,
                    'file': model_file.name,
                    'size': model_file.stat().st_size
                })
            
            return models_info
            
        except Exception as e:
            logger.error(f"Error getting model info for {asset}: {e}")
            return []


# Global prediction service instance
prediction_service = PredictionService()
