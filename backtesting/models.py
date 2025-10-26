"""
Backtesting models and data structures.
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TradeType(Enum):
    """نوع معامله"""
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(Enum):
    """وضعیت معامله"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Trade(BaseModel):
    """مدل یک معامله"""
    
    id: int
    entry_time: datetime
    entry_price: float
    trade_type: TradeType
    size: float = 1.0
    
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    status: TradeStatus = TradeStatus.OPEN
    
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    commission: float = 0.0
    
    @property
    def profit_loss(self) -> float:
        """محاسبه سود/زیان"""
        if self.status == TradeStatus.OPEN or self.exit_price is None:
            return 0.0
        
        if self.trade_type == TradeType.BUY:
            pnl = (self.exit_price - self.entry_price) * self.size
        else:  # SELL
            pnl = (self.entry_price - self.exit_price) * self.size
        
        return pnl - self.commission
    
    @property
    def profit_loss_pct(self) -> float:
        """درصد سود/زیان"""
        if self.status == TradeStatus.OPEN or self.exit_price is None:
            return 0.0
        
        return (self.profit_loss / (self.entry_price * self.size)) * 100
    
    @property
    def duration(self) -> Optional[float]:
        """مدت زمان معامله (ساعت)"""
        if self.exit_time is None:
            return None
        
        return (self.exit_time - self.entry_time).total_seconds() / 3600


class BacktestResult(BaseModel):
    """نتیجه backtest"""
    
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    
    initial_capital: float
    final_capital: float
    
    trades: List[Trade]
    
    # Performance metrics
    total_return: float = 0.0
    total_return_pct: float = 0.0
    
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    
    @property
    def total_profit(self) -> float:
        """مجموع سود"""
        return sum(t.profit_loss for t in self.trades if t.profit_loss > 0)
    
    @property
    def total_loss(self) -> float:
        """مجموع زیان"""
        return abs(sum(t.profit_loss for t in self.trades if t.profit_loss < 0))
    
    def to_dict(self) -> dict:
        """تبدیل به dictionary"""
        return {
            "strategy": self.strategy_name,
            "symbol": self.symbol,
            "period": f"{self.start_date.date()} to {self.end_date.date()}",
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": f"${self.total_return:.2f} ({self.total_return_pct:.2f}%)",
            "trades": {
                "total": self.total_trades,
                "wins": self.winning_trades,
                "losses": self.losing_trades,
                "win_rate": f"{self.win_rate:.2f}%"
            },
            "performance": {
                "avg_profit": f"${self.avg_profit:.2f}",
                "avg_loss": f"${self.avg_loss:.2f}",
                "profit_factor": f"{self.profit_factor:.2f}",
                "max_drawdown": f"${self.max_drawdown:.2f} ({self.max_drawdown_pct:.2f}%)"
            },
            "ratios": {
                "sharpe": f"{self.sharpe_ratio:.2f}" if self.sharpe_ratio else "N/A",
                "sortino": f"{self.sortino_ratio:.2f}" if self.sortino_ratio else "N/A"
            }
        }
