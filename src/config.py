"""
Configuration settings for the Financial ML Trading System.

This file contains all configurable parameters for the system including:
- Data sources and instruments
- Timeframes and periods
- Model parameters
- Database settings
- Trading parameters
"""

from typing import List, Dict, Any
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    # Load variables from a local .env file (if present) into the environment.
    # This file is never committed - see .env.example for the template.
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    # python-dotenv not installed: environment variables set another way
    # (shell export, systemd, Docker, Streamlit Cloud secrets, etc.) still work.
    pass

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
DATABASE_DIR = PROJECT_ROOT / "database"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Database
DATABASE_PATH = DATABASE_DIR / "trading.db"

# Instruments configuration
INSTRUMENTS: Dict[str, Dict[str, Any]] = {
    "BTC": {
        "yahoo_ticker": "BTC-USD",
        "name": "Bitcoin",
        "type": "crypto"
    },
    "XAU": {
        "yahoo_ticker": "GC=F",
        "name": "Gold",
        "type": "commodity"
    },
    "NASDAQ": {
        "yahoo_ticker": "^IXIC",
        "name": "NASDAQ",
        "type": "index"
    }
}

# Timeframes
TIMEFRAMES: List[str] = ["1d", "1h", "4h"]

# Data collection settings
HISTORICAL_YEARS: int = 5
START_DATE = "2019-01-01"
END_DATE = None  # None means current date

# Note: Yahoo Finance limits intraday data to last 730 days (2 years)
# Daily data can go back much further
INTRADAY_MAX_YEARS: int = 2

# Macro economic indicators (FRED)
MACRO_INDICATORS: List[str] = [
    "CPIAUCSL",  # CPI
    "CPILFESL",  # Core CPI
    "PPIACO",    # PPI
    "PCEPI",     # PCE
    "GDP",       # GDP
    "FEDFUNDS",  # Federal Funds Rate
    "PAYEMS",    # Nonfarm Payrolls
    "UNRATE",    # Unemployment Rate
    "UMCSENT",   # Consumer Confidence
    "HOUST",     # Housing Starts
    "TOTALSA",   # Retail Sales
    "NAPM",      # Manufacturing PMI
    "NAPMPI",    # Services PMI
    "ICSA",      # Initial Jobless Claims
]

# Market sentiment indicators
SENTIMENT_INDICATORS: List[str] = [
    "VIX",      # CBOE Volatility Index
    "DXY",      # US Dollar Index
    "US10Y",    # 10-Year Treasury Yield
]

# Feature engineering settings
TECHNICAL_INDICATORS: List[str] = [
    "EMA", "SMA", "RSI", "MACD", "ATR", "Bollinger_Bands",
    "Momentum", "ROC", "Stochastic", "ADX", "CCI", "OBV", "VWAP"
]

ROLLING_WINDOWS: List[int] = [5, 10, 20, 50, 100, 200]
LAG_FEATURES: List[int] = [1, 2, 3, 5, 10]

# Label settings
LABEL_TYPE: str = "binary"  # "binary" or "multiclass"
LOOKAHEAD_PERIOD: int = 1  # Number of periods to look ahead for label
THRESHOLD: float = 0.01  # 1% threshold for BUY/SELL signals

# Model settings
MODELS_TO_COMPARE: List[str] = [
    "LogisticRegression",
    "RandomForest",
    "ExtraTrees",
    "XGBoost",
    "LightGBM",
    "CatBoost"
]

# Validation settings
VALIDATION_METHOD: str = "walk_forward"  # "walk_forward" or "time_series_cv"
TRAIN_SIZE: float = 0.7  # 70% for training
VALIDATION_SIZE: float = 0.15  # 15% for validation
TEST_SIZE: float = 0.15  # 15% for testing

# Walk-forward validation settings
N_FOLDS: int = 5
MIN_TRAIN_SIZE: int = 1000  # Minimum number of samples for training

# Hyperparameter tuning
TUNING_METHOD: str = "optuna"  # "optuna", "random_search", "grid_search"
N_TRIALS: int = 100
TIMEOUT: int = 3600  # 1 hour timeout

# Backtesting settings
INITIAL_CAPITAL: float = 100000.0
COMMISSION: float = 0.001  # 0.1% commission
SLIPPAGE: float = 0.0001  # 0.01% slippage
POSITION_SIZE: float = 0.1  # 10% of capital per trade

# Real-time trading settings
UPDATE_INTERVAL: int = 60  # seconds
MAX_POSITIONS: int = 3
RISK_PER_TRADE: float = 0.02  # 2% risk per trade

# Random seed for reproducibility
RANDOM_STATE: int = 42

# Streamlit settings
STREAMLIT_TITLE = "Financial ML Trading System"
STREAMLIT_LAYOUT = "wide"

# News Analysis settings
NEWS_SOURCES: List[str] = [
    "Reuters", "Bloomberg", "CNBC", "Financial Times", "WSJ", 
    "Yahoo Finance", "MarketWatch"
]

NEWS_KEYWORDS: List[str] = [
    "gold", "xau", "precious metal", "inflation", "cpi",
    "federal reserve", "fed", "interest rate", "dollar",
    "usd", "treasury", "bond yield", "economic", "market",
    "trading", "investment", "forex", "commodity"
]

MAX_ARTICLES_PER_SOURCE: int = 10
NEWS_RETENTION_DAYS: int = 7

# Economic Calendar settings
HIGH_IMPACT_EVENTS: List[str] = [
    "CPI", "PPI", "GDP", "FOMC", "Non-Farm Payrolls",
    "Retail Sales", "ISM Manufacturing", "ISM Services",
    "Unemployment Rate", "Consumer Confidence", "Durable Goods"
]

MEDIUM_IMPACT_EVENTS: List[str] = [
    "ADP Employment", "Building Permits", "CB Consumer Confidence",
    "Core CPI", "Core PPI", "Existing Home Sales", "New Home Sales",
    "Trade Balance", "Weekly Jobless Claims"
]

# Sentiment Analysis settings
SENTIMENT_MODEL: str = "ProsusAI/finbert"
SENTIMENT_THRESHOLD: float = 0.6  # Minimum confidence for sentiment classification

# Historical Analysis settings
HISTORICAL_YEARS: int = 3
MIN_SIMILAR_EVENTS: int = 2
HISTORICAL_ACCURACY_THRESHOLD: float = 0.7

# AI Explanation settings
FACTOR_WEIGHTS: Dict[str, float] = {
    "economic": 0.35,
    "sentiment": 0.30,
    "historical": 0.25,
    "technical": 0.10
}

MIN_CONFIDENCE_THRESHOLD: float = 0.5

# Logging
LOG_LEVEL: str = "INFO"

# Crypto API Keys
# IMPORTANT: these are loaded from environment variables / a local .env file,
# never hardcoded. If you previously had real keys committed in this file,
# treat them as compromised (this repo is public) - revoke/regenerate them
# on each provider's dashboard, then put the NEW keys only in your local
# .env file (which is git-ignored and never committed).
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

# Economic Data API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "")
NEWS_DATA_API_KEY = os.getenv("NEWS_DATA_API_KEY", "")
FINHUB_API_KEY = os.getenv("FINHUB_API_KEY", "")
TRADING_ECONOMICS_API_KEY = os.getenv("TRADING_ECONOMICS_API_KEY", "")

# GitHub API
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")  # format: username/repo

_REQUIRED_KEYS_FOR_FULL_FUNCTIONALITY = [
    "COINMARKETCAP_API_KEY", "COINGECKO_API_KEY", "FRED_API_KEY",
    "TWELVEDATA_API_KEY", "NEWS_DATA_API_KEY",
]
_missing = [k for k in _REQUIRED_KEYS_FOR_FULL_FUNCTIONALITY if not globals()[k]]
if _missing:
    import warnings
    warnings.warn(
        "Missing API key(s) in environment: " + ", ".join(_missing) +
        ". Copy .env.example to .env and fill in your own keys, or set them "
        "as real environment variables. Features needing these keys will be "
        "degraded or unavailable until then.",
        stacklevel=2,
    )
