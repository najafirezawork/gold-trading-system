"""
Base strategy class for backtesting.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from data_layer import MarketData
from agents import AgentOutput


class BaseStrategy(ABC):
    """
    کلاس پایه برای استراتژی‌های معاملاتی.
    
    هر استراتژی باید از این کلاس ارث‌بری کند و متدهای
    should_enter و should_exit را پیاده‌سازی کند.
    """
    
    def __init__(self, name: str):
        """
        Initialize strategy.
        
        Args:
            name: نام استراتژی
        """
        self.name = name
        self.current_position = None  # None, "LONG", "SHORT"
    
    @abstractmethod
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """
        بررسی شرایط ورود به معامله.
        
        Args:
            market_data: داده‌های بازار
            current_index: ایندکس فعلی در داده‌ها
            agent_output: خروجی agent (اختیاری)
            
        Returns:
            "BUY" برای خرید، "SELL" برای فروش، None برای عدم ورود
        """
        pass
    
    @abstractmethod
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """
        بررسی شرایط خروج از معامله.
        
        Args:
            market_data: داده‌های بازار
            current_index: ایندکس فعلی
            entry_price: قیمت ورود
            position_type: نوع پوزیشن ("LONG" یا "SHORT")
            
        Returns:
            True اگر باید خارج شود، False در غیر این صورت
        """
        pass
    
    def get_stop_loss(self, entry_price: float, position_type: str) -> Optional[float]:
        """
        محاسبه stop loss (اختیاری).
        
        Args:
            entry_price: قیمت ورود
            position_type: نوع پوزیشن
            
        Returns:
            قیمت stop loss یا None
        """
        return None
    
    def get_take_profit(self, entry_price: float, position_type: str) -> Optional[float]:
        """
        محاسبه take profit (اختیاری).
        
        Args:
            entry_price: قیمت ورود
            position_type: نوع پوزیشن
            
        Returns:
            قیمت take profit یا None
        """
        return None
    
    def reset(self):
        """بازنشانی وضعیت استراتژی"""
        self.current_position = None
