"""
Database Module for AI Economic News Impact Prediction

This module handles database operations for the new system:
- economic_events table
- news_articles table
- predictions table
- Database initialization and management

Purpose: Store and retrieve economic events, news articles, and predictions
Input: Various data types (events, articles, predictions)
Output: Database operations (CRUD)
"""

import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from src.utils import setup_logger


class DatabaseManager:
    """
    Manages database operations for the prediction system.
    
    This class handles:
    - Database initialization
    - Economic events storage
    - News articles storage
    - Predictions storage
    - Data retrieval
    """
    
    def __init__(self, db_path: Path = None, logger=None):
        """
        Initialize DatabaseManager.
        
        Args:
            db_path: Path to database file
            logger: Optional logger instance
        """
        self.logger = logger or setup_logger("DatabaseManager")
        
        if db_path is None:
            # Default database path
            project_root = Path(__file__).parent.parent
            db_path = project_root / "database" / "predictions.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """
        Initialize database with required tables.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create economic_events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS economic_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    datetime TEXT NOT NULL,
                    forecast TEXT,
                    previous TEXT,
                    actual TEXT,
                    impact TEXT NOT NULL,
                    currency TEXT,
                    category TEXT,
                    asset_relevance TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create news_articles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    link TEXT,
                    summary TEXT,
                    sentiment TEXT,
                    confidence REAL,
                    impact TEXT,
                    asset TEXT,
                    published TEXT,
                    collected_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    current_price REAL,
                    next_event TEXT,
                    sentiment_summary TEXT,
                    model_used TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_economic_events_datetime 
                ON economic_events(datetime)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_news_articles_asset 
                ON news_articles(asset)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_asset 
                ON predictions(asset)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
                ON predictions(timestamp)
            """)
            
            conn.commit()
        
        self.logger.info(f"Database initialized at {self.db_path}")
    
    def save_economic_event(self, event: Dict[str, Any]) -> int:
        """
        Save economic event to database.
        
        Args:
            event: Economic event dictionary
        
        Returns:
            ID of inserted record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO economic_events 
                (event, datetime, forecast, previous, actual, impact, currency, category, asset_relevance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.get('event'),
                event.get('datetime', f"{event.get('date', '')} {event.get('time', '')}"),
                event.get('forecast'),
                event.get('previous'),
                event.get('actual'),
                event.get('impact'),
                event.get('currency'),
                event.get('category'),
                event.get('asset_relevance')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_economic_events_batch(self, events: List[Dict[str, Any]]) -> List[int]:
        """
        Save multiple economic events to database.
        
        Args:
            events: List of economic event dictionaries
        
        Returns:
            List of inserted record IDs
        """
        ids = []
        for event in events:
            event_id = self.save_economic_event(event)
            ids.append(event_id)
        
        return ids
    
    def get_economic_events(self, asset: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        Retrieve economic events from database.
        
        Args:
            asset: Optional asset filter
            days: Number of days to look back
        
        Returns:
            List of economic events
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM economic_events WHERE 1=1"
            params = []
            
            if asset:
                query += " AND asset_relevance = ?"
                params.append(asset)
            
            if days:
                cutoff_date = (datetime.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
                query += " AND datetime >= ?"
                params.append(cutoff_date)
            
            query += " ORDER BY datetime DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def save_news_article(self, article: Dict[str, Any]) -> int:
        """
        Save news article to database.
        
        Args:
            article: News article dictionary
        
        Returns:
            ID of inserted record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO news_articles 
                (title, source, link, summary, sentiment, confidence, impact, asset, published, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.get('title'),
                article.get('source'),
                article.get('link'),
                article.get('summary'),
                article.get('sentiment'),
                article.get('confidence'),
                article.get('impact'),
                article.get('asset'),
                article.get('published'),
                article.get('collected_at')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_news_articles_batch(self, articles: List[Dict[str, Any]]) -> List[int]:
        """
        Save multiple news articles to database.
        
        Args:
            articles: List of news article dictionaries
        
        Returns:
            List of inserted record IDs
        """
        ids = []
        for article in articles:
            article_id = self.save_news_article(article)
            ids.append(article_id)
        
        return ids
    
    def get_news_articles(self, asset: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve news articles from database.
        
        Args:
            asset: Optional asset filter
            limit: Maximum number of articles to retrieve
        
        Returns:
            List of news articles
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM news_articles WHERE 1=1"
            params = []
            
            if asset:
                query += " AND asset = ?"
                params.append(asset)
            
            query += " ORDER BY collected_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def save_prediction(self, prediction: Dict[str, Any]) -> int:
        """
        Save prediction to database.
        
        Args:
            prediction: Prediction dictionary
        
        Returns:
            ID of inserted record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert sentiment_summary to JSON string for storage
            import json
            sentiment_json = json.dumps(prediction.get('sentiment_summary', {}))
            
            cursor.execute("""
                INSERT INTO predictions 
                (asset, prediction, confidence, current_price, next_event, sentiment_summary, model_used, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.get('asset'),
                prediction.get('prediction'),
                prediction.get('confidence'),
                prediction.get('current_price'),
                json.dumps(prediction.get('next_event', {})) if prediction.get('next_event') else None,
                sentiment_json,
                prediction.get('model_used'),
                prediction.get('timestamp')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_predictions(self, asset: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve predictions from database.
        
        Args:
            asset: Optional asset filter
            limit: Maximum number of predictions to retrieve
        
        Returns:
            List of predictions
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM predictions WHERE 1=1"
            params = []
            
            if asset:
                query += " AND asset = ?"
                params.append(asset)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Parse JSON fields
            results = []
            for row in rows:
                row_dict = dict(row)
                try:
                    import json
                    if row_dict['sentiment_summary']:
                        row_dict['sentiment_summary'] = json.loads(row_dict['sentiment_summary'])
                    if row_dict['next_event']:
                        row_dict['next_event'] = json.loads(row_dict['next_event'])
                except:
                    pass
                results.append(row_dict)
            
            return results
    
    def get_prediction_accuracy(self, asset: str = None) -> Dict[str, Any]:
        """
        Calculate prediction accuracy statistics.
        
        Args:
            asset: Optional asset filter
        
        Returns:
            Dictionary with accuracy statistics
        """
        predictions = self.get_predictions(asset=asset, limit=1000)
        
        if not predictions:
            return {
                'total_predictions': 0,
                'buy_predictions': 0,
                'sell_predictions': 0,
                'average_confidence': 0.0,
                'accuracy': 0.0
            }
        
        # For now, return basic statistics
        # In production, this would compare predictions with actual market movements
        total = len(predictions)
        
        # Count predictions by type
        buy_count = sum(1 for p in predictions if p['prediction'] == 'BUY')
        sell_count = sum(1 for p in predictions if p['prediction'] == 'SELL')
        
        # Average confidence
        avg_confidence = sum(p['confidence'] for p in predictions) / total if total > 0 else 0
        
        return {
            'total_predictions': total,
            'buy_predictions': buy_count,
            'sell_predictions': sell_count,
            'average_confidence': avg_confidence,
            'accuracy': 0.0  # Would need actual results to calculate
        }
    
    def clear_old_data(self, days: int = 30):
        """
        Clear old data from database.
        
        Args:
            days: Number of days of data to keep
        """
        cutoff_date = (datetime.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clear old news articles
            cursor.execute("""
                DELETE FROM news_articles 
                WHERE collected_at < ?
            """, (cutoff_date,))
            
            # Clear old predictions
            cursor.execute("""
                DELETE FROM predictions 
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            conn.commit()
        
        self.logger.info(f"Cleared data older than {days} days")


if __name__ == "__main__":
    # Test database manager
    db = DatabaseManager()
    
    # Test saving economic event
    event = {
        'event': 'US CPI Release',
        'date': '2026-08-12',
        'time': '19:30',
        'forecast': '3.2%',
        'previous': '3.0%',
        'impact': 'HIGH',
        'currency': 'USD',
        'category': 'inflation',
        'asset_relevance': 'XAU'
    }
    event_id = db.save_economic_event(event)
    print(f"Saved economic event with ID: {event_id}")
    
    # Test saving news article
    article = {
        'title': 'Fed signals higher rates',
        'source': 'Reuters',
        'link': 'https://example.com',
        'summary': 'Federal Reserve signals higher interest rates',
        'sentiment': 'negative',
        'confidence': 0.75,
        'impact': 'HIGH',
        'asset': 'XAU',
        'published': '2026-08-12',
        'collected_at': datetime.now().isoformat()
    }
    article_id = db.save_news_article(article)
    print(f"Saved news article with ID: {article_id}")
    
    # Test saving prediction
    prediction = {
        'asset': 'XAU',
        'prediction': 'SELL',
        'confidence': 0.82,
        'current_price': 1950.50,
        'next_event': event,
        'sentiment_summary': {'overall_sentiment': 'negative', 'average_confidence': 0.75},
        'model_used': 'XGBoost',
        'timestamp': datetime.now().isoformat()
    }
    prediction_id = db.save_prediction(prediction)
    print(f"Saved prediction with ID: {prediction_id}")
    
    # Test retrieval
    print("\nRetrieved economic events:")
    events = db.get_economic_events(days=7)
    for e in events[:3]:
        print(f"- {e['event']}: {e['datetime']}")
    
    print("\nPrediction accuracy:")
    accuracy = db.get_prediction_accuracy()
    print(f"Total predictions: {accuracy['total_predictions']}")
    print(f"Average confidence: {accuracy['average_confidence']:.1%}")
