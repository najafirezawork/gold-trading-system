"""
Backtesting engine.
"""

import logging
from typing import Optional
from datetime import datetime

from data_layer import MarketData, TwelveDataClient
from agents import SignalAgent
from .strategy import BaseStrategy
from .models import Trade, TradeType, TradeStatus, BacktestResult
from .metrics import PerformanceMetrics


logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    موتور اصلی backtesting.
    
    این کلاس یک استراتژی را روی داده‌های تاریخی اجرا می‌کند
    و نتایج را تحلیل می‌کند.
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 10000.0,
        commission: float = 0.0,
        use_signal_agent: bool = False
    ):
        """
        Initialize backtest engine.
        
        Args:
            strategy: استراتژی معاملاتی
            initial_capital: سرمایه اولیه
            commission: کمیسیون هر معامله (دلار)
            use_signal_agent: استفاده از Signal Agent در تصمیم‌گیری
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.use_signal_agent = use_signal_agent
        
        self.capital = initial_capital
        self.trades = []
        self.equity_curve = [initial_capital]
        self.current_trade: Optional[Trade] = None
        
        if use_signal_agent:
            self.signal_agent = SignalAgent()
        else:
            self.signal_agent = None
        
        logger.info(f"Initialized BacktestEngine for strategy: {strategy.name}")
    
    def run(
        self,
        market_data: MarketData,
        verbose: bool = True
    ) -> BacktestResult:
        """
        اجرای backtest.
        
        Args:
            market_data: داده‌های تاریخی بازار
            verbose: نمایش پیشرفت
            
        Returns:
            BacktestResult با نتایج کامل
        """
        logger.info(f"Starting backtest for {market_data.symbol}")
        logger.info(f"Data points: {len(market_data)}")
        
        # بازنشانی وضعیت
        self._reset()
        
        # دریافت agent output (اگر لازم باشد)
        agent_output = None
        if self.signal_agent:
            agent_output = self.signal_agent.analyze(market_data)
        
        # حلقه اصلی backtest
        for i in range(len(market_data.data)):
            current_bar = market_data.data[i]
            
            # بررسی خروج از معامله فعلی
            if self.current_trade:
                should_exit = self._check_exit(market_data, i, current_bar.close)
                
                if should_exit:
                    self._close_trade(current_bar.datetime, current_bar.close)
            
            # بررسی ورود به معامله جدید
            if not self.current_trade:
                entry_signal = self.strategy.should_enter(
                    market_data, i, agent_output
                )
                
                if entry_signal:
                    self._open_trade(
                        current_bar.datetime,
                        current_bar.close,
                        entry_signal
                    )
            
            # بروزرسانی equity curve
            self._update_equity(current_bar.close)
            
            if verbose and (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(market_data.data)} bars")
        
        # بستن معامله باز (اگر وجود داشته باشد)
        if self.current_trade:
            last_bar = market_data.data[-1]
            self._close_trade(last_bar.datetime, last_bar.close)
        
        # محاسبه metrics
        result = PerformanceMetrics.calculate_metrics(
            trades=self.trades,
            initial_capital=self.initial_capital,
            final_capital=self.capital,
            equity_curve=self.equity_curve,
            strategy_name=self.strategy.name,
            symbol=market_data.symbol,
            start_date=market_data.data[0].datetime,
            end_date=market_data.data[-1].datetime
        )
        
        logger.info(f"Backtest completed: {result.total_trades} trades, "
                   f"${result.total_return:.2f} return ({result.total_return_pct:.2f}%)")
        
        return result
    
    def _reset(self):
        """بازنشانی وضعیت engine"""
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.current_trade = None
        self.strategy.reset()
    
    def _open_trade(self, entry_time: datetime, entry_price: float, signal: str):
        """باز کردن معامله جدید"""
        trade_id = len(self.trades) + 1
        trade_type = TradeType.BUY if signal == "BUY" else TradeType.SELL
        
        # محاسبه stop loss و take profit
        position_type = "LONG" if signal == "BUY" else "SHORT"
        stop_loss = self.strategy.get_stop_loss(entry_price, position_type)
        take_profit = self.strategy.get_take_profit(entry_price, position_type)
        
        self.current_trade = Trade(
            id=trade_id,
            entry_time=entry_time,
            entry_price=entry_price,
            trade_type=trade_type,
            size=1.0,  # می‌توان پویا محاسبه کرد
            commission=self.commission,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        self.strategy.current_position = position_type
        
        logger.debug(f"Opened {trade_type.value} trade #{trade_id} at ${entry_price:.2f}")
    
    def _close_trade(self, exit_time: datetime, exit_price: float):
        """بستن معامله فعلی"""
        if not self.current_trade:
            return
        
        self.current_trade.exit_time = exit_time
        self.current_trade.exit_price = exit_price
        self.current_trade.status = TradeStatus.CLOSED
        
        # بروزرسانی سرمایه
        self.capital += self.current_trade.profit_loss
        
        self.trades.append(self.current_trade)
        
        logger.debug(f"Closed trade #{self.current_trade.id}: "
                    f"P/L = ${self.current_trade.profit_loss:.2f} "
                    f"({self.current_trade.profit_loss_pct:.2f}%)")
        
        self.current_trade = None
        self.strategy.current_position = None
    
    def _check_exit(self, market_data: MarketData, index: int, current_price: float) -> bool:
        """بررسی شرایط خروج"""
        if not self.current_trade:
            return False
        
        # بررسی stop loss
        if self.current_trade.stop_loss:
            if self.current_trade.trade_type == TradeType.BUY:
                if current_price <= self.current_trade.stop_loss:
                    logger.debug(f"Stop loss hit at ${current_price:.2f}")
                    return True
            else:  # SELL
                if current_price >= self.current_trade.stop_loss:
                    logger.debug(f"Stop loss hit at ${current_price:.2f}")
                    return True
        
        # بررسی take profit
        if self.current_trade.take_profit:
            if self.current_trade.trade_type == TradeType.BUY:
                if current_price >= self.current_trade.take_profit:
                    logger.debug(f"Take profit hit at ${current_price:.2f}")
                    return True
            else:  # SELL
                if current_price <= self.current_trade.take_profit:
                    logger.debug(f"Take profit hit at ${current_price:.2f}")
                    return True
        
        # بررسی شرایط خروج استراتژی
        position_type = "LONG" if self.current_trade.trade_type == TradeType.BUY else "SHORT"
        
        return self.strategy.should_exit(
            market_data,
            index,
            self.current_trade.entry_price,
            position_type
        )
    
    def _update_equity(self, current_price: float):
        """بروزرسانی منحنی سرمایه"""
        equity = self.capital
        
        # اضافه کردن P/L شناور
        if self.current_trade:
            if self.current_trade.trade_type == TradeType.BUY:
                floating_pnl = (current_price - self.current_trade.entry_price) * self.current_trade.size
            else:
                floating_pnl = (self.current_trade.entry_price - current_price) * self.current_trade.size
            
            equity += floating_pnl
        
        self.equity_curve.append(equity)
