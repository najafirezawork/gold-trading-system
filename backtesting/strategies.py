"""
Example trading strategies for backtesting.
"""

from typing import Optional
import logging

from backtesting import BaseStrategy
from data_layer import MarketData
from agents import AgentOutput, SignalAgent
from agents.signal import TechnicalIndicators


logger = logging.getLogger(__name__)


class SimpleMAStrategy(BaseStrategy):
    """
    استراتژی ساده Moving Average Crossover.
    
    خرید: وقتی MA کوتاه از MA بلند رد شود (به بالا)
    فروش: وقتی MA کوتاه از MA بلند رد شود (به پایین)
    """
    
    def __init__(self, short_period: int = 20, long_period: int = 50):
        super().__init__(f"MA Crossover ({short_period}/{long_period})")
        self.short_period = short_period
        self.long_period = long_period
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """بررسی شرایط ورود"""
        if current_index < self.long_period + 1:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        
        # محاسبه MA برای بار فعلی و قبلی
        ma_short_current = TechnicalIndicators.calculate_sma(closes, self.short_period)
        ma_long_current = TechnicalIndicators.calculate_sma(closes, self.long_period)
        
        closes_prev = closes[:-1]
        ma_short_prev = TechnicalIndicators.calculate_sma(closes_prev, self.short_period)
        ma_long_prev = TechnicalIndicators.calculate_sma(closes_prev, self.long_period)
        
        # Golden Cross - خرید
        if ma_short_prev < ma_long_prev and ma_short_current > ma_long_current:
            return "BUY"
        
        # Death Cross - فروش
        if ma_short_prev > ma_long_prev and ma_short_current < ma_long_current:
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج در کراس برعکس"""
        if current_index < self.long_period + 1:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        
        ma_short_current = TechnicalIndicators.calculate_sma(closes, self.short_period)
        ma_long_current = TechnicalIndicators.calculate_sma(closes, self.long_period)
        
        closes_prev = closes[:-1]
        ma_short_prev = TechnicalIndicators.calculate_sma(closes_prev, self.short_period)
        ma_long_prev = TechnicalIndicators.calculate_sma(closes_prev, self.long_period)
        
        # خروج از LONG
        if position_type == "LONG":
            if ma_short_prev > ma_long_prev and ma_short_current < ma_long_current:
                return True
        
        # خروج از SHORT
        if position_type == "SHORT":
            if ma_short_prev < ma_long_prev and ma_short_current > ma_long_current:
                return True
        
        return False


class RSIStrategy(BaseStrategy):
    """
    استراتژی بر اساس RSI.
    
    خرید: RSI < 30 (oversold)
    فروش: RSI > 70 (overbought)
    """
    
    def __init__(self, rsi_period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__(f"RSI Strategy ({oversold}/{overbought})")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """بررسی شرایط ورود"""
        if current_index < self.rsi_period + 1:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # Oversold - خرید
        if rsi < self.oversold:
            return "BUY"
        
        # Overbought - فروش
        if rsi > self.overbought:
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج وقتی RSI به ناحیه خنثی برگردد"""
        if current_index < self.rsi_period + 1:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        rsi = TechnicalIndicators.calculate_rsi(closes, self.rsi_period)
        
        # خروج از LONG وقتی RSI > 50
        if position_type == "LONG" and rsi > 50:
            return True
        
        # خروج از SHORT وقتی RSI < 50
        if position_type == "SHORT" and rsi < 50:
            return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 2%"""
        if position_type == "LONG":
            return entry_price * 0.98
        else:  # SHORT
            return entry_price * 1.02
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 4%"""
        if position_type == "LONG":
            return entry_price * 1.04
        else:  # SHORT
            return entry_price * 0.96


class SignalAgentStrategy(BaseStrategy):
    """
    استراتژی بر اساس خروجی Signal Agent.
    
    از تحلیل تکنیکال کامل agent استفاده می‌کند.
    """
    
    def __init__(self, signal_threshold: float = 0.3):
        super().__init__(f"Signal Agent Strategy (threshold={signal_threshold})")
        self.signal_threshold = signal_threshold
        self.signal_agent = SignalAgent()
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """ورود بر اساس سیگنال agent"""
        if current_index < 50:  # حداقل داده لازم
            return None
        
        # بررسی agent output
        if agent_output and agent_output.signal is not None:
            if agent_output.signal > self.signal_threshold:
                return "BUY"
            elif agent_output.signal < -self.signal_threshold:
                return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """خروج بر اساس سیگنال معکوس"""
        if current_index < 50:
            return False
        
        # محاسبه سیگنال فعلی
        partial_data = MarketData(
            symbol=market_data.symbol,
            interval=market_data.interval,
            data=market_data.data[:current_index + 1],
            meta=market_data.meta
        )
        
        output = self.signal_agent.analyze(partial_data)
        
        # خروج از LONG
        if position_type == "LONG" and output.signal < 0:
            return True
        
        # خروج از SHORT
        if position_type == "SHORT" and output.signal > 0:
            return True
        
        return False
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """Stop loss 3%"""
        if position_type == "LONG":
            return entry_price * 0.97
        else:
            return entry_price * 1.03
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """Take profit 6%"""
        if position_type == "LONG":
            return entry_price * 1.06
        else:
            return entry_price * 0.94
