"""
Crypto Data API Module for Enhanced BTC Data

This module handles crypto data from multiple sources:
- CoinMarketCap API for comprehensive crypto data
- CoinGecko API for additional crypto metrics
- Enhanced market data for BTC/USD and other cryptocurrencies

Purpose: Provide enhanced crypto data for prediction and analysis
Input: CoinMarketCap API, CoinGecko API
Output: Enhanced crypto market data with additional metrics
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

from src.config import COINMARKETCAP_API_KEY, COINGECKO_API_KEY
from src.utils import setup_logger


class CryptoAPI:
    """
    Manages crypto data from multiple sources.
    
    This class handles:
    - CoinMarketCap API integration
    - CoinGecko API integration
    - Enhanced BTC/USD data
    - Additional crypto metrics
    """
    
    def __init__(self, logger=None):
        """
        Initialize CryptoAPI.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("CryptoAPI")
        
        # API endpoints
        self.coinmarketcap_base_url = "https://pro-api.coinmarketcap.com/v1"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        
        # API keys
        self.coinmarketcap_key = COINMARKETCAP_API_KEY
        self.coingecko_key = COINGECKO_API_KEY
        
        # Asset mappings
        self.coinmarketcap_ids = {
            'BTC': '1',
            'ETH': '1027',
            'XRP': '52',
            'ADA': '2010',
            'SOL': '5426'
        }
        
        self.coingecko_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'SOL': 'solana'
        }
    
    def get_coinmarketcap_data(self, asset: str = 'BTC') -> Dict[str, Any]:
        """
        Get crypto data from CoinMarketCap API.
        
        Args:
            asset: Asset symbol ('BTC', 'ETH', etc.)
        
        Returns:
            Dictionary with CoinMarketCap data
        """
        if asset not in self.coinmarketcap_ids:
            self.logger.error(f"Unknown asset for CoinMarketCap: {asset}")
            return {}
        
        try:
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': self.coinmarketcap_key
            }
            
            # Get latest quotes
            url = f"{self.coinmarketcap_base_url}/cryptocurrency/quotes/latest"
            params = {
                'id': self.coinmarketcap_ids[asset],
                'convert': 'USD'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                crypto_data = data['data'][self.coinmarketcap_ids[asset]]
                
                return {
                    'price': crypto_data['quote']['USD']['price'],
                    'volume_24h': crypto_data['quote']['USD']['volume_24h'],
                    'market_cap': crypto_data['quote']['USD']['market_cap'],
                    'percent_change_1h': crypto_data['quote']['USD']['percent_change_1h'],
                    'percent_change_24h': crypto_data['quote']['USD']['percent_change_24h'],
                    'percent_change_7d': crypto_data['quote']['USD']['percent_change_7d'],
                    'percent_change_30d': crypto_data['quote']['USD']['percent_change_30d'],
                    'market_cap_dominance': crypto_data['quote']['USD'].get('market_cap_dominance', 0),
                    'fully_diluted_market_cap': crypto_data['quote']['USD'].get('fully_diluted_market_cap', 0),
                    'circulating_supply': crypto_data['circulating_supply'],
                    'total_supply': crypto_data.get('total_supply', 0),
                    'max_supply': crypto_data.get('max_supply', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.logger.error(f"CoinMarketCap API error: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching CoinMarketCap data: {e}")
            return {}
    
    def get_coingecko_data(self, asset: str = 'BTC') -> Dict[str, Any]:
        """
        Get crypto data from CoinGecko API.
        
        Args:
            asset: Asset symbol ('BTC', 'ETH', etc.)
        
        Returns:
            Dictionary with CoinGecko data
        """
        if asset not in self.coingecko_ids:
            self.logger.error(f"Unknown asset for CoinGecko: {asset}")
            return {}
        
        try:
            headers = {
                'x-cg-demo-api-key': self.coingecko_key
            }
            
            # Get current data
            url = f"{self.coingecko_base_url}/coins/{self.coingecko_ids[asset]}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data.get('market_data', {})
                
                return {
                    'price': market_data.get('current_price', {}).get('usd', 0),
                    'price_btc': market_data.get('current_price', {}).get('btc', 0),
                    'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                    'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                    'price_change_14d': market_data.get('price_change_percentage_14d', 0),
                    'price_change_30d': market_data.get('price_change_percentage_30d', 0),
                    'price_change_1y': market_data.get('price_change_percentage_1y', 0),
                    'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                    'market_cap_rank': market_data.get('market_cap_rank', 0),
                    'total_volume': market_data.get('total_volume', {}).get('usd', 0),
                    'high_24h': market_data.get('high_24h', {}).get('usd', 0),
                    'low_24h': market_data.get('low_24h', {}).get('usd', 0),
                    'ath': market_data.get('ath', {}).get('usd', 0),
                    'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd', 0),
                    'ath_date': market_data.get('ath_date', {}).get('usd', ''),
                    'atl': market_data.get('atl', {}).get('usd', 0),
                    'atl_change_percentage': market_data.get('atl_change_percentage', {}).get('usd', 0),
                    'atl_date': market_data.get('atl_date', {}).get('usd', ''),
                    'circulating_supply': market_data.get('circulating_supply', 0),
                    'total_supply': market_data.get('total_supply', 0),
                    'max_supply': market_data.get('max_supply', 0),
                    'market_dominance': market_data.get('market_cap', {}).get('usd', 0) / market_data.get('total_volume', {}).get('usd', 1) if market_data.get('total_volume', {}).get('usd', 0) > 0 else 0,
                    'community_score': data.get('community_score', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.logger.error(f"CoinGecko API error: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching CoinGecko data: {e}")
            return {}
    
    def get_enhanced_crypto_data(self, asset: str = 'BTC') -> Dict[str, Any]:
        """
        Get enhanced crypto data combining both APIs.
        
        Args:
            asset: Asset symbol ('BTC', 'ETH', etc.)
        
        Returns:
            Dictionary with combined crypto data
        """
        # Get data from both sources
        coinmarketcap_data = self.get_coinmarketcap_data(asset)
        coingecko_data = self.get_coingecko_data(asset)
        
        # Combine data with CoinMarketCap as primary
        combined_data = {}
        
        if coinmarketcap_data:
            combined_data.update(coinmarketcap_data)
            combined_data['primary_source'] = 'CoinMarketCap'
        elif coingecko_data:
            combined_data.update(coingecko_data)
            combined_data['primary_source'] = 'CoinGecko'
        else:
            return {}
        
        # Add CoinGecko specific data if available
        if coingecko_data:
            combined_data['coingecko_data'] = coingecko_data
            combined_data['has_coingecko'] = True
        else:
            combined_data['has_coingecko'] = False
        
        return combined_data
    
    def get_crypto_ohlcv(self, asset: str = 'BTC', days: int = 30) -> pd.DataFrame:
        """
        Get OHLCV data from CoinGecko.
        
        Args:
            asset: Asset symbol ('BTC', 'ETH', etc.)
            days: Number of days of historical data
        
        Returns:
            DataFrame with OHLCV data
        """
        if asset not in self.coingecko_ids:
            self.logger.error(f"Unknown asset for CoinGecko OHLCV: {asset}")
            return pd.DataFrame()
        
        try:
            headers = {
                'x-cg-demo-api-key': self.coingecko_key
            }
            
            url = f"{self.coingecko_base_url}/coins/{self.coingecko_ids[asset]}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                prices = data.get('prices', [])
                market_caps = data.get('market_caps', [])
                total_volumes = data.get('total_volumes', [])
                
                # Create DataFrame
                df_data = []
                for i in range(len(prices)):
                    timestamp = prices[i][0]
                    date = datetime.fromtimestamp(timestamp / 1000)
                    
                    row = {
                        'timestamp': timestamp,
                        'date': date,
                        'open': prices[i][1],  # Using price as open (simplified)
                        'high': prices[i][1],  # Using price as high (simplified)
                        'low': prices[i][1],   # Using price as low (simplified)
                        'close': prices[i][1],  # Using price as close
                        'volume': total_volumes[i][1] if i < len(total_volumes) else 0,
                        'market_cap': market_caps[i][1] if i < len(market_caps) else 0
                    }
                    df_data.append(row)
                
                df = pd.DataFrame(df_data)
                df.set_index('date', inplace=True)
                
                self.logger.info(f"Retrieved {len(df)} days of OHLCV data for {asset}")
                return df
            else:
                self.logger.error(f"CoinGecko OHLCV API error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching CoinGecko OHLCV data: {e}")
            return pd.DataFrame()
    
    def get_crypto_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get Crypto Fear & Greed Index from alternative.me.
        
        Returns:
            Dictionary with fear & greed data
        """
        try:
            url = "https://api.alternative.me/fng/"
            params = {'limit': 1}
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    fear_greed = data['data'][0]
                    return {
                        'value': int(fear_greed['value']),
                        'classification': fear_greed['value_classification'],
                        'timestamp': fear_greed['timestamp'],
                        'time_until_update': fear_greed.get('time_until_update', '')
                    }
            return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching Fear & Greed Index: {e}")
            return {}


if __name__ == "__main__":
    # Test crypto API
    api = CryptoAPI()
    
    # Test CoinMarketCap data
    print("Testing CoinMarketCap API for BTC:")
    cmc_data = api.get_coinmarketcap_data('BTC')
    print(f"Price: ${cmc_data.get('price', 0):.2f}")
    print(f"24h Change: {cmc_data.get('percent_change_24h', 0):.2f}%")
    print(f"Market Cap: ${cmc_data.get('market_cap', 0):,.0f}")
    
    # Test CoinGecko data
    print("\nTesting CoinGecko API for BTC:")
    cg_data = api.get_coingecko_data('BTC')
    print(f"Price: ${cg_data.get('price', 0):.2f}")
    print(f"24h Change: {cg_data.get('price_change_24h', 0):.2f}%")
    print(f"Market Cap: ${cg_data.get('market_cap', 0):,.0f}")
    
    # Test combined data
    print("\nTesting Enhanced Crypto Data:")
    enhanced_data = api.get_enhanced_crypto_data('BTC')
    print(f"Primary Source: {enhanced_data.get('primary_source', 'N/A')}")
    print(f"Price: ${enhanced_data.get('price', 0):.2f}")
    print(f"Has CoinGecko: {enhanced_data.get('has_coingecko', False)}")
    
    # Test OHLCV data
    print("\nTesting OHLCV Data:")
    ohlcv_df = api.get_crypto_ohlcv('BTC', days=7)
    print(f"Data points: {len(ohlcv_df)}")
    print(f"Columns: {ohlcv_df.columns.tolist()}")
    
    # Test Fear & Greed Index
    print("\nTesting Fear & Greed Index:")
    fng = api.get_crypto_fear_greed_index()
    print(f"Value: {fng.get('value', 'N/A')}")
    print(f"Classification: {fng.get('classification', 'N/A')}")
