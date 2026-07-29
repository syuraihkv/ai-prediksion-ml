"""
Market Data API Module

This module handles market data for XAU/USD and BTC/USD:
- Fetching OHLCV data
- Fetching additional market indicators (DXY, Treasury Yields, Fear & Greed)
- Real-time price updates
- Historical data management

Purpose: Provide market data for prediction and analysis
Input: Market data APIs (Yahoo Finance, etc.)
Output: Structured market data with indicators
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path

from src.utils import setup_logger
from src.crypto_api import CryptoAPI


class MarketAPI:
    """
    Manages market data for XAU/USD and BTC/USD.
    
    This class handles:
    - OHLCV data fetching
    - Additional indicators (DXY, Treasury Yields, Fear & Greed)
    - Real-time price updates
    - Data preprocessing
    """
    
    def __init__(self, logger=None):
        """
        Initialize MarketAPI.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("MarketAPI")
        
        # Initialize Crypto API for enhanced crypto data
        self.crypto_api = CryptoAPI()
        
        # Asset configurations
        self.assets = {
            'XAU': {
                'ticker': 'GC=F',
                'name': 'Gold',
                'indicators': ['DXY', 'US10Y', 'US2Y']
            },
            'BTC': {
                'ticker': 'BTC-USD',
                'name': 'Bitcoin',
                'indicators': ['DXY', 'US10Y', 'Fear_Greed']
            }
        }
        
        # Additional tickers for indicators
        self.indicator_tickers = {
            'DXY': 'DX-Y.NYB',  # US Dollar Index
            'US10Y': '^TNX',    # 10-Year Treasury Yield
            'US2Y': '^IRX',     # 2-Year Treasury Yield
        }
    
    def get_ohlcv_data(self, asset: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        Get OHLCV data for specified asset.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            DataFrame with OHLCV data
        """
        if asset not in self.assets:
            self.logger.error(f"Unknown asset: {asset}")
            return pd.DataFrame()
        
        ticker = self.assets[asset]['ticker']
        
        try:
            data = yf.download(ticker, period=period, interval=interval, progress=False)
            
            # Handle case where yfinance returns a tuple (newer versions)
            if isinstance(data, tuple):
                data = data[0] if data else pd.DataFrame()
            
            if data.empty:
                self.logger.warning(f"No data retrieved for {asset}")
                return pd.DataFrame()
            
            # Standardize column names
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0].lower() for col in data.columns]
            else:
                data.columns = [col.lower() for col in data.columns]
            
            self.logger.info(f"Retrieved {len(data)} data points for {asset}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {asset}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, asset: str) -> Optional[float]:
        """
        Get current price for specified asset with enhanced real-time tracking.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
        
        Returns:
            Current price or None
        """
        if asset not in self.assets:
            return None
        
        # For BTC, try to get enhanced crypto data first
        if asset == 'BTC':
            try:
                enhanced_crypto_data = self.crypto_api.get_enhanced_crypto_data('BTC')
                if enhanced_crypto_data and 'price' in enhanced_crypto_data:
                    price = enhanced_crypto_data['price']
                    self.logger.info(f"Current price for {asset}: ${price:.2f} (Crypto API)")
                    return price
            except Exception as e:
                self.logger.warning(f"Failed to get crypto API price for {asset}: {e}")
        
        # Fallback to Yahoo Finance
        ticker = self.assets[asset]['ticker']
        
        try:
            # Try to get most recent data with multiple attempts for better reliability
            for interval in ['1m', '5m', '15m', '1h']:
                try:
                    data = yf.download(ticker, period='5d', interval=interval, progress=False)
                    
                    if not data.empty and len(data) > 0:
                        current_price = data['Close'].iloc[-1]
                        self.logger.info(f"Current price for {asset}: ${current_price:.2f} (Yahoo Finance - interval: {interval})")
                        return float(current_price)
                except Exception as e:
                    self.logger.debug(f"Attempt with interval {interval} failed: {e}")
                    continue
            
            self.logger.warning(f"No current price data for {asset}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching current price for {asset}: {e}")
            return None
    
    def get_price_change(self, asset: str) -> Dict[str, Any]:
        """
        Get price change information for specified asset.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
        
        Returns:
            Dictionary with price change data
        """
        if asset not in self.assets:
            self.logger.error(f"Unknown asset: {asset}")
            return {}
        
        ticker = self.assets[asset]['ticker']
        
        try:
            # Try multiple intervals for better reliability
            for interval in ['1h', '1d']:
                try:
                    data = yf.download(ticker, period='5d', interval=interval, progress=False)
                    
                    if not data.empty and len(data) >= 2:
                        current_price = float(data['Close'].iloc[-1])
                        previous_price = float(data['Close'].iloc[-2])
                        price_change = current_price - previous_price
                        price_change_pct = (price_change / previous_price) * 100
                        
                        self.logger.info(f"Price change for {asset}: {price_change:+.2f} ({price_change_pct:+.2f}%)")
                        
                        return {
                            'current_price': current_price,
                            'previous_price': previous_price,
                            'price_change': price_change,
                            'price_change_pct': price_change_pct,
                            'timestamp': datetime.now().isoformat()
                        }
                except Exception as e:
                    self.logger.debug(f"Price change attempt with interval {interval} failed: {e}")
                    continue
            
            self.logger.warning(f"Insufficient data for price change calculation for {asset}")
            return {}
        except Exception as e:
            self.logger.error(f"Error calculating price change for {asset}: {e}")
            return {}
    
    def get_technical_indicators(self, asset: str) -> Dict[str, Any]:
        """
        Get technical indicators for specified asset.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
        
        Returns:
            Dictionary with technical indicators
        """
        if asset not in self.assets:
            self.logger.error(f"Unknown asset: {asset}")
            return {}
        
        try:
            data = self.get_ohlcv_data(asset, period='1mo', interval='1d')
            
            if data.empty or len(data) < 14:
                self.logger.warning(f"Insufficient data for technical indicators for {asset}")
                return {}
            
            # Normalize column names to handle both uppercase and lowercase
            column_mapping = {}
            for col in data.columns:
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
            
            data.rename(columns=column_mapping, inplace=True)
            
            # Check if Close column exists
            if 'Close' not in data.columns:
                self.logger.error(f"Close column not found. Available columns: {data.columns.tolist()}")
                return {}
            
            # Calculate RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Calculate MACD
            exp12 = data['Close'].ewm(span=12, adjust=False).mean()
            exp26 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9, adjust=False).mean()
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            
            # Calculate Moving Averages
            ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = data['Close'].rolling(window=50).mean().iloc[-1]
            
            # Determine trend
            current_price = data['Close'].iloc[-1]
            trend = 'BULLISH' if current_price > ma20 > ma50 else 'BEARISH' if current_price < ma20 < ma50 else 'NEUTRAL'
            
            return {
                'rsi': current_rsi,
                'macd': current_macd,
                'macd_signal': current_signal,
                'ma20': ma20,
                'ma50': ma50,
                'current_price': current_price,
                'trend': trend,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators for {asset}: {e}")
            return {}
    
    def get_indicator_data(self, indicator: str, period: str = '1y') -> pd.DataFrame:
        """
        Get data for additional market indicators.
        
        Args:
            indicator: Indicator name ('DXY', 'US10Y', 'US2Y')
            period: Time period
        
        Returns:
            DataFrame with indicator data
        """
        if indicator not in self.indicator_tickers:
            self.logger.warning(f"Unknown indicator: {indicator}")
            return pd.DataFrame()
        
        ticker = self.indicator_tickers[indicator]
        
        try:
            data = yf.download(ticker, period=period, progress=False)
            
            if data.empty:
                self.logger.warning(f"No data retrieved for {indicator}")
                return pd.DataFrame()
            
            data.columns = [col.lower() for col in data.columns]
            self.logger.info(f"Retrieved {len(data)} data points for {indicator}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {indicator}: {e}")
            return pd.DataFrame()
    
    def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        """
        Get Fear & Greed Index for crypto markets.
        
        Returns:
            Dictionary with Fear & Greed data or None
        """
        # In production, this would call the Alternative.me API
        # For now, return mock data
        try:
            return {
                'value': 45,
                'classification': 'Neutral',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error fetching Fear & Greed Index: {e}")
            return None
    
    def get_complete_market_data(self, asset: str, period: str = '1y') -> Dict[str, pd.DataFrame]:
        """
        Get complete market data including main asset and indicators.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
            period: Time period
        
        Returns:
            Dictionary with DataFrames for asset and indicators
        """
        data = {
            'main': self.get_ohlcv_data(asset, period),
        }
        
        # Get asset-specific indicators
        if asset in self.assets:
            for indicator in self.assets[asset]['indicators']:
                if indicator == 'Fear_Greed':
                    # Fear & Greed is a single value, not time series
                    continue
                data[indicator] = self.get_indicator_data(indicator, period)
        
        return data
    
    def calculate_returns(self, data: pd.DataFrame, periods: int = 1) -> pd.Series:
        """
        Calculate returns for price data.
        
        Args:
            data: DataFrame with price data
            periods: Number of periods for return calculation
        
        Returns:
            Series with returns
        """
        if 'close' not in data.columns:
            return pd.Series()
        
        return data['close'].pct_change(periods)
    
    def calculate_volatility(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Calculate rolling volatility.
        
        Args:
            data: DataFrame with price data
            window: Rolling window size
        
        Returns:
            Series with volatility
        """
        if 'close' not in data.columns:
            return pd.Series()
        
        returns = self.calculate_returns(data)
        return returns.rolling(window=window).std()


if __name__ == "__main__":
    # Test market API
    api = MarketAPI()
    
    # Test XAU data
    print("Testing XAU/USD data:")
    xau_data = api.get_ohlcv_data('XAU', period='1mo')
    print(f"Data points: {len(xau_data)}")
    if not xau_data.empty:
        print(f"Latest price: {xau_data['close'].iloc[-1]:.2f}")
    
    # Test BTC data
    print("\nTesting BTC/USD data:")
    btc_data = api.get_ohlcv_data('BTC', period='1mo')
    print(f"Data points: {len(btc_data)}")
    if not btc_data.empty:
        print(f"Latest price: {btc_data['close'].iloc[-1]:.2f}")
    
    # Test indicators
    print("\nTesting DXY data:")
    dxy_data = api.get_indicator_data('DXY', period='1mo')
    print(f"Data points: {len(dxy_data)}")
    
    # Test current prices
    print("\nCurrent prices:")
    print(f"XAU/USD: {api.get_current_price('XAU')}")
    print(f"BTC/USD: {api.get_current_price('BTC')}")
