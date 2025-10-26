# Gold Trading Signal System 🏆

یک سیستم مدولار، قابل توسعه و تمیز برای دریافت و تحلیل سیگنال‌های معاملاتی طلا با استفاده از Twelve Data API.

## ویژگی‌ها ✨

- **معماری تمیز و مدولار**: طراحی بر اساس اصول SOLID
- **Multi-Agent System**: ترکیب Signal Agent, ML Agent, و Regime Detection 🎯
- **Machine Learning**: پیش‌بینی با RandomForest و XGBoost (96%+ accuracy) 🤖
- **تحلیل تکنیکال پیشرفته**: شامل RSI, MACD, Bollinger Bands, Moving Averages
- **Backtesting Module**: آزمایش و ارزیابی استراتژی‌ها روی داده‌های تاریخی
- **8 استراتژی آماده**: 3 ساده + 5 پیشرفته با win rate بالاتر
- **Integrated Trading System**: سیستم یکپارچه با وزن‌دهی خودکار بر اساس market regime
- **Docker Support**: آماده برای containerization و deployment
- **تصمیم‌گیری هوشمند**: Aggregation چند agent با وزن‌دهی confidence
- **قابل توسعه**: آماده برای افزودن ML models و سایر agent ها
- **مدیریت خطای جامع**: Error handling و logging کامل
- **Type-Safe**: استفاده از Type Hints در همه جا

## ساختار پروژه 📁

```
Data/
├── config/                      # تنظیمات و کانفیگ‌ها
│   ├── __init__.py
│   └── settings.py             # Settings با Pydantic
│
├── data_layer/                  # لایه دیتا و اتصال به API
│   ├── __init__.py
│   ├── client.py               # Twelve Data API Client
│   └── models.py               # Data Models (OHLCV, MarketData)
│
├── agents/                      # Agent های تحلیل و تصمیم‌گیری
│   ├── __init__.py
│   ├── base/                   # کلاس و interface پایه
│   │   ├── __init__.py
│   │   └── agent.py           # BaseAgent, AgentOutput
│   │
│   ├── signal/                 # Signal Agent (تحلیل تکنیکال)
│   │   ├── __init__.py
│   │   ├── signal_agent.py    # تحلیل تکنیکال طلا
│   │   └── indicators.py      # اندیکاتورهای تکنیکال
│   │
│   ├── ml/                     # ML Agent (Machine Learning) 🤖
│   │   ├── __init__.py
│   │   ├── ml_agent.py        # ML prediction agent
│   │   ├── feature_engineer.py # 70+ features extraction
│   │   └── models.py          # RandomForest, XGBoost, Ensemble
│   │
│   └── decision/               # Decision Agent
│       ├── __init__.py
│       └── decision_agent.py  # تصمیم‌گیری نهایی
│
├── backtesting/                 # ماژول Backtesting
│   ├── __init__.py
│   ├── models.py               # Trade, BacktestResult models
│   ├── strategy.py             # BaseStrategy interface
│   ├── strategies.py           # 3 استراتژی ساده
│   ├── advanced_strategies.py  # 5 استراتژی پیشرفته ⭐
│   ├── adaptive_engine.py      # Adaptive strategy selection 🧠
│   ├── regime_detector.py      # Market regime detection
│   ├── metrics.py              # محاسبه performance metrics
│   └── engine.py               # Backtesting engine
│
├── examples/                    # مثال‌های استفاده
│   ├── simple_integrated.py    # مثال ساده سیستم یکپارچه ⭐
│   ├── test_complete_system.py # تست کامل سیستم یکپارچه ⭐
│   ├── test_ml_agent.py        # تست و train ML Agent 🤖
│   ├── test_ml_quick.py        # تست سریع ML
│   ├── advanced_usage.py       # مثال‌های پیشرفته
│   ├── backtest_examples.py    # مثال‌های backtesting
│   └── test_advanced_strategies.py  # تست استراتژی‌های پیشرفته
│
├── models/                      # ML models directory
│   └── gold_ml_model.pkl       # Trained ML model
│
├── trading_system.py           # Integrated Trading System ⭐
├── main.py                     # نقطه ورود اصلی
├── requirements.txt            # وابستگی‌ها
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Docker services
├── .dockerignore
├── .env                       # API Key (در .gitignore)
├── .gitignore
├── README.md
├── ML_AGENT.md                # راهنمای ML Agent 🤖
├── INTEGRATED_SYSTEM.md       # راهنمای سیستم یکپارچه ⭐
└── DEVELOPER_GUIDE.md         # راهنمای توسعه‌دهنده
```

## نصب و راه‌اندازی 🚀

### روش 1: نصب مستقیم

#### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

#### 2. تنظیم API Key

فایل `.env` از قبل ایجاد شده و API key در آن قرار دارد.

#### 3. اجرا

**Simple Example:**
```bash
python examples/simple_integrated.py
```

**Complete System Test:**
```bash
python examples/test_complete_system.py
```

**Train ML Model:**
```bash
python examples/test_ml_agent.py
# Select option 1 to train
```

### روش 2: استفاده از Docker 🐳

#### Build و اجرا

**Windows PowerShell:**
```powershell
.\docker-run.ps1 build   # Build image
.\docker-run.ps1 run     # Run container
.\docker-run.ps1 logs    # View logs
.\docker-run.ps1 stop    # Stop container
.\docker-run.ps1 clean   # Clean up
```

**Linux/Mac:**
```bash
chmod +x docker-run.sh
./docker-run.sh build
./docker-run.sh run
```

**یا با Docker Compose:**
```bash
docker-compose build
docker-compose up -d
docker-compose logs -f
docker-compose down
```

#### مزایای Docker:
- محیط ایزوله و یکسان در همه سیستم‌ها
- نصب آسان و سریع
- مناسب برای production deployment
- Volume mounting برای log ها و نتایج

## استفاده ساده 💡

### Integrated Trading System (توصیه شده) ⭐

```python
from trading_system import IntegratedTradingSystem
from data_layer import TwelveDataClient

# Fetch data
client = TwelveDataClient()
market_data = client.get_time_series("XAU/USD", interval="1h", outputsize=500)

# Initialize system
system = IntegratedTradingSystem()
system.initialize()

# Get recommendation
recommendation = system.analyze(market_data)

print(f"Action: {recommendation.action}")
print(f"Confidence: {recommendation.confidence:.1%}")
print(f"Market Regime: {recommendation.market_regime}")
```

**Features:**
- 🎯 ترکیب Signal Agent (Technical) + ML Agent (Predictions)
- 🧠 تشخیص خودکار Market Regime (Trending/Ranging/Volatile)
- ⚖️ وزن‌دهی خودکار agents بر اساس regime
- 📊 توضیح کامل تصمیمات

برای جزئیات بیشتر: [INTEGRATED_SYSTEM.md](INTEGRATED_SYSTEM.md)

### استفاده دستی از Agents

```python
from config import settings
from data_layer import TwelveDataClient
from agents import SignalAgent, DecisionAgent

# Initialize
client = TwelveDataClient()
signal_agent = SignalAgent()
decision_agent = DecisionAgent()

# Fetch gold data
market_data = client.get_time_series("XAU/USD", interval="1h", outputsize=100)

# Analyze
signal_output = signal_agent.analyze(market_data)

# Make decision
decision = decision_agent.analyze([signal_output])

print(f"Decision: {decision.metadata['decision']}")
print(f"Signal: {decision.signal:.2f}")
print(f"Confidence: {decision.confidence:.2f}")
```

## مثال‌های پیشرفته 🎯

### 1. استفاده از سیستم یکپارچه

برای استفاده کامل از سیستم یکپارچه:

```bash
# Simple example
python examples/simple_integrated.py

# Complete test with all features
python examples/test_complete_system.py
```

### 2. ML Agent (Machine Learning) 🤖

```python
from agents.ml import MLAgent
from data_layer import TwelveDataClient

# Train model
client = TwelveDataClient()
train_data = client.get_time_series("XAU/USD", interval="1h", outputsize=2000)

ml_agent = MLAgent()
ml_agent.train(train_data, model_type="ensemble")  # RandomForest + XGBoost

# Make predictions
test_data = client.get_time_series("XAU/USD", interval="1h", outputsize=100)
prediction = ml_agent.analyze(test_data)

print(f"Recommendation: {prediction.recommendation}")
print(f"Confidence: {prediction.confidence:.1%}")
```

**Features:**
- 70+ extracted features (RSI, MACD, BB, ATR, price patterns, etc.)
- Ensemble model (RandomForest + XGBoost)
- 96%+ validation accuracy
- Feature importance analysis

برای جزئیات بیشتر: [ML_AGENT.md](ML_AGENT.md)

### 3. استفاده از سیستم تحلیل

برای مثال‌های بیشتر به `examples/advanced_usage.py` مراجعه کنید:

- تحلیل چند timeframe
- استفاده از threshold های سفارشی
- ذخیره نتایج در JSON
- افزودن agent های سفارشی

```bash
python examples/advanced_usage.py
```

### 4. Backtesting 📊

#### اجرای Backtest

```python
from data_layer import TwelveDataClient
from backtesting import BacktestEngine
from backtesting.strategies import RSIStrategy

# دریافت داده‌های تاریخی
client = TwelveDataClient()
market_data = client.get_time_series("XAU/USD", interval="1h", outputsize=500)

# ایجاد استراتژی
strategy = RSIStrategy(rsi_period=14, oversold=30, overbought=70)

# اجرای backtest
engine = BacktestEngine(
    strategy=strategy,
    initial_capital=10000.0,
    commission=2.0
)

result = engine.run(market_data, verbose=True)

# نمایش نتایج
print(f"Return: ${result.total_return:.2f} ({result.total_return_pct:.2f}%)")
print(f"Win Rate: {result.win_rate:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

#### استراتژی‌های موجود

**استراتژی‌های ساده:**
1. **SimpleMAStrategy**: Moving Average Crossover
2. **RSIStrategy**: RSI با stop loss/take profit
3. **SignalAgentStrategy**: استفاده از Signal Agent

**استراتژی‌های پیشرفته:** ⭐
4. **TrendFollowingStrategy**: ترکیب MA + RSI + MACD
5. **MeanReversionStrategy**: Bollinger Bands + RSI
6. **BreakoutStrategy**: شکست سطوح با Volume
7. **MultiConfirmationStrategy**: تایید از 4 منبع (بهترین دقت)
8. **AdaptiveRSIStrategy**: RSI تطبیقی با ATR

[راهنمای کامل استراتژی‌های پیشرفته](ADVANCED_STRATEGIES.md)

#### تست استراتژی‌های پیشرفته

```bash
python examples/test_advanced_strategies.py
```

انتخاب کنید:
- تست هر استراتژی به صورت جداگانه
- مقایسه همه استراتژی‌ها
3. **SignalAgentStrategy**: استفاده از Signal Agent

#### مثال‌های کامل Backtesting

```bash
python examples/backtest_examples.py
```

منوی تعاملی برای:
- Backtest هر استراتژی به صورت جداگانه
- مقایسه چندین استراتژی
- ذخیره نتایج در JSON

## اصول طراحی ⚡

این پروژه با رعایت کامل اصول زیر پیاده‌سازی شده:

### SOLID Principles
- **Single Responsibility**: هر کلاس یک مسئولیت
- **Open/Closed**: باز برای توسعه، بسته برای تغییر
- **Liskov Substitution**: همه agents جایگزین BaseAgent
- **Interface Segregation**: Interfaces کوچک و مشخص
- **Dependency Inversion**: وابستگی به abstractions

### Clean Code
- Type hints در همه جا
- Docstrings کامل
- Error handling جامع
- Logging مناسب
- کپسوله‌سازی صحیح

### Design Patterns
- **Strategy Pattern**: هر agent یک استراتژی
- **Template Method**: BaseAgent.analyze()
- **Factory**: آماده برای AgentFactory

## افزودن Agent جدید 🔧

```python
from agents.base import BaseAgent, AgentOutput, AgentType

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.ML, "My Custom Agent")
    
    def analyze(self, data) -> AgentOutput:
        # محاسبات شما
        signal = 0.5  # -1 to 1
        confidence = 0.8  # 0 to 1
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=signal,
            confidence=confidence,
            metadata={"custom_info": "..."}
        )
```

برای جزئیات بیشتر به `DEVELOPER_GUIDE.md` مراجعه کنید.

## اندیکاتورهای تکنیکال 📊

Signal Agent از اندیکاتورهای زیر استفاده می‌کند:

- **Moving Averages**: SMA(20), SMA(50), EMA(12)
- **RSI**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: با 2 انحراف معیار
- **ATR**: Average True Range (برای volatility)

## خروجی نمونه 📝

```
============================================================
Starting analysis for XAU/USD at 2025-10-26 12:00:00
Interval: 1h, Data points: 100
============================================================

Step 1: Fetching market data...
✓ Fetched 100 data points
Current Price: $2645.50

Step 2: Running technical analysis...
✓ Signal Agent Analysis:
  - Signal: 0.65
  - Confidence: 0.78
  - Analysis: Strong Buy

  Key Indicators:
    • RSI: 45.23
    • SMA(20): $2640.30
    • SMA(50): $2635.10
    • EMA(12): $2643.80
    • MACD: 0.0125
    • MACD Signal: 0.0113

Step 3: Making trading decision...
✓ Final Decision:
  - Decision: STRONG_BUY
  - Signal: 0.65
  - Confidence: 0.78

  Reasoning:
  Decision: STRONG_BUY based on analysis of 1 agent(s).
  Overall signal is strong bullish (0.65).
  Confidence level is high (0.78).
  - Signal agent suggests buy (signal=0.65, confidence=0.78)
```
## توسعه آینده 🚀

- [ ] ML Agent با TensorFlow/PyTorch
- [ ] Sentiment Analysis از news و social media
- [x] **Backtesting module** ✅
- [x] **8 استراتژی (3 ساده + 5 پیشرفته)** ✅
- [x] **Docker containerization** ✅
- [ ] Real-time streaming data
- [ ] Web dashboard با FastAPI + React
- [ ] Database integration (PostgreSQL)
- [ ] Portfolio management (چند نماد)
- [ ] Risk management (position sizing)
- [ ] Notification system (Telegram, Email)
- [ ] Genetic Algorithm برای optimization استراتژی‌ها
- [ ] Ensemble strategies (ترکیب چند استراتژی)

## مجوز 📄

این پروژه برای استفاده آزاد در اختیار شماست.

## مستندات کامل 📚

- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**: راهنمای توسعه‌دهنده و معماری سیستم
- **[BACKTESTING.md](BACKTESTING.md)**: راهنمای جامع Backtesting Module
- **[ADVANCED_STRATEGIES.md](ADVANCED_STRATEGIES.md)**: راهنمای کامل 5 استراتژی پیشرفته ⭐
- **[DOCKER.md](DOCKER.md)**: راهنمای استفاده از Docker
- **[API_REFERENCE.md](API_REFERENCE.md)**: مرجع کامل API
- **[CHANGELOG.md](CHANGELOG.md)**: تاریخچه تغییرات

## تماس و پشتیبانی 💬

برای سوالات و پیشنهادات:
- مستندات کامل در فایل‌های بالا
- مثال‌های استفاده در `examples/`
- تست‌ها در `test_system.py` و `test_backtesting.py`

---

**ساخته شده با ❤️ برای تحلیل بازار طلا**
