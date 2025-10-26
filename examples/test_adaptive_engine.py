"""
Example: Adaptive Strategy Selection
استفاده از Adaptive Engine برای انتخاب خودکار بهترین استراتژی
"""

import sys
from pathlib import Path

# اضافه کردن root directory به path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from data_layer.client import TwelveDataClient
from data_layer.models import MarketData
from backtesting.adaptive_engine import AdaptiveBacktestEngine
from backtesting.advanced_strategies import (
    TrendFollowingStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
    AdaptiveRSIStrategy
)
from backtesting.high_winrate_strategies import (
    ScalpingStrategy,
    SafeRSIStrategy
)


def main():
    """
    مقایسه Adaptive Engine با استفاده از strategy ثابت
    """
    
    print("="*80)
    print("ADAPTIVE STRATEGY SELECTION TEST")
    print("="*80)
    print()
    
    # دریافت داده
    print("Fetching data from Twelve Data API...")
    client = TwelveDataClient(
        api_key="e2527b8bfdac451094f85f9aa826bc65"
    )
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=1000
    )
    
    if not market_data or not market_data.data:
        print("Failed to fetch data")
        return
    
    data = market_data.data
    
    print(f"Fetched {len(data)} candles")
    print(f"   Period: {data[0].datetime} to {data[-1].datetime}")
    print()
    
    # ================================
    # قسمت 1: Adaptive Engine
    # ================================
    print("\n" + "="*80)
    print("PART 1: ADAPTIVE ENGINE")
    print("="*80)
    
    strategies_adaptive = {
        "TrendFollowing": TrendFollowingStrategy(),
        "MeanReversion": MeanReversionStrategy(),
        "AdaptiveRSI": AdaptiveRSIStrategy(),
        "SafeRSI": SafeRSIStrategy()
    }
    
    adaptive_engine = AdaptiveBacktestEngine(
        strategies=strategies_adaptive,
        regime_lookback=100,
        min_confidence=0.6,
        verbose=True
    )
    
    adaptive_result = adaptive_engine.run(
        data=data,
        initial_capital=10000,
        commission=2.0
    )
    
    # نمایش آمار
    stats = adaptive_engine.get_stats()
    print(f"\nAdaptive Engine Stats:")
    print(f"Regime Distribution: {stats['regime_distribution']}")
    print(f"Strategy Usage: {stats['strategy_usage']}")
    
    # ================================
    # قسمت 2: تک استراتژی (برای مقایسه)
    # ================================
    print("\n" + "="*80)
    print("PART 2: INDIVIDUAL STRATEGIES (For Comparison)")
    print("="*80)
    
    from backtesting.engine import BacktestEngine
    
    single_results = {}
    
    for name, strategy in strategies_adaptive.items():
        print(f"\n{name}:")
        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=10000,
            commission=2.0
        )
        
        result = engine.run(market_data, verbose=False)
        single_results[name] = result
        
        # تبدیل MarketData به لیست برای Adaptive Engine
        market_data_obj = MarketData(
            symbol="XAU/USD",
            interval="1h",
            data=data
        )
        
        print(f"  Return: {result.total_return_pct:+.2f}%")
        print(f"  Win Rate: {result.win_rate:.1f}%")
        print(f"  Trades: {result.total_trades}")
        print(f"  Sharpe: {result.sharpe_ratio:.2f}" if result.sharpe_ratio else "  Sharpe: N/A")
        print(f"  Max DD: {result.max_drawdown:.2f}%")
    
    # ================================
    # قسمت 3: مقایسه نهایی
    # ================================
    print("\n" + "="*80)
    print("FINAL COMPARISON")
    print("="*80)
    
    print(f"\n{'Strategy':<25} {'Return':<12} {'Win Rate':<12} {'Trades':<10} {'Sharpe':<10}")
    print("-"*80)
    
    # Adaptive
    print(f"{'Adaptive (Best)':<25} "
          f"{adaptive_result.total_return_pct:>+10.2f}% "
          f"{adaptive_result.win_rate:>10.1f}% "
          f"{adaptive_result.total_trades:>8} "
          f"{adaptive_result.sharpe_ratio:>8.2f}" if adaptive_result.sharpe_ratio else f"{'N/A':>8}")
    
    print()
    
    # Individual strategies
    for name, result in single_results.items():
        sharpe_str = f"{result.sharpe_ratio:>8.2f}" if result.sharpe_ratio else f"{'N/A':>8}"
        print(f"{name:<25} "
              f"{result.total_return_pct:>+10.2f}% "
              f"{result.win_rate:>10.1f}% "
              f"{result.total_trades:>8} "
              f"{sharpe_str}")
    
    print("\n" + "="*80)
    
    # محاسبه بهبود
    best_single = max(single_results.values(), key=lambda r: r.total_return_pct)
    improvement = adaptive_result.total_return_pct - best_single.total_return_pct
    
    print(f"\nInsights:")
    print(f"   Adaptive Engine Return: {adaptive_result.total_return_pct:+.2f}%")
    print(f"   Best Single Strategy: {best_single.total_return_pct:+.2f}%")
    print(f"   Improvement: {improvement:+.2f}%")
    
    if improvement > 0:
        print(f"   Adaptive engine outperformed by {improvement:.2f}%!")
    else:
        print(f"   Best single strategy performed better this time")
        print(f"      (This is expected in some market conditions)")
    
    print("\n" + "="*80)


def test_different_timeframes():
    """
    تست Adaptive Engine با timeframe های مختلف
    """
    
    print("\n" + "="*80)
    print("TESTING DIFFERENT TIMEFRAMES")
    print("="*80)
    
    collector = TwelveDataClient(
        api_key="e2527b8bfdac451094f85f9aa826bc65"
    )
    
    timeframes = ["15min", "1h", "4h"]
    
    strategies = {
        "Scalping": ScalpingStrategy(),  # برای 15min
        "MeanReversion": MeanReversionStrategy(),  # برای ranging
        "TrendFollowing": TrendFollowingStrategy(),  # برای trending
    }
    
    for interval in timeframes:
        print(f"\n{'='*80}")
        print(f"Timeframe: {interval}")
        print(f"{'='*80}")
        
        market_data = collector.get_time_series(
            symbol="XAU/USD",
            interval=interval,
            outputsize=500
        )
        
        if not market_data or not market_data.data:
            print(f"Failed to fetch {interval} data")
            continue
        
        data = market_data.data
        
        print(f"Fetched {len(data)} candles")
        
        adaptive_engine = AdaptiveBacktestEngine(
            strategies=strategies,
            regime_lookback=min(100, len(data) // 5),
            min_confidence=0.6,
            verbose=False
        )
        
        result = adaptive_engine.run(
            data=data,
            initial_capital=10000,
            commission=2.0
        )
        
        print(f"\nResult:")
        print(f"  Return: {result.total_return_pct:+.2f}%")
        print(f"  Win Rate: {result.win_rate:.1f}%")
        print(f"  Trades: {result.total_trades}")
        print(f"  Sharpe: {result.sharpe_ratio:.2f}" if result.sharpe_ratio else "  Sharpe: N/A")


if __name__ == "__main__":
    # تست اصلی
    main()
    
    # تست timeframe های مختلف
    # test_different_timeframes()  # Uncomment برای تست
