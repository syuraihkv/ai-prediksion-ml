"""
Prediction System for AI Economic News Impact Prediction

This module handles real-time prediction:
- Loading trained models
- Feature generation for prediction
- Making BUY/SELL predictions
- Confidence scoring
- Prediction logging

Purpose: Generate real-time BUY/SELL predictions with confidence scores
Input: Current market data, economic events, news data
Output: Prediction (BUY/SELL) with confidence and reasoning
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from pathlib import Path
import joblib
from datetime import datetime

from src.economic_api import EconomicAPI
from src.market_api import MarketAPI
try:
    from src.news_analyzer import NewsAnalyzer
    NEWS_ANALYZER_AVAILABLE = True
except ImportError:
    NEWS_ANALYZER_AVAILABLE = False
    NewsAnalyzer = None
from src.feature_engineering_new import NewsImpactFeatureEngineer
from src.utils import setup_logger


class PredictionSystem:
    """
    Generates real-time predictions for market direction.
    
    This class handles:
    - Model loading
    - Feature generation
    - Prediction generation
    - Confidence scoring
    - Prediction logging
    """
    
    def __init__(self, model_dir: Path = None, logger=None):
        """
        Initialize PredictionSystem.
        
        Args:
            model_dir: Directory containing saved models
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("PredictionSystem")
        self.model_dir = model_dir or Path("data/models")
        self.model = None
        self.model_name = None
        
        # Initialize components
        self.economic_api = EconomicAPI()
        self.market_api = MarketAPI()
        self.news_analyzer = NewsAnalyzer() if NEWS_ANALYZER_AVAILABLE else None
        self.feature_engineer = NewsImpactFeatureEngineer()
        
        # Load best model
        self._load_best_model()
    
    def _load_best_model(self):
        """
        Load the best trained model.
        """
        try:
            # Look for the best model file
            model_files = list(self.model_dir.glob("*.joblib"))
            
            if model_files:
                # Load the most recent model
                latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
                self.model = joblib.load(latest_model)
                self.model_name = latest_model.stem
                self.logger.info(f"Loaded model: {self.model_name}")
            else:
                self.logger.warning("No trained model found. Using default model.")
                # Create a simple default model for demonstration
                from sklearn.linear_model import LogisticRegression
                self.model = LogisticRegression(random_state=42)
                self.model_name = "Default_LogisticRegression"
                
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            self.model = None
    
    def load_all_models(self):
        """
        Load all available models for comparison.
        
        Returns:
            Dictionary of model names to model objects
        """
        models = {}
        try:
            model_files = list(self.model_dir.glob("*.joblib"))
            
            for model_file in model_files:
                try:
                    model = joblib.load(model_file)
                    models[model_file.stem] = model
                    self.logger.info(f"Loaded model: {model_file.stem}")
                except Exception as e:
                    self.logger.error(f"Error loading model {model_file.stem}: {e}")
            
            # Add default models if no models found
            if not models:
                from sklearn.linear_model import LogisticRegression
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.tree import DecisionTreeClassifier
                
                models['Logistic_Regression'] = LogisticRegression(random_state=42)
                models['Random_Forest'] = RandomForestClassifier(random_state=42, n_estimators=50)
                models['Decision_Tree'] = DecisionTreeClassifier(random_state=42)
                self.logger.info("Using default models for comparison")
            
            return models
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            return {}
    
    def compare_models(self, asset: str) -> Dict[str, Any]:
        """
        Compare predictions from multiple models.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
        
        Returns:
            Dictionary with model comparison results
        """
        models = self.load_all_models()
        
        if not models:
            return {'error': 'No models available for comparison'}
        
        # Generate features
        features = self.generate_features(asset)
        
        if not features:
            return {'error': 'Could not generate features'}
        
        # Prepare feature vector
        feature_vector = self._prepare_feature_vector(features)
        
        if feature_vector is None:
            return {'error': 'Could not prepare feature vector'}
        
        # Get predictions from all models
        model_predictions = {}
        
        for model_name, model in models.items():
            try:
                # Check if model is trained
                if not hasattr(model, 'coef_') and not hasattr(model, 'feature_importances_'):
                    self.logger.warning(f"Model {model_name} is not trained. Skipping.")
                    continue
                
                # Make prediction
                prediction_proba = model.predict_proba([feature_vector])[0]
                prediction = model.predict([feature_vector])[0]
                
                # Convert to BUY/SELL
                signal = 'BUY' if prediction == 1 else 'SELL'
                confidence = prediction_proba[prediction]
                
                model_predictions[model_name] = {
                    'signal': signal,
                    'confidence': confidence,
                    'prediction': prediction
                }
                
            except Exception as e:
                self.logger.error(f"Error with model {model_name}: {e}")
                # Add fallback prediction
                model_predictions[model_name] = {
                    'signal': 'HOLD',
                    'confidence': 0.5,
                    'prediction': 0
                }
        
        # Calculate consensus
        buy_votes = sum(1 for pred in model_predictions.values() if pred['signal'] == 'BUY')
        sell_votes = sum(1 for pred in model_predictions.values() if pred['signal'] == 'SELL')
        total_votes = len(model_predictions)
        
        if buy_votes > sell_votes:
            consensus_signal = 'BUY'
            consensus_strength = buy_votes / total_votes
        elif sell_votes > buy_votes:
            consensus_signal = 'SELL'
            consensus_strength = sell_votes / total_votes
        else:
            consensus_signal = 'HOLD'
            consensus_strength = 0.5
        
        return {
            'asset': asset,
            'model_predictions': model_predictions,
            'consensus_signal': consensus_signal,
            'consensus_strength': consensus_strength,
            'total_models': total_votes,
            'buy_votes': buy_votes,
            'sell_votes': sell_votes,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_features(self, asset: str) -> Dict[str, Any]:
        """
        Generate features for prediction.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
        
        Returns:
            Dictionary with all features
        """
        features = {}
        
        # Get market data
        market_data = self.market_api.get_ohlcv_data(asset, period='1mo')
        if not market_data.empty:
            technical_features = self.feature_engineer.create_technical_features(market_data)
            features['technical'] = technical_features.iloc[-1:].to_dict('records')[0]
        
        # Get economic events
        economic_events = self.economic_api.get_upcoming_events(days=7, asset=asset)
        if economic_events:
            economic_features = self.feature_engineer.create_economic_features(economic_events)
            if not economic_features.empty:
                features['economic'] = economic_features.iloc[0].to_dict()
        
        # Get news
        news_articles = self.news_analyzer.collect_news(asset=asset, max_articles=10)
        if news_articles:
            analyzed_news = self.news_analyzer.analyze_news_batch(news_articles)
            news_features = self.feature_engineer.create_news_features(analyzed_news)
            if not news_features.empty:
                features['news'] = news_features.iloc[0].to_dict()
        
        # Get market indicators
        indicator_data = {}
        if asset == 'XAU':
            indicator_data['DXY'] = self.market_api.get_indicator_data('DXY', period='1mo')
            indicator_data['US10Y'] = self.market_api.get_indicator_data('US10Y', period='1mo')
        else:  # BTC
            indicator_data['DXY'] = self.market_api.get_indicator_data('DXY', period='1mo')
            indicator_data['US10Y'] = self.market_api.get_indicator_data('US10Y', period='1mo')
        
        indicator_features = self.feature_engineer.create_market_indicator_features(indicator_data)
        if not indicator_features.empty:
            features['indicators'] = indicator_features.iloc[0].to_dict()
        
        return features
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> Optional[List[float]]:
        """
        Prepare feature vector for prediction.
        
        Args:
            features: Dictionary with all features
        
        Returns:
            Feature vector as list of floats, or None if preparation fails
        """
        try:
            feature_vector = []
            
            # Flatten technical features
            if 'technical' in features:
                for key, value in features['technical'].items():
                    if isinstance(value, (int, float)):
                        feature_vector.append(float(value))
                    else:
                        feature_vector.append(0.0)
            
            # Flatten economic features
            if 'economic' in features:
                for key, value in features['economic'].items():
                    if isinstance(value, (int, float)):
                        feature_vector.append(float(value))
                    else:
                        feature_vector.append(0.0)
            
            # Flatten news features
            if 'news' in features:
                for key, value in features['news'].items():
                    if isinstance(value, (int, float)):
                        feature_vector.append(float(value))
                    else:
                        feature_vector.append(0.0)
            
            # Flatten indicator features
            if 'indicators' in features:
                for key, value in features['indicators'].items():
                    if isinstance(value, (int, float)):
                        feature_vector.append(float(value))
                    else:
                        feature_vector.append(0.0)
            
            # If no features, return default vector
            if not feature_vector:
                feature_vector = [0.0] * 10  # Default 10 features
            
            return feature_vector
            
        except Exception as e:
            self.logger.error(f"Error preparing feature vector: {e}")
            return None
    
    def prepare_prediction_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare features for model prediction.
        
        Args:
            features: Dictionary with feature categories
        
        Returns:
            DataFrame with features ready for prediction
        """
        # Combine all features into single dictionary
        combined = {}
        
        for category, feature_dict in features.items():
            if isinstance(feature_dict, dict):
                combined.update(feature_dict)
        
        # Convert to DataFrame
        df = pd.DataFrame([combined])
        
        # Ensure all features are numeric
        df = df.select_dtypes(include=[np.number])
        df = df.fillna(0)
        
        return df
    
    def predict(self, asset: str) -> Dict[str, Any]:
        """
        Generate prediction for specified asset using model comparison consensus.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
        
        Returns:
            Dictionary with prediction and metadata
        """
        self.logger.info(f"Generating prediction for {asset}")
        
        # Generate features
        features = self.generate_features(asset)
        
        # Prepare features for model
        feature_df = self.prepare_prediction_features(features)
        
        # Get current price
        current_price = self.market_api.get_current_price(asset)
        
        # Get upcoming events
        upcoming_events = self.economic_api.get_upcoming_events(days=7, asset=asset)
        next_event = upcoming_events[0] if upcoming_events else None
        
        # Get news sentiment
        news_articles = self.news_analyzer.collect_news(asset=asset, max_articles=10)
        if news_articles:
            analyzed_news = self.news_analyzer.analyze_news_batch(news_articles)
            sentiment_summary = self.news_analyzer.get_asset_sentiment_summary(analyzed_news)
        else:
            sentiment_summary = {
                'overall_sentiment': 'neutral',
                'average_confidence': 0.5,
                'sentiment_distribution': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
            }
        
        # Use model comparison consensus for prediction
        model_comparison = self.compare_models(asset)
        
        if model_comparison and 'error' not in model_comparison and model_comparison.get('total_models', 0) > 0:
            # Use consensus from model comparison
            prediction = model_comparison['consensus_signal']
            confidence = model_comparison['consensus_strength']
            model_used = f"Consensus of {model_comparison['total_models']} trained model(s)"
            is_ml_backed = True
        else:
            # No trained ML model is available. Fall back to a news-sentiment
            # heuristic only, and say so explicitly -- this is NOT an ML
            # prediction and should not be displayed with the same confidence
            # framing as a real model signal.
            if sentiment_summary['overall_sentiment'] == 'positive':
                prediction = 'BUY'
                confidence = sentiment_summary['average_confidence']
            elif sentiment_summary['overall_sentiment'] == 'negative':
                prediction = 'SELL'
                confidence = sentiment_summary['average_confidence']
            else:
                prediction = 'HOLD'
                confidence = 0.5
            model_used = "No trained model available - sentiment-only heuristic (NOT an ML prediction)"
            is_ml_backed = False
        
        # Build result
        result = {
            'asset': asset,
            'is_ml_backed': is_ml_backed,
            'prediction': prediction,
            'confidence': confidence,
            'current_price': current_price,
            'next_event': next_event,
            'sentiment_summary': sentiment_summary,
            'features': features,
            'timestamp': datetime.now().isoformat(),
            'model_used': model_used
        }
        
        self.logger.info(f"Prediction for {asset}: {prediction} ({confidence:.1%} confidence) using {model_used}")
        
        return result
    
    def batch_predict(self, assets: List[str]) -> List[Dict[str, Any]]:
        """
        Generate predictions for multiple assets.
        
        Args:
            assets: List of asset symbols
        
        Returns:
            List of prediction results
        """
        results = []
        
        for asset in assets:
            try:
                result = self.predict(asset)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error predicting for {asset}: {e}")
        
        return results


if __name__ == "__main__":
    # Test prediction system
    predictor = PredictionSystem()
    
    # Test prediction for XAU
    print("Testing prediction for XAU/USD:")
    xau_prediction = predictor.predict('XAU')
    print(f"Prediction: {xau_prediction['prediction']}")
    print(f"Confidence: {xau_prediction['confidence']:.1%}")
    print(f"Current Price: {xau_prediction['current_price']}")
    
    # Test prediction for BTC
    print("\nTesting prediction for BTC/USD:")
    btc_prediction = predictor.predict('BTC')
    print(f"Prediction: {btc_prediction['prediction']}")
    print(f"Confidence: {btc_prediction['confidence']:.1%}")
    print(f"Current Price: {btc_prediction['current_price']}")
