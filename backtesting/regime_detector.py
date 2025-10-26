"""
Market Regime Detector
تشخیص وضعیت بازار (Trending, Ranging, Volatile)
"""

from typing import List, Literal
from dataclasses import dataclass
import numpy as np

from data_layer.models import OHLCV


MarketRegime = Literal["trending_up", "trending_down", "ranging", "volatile"]


@dataclass
class RegimeAnalysis:
    """نتیجه تحلیل market regime"""
    regime: MarketRegime
    confidence: float  # 0 to 1
    adx: float
    volatility: float
    trend_strength: float


class MarketRegimeDetector:
    """
    تشخیص market regime بر اساس:
    1. ADX (Average Directional Index) - قدرت ترند
    2. ATR (Average True Range) - volatility
    3. Price action - range یا trend
    """
    
    def __init__(
        self,
        adx_period: int = 14,
        atr_period: int = 14,
        trending_threshold: float = 25.0,  # ADX > 25 = trending
        strong_trending_threshold: float = 40.0,  # ADX > 40 = strong trend
        high_volatility_threshold: float = 2.0,  # ATR multiplier
    ):
        self.adx_period = adx_period
        self.atr_period = atr_period
        self.trending_threshold = trending_threshold
        self.strong_trending_threshold = strong_trending_threshold
        self.high_volatility_threshold = high_volatility_threshold
    
    def detect(self, data: List[OHLCV]) -> RegimeAnalysis:
        """
        تشخیص market regime فعلی
        
        Returns:
            RegimeAnalysis با regime و confidence
        """
        if len(data) < max(self.adx_period * 2, 50):
            # داده کافی نیست
            return RegimeAnalysis(
                regime="ranging",
                confidence=0.5,
                adx=0,
                volatility=0,
                trend_strength=0
            )
        
        # محاسبه indicators
        adx = self._calculate_adx(data)
        atr = self._calculate_atr(data)
        avg_price = np.mean([bar.close for bar in data[-20:]])
        volatility = (atr / avg_price) * 100  # ATR as % of price
        
        # تعیین trend direction
        sma_20 = np.mean([bar.close for bar in data[-20:]])
        sma_50 = np.mean([bar.close for bar in data[-50:]])
        trend_direction = "up" if sma_20 > sma_50 else "down"
        
        # محاسبه trend strength (0 to 1)
        trend_strength = min(adx / 100, 1.0)
        
        # تشخیص regime
        regime, confidence = self._classify_regime(
            adx, volatility, trend_direction, trend_strength
        )
        
        return RegimeAnalysis(
            regime=regime,
            confidence=confidence,
            adx=adx,
            volatility=volatility,
            trend_strength=trend_strength
        )
    
    def _classify_regime(
        self,
        adx: float,
        volatility: float,
        trend_direction: str,
        trend_strength: float
    ) -> tuple[MarketRegime, float]:
        """تعیین regime و confidence"""
        
        # Volatile market (high ATR)
        if volatility > self.high_volatility_threshold:
            confidence = min(volatility / self.high_volatility_threshold, 1.0)
            return "volatile", confidence
        
        # Strong trending market
        if adx > self.strong_trending_threshold:
            regime = "trending_up" if trend_direction == "up" else "trending_down"
            confidence = min(adx / 60, 1.0)  # Max confidence at ADX=60
            return regime, confidence
        
        # Moderate trending
        if adx > self.trending_threshold:
            regime = "trending_up" if trend_direction == "up" else "trending_down"
            confidence = (adx - self.trending_threshold) / (self.strong_trending_threshold - self.trending_threshold)
            return regime, confidence
        
        # Ranging market (low ADX)
        confidence = 1.0 - (adx / self.trending_threshold)  # Higher confidence = lower ADX
        return "ranging", confidence
    
    def _calculate_adx(self, data: List[OHLCV]) -> float:
        """
        محاسبه Average Directional Index (ADX)
        ADX = EMA of DX
        DX = 100 * |+DI - -DI| / (+DI + -DI)
        """
        period = self.adx_period
        
        # محاسبه True Range
        tr_list = []
        for i in range(1, len(data)):
            high = data[i].high
            low = data[i].low
            prev_close = data[i-1].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_list.append(tr)
        
        # محاسبه +DM و -DM
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(data)):
            high_diff = data[i].high - data[i-1].high
            low_diff = data[i-1].low - data[i].low
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm.append(high_diff)
            else:
                plus_dm.append(0)
            
            if low_diff > high_diff and low_diff > 0:
                minus_dm.append(low_diff)
            else:
                minus_dm.append(0)
        
        if len(tr_list) < period:
            return 0
        
        # Smooth با EMA
        tr_smooth = self._ema(tr_list, period)
        plus_dm_smooth = self._ema(plus_dm, period)
        minus_dm_smooth = self._ema(minus_dm, period)
        
        # محاسبه +DI و -DI
        if tr_smooth == 0:
            return 0
        
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        
        # محاسبه DX
        di_sum = plus_di + minus_di
        if di_sum == 0:
            return 0
        
        dx = 100 * abs(plus_di - minus_di) / di_sum
        
        # ADX = EMA of DX (ساده‌سازی شده)
        # در واقع باید DX را برای چند دوره محاسبه کنیم
        # اما برای سرعت، از مقدار فعلی استفاده می‌کنیم
        return dx
    
    def _calculate_atr(self, data: List[OHLCV]) -> float:
        """محاسبه Average True Range"""
        period = self.atr_period
        
        tr_list = []
        for i in range(1, len(data)):
            high = data[i].high
            low = data[i].low
            prev_close = data[i-1].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_list.append(tr)
        
        if len(tr_list) < period:
            return 0
        
        # ATR = EMA of TR
        atr = self._ema(tr_list, period)
        return atr
    
    def _ema(self, data: List[float], period: int) -> float:
        """محاسبه Exponential Moving Average"""
        if len(data) < period:
            return 0
        
        # محاسبه SMA اولیه
        sma = np.mean(data[:period])
        
        # محاسبه EMA
        multiplier = 2 / (period + 1)
        ema = sma
        
        for value in data[period:]:
            ema = (value * multiplier) + (ema * (1 - multiplier))
        
        return ema


class RegimeBasedFilter:
    """
    فیلتر معاملات بر اساس market regime
    """
    
    def should_trade(
        self,
        strategy_name: str,
        regime: MarketRegime,
        confidence: float,
        min_confidence: float = 0.6
    ) -> tuple[bool, str]:
        """
        آیا با این استراتژی و در این regime باید معامله کرد؟
        
        Returns:
            (should_trade, reason)
        """
        
        # Confidence کافی نیست
        if confidence < min_confidence:
            return False, f"Low confidence ({confidence:.1%})"
        
        # مطابقت strategy با regime
        matching = {
            "trending_up": ["TrendFollowing", "Breakout", "AdaptiveRSI"],
            "trending_down": ["TrendFollowing", "AdaptiveRSI"],
            "ranging": ["MeanReversion", "SafeRSI", "RSI"],
            "volatile": ["Scalping", "MeanReversion"]  # استراتژی‌های سریع
        }
        
        compatible_strategies = matching.get(regime, [])
        
        # چک کن strategy name شامل یکی از compatible ها باشد
        is_compatible = any(
            s.lower() in strategy_name.lower()
            for s in compatible_strategies
        )
        
        if not is_compatible:
            return False, f"Strategy not suitable for {regime} market"
        
        return True, f"Good match for {regime} market"
