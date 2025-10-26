"""
Test suite for Backtesting Module.

تست‌های جامع برای ماژول backtesting.
"""

import unittest
from datetime import datetime, timedelta
from typing import Optional

from data_layer import MarketData, OHLCV
from backtesting import (
    Trade, TradeType, TradeStatus, BacktestResult,
    BaseStrategy, BacktestEngine, PerformanceMetrics
)


class SimpleTestStrategy(BaseStrategy):
    """استراتژی ساده برای تست"""
    
    def __init__(self):
        super().__init__("Test Strategy")
        self.enter_count = 0
    
    def should_enter(self, market_data, current_index, agent_output=None):
        """ورود هر 10 بار"""
        self.enter_count += 1
        if self.enter_count % 10 == 0:
            return "BUY"
        return None
    
    def should_exit(self, market_data, current_index, entry_price, position_type):
        """خروج بعد از 5 کندل"""
        return True if current_index % 5 == 0 else False


class TestTrade(unittest.TestCase):
    """تست مدل Trade"""
    
    def setUp(self):
        self.entry_time = datetime.now()
        self.exit_time = self.entry_time + timedelta(hours=1)
    
    def test_trade_creation(self):
        """تست ساخت trade"""
        trade = Trade(
            id=1,
            trade_type=TradeType.BUY,
            entry_price=100.0,
            entry_time=self.entry_time,
            exit_price=105.0,
            exit_time=self.exit_time,
            status=TradeStatus.CLOSED
        )
        
        self.assertEqual(trade.id, 1)
        self.assertEqual(trade.trade_type, TradeType.BUY)
        self.assertEqual(trade.profit_loss, 5.0)
        self.assertEqual(trade.profit_loss_pct, 5.0)
    
    def test_trade_long_profit(self):
        """تست سود در LONG"""
        trade = Trade(
            id=1,
            trade_type=TradeType.BUY,
            entry_price=100.0,
            entry_time=self.entry_time,
            exit_price=110.0,
            exit_time=self.exit_time,
            status=TradeStatus.CLOSED
        )
        
        self.assertEqual(trade.profit_loss, 10.0)
        self.assertEqual(trade.profit_loss_pct, 10.0)
    
    def test_trade_long_loss(self):
        """تست زیان در LONG"""
        trade = Trade(
            id=1,
            trade_type=TradeType.BUY,
            entry_price=100.0,
            entry_time=self.entry_time,
            exit_price=95.0,
            exit_time=self.exit_time,
            status=TradeStatus.CLOSED
        )
        
        self.assertEqual(trade.profit_loss, -5.0)
        self.assertEqual(trade.profit_loss_pct, -5.0)
    
    def test_trade_short_profit(self):
        """تست سود در SHORT"""
        trade = Trade(
            id=1,
            trade_type=TradeType.SELL,
            entry_price=100.0,
            entry_time=self.entry_time,
            exit_price=90.0,
            exit_time=self.exit_time,
            status=TradeStatus.CLOSED
        )
        
        self.assertEqual(trade.profit_loss, 10.0)
        self.assertEqual(trade.profit_loss_pct, 10.0)
    
    def test_trade_duration(self):
        """تست محاسبه duration"""
        trade = Trade(
            id=1,
            trade_type=TradeType.BUY,
            entry_price=100.0,
            entry_time=self.entry_time,
            exit_price=105.0,
            exit_time=self.entry_time + timedelta(hours=2, minutes=30),
            status=TradeStatus.CLOSED
        )
        
        self.assertEqual(trade.duration.total_seconds(), 9000)  # 2.5 hours


class TestBaseStrategy(unittest.TestCase):
    """تست BaseStrategy"""
    
    def test_strategy_creation(self):
        """تست ساخت strategy"""
        strategy = SimpleTestStrategy()
        
        self.assertEqual(strategy.name, "Test Strategy")
        self.assertIsNone(strategy.get_stop_loss(100.0, "LONG"))
        self.assertIsNone(strategy.get_take_profit(100.0, "LONG"))


class TestPerformanceMetrics(unittest.TestCase):
    """تست محاسبات Performance Metrics"""
    
    def test_sharpe_ratio(self):
        """تست Sharpe Ratio"""
        returns = [0.01, 0.02, -0.01, 0.03, 0.01]  # روزانه
        sharpe = PerformanceMetrics.calculate_sharpe_ratio(returns)
        
        self.assertIsNotNone(sharpe)
        self.assertIsInstance(sharpe, float)
    
    def test_sortino_ratio(self):
        """تست Sortino Ratio"""
        returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        sortino = PerformanceMetrics.calculate_sortino_ratio(returns)
        
        self.assertIsNotNone(sortino)
        self.assertIsInstance(sortino, float)
    
    def test_max_drawdown(self):
        """تست Max Drawdown"""
        equity = [10000, 10500, 10200, 10800, 10300, 11000]
        max_dd, max_dd_pct = PerformanceMetrics.calculate_max_drawdown(equity)
        
        self.assertGreater(max_dd, 0)
        self.assertGreater(max_dd_pct, 0)
        self.assertLess(max_dd_pct, 100)


class TestBacktestEngine(unittest.TestCase):
    """تست Backtest Engine"""
    
    def setUp(self):
        """ساخت market data نمونه"""
        base_time = datetime.now()
        base_price = 2000.0
        
        data = []
        for i in range(100):
            # ساخت داده نوسانی
            price = base_price + (i % 10) * 5
            
            data.append(OHLCV(
                datetime=base_time + timedelta(hours=i),
                open=price,
                high=price + 2,
                low=price - 2,
                close=price,
                volume=1000.0
            ))
        
        self.market_data = MarketData(
            symbol="TEST/USD",
            interval="1h",
            data=data,
            meta={}
        )
        
        self.strategy = SimpleTestStrategy()
    
    def test_engine_creation(self):
        """تست ساخت engine"""
        engine = BacktestEngine(
            strategy=self.strategy,
            initial_capital=10000.0,
            commission=2.0
        )
        
        self.assertEqual(engine.initial_capital, 10000.0)
        self.assertEqual(engine.commission, 2.0)
        self.assertEqual(engine.strategy, self.strategy)
    
    def test_backtest_run(self):
        """تست اجرای backtest"""
        engine = BacktestEngine(
            strategy=self.strategy,
            initial_capital=10000.0,
            commission=2.0
        )
        
        result = engine.run(self.market_data, verbose=False)
        
        # بررسی نتایج
        self.assertIsInstance(result, BacktestResult)
        self.assertEqual(result.initial_capital, 10000.0)
        self.assertIsNotNone(result.final_capital)
        self.assertIsNotNone(result.total_return)
        self.assertGreaterEqual(result.total_trades, 0)
    
    def test_backtest_with_commission(self):
        """تست backtest با commission"""
        engine = BacktestEngine(
            strategy=self.strategy,
            initial_capital=10000.0,
            commission=10.0  # کمیسیون بالا
        )
        
        result = engine.run(self.market_data, verbose=False)
        
        # با commission بالا، return باید کمتر باشد
        self.assertIsNotNone(result.total_return)
    
    def test_equity_curve(self):
        """تست equity curve"""
        engine = BacktestEngine(
            strategy=self.strategy,
            initial_capital=10000.0,
            commission=2.0
        )
        
        result = engine.run(self.market_data, verbose=False)
        
        # equity curve باید وجود داشته باشد
        self.assertIsNotNone(result.equity_curve)
        self.assertGreater(len(result.equity_curve), 0)
        self.assertEqual(result.equity_curve[0], 10000.0)


class TestBacktestResult(unittest.TestCase):
    """تست BacktestResult model"""
    
    def test_result_creation(self):
        """تست ساخت result"""
        result = BacktestResult(
            strategy_name="Test",
            symbol="TEST/USD",
            interval="1h",
            start_date=datetime.now(),
            end_date=datetime.now(),
            initial_capital=10000.0,
            final_capital=11000.0,
            total_return=1000.0,
            total_return_pct=10.0,
            total_trades=10,
            winning_trades=6,
            losing_trades=4,
            win_rate=60.0,
            avg_profit=200.0,
            avg_loss=-100.0,
            profit_factor=2.0,
            max_drawdown=500.0,
            max_drawdown_pct=5.0,
            trades=[],
            equity_curve=[10000.0, 11000.0]
        )
        
        self.assertEqual(result.strategy_name, "Test")
        self.assertEqual(result.win_rate, 60.0)
        self.assertEqual(result.profit_factor, 2.0)
    
    def test_result_to_dict(self):
        """تست تبدیل به dictionary"""
        result = BacktestResult(
            strategy_name="Test",
            symbol="TEST/USD",
            interval="1h",
            start_date=datetime.now(),
            end_date=datetime.now(),
            initial_capital=10000.0,
            final_capital=11000.0,
            total_return=1000.0,
            total_return_pct=10.0,
            total_trades=5,
            winning_trades=3,
            losing_trades=2,
            win_rate=60.0,
            avg_profit=200.0,
            avg_loss=-100.0,
            profit_factor=1.5,
            max_drawdown=500.0,
            max_drawdown_pct=5.0,
            trades=[],
            equity_curve=[10000.0]
        )
        
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["strategy_name"], "Test")
        self.assertEqual(result_dict["total_trades"], 5)


def run_tests():
    """اجرای تمام تست‌ها"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Running Backtesting Module Tests")
    print("="*60 + "\n")
    
    run_tests()
