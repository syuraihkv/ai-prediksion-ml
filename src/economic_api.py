"""
Economic Calendar API Module

This module handles economic calendar data integration:
- Fetching economic events from various sources
- Event categorization and impact assessment
- Historical economic data
- Real-time event updates

Purpose: Provide economic calendar data for news impact analysis
Input: Economic calendar APIs
Output: Structured economic event data
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import requests
from pathlib import Path

from src.utils import setup_logger


class EconomicAPI:
    """
    Manages economic calendar data from various sources.
    
    This class handles:
    - Fetching upcoming economic events
    - Historical event data
    - Impact classification
    - Event filtering by asset relevance
    """
    
    def __init__(self, logger=None):
        """
        Initialize EconomicAPI.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("EconomicAPI")
        
        # High impact economic events for XAU/USD and BTC/USD
        self.high_impact_events = [
            'FOMC', 'CPI', 'Core CPI', 'PCE', 'NFP', 
            'Interest Rate Decision', 'GDP', 'PMI', 
            'Retail Sales', 'Fed Speech'
        ]
        
        # Medium impact events
        self.medium_impact_events = [
            'ADP Employment', 'ISM Manufacturing', 'ISM Services',
            'Existing Home Sales', 'Trade Balance', 'Weekly Jobless Claims'
        ]
        
        # Event categories
        self.event_categories = {
            'monetary': ['FOMC', 'Interest Rate Decision', 'Fed Speech'],
            'inflation': ['CPI', 'Core CPI', 'PCE', 'PPI'],
            'employment': ['NFP', 'ADP Employment', 'Unemployment Rate', 'Weekly Jobless Claims'],
            'growth': ['GDP', 'Retail Sales', 'PMI', 'ISM Manufacturing', 'ISM Services'],
            'housing': ['Existing Home Sales', 'Building Permits']
        }
        
        # Asset-specific event relevance
        self.xau_relevant_events = [
            'FOMC', 'CPI', 'Core CPI', 'PCE', 'Interest Rate Decision',
            'Fed Speech', 'GDP', 'NFP', 'PMI'
        ]
        
        self.btc_relevant_events = [
            'FOMC', 'Interest Rate Decision', 'Fed Speech', 'CPI',
            'NFP', 'GDP', 'Risk sentiment events'
        ]
    
    def get_upcoming_events(self, days: int = 7, asset: str = 'XAU') -> List[Dict[str, Any]]:
        """
        Get upcoming economic events relevant to the specified asset.
        
        Args:
            days: Number of days ahead to look
            asset: Asset type ('XAU' or 'BTC')
        
        Returns:
            List of upcoming events
        """
        # In production, this would call APIs like:
        # - Forex Factory API
        # - Investing.com Economic Calendar API
        # - TradingView Economic Calendar
        
        # Mock data for demonstration
        relevant_events = self.xau_relevant_events if asset == 'XAU' else self.btc_relevant_events
        
        upcoming_events = [
            {
                'event': 'US CPI Release',
                'date': '2026-08-12',
                'time': '19:30',
                'timezone': 'WIB',
                'impact': 'HIGH',
                'forecast': '3.2%',
                'previous': '3.0%',
                'currency': 'USD',
                'category': 'inflation',
                'asset_relevance': asset
            },
            {
                'event': 'FOMC Meeting Minutes',
                'date': '2026-08-17',
                'time': '01:00',
                'timezone': 'WIB',
                'impact': 'HIGH',
                'forecast': 'N/A',
                'previous': 'Hawkish',
                'currency': 'USD',
                'category': 'monetary',
                'asset_relevance': asset
            },
            {
                'event': 'US Retail Sales',
                'date': '2026-08-15',
                'time': '19:30',
                'timezone': 'WIB',
                'impact': 'MEDIUM',
                'forecast': '0.4%',
                'previous': '0.2%',
                'currency': 'USD',
                'category': 'growth',
                'asset_relevance': asset
            }
        ]
        
        # Filter by asset relevance
        filtered_events = [
            event for event in upcoming_events 
            if event['event'] in relevant_events or event['category'] in ['monetary', 'inflation']
        ]
        
        self.logger.info(f"Retrieved {len(filtered_events)} upcoming events for {asset}")
        return filtered_events
    
    def get_historical_events(self, event_name: str, years: int = 3) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific event.
        
        Args:
            event_name: Name of the event
            years: Number of years of historical data
        
        Returns:
            List of historical events
        """
        # Mock historical data
        historical_events = [
            {
                'event': event_name,
                'date': '2025-03-15',
                'actual': '3.1%',
                'forecast': '3.0%',
                'surprise': '+0.1%',
                'market_reaction_xau': 'Gold ↓ 1.4%',
                'market_reaction_btc': 'BTC ↓ 0.8%',
                'prediction_accuracy': 'Correct'
            },
            {
                'event': event_name,
                'date': '2024-12-13',
                'actual': '2.9%',
                'forecast': '3.1%',
                'surprise': '-0.2%',
                'market_reaction_xau': 'Gold ↑ 0.8%',
                'market_reaction_btc': 'BTC ↑ 1.2%',
                'prediction_accuracy': 'Incorrect'
            },
            {
                'event': event_name,
                'date': '2024-09-14',
                'actual': '3.2%',
                'forecast': '3.0%',
                'surprise': '+0.2%',
                'market_reaction_xau': 'Gold ↓ 2.1%',
                'market_reaction_btc': 'BTC ↓ 1.5%',
                'prediction_accuracy': 'Correct'
            }
        ]
        
        self.logger.info(f"Retrieved {len(historical_events)} historical events for {event_name}")
        return historical_events
    
    def calculate_surprise_probability(self, forecast: str, previous: str) -> Dict[str, float]:
        """
        Calculate probability of surprise (actual vs forecast).
        
        Args:
            forecast: Forecast value
            previous: Previous value
        
        Returns:
            Dictionary with surprise probabilities
        """
        try:
            forecast_val = float(forecast.replace('%', ''))
            previous_val = float(previous.replace('%', ''))
            
            # Simple probability calculation based on historical volatility
            surprise_prob = {
                'upside': 0.35,
                'downside': 0.35,
                'as_expected': 0.30
            }
            
            # Adjust based on trend
            if forecast_val > previous_val:
                surprise_prob['upside'] += 0.1
                surprise_prob['downside'] -= 0.05
                surprise_prob['as_expected'] -= 0.05
            elif forecast_val < previous_val:
                surprise_prob['downside'] += 0.1
                surprise_prob['upside'] -= 0.05
                surprise_prob['as_expected'] -= 0.05
            
            return surprise_prob
            
        except:
            return {'upside': 0.33, 'downside': 0.33, 'as_expected': 0.34}
    
    def to_dataframe(self, events: List[Dict]) -> pd.DataFrame:
        """
        Convert events to DataFrame.
        
        Args:
            events: List of event dictionaries
        
        Returns:
            DataFrame with events
        """
        return pd.DataFrame(events)


if __name__ == "__main__":
    # Test economic API
    api = EconomicAPI()
    
    # Get upcoming events for XAU
    upcoming_xau = api.get_upcoming_events(days=7, asset='XAU')
    print(f"Upcoming events for XAU: {len(upcoming_xau)}")
    for event in upcoming_xau:
        print(f"- {event['event']}: {event['date']} {event['time']} ({event['impact']})")
    
    # Get upcoming events for BTC
    upcoming_btc = api.get_upcoming_events(days=7, asset='BTC')
    print(f"\nUpcoming events for BTC: {len(upcoming_btc)}")
    for event in upcoming_btc:
        print(f"- {event['event']}: {event['date']} {event['time']} ({event['impact']})")
