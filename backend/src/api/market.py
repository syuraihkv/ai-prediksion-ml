"""
Market data API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

from src.schemas import MarketDataResponse
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/price/{asset}", response_model=MarketDataResponse)
async def get_market_price(asset: str):
    """Get current market price for an asset."""
    try:
        # Map asset to yfinance ticker
        ticker_map = {
            'BTC': 'BTC-USD',
            'XAU': 'GC=F',
            'ETH': 'ETH-USD',
        }
        ticker = ticker_map.get(asset.upper(), f"{asset.upper()}-USD")
        
        # Fetch data
        data = yf.download(ticker, period='1d', interval='1m', progress=False)
        
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {asset}")
        
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else data.iloc[-1]
        
        # Calculate 24h change
        price = latest['Close']
        previous_price = previous['Close']
        change_24h = ((price - previous_price) / previous_price) * 100
        
        return MarketDataResponse(
            asset=asset.upper(),
            price=float(price),
            change_24h=float(change_24h),
            volume_24h=float(latest['Volume']) if 'Volume' in latest else 0,
            high_24h=float(data['High'].max()),
            low_24h=float(data['Low'].min()),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error fetching market data for {asset}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{asset}")
async def get_market_history(
    asset: str,
    period: str = Query("1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y"),
    interval: str = Query("1d", description="Data interval: 1m, 5m, 15m, 30m, 1h, 1d")
):
    """Get historical market data for an asset."""
    try:
        ticker_map = {
            'BTC': 'BTC-USD',
            'XAU': 'GC=F',
            'ETH': 'ETH-USD',
        }
        ticker = ticker_map.get(asset.upper(), f"{asset.upper()}-USD")
        
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {asset}")
        
        # Convert to list of dicts
        history = []
        for index, row in data.iterrows():
            history.append({
                "timestamp": index.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": float(row['Volume']) if 'Volume' in row else 0
            })
        
        return {
            "asset": asset.upper(),
            "period": period,
            "interval": interval,
            "data": history
        }
        
    except Exception as e:
        logger.error(f"Error fetching history for {asset}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets")
async def get_supported_assets():
    """Get list of supported assets."""
    return {
        "assets": [
            {"symbol": "BTC", "name": "Bitcoin", "type": "crypto"},
            {"symbol": "ETH", "name": "Ethereum", "type": "crypto"},
            {"symbol": "XAU", "name": "Gold", "type": "commodity"},
        ]
    }
