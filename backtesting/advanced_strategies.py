"""
Advanced Trading Strategies - استراتژی‌های پیشرفته

ترکیب چندین اندیکاتور برای افزایش win rate و accuracy.
"""

from typing import Optional
import logging

from backtesting import BaseStrategy
from data_layer import MarketData
from agents import AgentOutput
from agents.signal import TechnicalIndicators


logger = logging.getLogger(__name__)


class TrendFollowingStrategy(BaseStrategy):
    """
    استراتژی Trend Following - ترکیب MA + RSI + MACD
    
    فقط در جهت ترند اصلی معامله می‌کند.
    
    Logic:
    - تشخیص ترند: SMA(50) vs SMA(200)
    - فیلتر RSI: نه oversold نه overbought
    - تایید MACD: crossover در جهت ترند
    - خروج: سیگنال معکوس یا stop loss
    """
    
    def __init__(
        self,
        fast_ma: int = 50,
        slow_ma: int = 200,
        rsi_period: int = 14,
        rsi_min: int = 40,
        rsi_max: int = 60
    ):
        super().__init__(f"Trend Following ({fast_ma}/{slow_ma})")
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.rsi_period = rsi_period
        self.rsi_min = rsi_min
        self.rsi_max = rsi_max
        self.current_trend = None  # "UP" or "DOWN"
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود فقط در جهت ترند اصلی"""
        if current_index < self.slow_ma + 1:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        
        # 1. تشخیص ترند
        fast = TechnicalIndicators.calculate_sma(closes, self.fast_ma)
        slow = TechnicalIndicators.calculate_sma(closes, self.slow_ma)
        
        if fast > slow:
            self.current_trend = "UP"
        else:
            self.current_trend = "DOWN"
        
        # 2. فیلتر RSI - نباید در extremes باشد
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        if rsi < self.rsi_min or rsi > self.rsi_max:
            return None
        
        # 3. MACD confirmation
        macd, signal, _ = TechnicalIndicators.calculate_macd(closes)
        
        # محاسبه MACD قبلی
        closes_prev = closes[:-1]
        macd_prev, signal_prev, _ = TechnicalIndicators.calculate_macd(closes_prev)
        
        # خرید: uptrend + MACD crossover up
        if self.current_trend == "UP":
            if macd_prev < signal_prev and macd > signal:
                return "BUY"
        
        # فروش: downtrend + MACD crossover down
        if self.current_trend == "DOWN":
            if macd_prev > signal_prev and macd < signal:
                return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج با سیگنال معکوس"""
        if current_index < self.slow_ma + 1:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        
        # MACD برای خروج
        macd, signal, _ = TechnicalIndicators.calculate_macd(closes)
        closes_prev = closes[:-1]
        macd_prev, signal_prev, _ = TechnicalIndicators.calculate_macd(closes_prev)
        
        # خروج LONG: MACD crossover down
        if position_type == "LONG":
            if macd_prev > signal_prev and macd < signal:
                return True
        
        # خروج SHORT: MACD crossover up
        if position_type == "SHORT":
            if macd_prev < signal_prev and macd > signal:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 2.5%"""
        if position_type == "LONG":
            return entry_price * 0.975
        else:
            return entry_price * 1.025
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 5%"""
        if position_type == "LONG":
            return entry_price * 1.05
        else:
            return entry_price * 0.95


class MeanReversionStrategy(BaseStrategy):
    """
    استراتژی Mean Reversion - بازگشت به میانگین
    
    از Bollinger Bands + RSI برای تشخیص extremes.
    
    Logic:
    - خرید: قیمت به lower band رسید + RSI < 30
    - فروش: قیمت به upper band رسید + RSI > 70
    - خروج: بازگشت به middle band
    """
    
    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        rsi_period: int = 14,
        rsi_oversold: int = 30,
        rsi_overbought: int = 70
    ):
        super().__init__(f"Mean Reversion (BB{bb_period}, RSI{rsi_period})")
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود در extremes"""
        if current_index < max(self.bb_period, self.rsi_period):
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
            closes, self.bb_period, self.bb_std
        )
        
        # RSI
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # خرید: lower band + oversold
        if current_price <= lower and rsi < self.rsi_oversold:
            return "BUY"
        
        # فروش: upper band + overbought
        if current_price >= upper and rsi > self.rsi_overbought:
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج در middle band"""
        if current_index < self.bb_period:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
            closes, self.bb_period, self.bb_std
        )
        
        # خروج LONG: قیمت به middle یا بالاتر رسید
        if position_type == "LONG" and current_price >= middle:
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            if profit_pct > 0.5:  # حداقل 0.5% سود
                return True
        
        # خروج SHORT: قیمت به middle یا پایین‌تر رسید
        if position_type == "SHORT" and current_price <= middle:
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            if profit_pct > 0.5:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 2%"""
        if position_type == "LONG":
            return entry_price * 0.98
        else:
            return entry_price * 1.02
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 3%"""
        if position_type == "LONG":
            return entry_price * 1.03
        else:
            return entry_price * 0.97


class BreakoutStrategy(BaseStrategy):
    """
    استراتژی Breakout - شکست سطوح
    
    تشخیص شکست سطوح مقاومت/حمایت با حجم بالا.
    
    Logic:
    - محاسبه highest/lowest N روز گذشته
    - خرید: شکست highest + volume بالا + RSI > 50
    - فروش: شکست lowest + volume بالا + RSI < 50
    - خروج: pullback یا stop loss
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        volume_multiplier: float = 1.5,
        rsi_period: int = 14
    ):
        super().__init__(f"Breakout ({lookback_period} bars)")
        self.lookback_period = lookback_period
        self.volume_multiplier = volume_multiplier
        self.rsi_period = rsi_period
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود در breakout"""
        if current_index < self.lookback_period + self.rsi_period:
            return None
        
        # داده‌های lookback period
        lookback_data = market_data.data[current_index - self.lookback_period:current_index]
        current_bar = market_data.data[current_index]
        
        # highest/lowest
        highest = max(bar.high for bar in lookback_data)
        lowest = min(bar.low for bar in lookback_data)
        
        # average volume (handle None values)
        volumes = [bar.volume for bar in lookback_data if bar.volume is not None]
        if not volumes:
            return None  # اگر volume نداریم، skip
        avg_volume = sum(volumes) / len(volumes)
        
        # RSI
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # بررسی volume فعلی
        if current_bar.volume is None:
            return None
        
        # Breakout بالا
        if (current_bar.close > highest and 
            current_bar.volume > avg_volume * self.volume_multiplier and
            rsi > 50):
            return "BUY"
        
        # Breakout پایین
        if (current_bar.close < lowest and
            current_bar.volume > avg_volume * self.volume_multiplier and
            rsi < 50):
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج در pullback"""
        if current_index < 5:
            return False
        
        current_price = market_data.data[current_index].close
        
        # خروج با سود 2%
        if position_type == "LONG":
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            if profit_pct > 2.0:
                return True
        
        if position_type == "SHORT":
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            if profit_pct > 2.0:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 1.5%"""
        if position_type == "LONG":
            return entry_price * 0.985
        else:
            return entry_price * 1.015
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 4%"""
        if position_type == "LONG":
            return entry_price * 1.04
        else:
            return entry_price * 0.96


class MultiConfirmationStrategy(BaseStrategy):
    """
    استراتژی Multi-Confirmation - تایید از چند منبع
    
    فقط وقتی معامله می‌کند که همه شرایط برقرار باشد:
    1. RSI در ناحیه مناسب
    2. MACD crossover
    3. قیمت بالای/پایین SMA
    4. Bollinger Bands موقعیت درست
    
    این استراتژی کمتر معامله می‌کند اما دقت بالاتری دارد.
    """
    
    def __init__(
        self,
        sma_period: int = 50,
        rsi_period: int = 14,
        bb_period: int = 20,
        bb_std: float = 2.0
    ):
        super().__init__(f"Multi-Confirmation (SMA{sma_period})")
        self.sma_period = sma_period
        self.rsi_period = rsi_period
        self.bb_period = bb_period
        self.bb_std = bb_std
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود با تایید از همه اندیکاتورها"""
        if current_index < max(self.sma_period, self.bb_period) + 1:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        # 1. SMA
        sma = TechnicalIndicators.calculate_sma(closes, self.sma_period)
        
        # 2. RSI
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # 3. MACD
        macd, signal, _ = TechnicalIndicators.calculate_macd(closes)
        closes_prev = closes[:-1]
        macd_prev, signal_prev, _ = TechnicalIndicators.calculate_macd(closes_prev)
        
        # 4. Bollinger Bands
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
            closes, self.bb_period, self.bb_std
        )
        
        # شرایط خرید - همه باید برقرار باشند
        buy_conditions = [
            current_price > sma,                    # قیمت بالای SMA
            30 < rsi < 55,                          # RSI نه oversold نه overbought
            macd_prev < signal_prev and macd > signal,  # MACD crossover up
            lower < current_price < middle          # قیمت در نصف پایین BB
        ]
        
        if all(buy_conditions):
            return "BUY"
        
        # شرایط فروش
        sell_conditions = [
            current_price < sma,                    # قیمت پایین SMA
            45 < rsi < 70,                          # RSI نه overbought نه oversold
            macd_prev > signal_prev and macd < signal,  # MACD crossover down
            middle < current_price < upper          # قیمت در نصف بالای BB
        ]
        
        if all(sell_conditions):
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج با شرایط معکوس"""
        if current_index < self.sma_period:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        sma = TechnicalIndicators.calculate_sma(closes, self.sma_period)
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # خروج LONG
        if position_type == "LONG":
            # شرایط خروج
            if current_price < sma or rsi > 70:
                return True
        
        # خروج SHORT
        if position_type == "SHORT":
            if current_price > sma or rsi < 30:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 2%"""
        if position_type == "LONG":
            return entry_price * 0.98
        else:
            return entry_price * 1.02
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 5%"""
        if position_type == "LONG":
            return entry_price * 1.05
        else:
            return entry_price * 0.95


class AdaptiveRSIStrategy(BaseStrategy):
    """
    استراتژی Adaptive RSI - RSI تطبیقی
    
    از ATR برای تنظیم پویای thresholds RSI استفاده می‌کند.
    در volatility بالا، thresholds را سخت‌تر می‌کند.
    
    Logic:
    - محاسبه ATR برای volatility
    - تنظیم RSI thresholds بر اساس ATR
    - ورود با RSI تطبیقی
    - Stop loss بر اساس ATR
    """
    
    def __init__(
        self,
        rsi_period: int = 14,
        atr_period: int = 14,
        base_oversold: int = 30,
        base_overbought: int = 70
    ):
        super().__init__(f"Adaptive RSI (ATR-based)")
        self.rsi_period = rsi_period
        self.atr_period = atr_period
        self.base_oversold = base_oversold
        self.base_overbought = base_overbought
        self.current_atr_multiplier = 1.0
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود با RSI تطبیقی"""
        if current_index < max(self.rsi_period, self.atr_period):
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        highs = [bar.high for bar in market_data.data[:current_index + 1]]
        lows = [bar.low for bar in market_data.data[:current_index + 1]]
        
        # RSI
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # ATR برای volatility
        atr = TechnicalIndicators.calculate_atr(highs, lows, closes, self.atr_period)
        avg_price = sum(closes[-20:]) / 20
        atr_pct = (atr / avg_price) * 100
        
        # تنظیم thresholds بر اساس volatility
        # volatility بالا → thresholds سخت‌تر
        if atr_pct > 1.5:  # volatility بالا
            oversold = self.base_oversold - 5
            overbought = self.base_overbought + 5
            self.current_atr_multiplier = 1.5
        elif atr_pct > 1.0:  # volatility متوسط
            oversold = self.base_oversold
            overbought = self.base_overbought
            self.current_atr_multiplier = 1.2
        else:  # volatility پایین
            oversold = self.base_oversold + 5
            overbought = self.base_overbought - 5
            self.current_atr_multiplier = 1.0
        
        # ورود
        if rsi < oversold:
            return "BUY"
        
        if rsi > overbought:
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج با RSI neutral"""
        if current_index < self.rsi_period:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # خروج وقتی RSI به ناحیه neutral برگردد
        if position_type == "LONG" and rsi > 50:
            return True
        
        if position_type == "SHORT" and rsi < 50:
            return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss بر اساس ATR"""
        stop_pct = 0.015 * self.current_atr_multiplier  # 1.5% تا 2.25%
        
        if position_type == "LONG":
            return entry_price * (1 - stop_pct)
        else:
            return entry_price * (1 + stop_pct)
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit بر اساس ATR"""
        take_pct = 0.04 * self.current_atr_multiplier  # 4% تا 6%
        
        if position_type == "LONG":
            return entry_price * (1 + take_pct)
        else:
            return entry_price * (1 - take_pct)
