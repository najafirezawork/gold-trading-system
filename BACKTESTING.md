# Backtesting Module Documentation 📊

راهنمای جامع استفاده از ماژول Backtesting برای آزمایش استراتژی‌های معاملاتی.

## فهرست مطالب

1. [معرفی](#معرفی)
2. [نصب و راه‌اندازی](#نصب-و-راهاندازی)
3. [معماری](#معماری)
4. [استفاده سریع](#استفاده-سریع)
5. [ساخت استراتژی سفارشی](#ساخت-استراتژی-سفارشی)
6. [Performance Metrics](#performance-metrics)
7. [مثال‌های کامل](#مثالهای-کامل)
8. [Best Practices](#best-practices)

---

## معرفی

Backtesting Module امکان آزمایش استراتژی‌های معاملاتی روی داده‌های تاریخی را فراهم می‌کند. با این ماژول می‌توانید:

- استراتژی‌های مختلف را پیاده‌سازی و تست کنید
- عملکرد را با metrics حرفه‌ای ارزیابی کنید (Sharpe, Sortino, Max Drawdown)
- از Signal Agent در استراتژی‌ها استفاده کنید
- Stop Loss و Take Profit تعریف کنید
- نتایج را به صورت JSON ذخیره کنید

## نصب و راه‌اندازی

همه وابستگی‌های لازم در `requirements.txt` موجود است:

```bash
pip install -r requirements.txt
```

## معماری

### کلاس‌های اصلی

```
backtesting/
├── models.py          # Trade, BacktestResult
├── strategy.py        # BaseStrategy (abstract)
├── strategies.py      # استراتژی‌های نمونه
├── metrics.py         # PerformanceMetrics
└── engine.py          # BacktestEngine
```

### Data Flow

```
Market Data → Strategy.should_enter() → Open Trade
    ↓
Trade Open → Strategy.should_exit() → Close Trade
    ↓
Closed Trades → PerformanceMetrics → BacktestResult
```

## استفاده سریع

### مثال ساده

```python
from data_layer import TwelveDataClient
from backtesting import BacktestEngine
from backtesting.strategies import RSIStrategy

# 1. دریافت داده‌های تاریخی
client = TwelveDataClient()
market_data = client.get_time_series(
    symbol="XAU/USD",
    interval="1h",
    outputsize=500
)

# 2. ایجاد استراتژی
strategy = RSIStrategy(
    rsi_period=14,
    oversold=30,
    overbought=70
)

# 3. ایجاد Backtest Engine
engine = BacktestEngine(
    strategy=strategy,
    initial_capital=10000.0,
    commission=2.0  # کمیسیون هر معامله
)

# 4. اجرای Backtest
result = engine.run(market_data, verbose=True)

# 5. نمایش نتایج
print(f"Total Return: ${result.total_return:.2f}")
print(f"Return %: {result.total_return_pct:.2f}%")
print(f"Win Rate: {result.win_rate:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown_pct:.2f}%")
```

### استراتژی‌های آماده

#### 1. Moving Average Crossover

```python
from backtesting.strategies import SimpleMAStrategy

strategy = SimpleMAStrategy(short_period=20, long_period=50)
```

**Logic:**
- خرید: وقتی MA کوتاه از MA بلند به سمت بالا رد شود (Golden Cross)
- فروش: وقتی MA کوتاه از MA بلند به سمت پایین رد شود (Death Cross)

#### 2. RSI Strategy

```python
from backtesting.strategies import RSIStrategy

strategy = RSIStrategy(
    rsi_period=14,
    oversold=30,
    overbought=70
)
```

**Logic:**
- خرید: RSI < 30 (oversold)
- فروش: RSI > 70 (overbought)
- Stop Loss: 2%
- Take Profit: 4%

#### 3. Signal Agent Strategy

```python
from backtesting.strategies import SignalAgentStrategy

strategy = SignalAgentStrategy(signal_threshold=0.3)
```

**Logic:**
- از Signal Agent برای تحلیل تکنیکال استفاده می‌کند
- خرید: signal > 0.3
- فروش: signal < -0.3
- Stop Loss: 3%
- Take Profit: 6%

## ساخت استراتژی سفارشی

### BaseStrategy Interface

```python
from typing import Optional
from backtesting import BaseStrategy
from data_layer import MarketData
from agents import AgentOutput

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("My Custom Strategy")
    
    def should_enter(
        self,
        market_data: MarketData,
        current_index: int,
        agent_output: Optional[AgentOutput] = None
    ) -> Optional[str]:
        """
        تصمیم‌گیری برای ورود به معامله.
        
        Returns:
            "BUY": خرید
            "SELL": فروش (short)
            None: عدم ورود
        """
        # Logic خود را پیاده کنید
        return "BUY"
    
    def should_exit(
        self,
        market_data: MarketData,
        current_index: int,
        entry_price: float,
        position_type: str  # "LONG" or "SHORT"
    ) -> bool:
        """
        تصمیم‌گیری برای خروج از معامله.
        
        Returns:
            True: خروج
            False: ادامه
        """
        # Logic خود را پیاده کنید
        return False
    
    def get_stop_loss(
        self,
        entry_price: float,
        position_type: str
    ) -> Optional[float]:
        """تعیین Stop Loss (اختیاری)"""
        if position_type == "LONG":
            return entry_price * 0.98  # 2% پایین‌تر
        else:
            return entry_price * 1.02  # 2% بالاتر
    
    def get_take_profit(
        self,
        entry_price: float,
        position_type: str
    ) -> Optional[float]:
        """تعیین Take Profit (اختیاری)"""
        if position_type == "LONG":
            return entry_price * 1.05  # 5% بالاتر
        else:
            return entry_price * 0.95  # 5% پایین‌تر
```

### مثال: Bollinger Bands Strategy

```python
from backtesting import BaseStrategy
from agents.signal import TechnicalIndicators

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__(f"Bollinger Bands ({period}, {std_dev})")
        self.period = period
        self.std_dev = std_dev
    
    def should_enter(self, market_data, current_index, agent_output=None):
        if current_index < self.period:
            return None
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
            closes, self.period, self.std_dev
        )
        
        current_price = closes[-1]
        
        # خرید: قیمت به باند پایین رسیده
        if current_price <= lower:
            return "BUY"
        
        # فروش: قیمت به باند بالا رسیده
        if current_price >= upper:
            return "SELL"
        
        return None
    
    def should_exit(self, market_data, current_index, entry_price, position_type):
        if current_index < self.period:
            return False
        
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
            closes, self.period, self.std_dev
        )
        
        current_price = closes[-1]
        
        # خروج LONG: قیمت به میانه یا بالاتر رسید
        if position_type == "LONG" and current_price >= middle:
            return True
        
        # خروج SHORT: قیمت به میانه یا پایین‌تر رسید
        if position_type == "SHORT" and current_price <= middle:
            return True
        
        return False
```

## Performance Metrics

### معیارهای محاسبه شده

```python
class BacktestResult:
    # Capital
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    
    # Trades
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float  # درصد
    
    # Performance
    avg_profit: float
    avg_loss: float
    profit_factor: float  # total_profit / total_loss
    
    # Risk Metrics
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: Optional[float]  # 252 trading days
    sortino_ratio: Optional[float]
    
    # Details
    trades: List[Trade]
    equity_curve: List[float]
```

### توضیحات Metrics

#### Sharpe Ratio
نسبت بازدهی به ریسک (volatility).

```
Sharpe = (Return - Risk_Free_Rate) / Standard_Deviation
```

- **> 1**: خوب
- **> 2**: عالی
- **> 3**: استثنایی

#### Sortino Ratio
مشابه Sharpe اما فقط downside volatility را در نظر می‌گیرد.

#### Max Drawdown
بیشترین افت سرمایه از peak.

```
Max Drawdown = (Peak - Trough) / Peak × 100
```

#### Profit Factor
نسبت سود کل به زیان کل.

```
Profit Factor = Total Profit / Total Loss
```

- **> 1.5**: قابل قبول
- **> 2**: خوب
- **> 3**: عالی

## مثال‌های کامل

### 1. مقایسه چند استراتژی

```python
from backtesting.strategies import (
    SimpleMAStrategy,
    RSIStrategy,
    SignalAgentStrategy
)

# دریافت داده
client = TwelveDataClient()
market_data = client.get_time_series("XAU/USD", "1h", 500)

# لیست استراتژی‌ها
strategies = [
    SimpleMAStrategy(20, 50),
    RSIStrategy(14, 30, 70),
    SignalAgentStrategy(0.3)
]

# اجرای backtest برای هر کدام
results = []
for strategy in strategies:
    engine = BacktestEngine(strategy, 10000.0, 2.0)
    result = engine.run(market_data, verbose=False)
    results.append(result)

# مقایسه
for result in results:
    print(f"{result.strategy_name}:")
    print(f"  Return: {result.total_return_pct:.2f}%")
    print(f"  Sharpe: {result.sharpe_ratio:.2f}")
    print(f"  Win Rate: {result.win_rate:.2f}%")
    print()

# بهترین استراتژی
best = max(results, key=lambda r: r.total_return)
print(f"🏆 Best: {best.strategy_name}")
```

### 2. ذخیره و تحلیل نتایج

```python
import json
from datetime import datetime

# اجرای backtest
result = engine.run(market_data)

# ذخیره در JSON
output = {
    "timestamp": datetime.now().isoformat(),
    "strategy": result.strategy_name,
    "symbol": result.symbol,
    "metrics": {
        "return_pct": result.total_return_pct,
        "sharpe": result.sharpe_ratio,
        "sortino": result.sortino_ratio,
        "max_drawdown_pct": result.max_drawdown_pct,
        "win_rate": result.win_rate,
        "profit_factor": result.profit_factor
    },
    "trades": [
        {
            "id": t.id,
            "type": t.trade_type.value,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "profit_loss_pct": t.profit_loss_pct,
            "entry_time": t.entry_time.isoformat(),
            "exit_time": t.exit_time.isoformat()
        }
        for t in result.trades
    ]
}

with open(f"results/backtest_{result.strategy_name}.json", "w") as f:
    json.dump(output, f, indent=2)
```

### 3. استفاده در Production

```python
# تست استراتژی روی داده‌های تاریخی
def validate_strategy(strategy, symbol, interval):
    client = TwelveDataClient()
    
    # دریافت داده‌های 3 ماه گذشته
    market_data = client.get_time_series(
        symbol=symbol,
        interval=interval,
        outputsize=2000
    )
    
    engine = BacktestEngine(strategy, 10000.0, 2.0)
    result = engine.run(market_data, verbose=False)
    
    # Validation Criteria
    is_valid = (
        result.win_rate >= 50 and
        result.sharpe_ratio >= 1.5 and
        result.max_drawdown_pct <= 20 and
        result.total_trades >= 10
    )
    
    return is_valid, result

# تست
strategy = RSIStrategy(14, 30, 70)
is_valid, result = validate_strategy(strategy, "XAU/USD", "1h")

if is_valid:
    print("✅ Strategy passed validation!")
    print(f"  Sharpe: {result.sharpe_ratio:.2f}")
    print(f"  Win Rate: {result.win_rate:.2f}%")
else:
    print("❌ Strategy failed validation")
```

## Best Practices

### 1. Overfitting جلوگیری کنید

```python
# تست روی Out-of-Sample data
def walk_forward_test(strategy, market_data, train_size=0.7):
    """
    Walk-forward testing:
    - Train روی 70% اول
    - Test روی 30% آخر
    """
    split_idx = int(len(market_data.data) * train_size)
    
    # Train data
    train_data = MarketData(
        symbol=market_data.symbol,
        interval=market_data.interval,
        data=market_data.data[:split_idx],
        meta=market_data.meta
    )
    
    # Test data
    test_data = MarketData(
        symbol=market_data.symbol,
        interval=market_data.interval,
        data=market_data.data[split_idx:],
        meta=market_data.meta
    )
    
    # Backtest روی test data
    engine = BacktestEngine(strategy, 10000.0, 2.0)
    result = engine.run(test_data)
    
    return result
```

### 2. Transaction Costs در نظر بگیرید

```python
# کمیسیون واقعی
engine = BacktestEngine(
    strategy=strategy,
    initial_capital=10000.0,
    commission=2.0  # $2 هر طرف معامله
)
```

### 3. Slippage مدل کنید

```python
# در future: اضافه کردن slippage به engine
# slippage = قیمت واقعی - قیمت مورد انتظار
```

### 4. چند Timeframe تست کنید

```python
intervals = ["15min", "1h", "4h", "1day"]

for interval in intervals:
    market_data = client.get_time_series("XAU/USD", interval, 500)
    result = engine.run(market_data)
    
    print(f"{interval}: {result.total_return_pct:.2f}%")
```

### 5. Monte Carlo Simulation

```python
import random

def monte_carlo_simulation(trades, num_simulations=1000):
    """
    شبیه‌سازی Monte Carlo برای ارزیابی robustness
    """
    results = []
    
    for _ in range(num_simulations):
        # ترتیب معاملات را تصادفی کنید
        shuffled = random.sample(trades, len(trades))
        
        capital = 10000.0
        for trade in shuffled:
            capital += trade.profit_loss
        
        results.append(capital)
    
    return {
        "mean": sum(results) / len(results),
        "std": ...,  # محاسبه انحراف معیار
        "percentile_5": sorted(results)[int(0.05 * len(results))],
        "percentile_95": sorted(results)[int(0.95 * len(results))]
    }
```

## اجرای مثال‌های آماده

```bash
# مثال‌های تعاملی
python examples/backtest_examples.py

# یا مستقیم
python -c "from examples.backtest_examples import compare_strategies; compare_strategies()"
```

---

**برای سوالات بیشتر به `DEVELOPER_GUIDE.md` مراجعه کنید.**
