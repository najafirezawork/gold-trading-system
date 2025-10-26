"""
Performance metrics calculator.
"""

import numpy as np
from typing import List, Optional, Tuple
from datetime import datetime

from .models import Trade, BacktestResult


class PerformanceMetrics:
    """محاسبه معیارهای عملکرد"""
    
    @staticmethod
    def calculate_metrics(
        trades: List[Trade],
        initial_capital: float,
        final_capital: float,
        equity_curve: List[float],
        strategy_name: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResult:
        """
        محاسبه تمام معیارهای عملکرد.
        
        Args:
            trades: لیست معاملات
            initial_capital: سرمایه اولیه
            final_capital: سرمایه نهایی
            equity_curve: منحنی سرمایه
            strategy_name: نام استراتژی
            symbol: نماد
            start_date: تاریخ شروع
            end_date: تاریخ پایان
            
        Returns:
            BacktestResult با تمام metrics
        """
        closed_trades = [t for t in trades if t.status.value == "CLOSED"]
        
        # بازده کل
        total_return = final_capital - initial_capital
        total_return_pct = (total_return / initial_capital) * 100
        
        # آمار معاملات
        total_trades = len(closed_trades)
        winning_trades = len([t for t in closed_trades if t.profit_loss > 0])
        losing_trades = len([t for t in closed_trades if t.profit_loss < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # میانگین سود/زیان
        profits = [t.profit_loss for t in closed_trades if t.profit_loss > 0]
        losses = [abs(t.profit_loss) for t in closed_trades if t.profit_loss < 0]
        
        avg_profit = np.mean(profits) if profits else 0.0
        avg_loss = np.mean(losses) if losses else 0.0
        
        # Profit Factor
        total_profit = sum(profits) if profits else 0.0
        total_loss = sum(losses) if losses else 0.0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0.0
        
        # Maximum Drawdown
        max_dd, max_dd_pct = PerformanceMetrics._calculate_max_drawdown(equity_curve, initial_capital)
        
        # Sharpe & Sortino Ratios
        sharpe = PerformanceMetrics._calculate_sharpe_ratio(closed_trades)
        sortino = PerformanceMetrics._calculate_sortino_ratio(closed_trades)
        
        return BacktestResult(
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=final_capital,
            trades=closed_trades,
            total_return=total_return,
            total_return_pct=total_return_pct,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino
        )
    
    @staticmethod
    def _calculate_max_drawdown(equity_curve: List[float], initial: float) -> tuple:
        """محاسبه Maximum Drawdown"""
        if not equity_curve:
            return 0.0, 0.0
        
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = equity_array - running_max
        
        max_dd = abs(np.min(drawdown))
        max_dd_pct = (max_dd / initial) * 100 if initial > 0 else 0.0
        
        return max_dd, max_dd_pct
    
    @staticmethod
    def _calculate_sharpe_ratio(trades: List[Trade], risk_free_rate: float = 0.0) -> Optional[float]:
        """
        محاسبه Sharpe Ratio.
        
        Args:
            trades: لیست معاملات
            risk_free_rate: نرخ بدون ریسک سالانه
            
        Returns:
            Sharpe ratio یا None
        """
        if not trades:
            return None
        
        returns = [t.profit_loss_pct for t in trades]
        
        if len(returns) < 2:
            return None
        
        mean_return = np.mean(returns)
        std_return = np.std(returns, ddof=1)
        
        if std_return == 0:
            return None
        
        # فرض بر اینکه بازده‌ها روزانه هستند
        sharpe = (mean_return - risk_free_rate) / std_return
        
        # Annualized Sharpe (فرض 252 روز معاملاتی)
        sharpe_annual = sharpe * np.sqrt(252)
        
        return sharpe_annual
    
    @staticmethod
    def _calculate_sortino_ratio(trades: List[Trade], target_return: float = 0.0) -> Optional[float]:
        """
        محاسبه Sortino Ratio.
        
        فقط نوسانات منفی را در نظر می‌گیرد.
        
        Args:
            trades: لیست معاملات
            target_return: بازده هدف
            
        Returns:
            Sortino ratio یا None
        """
        if not trades:
            return None
        
        returns = [t.profit_loss_pct for t in trades]
        
        if len(returns) < 2:
            return None
        
        mean_return = np.mean(returns)
        
        # فقط بازده‌های منفی
        downside_returns = [r for r in returns if r < target_return]
        
        if not downside_returns:
            return None
        
        downside_std = np.std(downside_returns, ddof=1)
        
        if downside_std == 0:
            return None
        
        sortino = (mean_return - target_return) / downside_std
        
        # Annualized
        sortino_annual = sortino * np.sqrt(252)
        
        return sortino_annual
