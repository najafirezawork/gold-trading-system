"""
Technical indicators calculations.
"""

import numpy as np
from typing import List, Dict, Any


class TechnicalIndicators:
    """Collection of technical analysis indicators."""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """
        Calculate Simple Moving Average.
        
        Args:
            prices: List of prices
            period: Period for SMA
            
        Returns:
            SMA value
        """
        if len(prices) < period:
            return np.mean(prices)
        return np.mean(prices[-period:])
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """
        Calculate Exponential Moving Average.
        
        Args:
            prices: List of prices
            period: Period for EMA
            
        Returns:
            EMA value
        """
        if len(prices) < period:
            return np.mean(prices)
        
        prices_array = np.array(prices)
        multiplier = 2 / (period + 1)
        ema = np.mean(prices_array[:period])
        
        for price in prices_array[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: List of prices
            period: Period for RSI (default: 14)
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple[float, float, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: List of prices
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        if len(prices) < slow_period:
            return 0.0, 0.0, 0.0
        
        fast_ema = TechnicalIndicators.calculate_ema(prices, fast_period)
        slow_ema = TechnicalIndicators.calculate_ema(prices, slow_period)
        macd_line = fast_ema - slow_ema
        
        # For simplicity, using a basic signal line calculation
        signal_line = macd_line * 0.9  # Simplified
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> tuple[float, float, float]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: List of prices
            period: Period for moving average
            std_dev: Number of standard deviations
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        if len(prices) < period:
            period = len(prices)
        
        recent_prices = prices[-period:]
        middle_band = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_atr(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> float:
        """
        Calculate Average True Range.
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of close prices
            period: Period for ATR
            
        Returns:
            ATR value
        """
        if len(highs) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        if len(true_ranges) < period:
            return np.mean(true_ranges)
        
        return np.mean(true_ranges[-period:])
    
    @staticmethod
    def calculate_fibonacci_retracements(
        high: float,
        low: float
    ) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels.
        
        Fibonacci levels: 23.6%, 38.2%, 50%, 61.8%, 78.6%
        
        Args:
            high: Highest price in the uptrend
            low: Lowest price in the downtrend
            
        Returns:
            Dictionary with Fibonacci levels
        """
        diff = high - low
        
        fib_levels = {
            "0": low,
            "23.6": low + (diff * 0.236),
            "38.2": low + (diff * 0.382),
            "50.0": low + (diff * 0.500),  # Middle point
            "61.8": low + (diff * 0.618),  # Golden ratio
            "78.6": low + (diff * 0.786),
            "100": high
        }
        
        return fib_levels
    
    @staticmethod
    def get_fibonacci_signal(
        current_price: float,
        fib_levels: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Get signal based on Fibonacci levels.
        
        Args:
            current_price: Current market price
            fib_levels: Fibonacci retracement levels
            
        Returns:
            Signal analysis based on proximity to Fibonacci levels
        """
        # Find nearest Fibonacci level
        levels_list = sorted(fib_levels.items(), key=lambda x: x[1])
        
        signal_strength = 0.0
        nearest_level = None
        distance_to_level = float('inf')
        
        for level_name, level_price in levels_list:
            distance = abs(current_price - level_price)
            if distance < distance_to_level:
                distance_to_level = distance
                nearest_level = (level_name, level_price)
        
        # Signal strength based on distance
        max_distance = (fib_levels["100"] - fib_levels["0"]) * 0.02  # 2% tolerance
        if distance_to_level <= max_distance:
            signal_strength = 1.0 - (distance_to_level / max_distance)
        
        return {
            "nearest_level": nearest_level[0] if nearest_level else None,
            "nearest_price": nearest_level[1] if nearest_level else None,
            "distance": distance_to_level,
            "signal_strength": signal_strength,
            "is_at_support": signal_strength > 0.8
        }
