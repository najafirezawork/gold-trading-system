"""
Signal agent for technical analysis of gold prices.
"""

import logging
from typing import Dict, Any

from agents.base import BaseAgent, AgentOutput, AgentType
from data_layer import MarketData
from .indicators import TechnicalIndicators


logger = logging.getLogger(__name__)


class SignalAgent(BaseAgent):
    """
    Technical analysis agent for generating trading signals.
    
    This agent analyzes market data using various technical indicators
    and produces a combined signal with confidence level.
    """
    
    def __init__(self, name: str = "Technical Signal Agent"):
        """Initialize the signal agent."""
        super().__init__(AgentType.SIGNAL, name)
        self.indicators = TechnicalIndicators()
    
    def analyze(self, data: MarketData) -> AgentOutput:
        """
        Analyze market data and generate trading signal.
        
        Args:
            data: MarketData object containing OHLCV data
            
        Returns:
            AgentOutput with signal and confidence
        """
        if not self.enabled:
            logger.warning(f"Agent {self.name} is disabled")
            return AgentOutput(
                agent_type=self.agent_type,
                signal=0.0,
                confidence=0.0,
                metadata={"status": "disabled"}
            )
        
        if len(data) < 30:
            logger.warning(f"Insufficient data for analysis: {len(data)} points")
            return AgentOutput(
                agent_type=self.agent_type,
                signal=0.0,
                confidence=0.0,
                metadata={"error": "insufficient_data"}
            )
        
        logger.info(f"Analyzing {len(data)} data points for {data.symbol}")
        
        # Extract price data
        closes = [item.close for item in data.data]
        highs = [item.high for item in data.data]
        lows = [item.low for item in data.data]
        
        # Calculate indicators
        indicators_result = self._calculate_all_indicators(closes, highs, lows)
        
        # Generate signal based on indicators
        signal, confidence = self._generate_signal(indicators_result, closes[-1])
        
        metadata = {
            "symbol": data.symbol,
            "current_price": closes[-1],
            "indicators": indicators_result,
            "analysis": self._get_signal_description(signal)
        }
        
        logger.info(f"Generated signal: {signal:.2f} with confidence: {confidence:.2f}")
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=signal,
            confidence=confidence,
            metadata=metadata
        )
    
    def _calculate_all_indicators(
        self,
        closes: list,
        highs: list,
        lows: list
    ) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        
        # Moving Averages
        sma_20 = self.indicators.calculate_sma(closes, 20)
        sma_50 = self.indicators.calculate_sma(closes, 50)
        ema_12 = self.indicators.calculate_ema(closes, 12)
        
        # RSI
        rsi = self.indicators.calculate_rsi(closes, 14)
        
        # MACD
        macd_line, signal_line, histogram = self.indicators.calculate_macd(closes)
        
        # Bollinger Bands
        upper_band, middle_band, lower_band = self.indicators.calculate_bollinger_bands(closes)
        
        # ATR (Volatility)
        atr = self.indicators.calculate_atr(highs, lows, closes)
        
        # Fibonacci Retracements
        fib_levels = self.indicators.calculate_fibonacci_retracements(
            max(highs), min(lows)
        )
        fib_signal = self.indicators.get_fibonacci_signal(closes[-1], fib_levels)
        
        return {
            "sma_20": sma_20,
            "sma_50": sma_50,
            "ema_12": ema_12,
            "rsi": rsi,
            "macd": {
                "macd_line": macd_line,
                "signal_line": signal_line,
                "histogram": histogram
            },
            "bollinger_bands": {
                "upper": upper_band,
                "middle": middle_band,
                "lower": lower_band
            },
            "atr": atr,
            "fibonacci": {
                "levels": fib_levels,
                "current_position": fib_signal
            }
        }
    
    def _generate_signal(self, indicators: Dict[str, Any], current_price: float) -> tuple[float, float]:
        """
        Generate trading signal based on indicators.
        
        Returns:
            Tuple of (signal, confidence)
            signal: -1 (strong sell) to 1 (strong buy)
            confidence: 0 to 1
        """
        signals = []
        weights = []
        
        # 1. Moving Average Signal
        if current_price > indicators["sma_20"]:
            signals.append(0.5)  # Bullish
            weights.append(0.2)
        else:
            signals.append(-0.5)  # Bearish
            weights.append(0.2)
        
        # 2. Golden/Death Cross Signal
        if indicators["sma_20"] > indicators["sma_50"]:
            signals.append(0.7)  # Strong bullish
            weights.append(0.25)
        elif indicators["sma_20"] < indicators["sma_50"]:
            signals.append(-0.7)  # Strong bearish
            weights.append(0.25)
        else:
            signals.append(0.0)  # Neutral
            weights.append(0.25)
        
        # 3. RSI Signal
        rsi = indicators["rsi"]
        if rsi < 30:
            signals.append(0.8)  # Oversold - buy signal
            weights.append(0.25)
        elif rsi > 70:
            signals.append(-0.8)  # Overbought - sell signal
            weights.append(0.25)
        else:
            # Normalize RSI to -1 to 1 range
            rsi_signal = (rsi - 50) / 50
            signals.append(rsi_signal)
            weights.append(0.15)
        
        # 4. MACD Signal
        macd_histogram = indicators["macd"]["histogram"]
        if macd_histogram > 0:
            signals.append(0.6)  # Bullish
            weights.append(0.2)
        else:
            signals.append(-0.6)  # Bearish
            weights.append(0.2)
        
        # 5. Bollinger Bands Signal
        bb = indicators["bollinger_bands"]
        if current_price < bb["lower"]:
            signals.append(0.7)  # Price near lower band - buy
            weights.append(0.1)
        elif current_price > bb["upper"]:
            signals.append(-0.7)  # Price near upper band - sell
            weights.append(0.1)
        else:
            # Normalize position within bands
            band_position = (current_price - bb["lower"]) / (bb["upper"] - bb["lower"])
            bb_signal = (band_position - 0.5) * 2  # Convert to -1 to 1
            signals.append(-bb_signal)  # Inverse (lower = buy)
            weights.append(0.1)
        
        # Calculate weighted signal
        total_weight = sum(weights)
        weighted_signal = sum(s * w for s, w in zip(signals, weights)) / total_weight
        
        # Calculate confidence based on signal agreement
        signal_agreement = 1 - (sum(abs(s - weighted_signal) for s in signals) / (len(signals) * 2))
        confidence = max(0.3, min(0.95, signal_agreement))
        
        return weighted_signal, confidence
    
    def _get_signal_description(self, signal: float) -> str:
        """Get human-readable signal description."""
        if signal > 0.6:
            return "Strong Buy"
        elif signal > 0.2:
            return "Buy"
        elif signal > -0.2:
            return "Neutral"
        elif signal > -0.6:
            return "Sell"
        else:
            return "Strong Sell"
