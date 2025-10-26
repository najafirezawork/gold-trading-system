"""
Data models for market data.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    """Open, High, Low, Close, Volume data model."""
    
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


class MarketData(BaseModel):
    """Market data container."""
    
    symbol: str
    interval: str
    data: List[OHLCV]
    meta: Optional[dict] = None
    
    def __len__(self) -> int:
        return len(self.data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for analysis."""
        return {
            "datetime": [item.datetime for item in self.data],
            "open": [item.open for item in self.data],
            "high": [item.high for item in self.data],
            "low": [item.low for item in self.data],
            "close": [item.close for item in self.data],
            "volume": [item.volume for item in self.data if item.volume is not None],
        }
