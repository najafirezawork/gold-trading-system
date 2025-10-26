"""
Twelve Data API client.
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .models import MarketData, OHLCV
from config import settings


logger = logging.getLogger(__name__)


class TwelveDataAPIError(Exception):
    """Custom exception for Twelve Data API errors."""
    pass


class TwelveDataClient:
    """Client for interacting with Twelve Data API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: Twelve Data API key. If None, uses settings.
        """
        self.api_key = api_key or settings.twelve_data_api_key
        self.base_url = settings.twelve_data_base_url
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            TwelveDataAPIError: If the request fails
        """
        params["apikey"] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "status" in data and data["status"] == "error":
                raise TwelveDataAPIError(f"API Error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise TwelveDataAPIError(f"Request failed: {str(e)}")
    
    def get_time_series(
        self,
        symbol: str,
        interval: str = "1h",
        outputsize: int = 100,
        timezone: str = "UTC"
    ) -> MarketData:
        """
        Get time series data for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "XAU/USD")
            interval: Time interval (1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month)
            outputsize: Number of data points to return
            timezone: Timezone for timestamps
            
        Returns:
            MarketData object containing OHLCV data
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "timezone": timezone,
        }
        
        logger.info(f"Fetching time series for {symbol} with interval {interval}")
        data = self._make_request("time_series", params)
        
        # Parse response
        if "values" not in data:
            raise TwelveDataAPIError("Invalid response: 'values' not found")
        
        ohlcv_list = []
        for item in data["values"]:
            ohlcv = OHLCV(
                datetime=datetime.fromisoformat(item["datetime"].replace("Z", "+00:00")),
                open=float(item["open"]),
                high=float(item["high"]),
                low=float(item["low"]),
                close=float(item["close"]),
                volume=float(item.get("volume", 0)) if item.get("volume") else None
            )
            ohlcv_list.append(ohlcv)
        
        market_data = MarketData(
            symbol=data["meta"]["symbol"],
            interval=data["meta"]["interval"],
            data=ohlcv_list,
            meta=data.get("meta", {})
        )
        
        logger.info(f"Successfully fetched {len(market_data)} data points")
        return market_data
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Quote data as dictionary
        """
        params = {"symbol": symbol}
        logger.info(f"Fetching quote for {symbol}")
        return self._make_request("quote", params)
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
