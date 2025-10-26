"""
Advanced Strategies Backtesting - تست استراتژی‌های پیشرفته

مقایسه استراتژی‌های پیشرفته برای یافتن بهترین استراتژی.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import logging
import json
from datetime import datetime

from data_layer import TwelveDataClient
from backtesting import BacktestEngine
from backtesting.advanced_strategies import (
    TrendFollowingStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
    MultiConfirmationStrategy,
    AdaptiveRSIStrategy
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_all_advanced_strategies():
    """تست همه استراتژی‌های پیشرفته"""
    
    logger.info("\n" + "="*70)
    logger.info("🚀 Advanced Trading Strategies Comparison")
    logger.info("="*70)
    
    # دریافت داده
    client = TwelveDataClient()
    logger.info("\n📊 Fetching historical data for XAU/USD...")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="4h",  # 4 ساعته برای سرعت بیشتر
        outputsize=500  # 500 کندل
    )
    
    logger.info(f"✓ Fetched {len(market_data)} candles")
    logger.info(f"  Period: {market_data.data[-1].datetime.date()} to {market_data.data[0].datetime.date()}")
    
    # لیست استراتژی‌های پیشرفته
    strategies = [
        TrendFollowingStrategy(fast_ma=50, slow_ma=200),
        MeanReversionStrategy(bb_period=20, bb_std=2.0),
        BreakoutStrategy(lookback_period=20),
        MultiConfirmationStrategy(sma_period=50),
        AdaptiveRSIStrategy(rsi_period=14, atr_period=14)
    ]
    
    results = []
    
    logger.info("\n" + "="*70)
    logger.info("⏳ Running backtests...")
    logger.info("="*70 + "\n")
    
    for i, strategy in enumerate(strategies, 1):
        logger.info(f"[{i}/{len(strategies)}] Testing {strategy.name}...")
        
        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=10000.0,
            commission=2.0
        )
        
        result = engine.run(market_data, verbose=False)
        results.append(result)
        
        logger.info(f"  ✓ Completed: {result.total_trades} trades, "
                   f"{result.total_return_pct:.2f}% return, "
                   f"{result.win_rate:.2f}% win rate")
    
    client.close()
    
    # مقایسه نتایج
    display_comparison(results)
    
    # ذخیره نتایج
    save_comparison(results)
    
    return results


def display_comparison(results):
    """نمایش مقایسه استراتژی‌ها"""
    
    logger.info("\n" + "="*70)
    logger.info("📊 DETAILED COMPARISON")
    logger.info("="*70 + "\n")
    
    # هدر جدول
    print(f"{'Strategy':<40} {'Return %':>10} {'Trades':>8} {'Win Rate':>10} {'Sharpe':>8} {'Max DD':>10}")
    print("-" * 90)
    
    # نمایش هر استراتژی
    for result in results:
        sharpe_str = f"{result.sharpe_ratio:.2f}" if result.sharpe_ratio else "N/A"
        
        print(f"{result.strategy_name:<40} "
              f"{result.total_return_pct:>9.2f}% "
              f"{result.total_trades:>8} "
              f"{result.win_rate:>9.2f}% "
              f"{sharpe_str:>8} "
              f"{result.max_drawdown_pct:>9.2f}%")
    
    # بهترین‌ها
    logger.info("\n" + "="*70)
    logger.info("🏆 TOP PERFORMERS")
    logger.info("="*70)
    
    # بهترین از نظر Return
    best_return = max(results, key=lambda r: r.total_return_pct)
    logger.info(f"\n💰 Best Return: {best_return.strategy_name}")
    logger.info(f"   Return: {best_return.total_return_pct:.2f}%")
    logger.info(f"   Capital: ${best_return.initial_capital:,.2f} → ${best_return.final_capital:,.2f}")
    
    # بهترین از نظر Win Rate
    best_winrate = max(results, key=lambda r: r.win_rate if r.total_trades > 0 else 0)
    if best_winrate.total_trades > 0:
        logger.info(f"\n🎯 Best Win Rate: {best_winrate.strategy_name}")
        logger.info(f"   Win Rate: {best_winrate.win_rate:.2f}%")
        logger.info(f"   Trades: {best_winrate.winning_trades}/{best_winrate.total_trades}")
    
    # بهترین از نظر Sharpe
    valid_sharpe = [r for r in results if r.sharpe_ratio is not None]
    if valid_sharpe:
        best_sharpe = max(valid_sharpe, key=lambda r: r.sharpe_ratio)
        logger.info(f"\n📈 Best Sharpe Ratio: {best_sharpe.strategy_name}")
        logger.info(f"   Sharpe: {best_sharpe.sharpe_ratio:.2f}")
        logger.info(f"   Risk-adjusted return: Excellent" if best_sharpe.sharpe_ratio > 2 else "   Risk-adjusted return: Good")
    
    # کمترین Drawdown
    best_drawdown = min(results, key=lambda r: abs(r.max_drawdown_pct))
    logger.info(f"\n🛡️ Lowest Drawdown: {best_drawdown.strategy_name}")
    logger.info(f"   Max Drawdown: {best_drawdown.max_drawdown_pct:.2f}%")
    
    # استراتژی متعادل
    logger.info(f"\n⚖️ Most Balanced Strategy:")
    
    # امتیازدهی
    scores = []
    for result in results:
        if result.total_trades < 5:  # حداقل 5 معامله
            continue
        
        score = 0
        # Return (40%)
        score += (result.total_return_pct / 10) * 0.4
        # Win Rate (30%)
        score += (result.win_rate / 100) * 0.3
        # Sharpe (20%)
        if result.sharpe_ratio:
            score += max(0, result.sharpe_ratio / 3) * 0.2
        # Low Drawdown (10%)
        score += (1 - abs(result.max_drawdown_pct) / 20) * 0.1
        
        scores.append((result, score))
    
    if scores:
        best_balanced = max(scores, key=lambda x: x[1])
        result, score = best_balanced
        logger.info(f"   {result.strategy_name}")
        logger.info(f"   Overall Score: {score:.2f}/1.00")
        sharpe_str = f"{result.sharpe_ratio:.2f}" if result.sharpe_ratio else "N/A"
        logger.info(f"   Return: {result.total_return_pct:.2f}%, Win Rate: {result.win_rate:.2f}%, Sharpe: {sharpe_str}")


def save_comparison(results):
    """ذخیره مقایسه در JSON"""
    import os
    
    os.makedirs("results", exist_ok=True)
    
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "Advanced Strategies Comparison",
        "total_strategies": len(results),
        "strategies": []
    }
    
    for result in results:
        comparison["strategies"].append({
            "name": result.strategy_name,
            "metrics": {
                "return_pct": result.total_return_pct,
                "total_trades": result.total_trades,
                "win_rate": result.win_rate,
                "sharpe_ratio": result.sharpe_ratio,
                "sortino_ratio": result.sortino_ratio,
                "max_drawdown_pct": result.max_drawdown_pct,
                "profit_factor": result.profit_factor
            },
            "capital": {
                "initial": result.initial_capital,
                "final": result.final_capital,
                "return": result.total_return
            }
        })
    
    filepath = "results/advanced_strategies_comparison.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n💾 Comparison saved to: {filepath}")


def test_specific_strategy(strategy_name: str):
    """تست دقیق یک استراتژی خاص"""
    
    strategies_map = {
        "1": TrendFollowingStrategy(50, 200),
        "2": MeanReversionStrategy(20, 2.0),
        "3": BreakoutStrategy(20),
        "4": MultiConfirmationStrategy(50),
        "5": AdaptiveRSIStrategy(14, 14)
    }
    
    if strategy_name not in strategies_map:
        logger.error("Invalid strategy selection")
        return
    
    strategy = strategies_map[strategy_name]
    
    logger.info("\n" + "="*70)
    logger.info(f"🔍 Detailed Test: {strategy.name}")
    logger.info("="*70)
    
    client = TwelveDataClient()
    logger.info("\nFetching data...")
    
    market_data = client.get_time_series("XAU/USD", "1h", 1000)
    
    logger.info(f"✓ Fetched {len(market_data)} candles")
    
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=10000.0,
        commission=2.0
    )
    
    logger.info("\nRunning backtest with verbose output...\n")
    result = engine.run(market_data, verbose=True)
    
    # نمایش نتایج دقیق
    logger.info("\n" + "="*70)
    logger.info("📊 DETAILED RESULTS")
    logger.info("="*70)
    
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
        logger.info(f"\n📊 Risk Metrics:")
        logger.info(f"  Sharpe Ratio:   {result.sharpe_ratio:.2f}")
        if result.sortino_ratio:
            logger.info(f"  Sortino Ratio:  {result.sortino_ratio:.2f}")
    
    # نمایش معاملات
    if result.trades:
        logger.info(f"\n📝 All Trades:")
        for trade in result.trades:
            status = "✓" if trade.profit_loss > 0 else "✗"
            logger.info(f"  {status} #{trade.id} {trade.trade_type.value}: "
                       f"${trade.entry_price:.2f} → ${trade.exit_price:.2f} | "
                       f"P/L: ${trade.profit_loss:.2f} ({trade.profit_loss_pct:.2f}%)")
    
    # ذخیره
    filename = f"backtest_{strategy.name.replace(' ', '_').lower()}.json"
    filepath = f"results/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"\n💾 Results saved to: {filepath}")
    
    client.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Gold Trading System - Advanced Strategies Testing")
    print("="*70)
    print("\nSelect test mode:")
    print("1. Trend Following Strategy")
    print("2. Mean Reversion Strategy")
    print("3. Breakout Strategy")
    print("4. Multi-Confirmation Strategy")
    print("5. Adaptive RSI Strategy")
    print("6. Compare ALL Advanced Strategies")
    print()
    
    choice = input("شماره (1-6): ").strip()
    
    if choice == "6":
        test_all_advanced_strategies()
    elif choice in ["1", "2", "3", "4", "5"]:
        test_specific_strategy(choice)
    else:
        print("❌ Invalid choice")
