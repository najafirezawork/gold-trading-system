# 📋 خلاصه جامع پروژه - Gold Trading Signal System

## 🎯 مقدمه

**Gold Trading Signal System** یک پلتفرم توسعه‌یافته برای تحلیل و تصمیم‌گیری معاملات طلا است که ترکیبی از:

✅ **۷ اندیکاتور تکنیکالی**  
✅ **۳ مدل Machine Learning**  
✅ **۵ Agent هوشمند**  
✅ **۵ استراتژی Backtesting**  

---

## 📊 آمار پروژه

| معیار | مقدار |
|------|--------|
| 🐍 فایل‌های Python | 38 |
| 📝 خطوط کد | 1,851+ |
| 📄 مستندات | 5 فایل |
| 🎯 اندیکاتورها | 7 |
| 🤖 ML Models | 3 |
| 🎛️ Agents | 5 |
| 🧪 استراتژی‌ها | 5 |
| ✅ تست‌های موفق | 100% |

---

## 🏗️ معماری سیستم

### لایه‌ها

```
┌─────────────────────────────┐
│    API/Interface Layer       │
├─────────────────────────────┤
│  Agent Orchestration Layer   │
├─────────────────────────────┤
│  Technical Analysis Layer    │
├─────────────────────────────┤
│   Machine Learning Layer     │
├─────────────────────────────┤
│     Data Layer (API)         │
├─────────────────────────────┤
│   External Services          │
└─────────────────────────────┘
```

### Agents

1. **Signal Agent** - تحلیل 7 اندیکاتور → سیگنال (-1 to 1)
2. **ML Agent** - 70+ features → احتمالات
3. **Decision Agent** - تجمیع سیگنال‌ها → تصمیم نهایی
4. **Risk Agent** - مدیریت ریسک
5. **Meta Agent** - ارکستر اصلی

---

## 📁 ساختار دایرکتوری

```
gold-trading-system/
├── agents/                 # سیستم Agent‌ها
│   ├── base/              # BaseAgent
│   ├── signal/            # 7 اندیکاتور تکنیکالی
│   ├── ml/                # Machine Learning
│   ├── decision/          # تصمیم‌گیری
│   ├── risk/              # مدیریت ریسک
│   └── technical/         # تحلیل تکنیکالی پیشرفته
│
├── backtesting/           # موتور Backtesting
│   ├── engine.py          # اصلی
│   ├── strategy.py        # Base strategy
│   ├── strategies.py      # استراتژی‌های ساده
│   ├── advanced_strategies.py  # استراتژی‌های پیشرفته
│   ├── metrics.py         # محاسبه metrics
│   └── regime_detector.py # تشخیص رژیم بازار
│
├── data_layer/            # دریافت داده
│   ├── client.py          # TwelveData API
│   └── models.py          # Pydantic models
│
├── config/                # تنظیمات
│   └── settings.py        # پیکربندی
│
├── models/                # ML Models
├── results/               # نتایج تست
│
└── 📚 مستندات/
    ├── README.md                 # اینجا
    ├── ARCHITECTURE_DETAILED.md  # معماری
    ├── FIBONACCI_INDICATOR.md    # فیبوناچی
    └── TEST_SIGNAL_AGENT_GUIDE.md
```

---

## 📈 اندیکاتورهای تکنیکالی

### 1-6: اندیکاتورهای استاندارد

| # | نام | نوع | مقصد |
|---|-----|-----|------|
| 1 | SMA | Moving Avg | روند بلندمدت |
| 2 | EMA | Moving Avg | روند کوتاه‌مدت |
| 3 | RSI | Momentum | اشباع |
| 4 | MACD | Trend | جهت روند |
| 5 | BB | Volatility | حمایت/مقاومت |
| 6 | ATR | Volatility | نوسان‌پذیری |

### 7: Fibonacci (فیبوناچی) ⭐

```
سطح‌های حمایت و مقاومت:
0%    ← نقطه شروع
23.6% ← حمایت ضعیف
38.2% ← حمایت متوسط
50%   ← نقطه میانی
61.8% ← حمایت قوی (نسبت طلایی)
78.6% ← حمایت بسیار قوی
100%  ← نقطه انتهایی
```

---

## 🔄 فلوی داده

```
1. دریافت داده
   ↓
2. تحلیل Signal Agent (7 اندیکاتور)
   ↓
3. تحلیل ML Agent (70+ features)
   ↓
4. Decision Agent (تجمیع)
   ↓
5. سیگنال نهایی (BUY/SELL/HOLD)
```

---

## 🧪 نتایج تست

### Signal Agent Test
```
✅ دریافت داده           → PASSED
✅ اندیکاتورها (7)      → PASSED
✅ تولید سیگنال        → PASSED
✅ صحت‌سنجی            → PASSED
✅ Edge Cases           → PASSED

نرخ موفقیت: 100%
زمان: 2.5 ثانیه
```

### مثال نتایج
```
Signal Value: 0.2599
Confidence: 70.99%
Interpretation: 🟢 خرید
```

---

## 🚀 شروع سریع

### نصب

```bash
git clone https://github.com/najafirezawork/gold-trading-system.git
cd gold-trading-system
pip install -r requirements.txt
```

### استفاده ساده

```python
from agents import SignalAgent
from data_layer import TwelveDataClient

client = TwelveDataClient()
agent = SignalAgent()

data = client.get_time_series("XAU/USD", "1h", 200)
signal = agent.analyze(data)

print(f"Signal: {signal.signal:.2f}")
print(f"Confidence: {signal.confidence:.2%}")
```

---

## 🧬 Machine Learning

### Features

70+ features از این دسته‌ها:
- Price Features (10)
- Moving Averages (15)
- Momentum (20)
- Volatility (15)
- Pattern Recognition (10)

### Models

1. **RandomForest** - Ensemble of trees
2. **XGBoost** - Gradient boosting
3. **Ensemble** - Weighted combination

---

## 📊 Backtesting

### استراتژی‌ها

1. SMACrossover
2. RSIBased
3. MACDDivergence
4. BollingerBreakout
5. MultiIndicator

### Metrics

- Total Return
- Win Rate
- Sharpe Ratio
- Sortino Ratio
- Max Drawdown
- Profit Factor

---

## 🐳 Docker

```bash
# شروع سریع
.\docker-run.ps1              # Windows
bash docker-run.sh            # Linux/Mac

# یا Docker Compose
docker-compose up -d
```

---

## 🎯 نقاط قوت

✅ معماری قابل توسعه  
✅ ۷ اندیکاتور دقیق  
✅ Machine Learning پیشرفته  
✅ Backtesting جامع  
✅ ۱۰۰% تست‌های موفق  
✅ مستندات کامل  
✅ Docker ready  
✅ Production ready  

---

## ⚠️ محدودیت‌ها

❌ API Rate Limiting  
❌ Latency Real-time  
❌ Historical Data محدود  
❌ ممکن overfitting در ML  

---

## 🚀 مراحل بعدی

1. Real-time Trading Integration
2. Alert System
3. Portfolio Management
4. Web Dashboard
5. Paper Trading Mode

---

## 📞 تماس

- 🐙 GitHub: najafirezawork/gold-trading-system
- 📧 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

## 📄 لایسنس

MIT License

---

## 👨‍💻 درباره

توسط تیم توسعه‌دهندگان حرفه‌ای ساخته شده  
**نسخه**: 2.1.0  
**وضعیت**: ✅ Production Ready  
**تاریخ**: 28 اکتبر 2025

---

## 🎓 منابع

- [Investopedia - Technical Analysis](https://www.investopedia.com/)
- [Twelve Data API](https://twelvedata.com/)
- [Python Finance](https://pandas.pydata.org/)

---

**آخرین بروزرسانی**: 28 اکتبر 2025
