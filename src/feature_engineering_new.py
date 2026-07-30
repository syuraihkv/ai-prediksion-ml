"""
Feature Engineering Module for AI Economic News Impact Prediction

This module creates features for the new prediction system:
- Economic features (CPI surprise, rate changes, inflation pressure)
- Technical features (EMA, RSI, MACD, ATR, Bollinger Bands)
- News features (sentiment scores, impact scores)
- Market indicator features (DXY, Treasury Yields, Fear & Greed)

Purpose: Transform raw data into predictive features for BUY/SELL classification
Input: Market data, economic data, news data
Output: Feature matrix ready for model training
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
try:
    from ta import add_all_ta_features
    from ta.trend import SMAIndicator, EMAIndicator, MACD
    from ta.momentum import RSIIndicator
    from ta.volatility import AverageTrueRange, BollingerBands
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    add_all_ta_features = None
    SMAIndicator = None
    EMAIndicator = None
    MACD = None
    RSIIndicator = None
    AverageTrueRange = None
    BollingerBands = None

from src.utils import setup_logger


class NewsImpactFeatureEngineer:
    """
    Creates features for economic news impact prediction.
    
    This class handles:
    - Economic event features
    - Technical indicators
    - News sentiment features
    - Market indicator features
    """
    
    def __init__(self, logger=None):
        """
        Initialize FeatureEngineer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("NewsImpactFeatureEngineer")
    
    def create_economic_features(self, economic_events: List[Dict]) -> pd.DataFrame:
        """
        Create features from economic events.
        
        Args:
            economic_events: List of economic event dictionaries
        
        Returns:
            DataFrame with economic features
        """
        if not economic_events:
            return pd.DataFrame()
        
        features = []
        
        for event in economic_events:
            feature = {
                'event_impact_high': 1 if event.get('impact') == 'HIGH' else 0,
                'event_impact_medium': 1 if event.get('impact') == 'MEDIUM' else 0,
                'event_category_monetary': 1 if event.get('category') == 'monetary' else 0,
                'event_category_inflation': 1 if event.get('category') == 'inflation' else 0,
                'event_category_employment': 1 if event.get('category') == 'employment' else 0,
                'event_category_growth': 1 if event.get('category') == 'growth' else 0,
            }
            
            # Calculate forecast vs previous difference
            try:
                forecast = float(event.get('forecast', '0').replace('%', ''))
                previous = float(event.get('previous', '0').replace('%', ''))
                feature['forecast_vs_previous'] = forecast - previous
                feature['forecast_increase'] = 1 if forecast > previous else 0
            except:
                feature['forecast_vs_previous'] = 0
                feature['forecast_increase'] = 0
            
            features.append(feature)
        
        return pd.DataFrame(features)
    
    def create_technical_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Create technical indicators from market data.
        
        Args:
            market_data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with technical features
        """
        if market_data.empty:
            return pd.DataFrame()
        
        df = market_data.copy()
        
        # Normalize column names to handle both uppercase and lowercase
        column_mapping = {}
        for col in df.columns:
            if col.lower() == 'close':
                column_mapping[col] = 'Close'
            elif col.lower() == 'high':
                column_mapping[col] = 'High'
            elif col.lower() == 'low':
                column_mapping[col] = 'Low'
            elif col.lower() == 'open':
                column_mapping[col] = 'Open'
            elif col.lower() == 'volume':
                column_mapping[col] = 'Volume'
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Check if required columns exist
        required_columns = ['Close', 'High', 'Low']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            self.logger.error(f"Available columns: {df.columns.tolist()}")
            return pd.DataFrame()
        
        # EMAs
        for window in [20, 50, 200]:
            df[f'EMA_{window}'] = EMAIndicator(close=df['Close'], window=window).ema_indicator()
        
        # RSI
        df['RSI_14'] = RSIIndicator(close=df['Close'], window=14).rsi()
        
        # MACD
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()
        
        # ATR
        df['ATR_14'] = AverageTrueRange(
            high=df['High'], low=df['Low'], close=df['Close'], window=14
        ).average_true_range()
        
        # Bollinger Bands
        bollinger = BollingerBands(close=df['Close'], window=20)
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        df['BB_Width'] = bollinger.bollinger_wband()
        
        # Returns
        df['Return_1d'] = df['Close'].pct_change()
        df['Return_5d'] = df['Close'].pct_change(5)
        df['Return_20d'] = df['Close'].pct_change(20)
        
        # Volatility
        df['Volatility_20d'] = df['Return_1d'].rolling(20).std()
        
        self.logger.info("Created technical features")
        
        return df
    
    def create_news_features(self, news_articles: List[Dict]) -> pd.DataFrame:
        """
        Create features from news articles.
        
        Args:
            news_articles: List of analyzed news articles
        
        Returns:
            DataFrame with news features
        """
        if not news_articles:
            return pd.DataFrame()
        
        # Aggregate sentiment
        sentiment_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
        impact_scores = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for article in news_articles:
            sentiment_scores[article.get('sentiment', 'neutral')] += 1
            impact_scores[article.get('impact', 'LOW')] += 1
        
        total = len(news_articles)
        
        features = {
            'news_sentiment_positive': sentiment_scores['positive'] / total if total > 0 else 0,
            'news_sentiment_neutral': sentiment_scores['neutral'] / total if total > 0 else 0,
            'news_sentiment_negative': sentiment_scores['negative'] / total if total > 0 else 0,
            'news_impact_high': impact_scores['HIGH'] / total if total > 0 else 0,
            'news_impact_medium': impact_scores['MEDIUM'] / total if total > 0 else 0,
            'news_impact_low': impact_scores['LOW'] / total if total > 0 else 0,
            'news_total_count': total
        }
        
        return pd.DataFrame([features])
    
    def create_market_indicator_features(self, indicator_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create features from market indicators (DXY, Treasury Yields, etc.).
        
        Args:
            indicator_data: Dictionary of indicator DataFrames
        
        Returns:
            DataFrame with indicator features
        """
        features = {}
        
        for indicator_name, df in indicator_data.items():
            if df.empty:
                continue
            
            # Latest value
            if 'close' in df.columns:
                features[f'{indicator_name}_latest'] = df['close'].iloc[-1]
                features[f'{indicator_name}_change_1d'] = df['close'].pct_change().iloc[-1]
                features[f'{indicator_name}_change_5d'] = df['close'].pct_change(5).iloc[-1]
        
        return pd.DataFrame([features])
    
    def create_target_labels(self, market_data: pd.DataFrame, lookahead: int = 1, 
                           threshold: float = 0.01) -> pd.Series:
        """
        Create binary target labels (BUY/SELL).
        
        Args:
            market_data: DataFrame with price data
            lookahead: Number of periods to look ahead
            threshold: Return threshold for classification
        
        Returns:
            Series with binary labels (1=BUY, 0=SELL)
        """
        future_return = market_data['Close'].pct_change(lookahead).shift(-lookahead)
        target = (future_return > threshold).astype(int)
        
        return target
    
    def combine_features(self, technical_df: pd.DataFrame, economic_df: pd.DataFrame,
                       news_df: pd.DataFrame, indicator_df: pd.DataFrame) -> pd.DataFrame:
        """
        Combine all feature types into single DataFrame.
        
        Args:
            technical_df: Technical features
            economic_df: Economic features
            news_df: News features
            indicator_df: Market indicator features
        
        Returns:
            Combined feature DataFrame
        """
        # Start with technical features (time series)
        combined = technical_df.copy()
        
        # Add economic features (broadcast to all rows)
        if not economic_df.empty:
            for col in economic_df.columns:
                combined[col] = economic_df[col].iloc[0] if len(economic_df) > 0 else 0
        
        # Add news features (broadcast to all rows)
        if not news_df.empty:
            for col in news_df.columns:
                combined[col] = news_df[col].iloc[0] if len(news_df) > 0 else 0
        
        # Add indicator features (broadcast to all rows)
        if not indicator_df.empty:
            for col in indicator_df.columns:
                combined[col] = indicator_df[col].iloc[0] if len(indicator_df) > 0 else 0
        
        self.logger.info(f"Combined features. Final shape: {combined.shape}")
        
        return combined


if __name__ == "__main__":
    # Test feature engineering
    engineer = NewsImpactFeatureEngineer()
    
    # Test with sample data
    sample_market_data = pd.DataFrame({
        'Open': [100, 101, 102],
        'High': [102, 103, 104],
        'Low': [99, 100, 101],
        'Close': [101, 102, 103],
        'Volume': [1000, 1100, 1200]
    })
    
    technical_features = engineer.create_technical_features(sample_market_data)
    print("Technical features created:")
    print(technical_features.head())
