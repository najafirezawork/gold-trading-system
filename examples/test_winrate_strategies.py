"""
Realistic High Win Rate Strategy

استراتژی واقع‌بینانه با تمرکز روی:
1. Win rate بالا (65%+)
2. Risk/Reward معقول (1:1.5 حداقل)
3. تعداد معاملات قابل قبول
"""

import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import logging
from data_layer import TwelveDataClient
from backtesting import BacktestEngine
from backtesting.high_winrate_strategies import (
    ScalpingStrategy,
    ConservativeStrategy,
    SafeRSIStrategy,
    PullbackStrategy
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_winrate_strategies():
    """تست استراتژی‌های با تمرکز Win Rate"""
    
    print("\n" + "="*70)
    print("🎯 HIGH WIN RATE STRATEGIES TEST")
    print("="*70)
    
    client = TwelveDataClient()
    
    print("\n📊 Fetching data (1000 candles, 15min interval for more trades)...")
    market_data = client.get_time_series("XAU/USD", "15min", 1000)
    
    print(f"✓ Data: {len(market_data)} candles")
    print(f"  Period: {market_data.data[-1].datetime.date()} to {market_data.data[0].datetime.date()}")
    
    strategies = [
        ScalpingStrategy(5, 10),
        SafeRSIStrategy(),
        PullbackStrategy(),
        ConservativeStrategy()
    ]
    
    results = []
    
    print("\n" + "="*70)
    print("⏳ Running tests...")
    print("="*70 + "\n")
    
    for strategy in strategies:
        print(f"Testing {strategy.name}...")
        
        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=10000.0,
            commission=2.0
        )
        
        result = engine.run(market_data, verbose=False)
        results.append(result)
        
        print(f"  ✓ {result.total_trades} trades, "
              f"{result.win_rate:.1f}% win rate, "
              f"{result.total_return_pct:+.2f}% return")
    
    client.close()
    
    # نمایش جدول
    print("\n" + "="*70)
    print("📊 RESULTS COMPARISON")
    print("="*70 + "\n")
    
    print(f"{'Strategy':<35} {'WinRate':>8} {'Trades':>7} {'Return%':>9} {'AvgWin':>9} {'AvgLoss':>9}")
    print("-" * 90)
    
    for r in results:
        avg_win = f"${r.avg_profit:.2f}" if r.winning_trades > 0 else "N/A"
        avg_loss = f"${r.avg_loss:.2f}" if r.losing_trades > 0 else "N/A"
        
        print(f"{r.strategy_name:<35} "
              f"{r.win_rate:>7.1f}% "
              f"{r.total_trades:>7} "
              f"{r.total_return_pct:>8.2f}% "
              f"{avg_win:>9} "
              f"{avg_loss:>9}")
    
    # بهترین win rate
    print("\n" + "="*70)
    print("🏆 TOP PERFORMERS")
    print("="*70)
    
    valid_results = [r for r in results if r.total_trades >= 5]
    
    if valid_results:
        best_winrate = max(valid_results, key=lambda r: r.win_rate)
        print(f"\n🎯 Highest Win Rate: {best_winrate.strategy_name}")
        print(f"   Win Rate: {best_winrate.win_rate:.2f}%")
        print(f"   Trades: {best_winrate.winning_trades}/{best_winrate.total_trades}")
        print(f"   Return: {best_winrate.total_return_pct:+.2f}%")
        
        if best_winrate.winning_trades > 0 and best_winrate.losing_trades > 0:
            rr_ratio = abs(best_winrate.avg_profit / best_winrate.avg_loss)
            print(f"   Risk/Reward: 1:{rr_ratio:.2f}")
        
        # بهترین return
        best_return = max(valid_results, key=lambda r: r.total_return_pct)
        if best_return != best_winrate:
            print(f"\n💰 Best Return: {best_return.strategy_name}")
            print(f"   Return: {best_return.total_return_pct:+.2f}%")
            print(f"   Win Rate: {best_return.win_rate:.2f}%")
        
        # متعادل‌ترین
        print(f"\n⚖️ Most Balanced:")
        
        # امتیازدهی: Win Rate (40%) + Return (30%) + Risk/Reward (30%)
        scores = []
        for r in valid_results:
            if r.losing_trades == 0:
                continue
                
            score = 0
            # Win Rate (40%)
            score += (r.win_rate / 100) * 0.4
            # Return (30%)
            score += max(0, min(1, (r.total_return_pct + 10) / 20)) * 0.3
            # Risk/Reward (30%)
            rr = abs(r.avg_profit / r.avg_loss) if r.avg_loss != 0 else 0
            score += min(1, rr / 2) * 0.3
            
            scores.append((r, score))
        
        if scores:
            best_balanced = max(scores, key=lambda x: x[1])
            r, score = best_balanced
            
            rr_ratio = abs(r.avg_profit / r.avg_loss)
            
            print(f"   {r.strategy_name}")
            print(f"   Score: {score:.3f}/1.000")
            print(f"   Win Rate: {r.win_rate:.1f}%, Return: {r.total_return_pct:+.2f}%, R/R: 1:{rr_ratio:.2f}")
    
    # نکات
    print("\n" + "="*70)
    print("💡 ANALYSIS")
    print("="*70)
    
    print("\n📈 Win Rate vs Return:")
    print("   - Win rate بالا همیشه = سود بیشتر نیست")
    print("   - Risk/Reward ratio مهم‌تر از win rate است")
    print("   - تعداد معاملات باید معقول باشد")
    
    print("\n🎯 برای Win Rate بالا:")
    print("   ✓ Take profit کوچک‌تر (0.5%-1%)")
    print("   ✓ Stop loss خیلی تنگ (0.3%-0.5%)")
    print("   ✓ فیلتر شدید سیگنال‌ها")
    print("   ✓ Timeframe کوچک‌تر (15m, 5m)")
    
    print("\n⚠️ Trade-offs:")
    print("   - Win Rate بالا → Profit کوچک‌تر per trade")
    print("   - Win Rate بالا → Commission impact بیشتر")
    print("   - Win Rate بالا → نیاز به monitoring بیشتر")


if __name__ == "__main__":
    test_winrate_strategies()
