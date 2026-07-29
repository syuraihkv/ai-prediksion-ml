"""
ML Training Pipeline for AI Economic News Impact Prediction

This module handles model training for BUY/SELL prediction:
- Time-series data splitting (2015-2022 train, 2023-2024 validation, 2025 test)
- Multiple model training (Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost)
- Model comparison and selection
- Performance evaluation
- Model saving

Purpose: Train ML models to predict market direction based on economic news impact
Input: Feature matrix with economic, technical, and news features
Output: Trained models with performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from pathlib import Path
import joblib

from src.utils import setup_logger


class ModelTrainer:
    """
    Trains ML models for economic news impact prediction.
    
    This class handles:
    - Time-series data splitting
    - Multiple model training
    - Model comparison
    - Performance evaluation
    - Model saving
    """
    
    def __init__(self, logger=None):
        """
        Initialize ModelTrainer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("ModelTrainer")
        self.models = {}
        self.best_model = None
        self.best_model_name = None
    
    def split_time_series_data(self, df: pd.DataFrame, date_column: str = 'Date') -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data by time periods to prevent data leakage.
        
        Args:
            df: DataFrame with features and target
            date_column: Name of date column
        
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        # Ensure date column is datetime
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.sort_values(date_column)
        
        # Define time periods
        train_end = '2022-12-31'
        val_end = '2024-12-31'
        
        if date_column in df.columns:
            train_df = df[df[date_column] <= train_end]
            val_df = df[(df[date_column] > train_end) & (df[date_column] <= val_end)]
            test_df = df[df[date_column] > val_end]
        else:
            # If no date column, use index-based split
            n = len(df)
            train_size = int(n * 0.7)
            val_size = int(n * 0.15)
            
            train_df = df.iloc[:train_size]
            val_df = df.iloc[train_size:train_size + val_size]
            test_df = df.iloc[train_size + val_size:]
        
        self.logger.info(f"Data split - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        return train_df, val_df, test_df
    
    def prepare_features(self, df: pd.DataFrame, target_column: str = 'Target') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for training.
        
        Args:
            df: DataFrame with features and target
            target_column: Name of target column
        
        Returns:
            Tuple of (X, y)
        """
        # Separate features and target
        if target_column in df.columns:
            y = df[target_column]
            X = df.drop(columns=[target_column])
        else:
            raise ValueError(f"Target column '{target_column}' not found in DataFrame")
        
        # Remove non-numeric columns
        X = X.select_dtypes(include=[np.number])
        
        # Remove columns with NaN
        X = X.fillna(0)
        
        self.logger.info(f"Features prepared - X shape: {X.shape}, y shape: {y.shape}")
        
        return X, y
    
    def train_logistic_regression(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        Train Logistic Regression model.
        
        Args:
            X_train: Training features
            y_train: Training target
        
        Returns:
            Trained model
        """
        model = LogisticRegression(
            random_state=42,
            max_iter=1000,
            class_weight='balanced'
        )
        model.fit(X_train, y_train)
        return model
    
    def train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        Train Random Forest model.
        
        Args:
            X_train: Training features
            y_train: Training target
        
        Returns:
            Trained model
        """
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        model.fit(X_train, y_train)
        return model
    
    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        Train XGBoost model.
        
        Args:
            X_train: Training features
            y_train: Training target
        
        Returns:
            Trained model
        """
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        return model
    
    def train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        Train LightGBM model.
        
        Args:
            X_train: Training features
            y_train: Training target
        
        Returns:
            Trained model
        """
        model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
        model.fit(X_train, y_train)
        return model
    
    def train_catboost(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        Train CatBoost model.
        
        Args:
            X_train: Training features
            y_train: Training target
        
        Returns:
            Trained model
        """
        model = cb.CatBoostClassifier(
            iterations=100,
            depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=False
        )
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target
        
        Returns:
            Dictionary with performance metrics
        """
        y_pred = model.predict(X_test)
        
        # Try to get probabilities for AUC
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, y_proba)
        except:
            auc = None
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'roc_auc': auc
        }
        
        return metrics
    
    def train_all_models(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Dict[str, Any]]:
        """
        Train all models and compare performance.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
        
        Returns:
            Dictionary with model results
        """
        results = {}
        
        # Train each model
        models_to_train = {
            'LogisticRegression': self.train_logistic_regression,
            'RandomForest': self.train_random_forest,
            'XGBoost': self.train_xgboost,
            'LightGBM': self.train_lightgbm,
            'CatBoost': self.train_catboost
        }
        
        for model_name, train_func in models_to_train.items():
            self.logger.info(f"Training {model_name}...")
            
            try:
                model = train_func(X_train, y_train)
                metrics = self.evaluate_model(model, X_val, y_val)
                
                results[model_name] = {
                    'model': model,
                    'metrics': metrics
                }
                
                self.models[model_name] = model
                self.logger.info(f"{model_name} - Accuracy: {metrics['accuracy']:.4f}")
                
            except Exception as e:
                self.logger.error(f"Error training {model_name}: {e}")
        
        # Select best model based on accuracy
        if results:
            best_model_name = max(results.keys(), key=lambda x: results[x]['metrics']['accuracy'])
            self.best_model = results[best_model_name]['model']
            self.best_model_name = best_model_name
            self.logger.info(f"Best model: {best_model_name}")
        
        return results
    
    def compare_models(self, results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        Compare model performance.
        
        Args:
            results: Dictionary with model results
        
        Returns:
            DataFrame with model comparison
        """
        comparison_data = []
        
        for model_name, result in results.items():
            metrics = result['metrics']
            comparison_data.append({
                'Model': model_name,
                'Accuracy': metrics['accuracy'],
                'Precision': metrics['precision'],
                'Recall': metrics['recall'],
                'F1 Score': metrics['f1_score'],
                'ROC AUC': metrics['roc_auc']
            })
        
        df = pd.DataFrame(comparison_data).sort_values('Accuracy', ascending=False)
        
        return df
    
    def save_model(self, model: Any, model_name: str, save_dir: Path):
        """
        Save trained model to disk.
        
        Args:
            model: Trained model
            model_name: Name of the model
            save_dir: Directory to save the model
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = save_dir / f"{model_name}.joblib"
        joblib.dump(model, model_path)
        
        self.logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    # Test model training
    trainer = ModelTrainer()
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    
    X = pd.DataFrame({
        'feature_1': np.random.randn(n_samples),
        'feature_2': np.random.randn(n_samples),
        'feature_3': np.random.randn(n_samples),
    })
    
    y = pd.Series(np.random.randint(0, 2, n_samples))
    
    # Split data
    train_size = int(n_samples * 0.7)
    val_size = int(n_samples * 0.15)
    
    X_train, X_val, X_test = X.iloc[:train_size], X.iloc[train_size:train_size+val_size], X.iloc[train_size+val_size:]
    y_train, y_val, y_test = y.iloc[:train_size], y.iloc[train_size:train_size+val_size], y.iloc[train_size+val_size:]
    
    # Train models
    results = trainer.train_all_models(X_train, y_train, X_val, y_val)
    
    # Compare models
    comparison = trainer.compare_models(results)
    print("Model Comparison:")
    print(comparison)
    
    # Save best model
    if trainer.best_model:
        trainer.save_model(trainer.best_model, trainer.best_model_name, Path("models"))
