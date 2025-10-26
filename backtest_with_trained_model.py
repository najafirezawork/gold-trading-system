"""
🎯 Backtesting با مدل Train شده
====================================

این اسکریپت:
1. مدل ML را train می‌کنه
2. مدل رو ذخیره می‌کنه
3. Backtesting با مدل ذخیره شده انجام می‌ده
4. نتایج رو نمایش می‌ده
"""

from agents.ml.ml_agent import MLAgent
from agents.signal.signal_agent import SignalAgent
from data_layer.client import TwelveDataClient
from data_layer import MarketData
from backtesting.engine import BacktestEngine
from backtesting.strategy import BaseStrategy
from datetime import datetime
from typing import Optional
import os


class MLSignalStrategy(BaseStrategy):
    """
    استراتژی Backtesting با ML Signal Generator
    """
    
    def __init__(
        self,
        ml_agent: MLAgent,
        signal_agent: SignalAgent,
        ml_threshold: float = 0.65,
        trend_threshold: float = 0.15
    ):
        """
        Args:
            ml_agent: ML Agent برای سیگنال‌های ML
            signal_agent: Signal Agent برای سیگنال‌های Technical
            ml_threshold: حداقل احتمال ML برای تصمیم
            trend_threshold: حداقل قدرت ترند برای تصمیم
        """
        super().__init__(name="ML Signal Strategy")
        self.ml_agent = ml_agent
        self.signal_agent = signal_agent
        self.ml_threshold = ml_threshold
        self.trend_threshold = trend_threshold
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output=None
    ) -> Optional[str]:
        """
        تصمیم برای ورود به معامله
        
        Returns:
            "BUY" for long, "SELL" for short, None for no entry
        """
        # نیاز به حداقل 100 candle برای feature engineering
        if current_index < 100:
            return None
        
        # ساخت MarketData object برای داده‌های تا current_index
        from data_layer.models import MarketData as MD, OHLCV
        
        # استفاده از داده‌های تا current_index
        current_market_data = MD(
            symbol=market_data.symbol,
            interval=market_data.interval,
            data=market_data.data[:current_index + 1]
        )
        
        try:
            # دریافت ML Signals
            ml_signal = self.ml_agent.analyze(current_market_data)
            
            # دریافت Technical Signals
            tech_signal = self.signal_agent.analyze(current_market_data)
            tech_recommendation = "BUY" if tech_signal.signal > 0.3 else "SELL" if tech_signal.signal < -0.3 else "HOLD"
        except Exception as e:
            # در صورت خطا، signal نده
            return None
        
        # Strategy 1: Strong ML + Strong Trend
        if ml_signal.prob_up > self.ml_threshold and ml_signal.trend_strength > self.trend_threshold:
            return "BUY"
        
        elif ml_signal.prob_down > self.ml_threshold and ml_signal.trend_strength > self.trend_threshold:
            return "SELL"
        
        # Strategy 2: Technical + ML Momentum Agreement
        elif tech_recommendation == "BUY" and ml_signal.momentum > 0:
            return "BUY"
        
        elif tech_recommendation == "SELL" and ml_signal.momentum < 0:
            return "SELL"
        
        return None
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str
    ) -> bool:
        """
        تصمیم برای خروج از معامله
        
        Returns:
            True if should exit, False otherwise
        """
        # ساخت MarketData object
        from data_layer.models import MarketData as MD
        
        current_market_data = MD(
            symbol=market_data.symbol,
            interval=market_data.interval,
            data=market_data.data[:current_index + 1]
        )
        
        try:
            # دریافت ML Signals
            ml_signal = self.ml_agent.analyze(current_market_data)
        except Exception:
            # در صورت خطا، از stop loss/take profit استفاده کن
            ml_signal = None
        
        current_price = market_data.data[current_index].close
        
        # محاسبه سود/زیان
        if position_type == "LONG":
            pnl_percent = (current_price - entry_price) / entry_price
        else:  # SHORT
            pnl_percent = (entry_price - current_price) / entry_price
        
        # Stop Loss: -2%
        if pnl_percent < -0.02:
            return True
        
        # Take Profit: +3%
        if pnl_percent > 0.03:
            return True
        
        # سیگنال معکوس قوی (فقط اگر ml_signal موجود باشه)
        if ml_signal:
            if position_type == "LONG":
                # در حال LONG هستیم، اگر سیگنال SHORT قوی اومد
                if ml_signal.prob_down > self.ml_threshold and ml_signal.trend_strength > self.trend_threshold:
                    return True
            else:  # SHORT
                # در حال SHORT هستیم، اگر سیگنال LONG قوی اومد
                if ml_signal.prob_up > self.ml_threshold and ml_signal.trend_strength > self.trend_threshold:
                    return True
        
        return False


def train_model(outputsize: int = 1000):
    """
    Train کردن و ذخیره مدل ML
    
    Args:
        outputsize: تعداد candle برای training
        
    Returns:
        ml_agent: ML Agent با مدل train شده
    """
    print("="*70)
    print("🎯 STEP 1: Training ML Model")
    print("="*70)
    
    # 1. دریافت داده
    print("\n1️⃣ Fetching training data...")
    client = TwelveDataClient()
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="4h",
        outputsize=outputsize
    )
    print(f"✅ Got {len(market_data)} candles for training")
    
    # 2. ایجاد ML Agent
    print("\n2️⃣ Creating ML Agent...")
    ml_agent = MLAgent(
        model_path="models/gold_signal_backtest.pkl"
    )
    print("✅ ML Agent created")
    
    # 3. Train کردن
    print("\n3️⃣ Training ML Agent...")
    print("⚠️  This may take a few minutes...")
    
    metrics = ml_agent.train(
        market_data=market_data,
        val_split=0.2,
        save_model=True  # ✅ ذخیره مدل
    )
    
    print("\n✅ Model trained and saved!")
    print(f"📁 Model saved to: models/gold_signal_backtest.pkl")
    print(f"📊 Validation Accuracy: {metrics.get('val_accuracy', 0):.2%}")
    
    return ml_agent


def run_backtest(ml_agent: MLAgent, backtest_size: int = 500):
    """
    اجرای Backtest با مدل train شده
    
    Args:
        ml_agent: ML Agent با مدل train شده
        backtest_size: تعداد candle برای backtest
    """
    print("\n" + "="*70)
    print("🎯 STEP 2: Running Backtest")
    print("="*70)
    
    # 1. دریافت داده backtest
    print("\n1️⃣ Fetching backtest data...")
    client = TwelveDataClient()
    backtest_data = client.get_time_series(
        symbol="XAU/USD",
        interval="4h",
        outputsize=backtest_size
    )
    print(f"✅ Got {len(backtest_data)} candles for backtesting")
    
    # 2. ایجاد Signal Agent
    print("\n2️⃣ Creating Signal Agent...")
    signal_agent = SignalAgent()
    print("✅ Signal Agent created")
    
    # 3. ایجاد استراتژی
    print("\n3️⃣ Creating ML Signal Strategy...")
    strategy = MLSignalStrategy(
        ml_agent=ml_agent,
        signal_agent=signal_agent,
        ml_threshold=0.65,
        trend_threshold=0.15
    )
    print("✅ Strategy created")
    
    # 4. اجرای Backtest
    print("\n4️⃣ Running backtest...")
    print("⚠️  This may take a few minutes...")
    
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=10000.0,
        commission=10.0  # $10 per trade
    )
    
    results = engine.run(
        market_data=backtest_data,
        verbose=True
    )
    
    # 5. نمایش نتایج
    print("\n" + "="*70)
    print("📊 BACKTEST RESULTS")
    print("="*70)
    
    print(f"\n💰 Performance:")
    print(f"   Initial Capital:     ${results.initial_capital:,.2f}")
    print(f"   Final Capital:       ${results.final_capital:,.2f}")
    print(f"   Total Return:        {results.total_return_pct:.2%}")
    print(f"   Max Drawdown:        {results.max_drawdown_pct:.2%}")
    
    print(f"\n📈 Trade Statistics:")
    print(f"   Total Trades:        {results.total_trades}")
    print(f"   Winning Trades:      {results.winning_trades}")
    print(f"   Losing Trades:       {results.losing_trades}")
    print(f"   Win Rate:            {results.win_rate:.2%}")
    
    print(f"\n💵 Profit/Loss:")
    print(f"   Net Profit:          ${results.total_return:,.2f}")
    print(f"   Avg Profit:          ${results.avg_profit:,.2f}")
    print(f"   Avg Loss:            ${results.avg_loss:,.2f}")
    print(f"   Profit Factor:       {results.profit_factor:.2f}")
    
    print(f"\n⏱️  Duration:")
    print(f"   Start Date:          {results.start_date}")
    print(f"   End Date:            {results.end_date}")
    
    # ذخیره نتایج
    print(f"\n💾 Saving results...")
    import json
    result_file = f"results/backtest_ml_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # تبدیل به dict برای JSON
    results_dict = {
        'strategy_name': results.strategy_name,
        'symbol': results.symbol,
        'start_date': str(results.start_date),
        'end_date': str(results.end_date),
        'initial_capital': results.initial_capital,
        'final_capital': results.final_capital,
        'total_return': results.total_return,
        'total_return_pct': results.total_return_pct,
        'total_trades': results.total_trades,
        'winning_trades': results.winning_trades,
        'losing_trades': results.losing_trades,
        'win_rate': results.win_rate,
        'avg_profit': results.avg_profit,
        'avg_loss': results.avg_loss,
        'profit_factor': results.profit_factor,
        'max_drawdown': results.max_drawdown,
        'max_drawdown_pct': results.max_drawdown_pct,
    }
    
    with open(result_file, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"✅ Results saved to: {result_file}")
    
    return results_dict


def main():
    """
    اجرای کامل: Training + Backtesting
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        ML Agent Training & Backtesting System                    ║
╚══════════════════════════════════════════════════════════════════╝

این اسکریپت در دو مرحله کار می‌کنه:
1. Training: مدل ML رو train می‌کنه و ذخیره می‌کنه
2. Backtesting: با مدل ذخیره شده، backtest انجام می‌ده

⏱️  زمان تقریبی: 5-10 دقیقه
    """)
    
    try:
        # مرحله 1: Training
        ml_agent = train_model(outputsize=1000)
        
        # مرحله 2: Backtesting
        results = run_backtest(ml_agent, backtest_size=500)
        
        # خلاصه نهایی
        print("\n" + "="*70)
        print("✅ COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Model saved to: models/gold_signal_backtest.pkl")
        print(f"📊 Final Return: {results['total_return_pct']:.2%}")
        print(f"🎯 Win Rate: {results['win_rate']:.2%}")
        print(f"💰 Net Profit: ${results['total_return']:,.2f}")
        
        if results['total_return'] > 0:
            print("\n🎉 Profitable strategy!")
        else:
            print("\n⚠️  Strategy needs optimization")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
