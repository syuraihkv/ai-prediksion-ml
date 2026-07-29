"""
AI Explanation Module for Economic News Impact Prediction

This module generates human-readable explanations for AI predictions:
- Combines economic factors, news sentiment, and technical indicators
- Generates comprehensive market analysis
- Creates structured explanations with reasoning
- Provides confidence assessment

Purpose: Explain AI predictions in human-readable format
Input: Prediction results, market data, news data, economic events
Output: Structured explanation with reasoning and confidence
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.utils import setup_logger


class AIExplainer:
    """
    Generates human-readable explanations for AI predictions.
    
    This class handles:
    - Combining multiple analysis sources
    - Generating structured explanations
    - Creating factor breakdowns
    - Providing confidence reasoning
    """
    
    def __init__(self, logger=None):
        """
        Initialize AIExplainer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("AIExplainer")
        
        # Factor weights for explanation generation
        self.factor_weights = {
            'economic': 0.35,
            'sentiment': 0.30,
            'technical': 0.20,
            'historical': 0.15
        }
    
    def generate_explanation(self, prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for prediction.
        
        Args:
            prediction_result: Prediction result from prediction system
        
        Returns:
            Comprehensive explanation dictionary
        """
        asset = prediction_result['asset']
        prediction = prediction_result['prediction']
        confidence = prediction_result['confidence']
        sentiment_summary = prediction_result.get('sentiment_summary', {})
        next_event = prediction_result.get('next_event')
        features = prediction_result.get('features', {})
        
        explanation = {
            'asset': asset,
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'reasoning': self._generate_reasoning(
                asset, prediction, sentiment_summary, next_event, features
            ),
            'supporting_factors': self._generate_supporting_factors(
                asset, sentiment_summary, features
            ),
            'risk_factors': self._generate_risk_factors(
                asset, sentiment_summary, next_event
            ),
            'market_context': self._generate_market_context(
                asset, sentiment_summary, next_event
            ),
            'ai_conclusion': self._generate_ai_conclusion(
                asset, prediction, confidence, sentiment_summary
            )
        }
        
        return explanation
    
    def _generate_reasoning(self, asset: str, prediction: str, 
                          sentiment_summary: Dict, next_event: Dict,
                          features: Dict) -> List[str]:
        """
        Generate reasoning points for the prediction.
        
        Args:
            asset: Asset symbol
            prediction: Prediction (BUY/SELL)
            sentiment_summary: Sentiment analysis results
            next_event: Next economic event
            features: Feature data
        
        Returns:
            List of reasoning points
        """
        reasoning = []
        
        # Sentiment reasoning
        overall_sentiment = sentiment_summary.get('overall_sentiment', 'neutral')
        if overall_sentiment == 'positive' and prediction == 'BUY':
            reasoning.append(f"Market sentiment is positive, supporting {prediction} prediction for {asset}.")
        elif overall_sentiment == 'negative' and prediction == 'SELL':
            reasoning.append(f"Market sentiment is negative, supporting {prediction} prediction for {asset}.")
        elif overall_sentiment == 'positive' and prediction == 'SELL':
            reasoning.append(f"Market sentiment is positive but technical factors suggest {prediction} for {asset}.")
        elif overall_sentiment == 'negative' and prediction == 'BUY':
            reasoning.append(f"Market sentiment is negative but technical factors suggest {prediction} for {asset}.")
        
        # Economic event reasoning
        if next_event:
            event_name = next_event.get('event', 'Unknown')
            event_impact = next_event.get('impact', 'MEDIUM')
            reasoning.append(f"Upcoming {event_name} ({event_impact} impact) may influence {asset} direction.")
            
            # Forecast vs previous
            forecast = next_event.get('forecast', 'N/A')
            previous = next_event.get('previous', 'N/A')
            if forecast != 'N/A' and previous != 'N/A':
                try:
                    forecast_val = float(forecast.replace('%', ''))
                    previous_val = float(previous.replace('%', ''))
                    if forecast_val > previous_val:
                        reasoning.append(f"Economic forecast ({forecast}) higher than previous ({previous}), suggesting potential tightening.")
                    elif forecast_val < previous_val:
                        reasoning.append(f"Economic forecast ({forecast}) lower than previous ({previous}), suggesting potential easing.")
                except:
                    pass
        
        # Technical reasoning
        if 'technical' in features:
            rsi = features['technical'].get('RSI_14')
            if rsi:
                if rsi > 70:
                    reasoning.append(f"RSI ({rsi:.1f}) indicates overbought conditions, supporting {prediction}.")
                elif rsi < 30:
                    reasoning.append(f"RSI ({rsi:.1f}) indicates oversold conditions, supporting {prediction}.")
        
        return reasoning
    
    def _generate_supporting_factors(self, asset: str, sentiment_summary: Dict,
                                    features: Dict) -> List[Dict[str, Any]]:
        """
        Generate supporting factors for the prediction.
        
        Args:
            asset: Asset symbol
            sentiment_summary: Sentiment analysis results
            features: Feature data
        
        Returns:
            List of supporting factors with scores
        """
        factors = []
        
        # Sentiment support
        overall_sentiment = sentiment_summary.get('overall_sentiment', 'neutral')
        confidence = sentiment_summary.get('average_confidence', 0.5)
        factors.append({
            'name': 'Market Sentiment',
            'value': overall_sentiment.title(),
            'support_score': confidence,
            'reasoning': f'Sentiment analysis with {confidence:.1%} confidence'
        })
        
        # Economic support
        if 'economic' in features:
            forecast_increase = features['economic'].get('forecast_increase', 0)
            factors.append({
                'name': 'Economic Indicator',
                'value': 'Increasing' if forecast_increase else 'Stable/Decreasing',
                'support_score': 0.7 if forecast_increase else 0.5,
                'reasoning': 'Economic data trend analysis'
            })
        
        # Technical support
        if 'technical' in features:
            macd = features['technical'].get('MACD', 0)
            factors.append({
                'name': 'Technical Momentum',
                'value': 'Bullish' if macd > 0 else 'Bearish',
                'support_score': 0.6,
                'reasoning': 'MACD indicator analysis'
            })
        
        # Sort by support score
        factors.sort(key=lambda x: x['support_score'], reverse=True)
        
        return factors
    
    def _generate_risk_factors(self, asset: str, sentiment_summary: Dict,
                             next_event: Dict) -> List[str]:
        """
        Generate risk factors for the prediction.
        
        Args:
            asset: Asset symbol
            sentiment_summary: Sentiment analysis results
            next_event: Next economic event
        
        Returns:
            List of risk factors
        """
        risks = []
        
        # Sentiment risk
        if 'sentiment_distribution' in sentiment_summary:
            dist = sentiment_summary['sentiment_distribution']
            if dist.get('neutral', 0) > 0.4:
                risks.append("High neutral sentiment suggests uncertain market direction")
        
        # Economic event risk
        if next_event:
            event_name = next_event.get('event', 'Unknown')
            risks.append(f"{event_name} actual data may differ from forecast, changing market direction")
        
        # Market volatility risk
        risks.append(f"Unexpected market volatility may reverse {asset} direction")
        
        return risks
    
    def _generate_market_context(self, asset: str, sentiment_summary: Dict,
                               next_event: Dict) -> str:
        """
        Generate market context summary.
        
        Args:
            asset: Asset symbol
            sentiment_summary: Sentiment analysis results
            next_event: Next economic event
        
        Returns:
            Market context string
        """
        context_parts = []
        
        context_parts.append(f"Asset: {asset}")
        
        if 'overall_sentiment' in sentiment_summary:
            context_parts.append(f"Current sentiment: {sentiment_summary['overall_sentiment']}")
        
        if 'sentiment_distribution' in sentiment_summary:
            dist = sentiment_summary['sentiment_distribution']
            context_parts.append(f"Sentiment breakdown: {dist.get('positive', 0):.0%} positive, {dist.get('negative', 0):.0%} negative, {dist.get('neutral', 0):.0%} neutral")
        
        if next_event:
            context_parts.append(f"Next event: {next_event.get('event', 'Unknown')} on {next_event.get('date', 'N/A')}")
        
        return " | ".join(context_parts)
    
    def _generate_ai_conclusion(self, asset: str, prediction: str, confidence: float,
                               sentiment_summary: Dict) -> str:
        """
        Generate final AI conclusion.
        
        Args:
            asset: Asset symbol
            prediction: Prediction (BUY/SELL)
            confidence: Confidence score
            sentiment_summary: Sentiment analysis results
        
        Returns:
            Formatted AI conclusion
        """
        direction = "bullish" if prediction == "BUY" else "bearish"
        
        conclusion = f"""
Based on comprehensive analysis of economic indicators, market sentiment, and technical factors:

**Prediction:** {prediction} {asset}

**Confidence:** {confidence:.1%}

**Market Direction:** {direction}

**Key Factors:**
- Market sentiment: {sentiment_summary.get('overall_sentiment', 'neutral').title()}
- Sentiment confidence: {sentiment_summary.get('average_confidence', 0.5):.1%}
- Technical indicators support {direction} outlook

**Expected Impact:**
{'Positive for' if prediction == 'BUY' else 'Negative for'} {asset} based on current market conditions and upcoming economic events.
"""
        return conclusion.strip()
    
    def format_for_display(self, explanation: Dict[str, Any]) -> str:
        """
        Format explanation for dashboard display.
        
        Args:
            explanation: Explanation dictionary
        
        Returns:
            Formatted explanation string
        """
        formatted = []
        
        formatted.append(f"## AI Analysis for {explanation['asset']}")
        formatted.append(f"**Prediction:** {explanation['prediction']}")
        formatted.append(f"**Confidence:** {explanation['confidence']:.1%}")
        formatted.append("")
        
        formatted.append("### Reasoning")
        for i, reason in enumerate(explanation['reasoning'], 1):
            formatted.append(f"{i}. {reason}")
        
        formatted.append("")
        formatted.append("### Supporting Factors")
        for factor in explanation['supporting_factors']:
            formatted.append(f"- **{factor['name']}**: {factor['value']} ({factor['support_score']:.1%} support)")
        
        if explanation['risk_factors']:
            formatted.append("")
            formatted.append("### Risk Factors")
            for risk in explanation['risk_factors']:
                formatted.append(f"- {risk}")
        
        formatted.append("")
        formatted.append("### Market Context")
        formatted.append(explanation['market_context'])
        
        formatted.append("")
        formatted.append("### AI Conclusion")
        formatted.append(explanation['ai_conclusion'])
        
        return "\n".join(formatted)


if __name__ == "__main__":
    # Test AI explainer
    explainer = AIExplainer()
    
    # Sample prediction result
    sample_prediction = {
        'asset': 'XAU',
        'prediction': 'BUY',
        'confidence': 0.82,
        'current_price': 1950.50,
        'sentiment_summary': {
            'overall_sentiment': 'positive',
            'average_confidence': 0.75,
            'sentiment_distribution': {'positive': 0.60, 'neutral': 0.25, 'negative': 0.15}
        },
        'next_event': {
            'event': 'US CPI Release',
            'date': '2026-08-12',
            'impact': 'HIGH',
            'forecast': '3.2%',
            'previous': '3.0%'
        },
        'features': {
            'technical': {
                'RSI_14': 55.0,
                'MACD': 0.5
            },
            'economic': {
                'forecast_increase': 1
            }
        }
    }
    
    # Generate explanation
    explanation = explainer.generate_explanation(sample_prediction)
    
    # Display formatted explanation
    print(explainer.format_for_display(explanation))
