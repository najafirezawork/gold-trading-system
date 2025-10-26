"""
High Win Rate Strategies - استراتژی‌های با Win Rate بالا

این استراتژی‌ها برای افزایش win rate طراحی شده‌اند.
"""

from typing import Optional
import logging

from backtesting import BaseStrategy
from data_layer import MarketData
from agents import AgentOutput
from agents.signal import TechnicalIndicators


logger = logging.getLogger(__name__)


class ScalpingStrategy(BaseStrategy):
    """
    استراتژی Scalping - سود کم، ریسک کم، تعداد زیاد
    
    هدف: Win Rate بالای 70%
    
    Logic:
    - خرید/فروش در نقاط کم ریسک
    - Take Profit کوچک (0.3%)
    - Stop Loss خیلی کوچک (0.15%)
    - خروج سریع
    """
    
    def __init__(self, ema_fast: int = 5, ema_slow: int = 10):
        super().__init__(f"Scalping (EMA {ema_fast}/{ema_slow})")
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود با EMA Crossover"""
        if current_index < self.ema_slow:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        
        # EMA های سریع
        ema_fast = TechnicalIndicators.calculate_ema(closes, self.ema_fast)
        ema_slow = TechnicalIndicators.calculate_ema(closes, self.ema_slow)
        
        # EMA قبلی
        closes_prev = closes[:-1]
        ema_fast_prev = TechnicalIndicators.calculate_ema(closes_prev, self.ema_fast)
        ema_slow_prev = TechnicalIndicators.calculate_ema(closes_prev, self.ema_slow)
        
        # Crossover up
        if ema_fast_prev < ema_slow_prev and ema_fast > ema_slow:
            return "BUY"
        
        # Crossover down
        if ema_fast_prev > ema_slow_prev and ema_fast < ema_slow:
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج سریع با سود کوچک"""
        current_price = market_data.data[current_index].close
        
        # خروج با سود 0.2%
        if position_type == "LONG":
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            if profit_pct >= 0.2:
                return True
        
        if position_type == "SHORT":
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            if profit_pct >= 0.2:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss خیلی کوچک - 0.15%"""
        if position_type == "LONG":
            return entry_price * 0.9985
        else:
            return entry_price * 1.0015
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit کوچک - 0.3%"""
        if position_type == "LONG":
            return entry_price * 1.003
        else:
            return entry_price * 0.997


class ConservativeStrategy(BaseStrategy):
    """
    استراتژی محافظه‌کار - فقط موقعیت‌های امن
    
    هدف: Win Rate بالای 75%
    
    Logic:
    - فقط در قوی‌ترین سیگنال‌ها ورود
    - چند شرط سخت برای فیلتر
    - Take Profit متوسط (1%)
    - Stop Loss کوچک (0.5%)
    """
    
    def __init__(self):
        super().__init__("Conservative High Win Rate")
        self.min_rsi = 35
        self.max_rsi = 65
        self.sma_period = 20
        self.rsi_period = 14
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود فقط در شرایط ایده‌آل"""
        if current_index < max(self.sma_period, self.rsi_period) + 5:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        highs = [bar.high for bar in market_data.data[:current_index + 1]]
        lows = [bar.low for bar in market_data.data[:current_index + 1]]
        
        current_price = closes[-1]
        
        # RSI
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # RSI باید در ناحیه neutral باشد (نه extreme)
        if rsi < self.min_rsi or rsi > self.max_rsi:
            return None
        
        # SMA
        sma = TechnicalIndicators.calculate_sma(closes, self.sma_period)
        
        # MACD
        macd, signal, _ = TechnicalIndicators.calculate_macd(closes)
        
        # ATR برای volatility
        atr = TechnicalIndicators.calculate_atr(highs, lows, closes, 14)
        atr_pct = (atr / current_price) * 100
        
        # فقط در volatility پایین معامله کن
        if atr_pct > 1.0:
            return None
        
        # محاسبه قدرت ترند
        sma_5 = TechnicalIndicators.calculate_sma(closes, 5)
        sma_20 = TechnicalIndicators.calculate_sma(closes, 20)
        
        # شرایط خرید - همه باید برقرار باشند
        buy_conditions = [
            current_price > sma,          # بالای SMA
            sma_5 > sma_20,               # ترند صعودی کوتاه‌مدت
            macd > signal,                # MACD مثبت
            38 < rsi < 55,                # RSI مناسب
            atr_pct < 0.8                 # volatility کم
        ]
        
        if all(buy_conditions):
            return "BUY"
        
        # شرایط فروش
        sell_conditions = [
            current_price < sma,
            sma_5 < sma_20,
            macd < signal,
            45 < rsi < 62,
            atr_pct < 0.8
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
        """خروج با اولین سیگنال ضعیف"""
        if current_index < 5:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        sma = TechnicalIndicators.calculate_sma(closes, self.sma_period)
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # خروج LONG
        if position_type == "LONG":
            # خروج با سود 0.8%
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            if profit_pct >= 0.8:
                return True
            
            # خروج اگر شرایط ضعیف شد
            if current_price < sma or rsi > 65:
                return True
        
        # خروج SHORT
        if position_type == "SHORT":
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            if profit_pct >= 0.8:
                return True
            
            if current_price > sma or rsi < 35:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 0.5%"""
        if position_type == "LONG":
            return entry_price * 0.995
        else:
            return entry_price * 1.005
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 1%"""
        if position_type == "LONG":
            return entry_price * 1.01
        else:
            return entry_price * 0.99


class SafeRSIStrategy(BaseStrategy):
    """
    استراتژی RSI امن - فقط extremes واقعی
    
    هدف: Win Rate بالای 70%
    
    Logic:
    - RSI extremes خیلی شدید (< 25 or > 75)
    - تایید با Bollinger Bands
    - Take Profit سریع (0.5%)
    - Win Rate بالا با risk/reward متوسط
    """
    
    def __init__(self):
        super().__init__("Safe RSI (High Win Rate)")
        self.rsi_period = 14
        self.rsi_oversold = 25  # سخت‌تر
        self.rsi_overbought = 75  # سخت‌تر
        self.bb_period = 20
        self.bb_std = 2.0
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود فقط در extremes شدید"""
        if current_index < max(self.rsi_period, self.bb_period):
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        # RSI
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
            closes, self.bb_period, self.bb_std
        )
        
        # خرید: RSI خیلی oversold + قیمت نزدیک یا زیر lower band
        if rsi < self.rsi_oversold and current_price <= lower * 1.002:
            return "BUY"
        
        # فروش: RSI خیلی overbought + قیمت نزدیک یا بالای upper band
        if rsi > self.rsi_overbought and current_price >= upper * 0.998:
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج سریع با سود کوچک"""
        if current_index < self.rsi_period:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # خروج LONG
        if position_type == "LONG":
            # خروج با سود 0.4%
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            if profit_pct >= 0.4:
                return True
            
            # یا RSI به neutral برگشت
            if rsi > 45:
                return True
        
        # خروج SHORT
        if position_type == "SHORT":
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            if profit_pct >= 0.4:
                return True
            
            if rsi < 55:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 0.6%"""
        if position_type == "LONG":
            return entry_price * 0.994
        else:
            return entry_price * 1.006
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 0.5%"""
        if position_type == "LONG":
            return entry_price * 1.005
        else:
            return entry_price * 0.995


class PullbackStrategy(BaseStrategy):
    """
    استراتژی Pullback - خرید در تصحیح
    
    هدف: Win Rate بالای 65%
    
    Logic:
    - تشخیص ترند قوی
    - منتظر pullback (تصحیح)
    - خرید در pullback با RSI support
    - Probability بالا برای ادامه ترند
    """
    
    def __init__(self):
        super().__init__("Pullback (Trend Continuation)")
        self.sma_fast = 20
        self.sma_slow = 50
        self.rsi_period = 14
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود در pullback"""
        if current_index < self.sma_slow + 10:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        # تشخیص ترند
        sma_fast = TechnicalIndicators.calculate_sma(closes, self.sma_fast)
        sma_slow = TechnicalIndicators.calculate_sma(closes, self.sma_slow)
        
        # RSI
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # قدرت ترند - 10 کندل اخیر
        trend_strength = (closes[-1] - closes[-10]) / closes[-10] * 100
        
        # Uptrend قوی + Pullback
        if sma_fast > sma_slow * 1.01:  # ترند صعودی قوی
            # Pullback: قیمت به SMA fast نزدیک شده + RSI پایین اما نه extreme
            if (current_price <= sma_fast * 1.003 and 
                35 < rsi < 50 and
                trend_strength > 0.5):  # ترند هنوز مثبت
                return "BUY"
        
        # Downtrend قوی + Pullback
        if sma_fast < sma_slow * 0.99:  # ترند نزولی قوی
            if (current_price >= sma_fast * 0.997 and
                50 < rsi < 65 and
                trend_strength < -0.5):
                return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج با سود یا شکست ترند"""
        if current_index < self.sma_fast:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        current_price = closes[-1]
        
        sma_fast = TechnicalIndicators.calculate_sma(closes, self.sma_fast)
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # خروج LONG
        if position_type == "LONG":
            # سود 1.2%
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            if profit_pct >= 1.2:
                return True
            
            # شکست ترند
            if current_price < sma_fast * 0.997 or rsi > 70:
                return True
        
        # خروج SHORT
        if position_type == "SHORT":
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            if profit_pct >= 1.2:
                return True
            
            if current_price > sma_fast * 1.003 or rsi < 30:
                return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 0.8%"""
        if position_type == "LONG":
            return entry_price * 0.992
        else:
            return entry_price * 1.008
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 1.5%"""
        if position_type == "LONG":
            return entry_price * 1.015
        else:
            return entry_price * 0.985
