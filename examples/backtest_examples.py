"""
Backtesting Examples - مثال‌های استفاده از backtesting

این فایل نحوه استفاده از backtesting module را نشان می‌دهد.
"""

import sys
from pathlib import Path

# اضافه کردن root directory به path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import logging
import json
from datetime import datetime

from data_layer import TwelveDataClient
from backtesting import BacktestEngine
from backtesting.strategies import SimpleMAStrategy, RSIStrategy, SignalAgentStrategy


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backtest_ma_strategy():
    """مثال 1: Backtest استراتژی Moving Average"""
    
    logger.info("\n" + "="*60)
    logger.info("📊 Backtesting MA Crossover Strategy")
    logger.info("="*60)
    
    # دریافت داده‌های تاریخی
    client = TwelveDataClient()
    logger.info("Fetching historical data for XAU/USD...")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=500  # 500 ساعت داده
    )
    
    logger.info(f"✓ Fetched {len(market_data)} candles")
    logger.info(f"  Period: {market_data.data[-1].datetime.date()} to {market_data.data[0].datetime.date()}")
    
    # ایجاد استراتژی
    strategy = SimpleMAStrategy(short_period=20, long_period=50)
    
    # ایجاد backtest engine
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=10000.0,
        commission=2.0  # $2 کمیسیون هر معامله
    )
    
    # اجرای backtest
    logger.info("\nRunning backtest...")
    result = engine.run(market_data, verbose=True)
    
    # نمایش نتایج
    print_backtest_results(result)
    
    # ذخیره نتایج
    save_results(result, "backtest_ma_strategy.json")
    
    client.close()


def backtest_rsi_strategy():
    """مثال 2: Backtest استراتژی RSI"""
    
    logger.info("\n" + "="*60)
    logger.info("📊 Backtesting RSI Strategy")
    logger.info("="*60)
    
    client = TwelveDataClient()
    logger.info("Fetching historical data...")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=500
    )
    
    logger.info(f"✓ Fetched {len(market_data)} candles")
    
    # استراتژی RSI
    strategy = RSIStrategy(rsi_period=14, oversold=30, overbought=70)
    
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=10000.0,
        commission=2.0
    )
    
    logger.info("\nRunning backtest...")
    result = engine.run(market_data, verbose=True)
    
    print_backtest_results(result)
    save_results(result, "backtest_rsi_strategy.json")
    
    client.close()


def backtest_signal_agent_strategy():
    """مثال 3: Backtest استراتژی Signal Agent"""
    
    logger.info("\n" + "="*60)
    logger.info("📊 Backtesting Signal Agent Strategy")
    logger.info("="*60)
    
    client = TwelveDataClient()
    logger.info("Fetching historical data...")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="4h",
        outputsize=300  # 300 کندل 4 ساعته
    )
    
    logger.info(f"✓ Fetched {len(market_data)} candles")
    
    # استراتژی با Signal Agent
    strategy = SignalAgentStrategy(signal_threshold=0.3)
    
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=10000.0,
        commission=2.0,
        use_signal_agent=True  # استفاده از agent
    )
    
    logger.info("\nRunning backtest with Signal Agent...")
    result = engine.run(market_data, verbose=True)
    
    print_backtest_results(result)
    save_results(result, "backtest_signal_agent.json")
    
    client.close()


def compare_strategies():
    """مثال 4: مقایسه چند استراتژی"""
    
    logger.info("\n" + "="*60)
    logger.info("📊 Comparing Multiple Strategies")
    logger.info("="*60)
    
    client = TwelveDataClient()
    logger.info("Fetching historical data...")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=500
    )
    
    logger.info(f"✓ Fetched {len(market_data)} candles")
    
    # لیست استراتژی‌ها
    strategies = [
        SimpleMAStrategy(20, 50),
        RSIStrategy(14, 30, 70),
        SignalAgentStrategy(0.3)
    ]
    
    results = []
    
    for strategy in strategies:
        logger.info(f"\n Testing {strategy.name}...")
        
        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=10000.0,
            commission=2.0,
            use_signal_agent=isinstance(strategy, SignalAgentStrategy)
        )
        
        result = engine.run(market_data, verbose=False)
        results.append(result)
    
    # مقایسه نتایج
    logger.info("\n" + "="*60)
    logger.info("📊 Comparison Results")
    logger.info("="*60)
    
    print("\n{:<30} {:>12} {:>12} {:>10} {:>12}".format(
        "Strategy", "Return", "Return %", "Trades", "Win Rate"
    ))
    print("-" * 80)
    
    for result in results:
        print("{:<30} ${:>11.2f} {:>11.2f}% {:>10} {:>11.2f}%".format(
            result.strategy_name,
            result.total_return,
            result.total_return_pct,
            result.total_trades,
            result.win_rate
        ))
    
    # بهترین استراتژی
    best = max(results, key=lambda r: r.total_return)
    logger.info(f"\n🏆 Best Strategy: {best.strategy_name}")
    logger.info(f"   Return: ${best.total_return:.2f} ({best.total_return_pct:.2f}%)")
    
    client.close()


def print_backtest_results(result):
    """نمایش نتایج backtest"""
    
    logger.info("\n" + "="*60)
    logger.info("📊 Backtest Results")
    logger.info("="*60)
    
    logger.info(f"\nStrategy: {result.strategy_name}")
    logger.info(f"Symbol: {result.symbol}")
    logger.info(f"Period: {result.start_date.date()} to {result.end_date.date()}")
    
    logger.info(f"\n💰 Capital:")
    logger.info(f"  Initial:  ${result.initial_capital:,.2f}")
    logger.info(f"  Final:    ${result.final_capital:,.2f}")
    logger.info(f"  Return:   ${result.total_return:,.2f} ({result.total_return_pct:.2f}%)")
    
    logger.info(f"\n📈 Trades:")
    logger.info(f"  Total:    {result.total_trades}")
    logger.info(f"  Winners:  {result.winning_trades}")
    logger.info(f"  Losers:   {result.losing_trades}")
    logger.info(f"  Win Rate: {result.win_rate:.2f}%")
    
    logger.info(f"\n💵 Performance:")
    logger.info(f"  Avg Profit:     ${result.avg_profit:.2f}")
    logger.info(f"  Avg Loss:       ${result.avg_loss:.2f}")
    logger.info(f"  Profit Factor:  {result.profit_factor:.2f}")
    logger.info(f"  Max Drawdown:   ${result.max_drawdown:.2f} ({result.max_drawdown_pct:.2f}%)")
    
    if result.sharpe_ratio:
        logger.info(f"\n📊 Ratios:")
        logger.info(f"  Sharpe:   {result.sharpe_ratio:.2f}")
        if result.sortino_ratio:
            logger.info(f"  Sortino:  {result.sortino_ratio:.2f}")
    
    # نمایش چند معامله نمونه
    if result.trades:
        logger.info(f"\n📝 Sample Trades (first 5):")
        for trade in result.trades[:5]:
            logger.info(f"  #{trade.id} {trade.trade_type.value}: "
                       f"${trade.entry_price:.2f} → ${trade.exit_price:.2f} | "
                       f"P/L: ${trade.profit_loss:.2f} ({trade.profit_loss_pct:.2f}%)")


def save_results(result, filename: str):
    """ذخیره نتایج در JSON"""
    import os
    
    # ساخت دایرکتوری results
    os.makedirs("results", exist_ok=True)
    
    filepath = f"results/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"\n💾 Results saved to: {filepath}")


if __name__ == "__main__":
    print("\n🚀 Gold Trading System - Backtesting Examples\n")
    print("انتخاب کنید:")
    print("1. Backtest MA Crossover Strategy")
    print("2. Backtest RSI Strategy")
    print("3. Backtest Signal Agent Strategy")
    print("4. Compare All Strategies")
    print()
    
    choice = input("شماره (1-4): ").strip()
    
    if choice == "1":
        backtest_ma_strategy()
    elif choice == "2":
        backtest_rsi_strategy()
    elif choice == "3":
        backtest_signal_agent_strategy()
    elif choice == "4":
        compare_strategies()
    else:
        print("❌ Invalid choice")
