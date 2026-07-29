"""
Fundamental Analysis Module for AI Economic News Impact Prediction

This module handles fundamental analysis validation:
- Economic indicator analysis
- Event impact assessment
- Fundamental signal generation
- Correlation with market movements

Purpose: Validate predictions using fundamental analysis
Input: Economic events, market data, indicators
Output: Fundamental analysis signals and validation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.utils import setup_logger
from src.economic_data_api import EconomicDataAPI


class FundamentalAnalyzer:
    """
    Performs fundamental analysis for prediction validation.
    
    This class handles:
    - Economic indicator analysis
    - Event impact assessment
    - Fundamental signal generation
    - Market correlation analysis
    """
    
    def __init__(self, logger=None):
        """
        Initialize FundamentalAnalyzer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("FundamentalAnalyzer")
        
        # Initialize Economic Data API
        self.economic_data_api = EconomicDataAPI()
        
        # Economic indicator weights for XAU
        self.xau_indicator_weights = {
            'interest_rate': 0.25,
            'inflation': 0.20,
            'dollar_strength': 0.20,
            'treasury_yields': 0.15,
            'geopolitical': 0.10,
            'demand_supply': 0.10
        }
        
        # Economic indicator weights for BTC
        self.btc_indicator_weights = {
            'interest_rate': 0.20,
            'inflation': 0.15,
            'dollar_strength': 0.15,
            'regulatory': 0.20,
            'institutional_adoption': 0.15,
            'market_sentiment': 0.15
        }
    
    def analyze_fundamental_signals(self, asset: str, economic_events: List[Dict], 
                                   market_data: Dict) -> Dict[str, Any]:
        """
        Analyze fundamental signals for prediction validation.
        
        Args:
            asset: Asset symbol ('XAU' or 'BTC')
            economic_events: List of economic events
            market_data: Market data dictionary
        
        Returns:
            Fundamental analysis results
        """
        if asset not in ['XAU', 'BTC']:
            self.logger.error(f"Unknown asset: {asset}")
            return {}
        
        # Get appropriate indicator weights
        weights = self.xau_indicator_weights if asset == 'XAU' else self.btc_indicator_weights
        
        # Analyze economic events
        event_signals = self._analyze_economic_events(economic_events, asset)
        
        # Analyze market indicators
        market_signals = self._analyze_market_indicators(market_data, asset)
        
        # Combine signals
        combined_signal = self._combine_signals(event_signals, market_signals, weights)
        
        return {
            'asset': asset,
            'fundamental_signal': combined_signal['signal'],
            'fundamental_strength': combined_signal['strength'],
            'event_signals': event_signals,
            'market_signals': market_signals,
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_economic_events(self, events: List[Dict], asset: str) -> Dict[str, Any]:
        """
        Analyze economic events for fundamental signals.
        
        Args:
            events: List of economic events
            asset: Asset symbol
        
        Returns:
            Event analysis results
        """
        if not events:
            return {'signal': 'NEUTRAL', 'strength': 0.0, 'details': []}
        
        signals = []
        
        for event in events:
            event_signal = self._assess_event_impact(event, asset)
            signals.append({
                'event': event.get('event', 'Unknown'),
                'signal': event_signal['signal'],
                'strength': event_signal['strength'],
                'reasoning': event_signal['reasoning']
            })
        
        # Aggregate signals
        buy_signals = sum(1 for s in signals if s['signal'] == 'BUY')
        sell_signals = sum(1 for s in signals if s['signal'] == 'SELL')
        total_signals = len(signals)
        
        if buy_signals > sell_signals:
            overall_signal = 'BUY'
            strength = buy_signals / total_signals if total_signals > 0 else 0
        elif sell_signals > buy_signals:
            overall_signal = 'SELL'
            strength = sell_signals / total_signals if total_signals > 0 else 0
        else:
            overall_signal = 'NEUTRAL'
            strength = 0.5
        
        return {
            'signal': overall_signal,
            'strength': strength,
            'details': signals
        }
    
    def _assess_event_impact(self, event: Dict, asset: str) -> Dict[str, Any]:
        """
        Assess the impact of a single economic event.
        
        Args:
            event: Economic event dictionary
            asset: Asset symbol
        
        Returns:
            Event impact assessment
        """
        event_name = event.get('event', '').lower()
        impact = event.get('impact', 'MEDIUM')
        forecast = event.get('forecast', 'N/A')
        previous = event.get('previous', 'N/A')
        
        # Default neutral signal
        signal = 'NEUTRAL'
        strength = 0.5
        reasoning = "No clear directional bias"
        
        # Interest rate events
        if 'interest rate' in event_name or 'fomc' in event_name or 'fed' in event_name:
            try:
                forecast_val = float(forecast.replace('%', '')) if forecast != 'N/A' else 0
                previous_val = float(previous.replace('%', '')) if previous != 'N/A' else 0
                
                if forecast_val > previous_val:
                    # Rate hike - generally negative for both assets
                    signal = 'SELL'
                    strength = 0.7 if impact == 'HIGH' else 0.5
                    reasoning = "Interest rate increase expected, negative for risk assets"
                elif forecast_val < previous_val:
                    # Rate cut - generally positive for both assets
                    signal = 'BUY'
                    strength = 0.7 if impact == 'HIGH' else 0.5
                    reasoning = "Interest rate decrease expected, positive for risk assets"
            except:
                pass
        
        # Inflation events (CPI, PCE)
        elif 'cpi' in event_name or 'pce' in event_name or 'inflation' in event_name:
            try:
                forecast_val = float(forecast.replace('%', '')) if forecast != 'N/A' else 0
                previous_val = float(previous.replace('%', '')) if previous != 'N/A' else 0
                
                if forecast_val > previous_val:
                    # Higher inflation - complex impact
                    if asset == 'XAU':
                        signal = 'BUY'  # Gold as inflation hedge
                        reasoning = "Higher inflation expected, positive for gold as hedge"
                    else:
                        signal = 'SELL'  # Higher rates may follow
                        reasoning = "Higher inflation may lead to rate hikes, negative for BTC"
                    strength = 0.6 if impact == 'HIGH' else 0.4
                elif forecast_val < previous_val:
                    # Lower inflation
                    if asset == 'XAU':
                        signal = 'SELL'
                        reasoning = "Lower inflation expected, reduces gold appeal"
                    else:
                        signal = 'BUY'
                        reasoning = "Lower inflation may reduce rate hike pressure, positive for BTC"
                    strength = 0.6 if impact == 'HIGH' else 0.4
            except:
                pass
        
        # Employment events (NFP, unemployment)
        elif 'nfp' in event_name or 'employment' in event_name or 'unemployment' in event_name:
            try:
                forecast_val = float(forecast.replace('%', '')) if forecast != 'N/A' else 0
                previous_val = float(previous.replace('%', '')) if previous != 'N/A' else 0
                
                if forecast_val > previous_val and 'unemployment' not in event_name:
                    # Strong employment - generally positive for economy
                    signal = 'SELL'  # May lead to rate hikes
                    reasoning = "Strong employment data may lead to rate hikes"
                    strength = 0.6 if impact == 'HIGH' else 0.4
                elif forecast_val < previous_val and 'unemployment' not in event_name:
                    # Weak employment - generally negative for economy
                    signal = 'BUY'  # May delay rate hikes
                    reasoning = "Weak employment data may delay rate hikes"
                    strength = 0.6 if impact == 'HIGH' else 0.4
            except:
                pass
        
        # GDP events
        elif 'gdp' in event_name:
            try:
                forecast_val = float(forecast.replace('%', '')) if forecast != 'N/A' else 0
                previous_val = float(previous.replace('%', '')) if previous != 'N/A' else 0
                
                if forecast_val > previous_val:
                    signal = 'SELL'  # Strong growth may lead to rate hikes
                    reasoning = "Strong GDP growth may lead to rate hikes"
                    strength = 0.6 if impact == 'HIGH' else 0.4
                elif forecast_val < previous_val:
                    signal = 'BUY'  # Weak growth may delay rate hikes
                    reasoning = "Weak GDP growth may delay rate hikes"
                    strength = 0.6 if impact == 'HIGH' else 0.4
            except:
                pass
        
        # Adjust strength based on impact level
        if impact == 'HIGH':
            strength = min(1.0, strength + 0.2)
        elif impact == 'LOW':
            strength = max(0.3, strength - 0.2)
        
        return {
            'signal': signal,
            'strength': strength,
            'reasoning': reasoning
        }
    
    def _analyze_market_indicators(self, market_data: Dict, asset: str) -> Dict[str, Any]:
        """
        Analyze market indicators for fundamental signals.
        
        Args:
            market_data: Market data dictionary
            asset: Asset symbol
        
        Returns:
            Market indicator analysis
        """
        signals = {}
        
        # Analyze DXY (US Dollar Index)
        if 'dxy' in market_data:
            dxy_value = market_data['dxy']
            if dxy_value > 105:
                signals['dxy'] = {'signal': 'SELL', 'strength': 0.7, 'reasoning': 'Strong dollar negative for assets'}
            elif dxy_value < 100:
                signals['dxy'] = {'signal': 'BUY', 'strength': 0.7, 'reasoning': 'Weak dollar positive for assets'}
            else:
                signals['dxy'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reasoning': 'Dollar in neutral range'}
        
        # Analyze Treasury Yields
        if 'us10y' in market_data:
            yield_value = market_data['us10y']
            if yield_value > 4.5:
                signals['treasury'] = {'signal': 'SELL', 'strength': 0.6, 'reasoning': 'High yields negative for assets'}
            elif yield_value < 3.5:
                signals['treasury'] = {'signal': 'BUY', 'strength': 0.6, 'reasoning': 'Low yields positive for assets'}
            else:
                signals['treasury'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reasoning': 'Yields in neutral range'}
        
        # Analyze price trend
        if 'price_change_pct' in market_data:
            price_change = market_data['price_change_pct']
            # Handle both scalar and Series values
            if isinstance(price_change, (int, float)):
                if price_change > 2:
                    signals['price_trend'] = {'signal': 'BUY', 'strength': 0.6, 'reasoning': 'Strong upward momentum'}
                elif price_change < -2:
                    signals['price_trend'] = {'signal': 'SELL', 'strength': 0.6, 'reasoning': 'Strong downward momentum'}
                else:
                    signals['price_trend'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reasoning': 'Price in consolidation'}
            else:
                # Handle Series or other types
                try:
                    price_change_val = float(price_change)
                    if price_change_val > 2:
                        signals['price_trend'] = {'signal': 'BUY', 'strength': 0.6, 'reasoning': 'Strong upward momentum'}
                    elif price_change_val < -2:
                        signals['price_trend'] = {'signal': 'SELL', 'strength': 0.6, 'reasoning': 'Strong downward momentum'}
                    else:
                        signals['price_trend'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reasoning': 'Price in consolidation'}
                except:
                    signals['price_trend'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reasoning': 'Unable to determine trend'}
        
        return signals
    
    def _combine_signals(self, event_signals: Dict, market_signals: Dict, 
                       weights: Dict[str, float]) -> Dict[str, Any]:
        """
        Combine event and market signals.
        
        Args:
            event_signals: Event analysis results
            market_signals: Market indicator analysis
            weights: Indicator weights
        
        Returns:
            Combined signal analysis
        """
        all_signals = []
        
        # Add event signals
        if event_signals.get('details'):
            for detail in event_signals['details']:
                all_signals.append({
                    'signal': detail['signal'],
                    'strength': detail['strength'],
                    'weight': 0.5  # Event signals have moderate weight
                })
        
        # Add market signals
        for indicator, signal_data in market_signals.items():
            all_signals.append({
                'signal': signal_data['signal'],
                'strength': signal_data['strength'],
                'weight': weights.get(indicator, 0.1)
            })
        
        if not all_signals:
            return {'signal': 'NEUTRAL', 'strength': 0.5}
        
        # Calculate weighted signal
        buy_score = 0
        sell_score = 0
        total_weight = 0
        
        for signal in all_signals:
            weight = signal['weight']
            strength = signal['strength']
            
            if signal['signal'] == 'BUY':
                buy_score += weight * strength
            elif signal['signal'] == 'SELL':
                sell_score += weight * strength
            
            total_weight += weight
        
        # Determine final signal
        if buy_score > sell_score:
            final_signal = 'BUY'
            final_strength = buy_score / total_weight if total_weight > 0 else 0.5
        elif sell_score > buy_score:
            final_signal = 'SELL'
            final_strength = sell_score / total_weight if total_weight > 0 else 0.5
        else:
            final_signal = 'NEUTRAL'
            final_strength = 0.5
        
        return {
            'signal': final_signal,
            'strength': final_strength
        }


if __name__ == "__main__":
    # Test fundamental analyzer
    analyzer = FundamentalAnalyzer()
    
    # Sample economic events
    sample_events = [
        {
            'event': 'US Interest Rate Decision',
            'date': '2026-08-12',
            'time': '19:30',
            'impact': 'HIGH',
            'forecast': '5.25%',
            'previous': '5.00%'
        },
        {
            'event': 'US CPI Release',
            'date': '2026-08-13',
            'time': '19:30',
            'impact': 'HIGH',
            'forecast': '3.2%',
            'previous': '3.0%'
        }
    ]
    
    # Sample market data
    sample_market_data = {
        'dxy': 103.5,
        'us10y': 4.2,
        'price_change_pct': 1.5
    }
    
    # Analyze fundamental signals
    fundamental_analysis = analyzer.analyze_fundamental_signals('XAU', sample_events, sample_market_data)
    
    print("Fundamental Analysis Results:")
    print(f"Signal: {fundamental_analysis['fundamental_signal']}")
    print(f"Strength: {fundamental_analysis['fundamental_strength']:.1%}")
    print(f"Event Signals: {fundamental_analysis['event_signals']}")
    print(f"Market Signals: {fundamental_analysis['market_signals']}")
