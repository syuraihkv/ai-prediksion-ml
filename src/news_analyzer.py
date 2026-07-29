"""
News Analyzer Module

This module handles financial news analysis:
- Collecting news from various sources
- Asset-specific news filtering
- Sentiment analysis using FinBERT
- News impact scoring
- Real-time news updates
- Indonesian language translation

Purpose: Analyze financial news for market prediction
Input: News sources (RSS, web)
Output: Structured news data with sentiment and impact
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time
from deep_translator import GoogleTranslator

from src.utils import setup_logger


class NewsAnalyzer:
    """
    Analyzes financial news for market prediction.
    
    This class handles:
    - News collection from RSS feeds
    - Asset-specific news filtering
    - Sentiment analysis
    - News impact assessment
    """
    
    def __init__(self, logger=None):
        """
        Initialize NewsAnalyzer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("NewsAnalyzer")
        
        # Initialize translator
        self.translator = GoogleTranslator(source='auto', target='id')
        
        # Major financial news RSS feeds
        self.rss_feeds = {
            'Reuters': 'https://www.reuters.com/rssFeed/marketsNews',
            'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
            'MarketWatch': 'https://www.marketwatch.com/rss/topstories'
        }
        
        # Asset-specific keywords
        self.xau_keywords = [
            'gold', 'xau', 'precious metal', 'inflation', 'cpi',
            'federal reserve', 'fed', 'interest rate', 'dollar',
            'usd', 'treasury', 'bond yield', 'safe haven', 'commodity'
        ]
        
        self.btc_keywords = [
            'bitcoin', 'btc', 'crypto', 'cryptocurrency', 'digital asset',
            'federal reserve', 'fed', 'interest rate', 'inflation', 'risk sentiment',
            'regulation', 'sec', 'etf', 'institutional'
        ]
        
        # Impact keywords
        self.high_impact_keywords = [
            'surge', 'plunge', 'crash', 'rally', 'breakthrough',
            'crisis', 'shock', 'emergency', 'unprecedented', 'major'
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def collect_news(self, asset: str = 'XAU', max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Collect news relevant to specified asset.
        
        Args:
            asset: Asset type ('XAU' or 'BTC')
            max_articles: Maximum number of articles to collect
        
        Returns:
            List of relevant articles
        """
        keywords = self.xau_keywords if asset == 'XAU' else self.btc_keywords
        all_articles = []
        
        for source, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:max_articles // len(self.rss_feeds)]:
                    article = {
                        'source': source,
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', ''),
                        'asset': asset,
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    # Filter by asset relevance
                    if self._is_asset_relevant(article['title'] + ' ' + article['summary'], keywords):
                        # Assess impact
                        article['impact'] = self._assess_impact(article['title'] + ' ' + article['summary'])
                        all_articles.append(article)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error collecting from {source}: {e}")
        
        self.logger.info(f"Collected {len(all_articles)} articles for {asset}")
        return all_articles
    
    def _is_asset_relevant(self, text: str, keywords: List[str]) -> bool:
        """
        Check if text is relevant to the asset.
        
        Args:
            text: Text to check
            keywords: Asset-specific keywords
        
        Returns:
            True if relevant, False otherwise
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def _assess_impact(self, text: str) -> str:
        """
        Assess the impact level of news.
        
        Args:
            text: Text to assess
        
        Returns:
            Impact level ('HIGH', 'MEDIUM', 'LOW')
        """
        text_lower = text.lower()
        
        # Check for high impact keywords
        if any(keyword in text_lower for keyword in self.high_impact_keywords):
            return 'HIGH'
        
        # Check for medium impact indicators
        medium_indicators = ['increase', 'decrease', 'rise', 'fall', 'change', 'report', 'data']
        if any(indicator in text_lower for indicator in medium_indicators):
            return 'MEDIUM'
        
        return 'LOW'
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text (using keyword-based approach for now).
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment analysis results
        """
        # In production, this would use FinBERT
        # For now, use keyword-based analysis
        
        bullish_keywords = ['rally', 'surge', 'gain', 'rise', 'increase', 'growth', 'bullish', 'positive', 'strong']
        bearish_keywords = ['decline', 'fall', 'drop', 'decrease', 'loss', 'weakness', 'bearish', 'negative', 'pressure']
        
        text_lower = text.lower()
        
        bullish_count = sum(1 for keyword in bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in bearish_keywords if keyword in text_lower)
        
        if bullish_count > bearish_count:
            sentiment = 'positive'
            confidence = min(0.8, 0.5 + (bullish_count / (bullish_count + bearish_count + 1)) * 0.3)
        elif bearish_count > bullish_count:
            sentiment = 'negative'
            confidence = min(0.8, 0.5 + (bearish_count / (bullish_count + bearish_count + 1)) * 0.3)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'bullish_score': bullish_count,
            'bearish_score': bearish_count
        }
    
    def analyze_news_batch(self, articles: List[Dict]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment and impact direction for a batch of articles with Indonesian translation.
        
        Args:
            articles: List of articles
        
        Returns:
            List of articles with sentiment analysis, impact direction, and translation
        """
        for article in articles:
            text = article['title'] + ' ' + article['summary']
            sentiment_result = self.analyze_sentiment(text)
            article.update(sentiment_result)
            
            # Determine impact direction
            article['impact_direction'] = self._determine_impact_direction(text, sentiment_result['sentiment'])
            
            # Translate to Indonesian
            try:
                title_id = self.translator.translate(article.get('title', ''))[:200]  # Limit length
                summary_id = self.translator.translate(article.get('summary', ''))[:300]  # Limit length
            except:
                title_id = article.get('title', '')
                summary_id = article.get('summary', '')
            
            article['title_id'] = title_id
            article['summary_id'] = summary_id
        
        return articles
    
    def _determine_impact_direction(self, text: str, sentiment: str) -> str:
        """
        Determine the impact direction (BUY/SELL/HOLD) based on news content.
        
        Args:
            text: News text
            sentiment: Sentiment analysis result
        
        Returns:
            Impact direction ('BUY', 'SELL', 'HOLD')
        """
        text_lower = text.lower()
        
        # BUY indicators
        buy_keywords = [
            'positive', 'growth', 'increase', 'rise', 'gain', 'profit', 'bullish',
            'strength', 'support', 'upgrade', 'beat', 'exceed', 'outperform',
            'rally', 'surge', 'boost', 'favorable', 'optimistic', 'recovery'
        ]
        
        # SELL indicators
        sell_keywords = [
            'negative', 'decline', 'decrease', 'fall', 'loss', 'bearish',
            'weakness', 'resistance', 'downgrade', 'miss', 'underperform',
            'drop', 'plunge', 'cut', 'unfavorable', 'pessimistic', 'concern'
        ]
        
        buy_score = sum(1 for keyword in buy_keywords if keyword in text_lower)
        sell_score = sum(1 for keyword in sell_keywords if keyword in text_lower)
        
        if sentiment == 'positive' and buy_score > sell_score:
            return 'BUY'
        elif sentiment == 'negative' and sell_score > buy_score:
            return 'SELL'
        elif buy_score > sell_score:
            return 'BUY'
        elif sell_score > buy_score:
            return 'SELL'
        else:
            return 'HOLD'
    
    def get_asset_sentiment_summary(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Get sentiment summary for an asset.
        
        Args:
            articles: List of analyzed articles
        
        Returns:
            Sentiment summary statistics
        """
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'average_confidence': 0.0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'total_articles': 0
            }
        
        # Count sentiments
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        total_confidence = 0
        
        for article in articles:
            sentiment_counts[article['sentiment']] += 1
            total_confidence += article['confidence']
        
        total = len(articles)
        avg_confidence = total_confidence / total if total > 0 else 0
        
        # Determine overall sentiment
        if sentiment_counts['positive'] > sentiment_counts['negative']:
            overall = 'positive'
        elif sentiment_counts['negative'] > sentiment_counts['positive']:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'average_confidence': avg_confidence,
            'sentiment_distribution': {
                k: v / total for k, v in sentiment_counts.items()
            },
            'total_articles': total
        }
    
    def to_dataframe(self, articles: List[Dict]) -> pd.DataFrame:
        """
        Convert articles to DataFrame.
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            DataFrame with articles
        """
        return pd.DataFrame(articles)


if __name__ == "__main__":
    # Test news analyzer
    analyzer = NewsAnalyzer()
    
    # Test XAU news collection
    print("Testing XAU news collection:")
    xau_news = analyzer.collect_news(asset='XAU', max_articles=10)
    print(f"Collected {len(xau_news)} articles")
    
    # Test sentiment analysis
    if xau_news:
        analyzed = analyzer.analyze_news_batch(xau_news)
        summary = analyzer.get_asset_sentiment_summary(analyzed)
        print(f"Overall sentiment: {summary['overall_sentiment']}")
        print(f"Average confidence: {summary['average_confidence']:.2%}")
