"""
Economic Data API Module for Enhanced Economic Indicators

This module handles economic data from multiple sources:
- FRED API (Federal Reserve Economic Data) for US economic indicators
- 12Data API for financial and economic data
- News Data API for news sources
- FinHub API for market data
- Trading Economics API for global economic indicators

Purpose: Provide enhanced economic data for fundamental analysis
Input: Multiple economic data APIs
Output: Enhanced economic indicators and news data
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

from src.config import FRED_API_KEY, TWELVEDATA_API_KEY, NEWS_DATA_API_KEY
from src.utils import setup_logger


class EconomicDataAPI:
    """
    Manages economic data from multiple sources.
    
    This class handles:
    - FRED API integration for US economic indicators
    - 12Data API for financial data
    - News Data API for news sources
    - Enhanced economic indicators for fundamental analysis
    """
    
    def __init__(self, logger=None):
        """
        Initialize EconomicDataAPI.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("EconomicDataAPI")
        
        # API endpoints
        self.fred_base_url = "https://api.stlouisfed.org/fred"
        self.twelvedata_base_url = "https://api.twelvedata.com"
        self.newsdata_base_url = "https://newsdata.io/api/1"
        
        # API keys
        self.fred_key = FRED_API_KEY
        self.twelvedata_key = TWELVEDATA_API_KEY
        self.newsdata_key = NEWS_DATA_API_KEY
        
        # Common FRED series IDs
        self.fred_series = {
            'CPI': 'CPIAUCSL',           # Consumer Price Index
            'Core_CPI': 'CPILFESL',      # Core CPI
            'PPI': 'PPIACO',             # Producer Price Index
            'PCE': 'PCEPI',              # Personal Consumption Expenditures
            'GDP': 'GDP',                # Gross Domestic Product
            'FEDFUNDS': 'FEDFUNDS',      # Federal Funds Rate
            'PAYEMS': 'PAYEMS',          # Nonfarm Payrolls
            'UNRATE': 'UNRATE',          # Unemployment Rate
            'UMCSENT': 'UMCSENT',        # Consumer Confidence
            'HOUST': 'HOUST',            # Housing Starts
            'TOTALSA': 'TOTALSA',        # Retail Sales
            'NAPM': 'NAPM',              # Manufacturing PMI
            'NAPMPI': 'NAPMPI',          # Services PMI
            'ICSA': 'ICSA',              # Initial Jobless Claims
            'DGS10': 'DGS10',            # 10-Year Treasury Yield
            'DGS2': 'DGS2',              # 2-Year Treasury Yield
            'DTWEXBGS': 'DTWEXBGS',      # US Dollar Index
            'VIXCLS': 'VIXCLS',          # VIX
        }
    
    def get_fred_data(self, series_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get data from FRED API for a specific series.
        
        Args:
            series_id: FRED series ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            DataFrame with FRED data
        """
        try:
            url = f"{self.fred_base_url}/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.fred_key,
                'file_type': 'json',
                'observation_start': start_date,
                'observation_end': end_date
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                observations = data.get('observations', [])
                
                df_data = []
                for obs in observations:
                    if obs['value'] != '.':
                        df_data.append({
                            'date': obs['date'],
                            'value': float(obs['value'])
                        })
                
                df = pd.DataFrame(df_data)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    df.rename(columns={'value': series_id}, inplace=True)
                
                self.logger.info(f"Retrieved {len(df)} data points for FRED series {series_id}")
                return df
            else:
                self.logger.error(f"FRED API error for {series_id}: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching FRED data for {series_id}: {e}")
            return pd.DataFrame()
    
    def get_multiple_fred_series(self, series_list: List[str], start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get data for multiple FRED series.
        
        Args:
            series_list: List of FRED series IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            DataFrame with all series data
        """
        all_data = {}
        
        for series_id in series_list:
            df = self.get_fred_data(series_id, start_date, end_date)
            if not df.empty:
                all_data[series_id] = df[series_id]
            
            # Rate limiting
            time.sleep(0.1)
        
        if all_data:
            combined_df = pd.DataFrame(all_data)
            self.logger.info(f"Retrieved {len(combined_df)} data points for {len(series_list)} FRED series")
            return combined_df
        else:
            return pd.DataFrame()
    
    def search_fred_series(self, search_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for FRED series.
        
        Args:
            search_text: Text to search for
            limit: Maximum number of results
        
        Returns:
            List of matching series
        """
        try:
            url = f"{self.fred_base_url}/series/search"
            params = {
                'search_text': search_text,
                'api_key': self.fred_key,
                'file_type': 'json',
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                series = data.get('seriess', [])
                
                return [{
                    'id': s['id'],
                    'title': s['title'],
                    'observation_start': s.get('observation_start'),
                    'observation_end': s.get('observation_end'),
                    'frequency': s.get('frequency'),
                    'units': s.get('units')
                } for s in series]
            else:
                self.logger.error(f"FRED search error: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching FRED series: {e}")
            return []
    
    def get_twelvedata_economic_data(self, symbol: str, interval: str = 'daily', outputsize: int = 30) -> pd.DataFrame:
        """
        Get economic data from 12Data API.
        
        Args:
            symbol: Symbol to fetch data for
            interval: Data interval (daily, weekly, monthly)
            outputsize: Number of data points
        
        Returns:
            DataFrame with 12Data economic data
        """
        try:
            url = f"{self.twelvedata_base_url}/time_series"
            params = {
                'symbol': symbol,
                'interval': interval,
                'apikey': self.twelvedata_key,
                'outputsize': outputsize
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'values' in data:
                    df_data = []
                    for item in data['values']:
                        df_data.append({
                            'date': item['datetime'],
                            'open': float(item['open']),
                            'high': float(item['high']),
                            'low': float(item['low']),
                            'close': float(item['close']),
                            'volume': float(item.get('volume', 0))
                        })
                    
                    df = pd.DataFrame(df_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    
                    self.logger.info(f"Retrieved {len(df)} data points from 12Data for {symbol}")
                    return df
            else:
                self.logger.error(f"12Data API error for {symbol}: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching 12Data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_newsdata_news(self, query: str = None, language: str = 'en', country: str = 'us') -> List[Dict[str, Any]]:
        """
        Get news from NewsData API.
        
        Args:
            query: Search query for news
            language: Language code
            country: Country code
        
        Returns:
            List of news articles
        """
        try:
            url = f"{self.newsdata_base_url}/news"
            params = {
                'apikey': self.newsdata_key,
                'language': language,
                'country': country
            }
            
            if query:
                params['q'] = query
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data:
                    articles = []
                    for article in data['results']:
                        articles.append({
                            'title': article.get('title'),
                            'description': article.get('description'),
                            'link': article.get('link'),
                            'source': article.get('source_id'),
                            'published_date': article.get('pubDate'),
                            'category': article.get('category'),
                            'keywords': article.get('keywords', [])
                        })
                    
                    self.logger.info(f"Retrieved {len(articles)} articles from NewsData")
                    return articles
            else:
                self.logger.error(f"NewsData API error: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching NewsData: {e}")
            return []
    
    def get_enhanced_economic_indicators(self, indicators: List[str] = None) -> Dict[str, Any]:
        """
        Get enhanced economic indicators from multiple sources.
        
        Args:
            indicators: List of indicators to fetch (default: common indicators)
        
        Returns:
            Dictionary with enhanced economic data
        """
        if indicators is None:
            indicators = ['CPI', 'Core_CPI', 'FEDFUNDS', 'UNRATE', 'GDP', 'PAYEMS', 'DGS10', 'DTWEXBGS']
        
        # Get FRED data
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        fred_data = self.get_multiple_fred_series(indicators, start_date, end_date)
        
        # Calculate latest values and changes
        enhanced_data = {}
        
        if not fred_data.empty:
            for indicator in indicators:
                if indicator in fred_data.columns:
                    latest_value = fred_data[indicator].iloc[-1]
                    previous_value = fred_data[indicator].iloc[-2] if len(fred_data) > 1 else latest_value
                    change = latest_value - previous_value
                    change_pct = (change / previous_value * 100) if previous_value != 0 else 0
                    
                    enhanced_data[indicator] = {
                        'latest_value': latest_value,
                        'previous_value': previous_value,
                        'change': change,
                        'change_pct': change_pct,
                        'trend': 'up' if change > 0 else 'down' if change < 0 else 'neutral',
                        'data_points': len(fred_data[indicator].dropna())
                    }
        
        return {
            'indicators': enhanced_data,
            'data_source': 'FRED',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_global_economic_data(self, country: str = 'US') -> Dict[str, Any]:
        """
        Get global economic data for fundamental analysis.
        
        Args:
            country: Country code for data
        
        Returns:
            Dictionary with global economic data
        """
        # Map countries to FRED series
        country_series = {
            'US': ['CPI', 'FEDFUNDS', 'UNRATE', 'GDP'],
            'Canada': ['CPI', 'UNRATE', 'GDP'],  # Would need Canadian-specific series
            'UK': ['CPI', 'UNRATE', 'GDP'],     # Would need UK-specific series
        }
        
        indicators = country_series.get(country, country_series['US'])
        
        return self.get_enhanced_economic_indicators(indicators)


if __name__ == "__main__":
    # Test Economic Data API
    api = EconomicDataAPI()
    
    # Test FRED data
    print("Testing FRED API for CPI:")
    cpi_data = api.get_fred_data('CPI', start_date='2025-01-01')
    print(f"Data points: {len(cpi_data)}")
    if not cpi_data.empty:
        print(f"Latest CPI: {cpi_data['CPI'].iloc[-1]:.2f}")
    
    # Test FRED search
    print("\nTesting FRED Search for 'inflation':")
    search_results = api.search_fred_series('inflation', limit=5)
    print(f"Found {len(search_results)} series")
    for result in search_results[:3]:
        print(f"- {result['id']}: {result['title']}")
    
    # Test enhanced indicators
    print("\nTesting Enhanced Economic Indicators:")
    enhanced_data = api.get_enhanced_economic_indicators(['CPI', 'FEDFUNDS', 'UNRATE'])
    print(f"Indicators retrieved: {len(enhanced_data['indicators'])}")
    for indicator, data in enhanced_data['indicators'].items():
        print(f"- {indicator}: {data['latest_value']:.2f} ({data['change_pct']:+.2f}%)")
    
    # Test NewsData
    print("\nTesting NewsData API:")
    news = api.get_newsdata_news(query='economy', country='us')
    print(f"Articles retrieved: {len(news)}")
    if news:
        print(f"First article: {news[0]['title']}")
