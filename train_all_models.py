"""
Script to train all ML models for XAU and BTC assets.
This will train Logistic Regression, Random Forest, XGBoost, LightGBM, and CatBoost for both assets.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import joblib

from src.train import ModelTrainer
from src.config import MODELS_DIR
from src.utils import setup_logger

logger = setup_logger("TrainAllModels")


def generate_sample_data(n_samples=1000, n_features=20):
    """Generate sample training data for demonstration."""
    np.random.seed(42)
    
    X = pd.DataFrame(np.random.randn(n_samples, n_features), 
                     columns=[f'feature_{i}' for i in range(n_features)])
    
    # Create somewhat realistic target variable
    y = pd.Series(np.random.randint(0, 2, n_samples))
    
    return X, y


def train_models_for_asset(asset: str):
    """Train all models for a specific asset."""
    logger.info(f"Training models for {asset}...")
    
    # Initialize trainer
    trainer = ModelTrainer(logger=logger)
    
    # Generate sample data (in production, this would come from real data)
    X, y = generate_sample_data(n_samples=1000, n_features=20)
    
    # Split data
    train_size = int(len(X) * 0.7)
    val_size = int(len(X) * 0.15)
    
    X_train, X_val, X_test = X.iloc[:train_size], X.iloc[train_size:train_size+val_size], X.iloc[train_size+val_size:]
    y_train, y_val, y_test = y.iloc[:train_size], y.iloc[train_size:train_size+val_size], y.iloc[train_size+val_size:]
    
    # Train all models
    results = trainer.train_all_models(X_train, y_train, X_val, y_val)
    
    # Save all models
    for model_name, model_data in results.items():
        model = model_data['model']
        filename = f"{asset}_{model_name}.joblib"
        save_path = MODELS_DIR / filename
        joblib.dump(model, save_path)
        logger.info(f"Saved {filename} to {save_path}")
    
    # Compare models
    comparison = trainer.compare_models(results)
    logger.info(f"Model comparison for {asset}:")
    logger.info(comparison)
    
    return results


def main():
    """Main function to train models for all assets."""
    logger.info("Starting model training for all assets...")
    
    # Ensure models directory exists
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Train models for XAU
    xau_results = train_models_for_asset('XAU')
    
    # Train models for BTC
    btc_results = train_models_for_asset('BTC')
    
    logger.info("Model training completed for all assets!")
    
    # List all trained models
    model_files = list(MODELS_DIR.glob('*.joblib'))
    logger.info(f"Total models trained: {len(model_files)}")
    for model_file in model_files:
        logger.info(f"  - {model_file.name}")


if __name__ == "__main__":
    main()
