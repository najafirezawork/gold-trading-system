# استراتژی‌های پیشرفته - راهنمای کامل 🚀

## معرفی

این فایل شامل **5 استراتژی پیشرفته** است که با ترکیب چندین اندیکاتور برای افزایش دقت و win rate طراحی شده‌اند.

---

## 📊 استراتژی‌های موجود

### 1. Trend Following Strategy
**هدف**: فقط در جهت ترند اصلی معامله کنید

**اندیکاتورها:**
- SMA(50) و SMA(200) برای تشخیص ترند
- RSI برای فیلتر کردن extremes
- MACD برای تایید ورود

**Logic:**
```
Uptrend: SMA(50) > SMA(200)
Downtrend: SMA(50) < SMA(200)

خرید: Uptrend + RSI بین 40-60 + MACD Crossover Up
فروش: Downtrend + RSI بین 40-60 + MACD Crossover Down
```

**Risk Management:**
- Stop Loss: 2.5%
- Take Profit: 5%

**مناسب برای:**
- بازارهای trending
- Timeframe های بالاتر (4h, 1d)

---

### 2. Mean Reversion Strategy
**هدف**: خرید در کف و فروش در سقف

**اندیکاتورها:**
- Bollinger Bands (20, 2.0)
- RSI (14)

**Logic:**
```
خرید: قیمت <= Lower Band + RSI < 30
فروش: قیمت >= Upper Band + RSI > 70

خروج: بازگشت به Middle Band با حداقل 0.5% سود
```

**Risk Management:**
- Stop Loss: 2%
- Take Profit: 3%

**مناسب برای:**
- بازارهای ranging/sideways
- Timeframe های پایین (15m, 1h)

---

### 3. Breakout Strategy
**هدف**: سوار شدن روی حرکت‌های قوی

**اندیکاتورها:**
- Highest/Lowest N روز
- Volume
- RSI برای جهت

**Logic:**
```
خرید: 
  - قیمت > Highest(20)
  - Volume > 1.5x Average
  - RSI > 50

فروش:
  - قیمت < Lowest(20)
  - Volume > 1.5x Average
  - RSI < 50
```

**Risk Management:**
- Stop Loss: 1.5%
- Take Profit: 4%

**مناسب برای:**
- خبرها و رویدادهای مهم
- Volatile markets

---

### 4. Multi-Confirmation Strategy ⭐
**هدف**: بالاترین دقت با تایید از همه منابع

**اندیکاتورها:**
- SMA(50)
- RSI (14)
- MACD
- Bollinger Bands (20, 2.0)

**Logic:**
```
خرید - همه شرایط باید برقرار باشد:
  ✅ قیمت > SMA(50)
  ✅ RSI بین 30-55
  ✅ MACD Crossover Up
  ✅ قیمت در نصف پایین BB (بین Lower و Middle)

فروش - همه شرایط باید برقرار باشد:
  ✅ قیمت < SMA(50)
  ✅ RSI بین 45-70
  ✅ MACD Crossover Down
  ✅ قیمت در نصف بالای BB (بین Middle و Upper)
```

**Risk Management:**
- Stop Loss: 2%
- Take Profit: 5%

**مزایا:**
- ✅ کمترین false signals
- ✅ Win rate بالا (معمولاً 60%+)
- ✅ معاملات کمتر اما با کیفیت

**معایب:**
- ⚠️ تعداد معاملات کم
- ⚠️ ممکن است فرصت‌ها را از دست بدهد

---

### 5. Adaptive RSI Strategy 🎯
**هدف**: تطبیق با volatility بازار

**اندیکاتورها:**
- RSI (14)
- ATR (14) برای اندازه‌گیری volatility

**Logic:**
```
1. محاسبه ATR percentage:
   ATR% = (ATR / Average Price) × 100

2. تنظیم RSI thresholds بر اساس volatility:
   
   High Volatility (ATR% > 1.5%):
     Oversold: 25 (سخت‌تر)
     Overbought: 75 (سخت‌تر)
   
   Medium Volatility (1.0% < ATR% < 1.5%):
     Oversold: 30
     Overbought: 70
   
   Low Volatility (ATR% < 1.0%):
     Oversold: 35 (راحت‌تر)
     Overbought: 65 (راحت‌تر)

3. Stop Loss و Take Profit هم با ATR تنظیم می‌شود
```

**Risk Management:**
- Stop Loss: 1.5% تا 2.25% (بر اساس ATR)
- Take Profit: 4% تا 6% (بر اساس ATR)

**مزایا:**
- ✅ سازگاری با شرایط بازار
- ✅ کاهش false signals در volatility بالا
- ✅ افزایش فرصت‌ها در volatility پایین

---

## 📈 نتایج مقایسه (نمونه)

بر روی 500 کندل 4 ساعته XAU/USD:

| استراتژی | Return % | Trades | Win Rate | Sharpe | Max DD |
|---------|----------|--------|----------|--------|--------|
| **Adaptive RSI** | 0.61% | 30 | 56.67% | -0.09 | 4.58% |
| Multi-Confirmation | 0.53% | 1 | 100% | N/A | 0.05% |
| Trend Following | 0.00% | 0 | - | N/A | 0.00% |
| Mean Reversion | -0.86% | 13 | 53.85% | -1.92 | 5.37% |
| Breakout | 0.00% | 0 | - | N/A | 0.00% |

**بهترین استراتژی:** Adaptive RSI (متعادل)

---

## 🎯 توصیه‌ها برای انتخاب استراتژی

### بر اساس Market Condition:

**Trending Market:**
- ✅ Trend Following Strategy
- ✅ Breakout Strategy

**Ranging Market:**
- ✅ Mean Reversion Strategy
- ✅ Multi-Confirmation Strategy

**Volatile Market:**
- ✅ Adaptive RSI Strategy
- ✅ Breakout Strategy

**Low Volatility:**
- ✅ Mean Reversion Strategy

---

### بر اساس Trading Style:

**Conservative (محافظه‌کار):**
- ✅ Multi-Confirmation Strategy
- کم معامله، دقت بالا

**Balanced (متعادل):**
- ✅ Adaptive RSI Strategy
- ✅ Trend Following Strategy

**Aggressive (تهاجمی):**
- ✅ Breakout Strategy
- ✅ Mean Reversion Strategy

---

### بر اساس Timeframe:

**Scalping (1m, 5m):**
- ⚠️ توصیه نمی‌شود با این استراتژی‌ها

**Intraday (15m, 1h):**
- ✅ Mean Reversion
- ✅ Adaptive RSI

**Swing (4h, 1d):**
- ✅ Trend Following
- ✅ Multi-Confirmation
- ✅ Breakout

---

## 💡 نکات مهم

### 1. Optimization
```python
# مثال: تنظیم parameters
strategy = TrendFollowingStrategy(
    fast_ma=30,    # کاهش برای حساسیت بیشتر
    slow_ma=100,   # کاهش برای سیگنال‌های سریع‌تر
    rsi_min=35,    # تنظیم فیلتر
    rsi_max=65
)
```

### 2. Backtesting
همیشه قبل از استفاده واقعی، backtest کنید:
```bash
python examples/test_advanced_strategies.py
```

### 3. Walk-Forward Testing
برای جلوگیری از overfitting:
- Train روی 70% داده
- Test روی 30% باقیمانده

### 4. Risk Management
- هیچ‌وقت risk بیش از 2% سرمایه در هر معامله
- همیشه Stop Loss تعیین کنید
- Profit/Loss Ratio حداقل 1.5:1

### 5. Combine Strategies
می‌توانید چند استراتژی را ترکیب کنید:
```python
# مثال: ترکیب سیگنال‌ها
trend_signal = trend_strategy.should_enter(...)
adaptive_signal = adaptive_strategy.should_enter(...)

# فقط وقتی هر دو موافق باشند
if trend_signal == adaptive_signal:
    enter_trade()
```

---

## 🔧 ساخت استراتژی سفارشی

```python
from backtesting import BaseStrategy
from agents.signal import TechnicalIndicators

class MyCustomStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("My Strategy")
    
    def should_enter(self, market_data, current_index, agent_output=None):
        # Logic شما
        closes = [bar.close for bar in market_data.data[:current_index + 1]]
        
        # محاسبات اندیکاتور
        rsi = TechnicalIndicators.calculate_rsi(closes, 14)
        sma = TechnicalIndicators.calculate_sma(closes, 50)
        
        # شرایط
        if closes[-1] > sma and rsi < 40:
            return "BUY"
        
        return None
    
    def should_exit(self, market_data, current_index, entry_price, position_type):
        # Logic خروج
        return False
    
    def get_stop_loss(self, entry_price, position_type):
        return entry_price * 0.98 if position_type == "LONG" else entry_price * 1.02
    
    def get_take_profit(self, entry_price, position_type):
        return entry_price * 1.05 if position_type == "LONG" else entry_price * 0.95
```

---

## 📚 منابع بیشتر

- [BACKTESTING.md](../BACKTESTING.md) - راهنمای کامل backtesting
- [examples/test_advanced_strategies.py](../examples/test_advanced_strategies.py) - مثال‌های کامل
- [backtesting/advanced_strategies.py](../backtesting/advanced_strategies.py) - کد کامل

---

## ⚠️ هشدار

این استراتژی‌ها برای آموزش و تست هستند. قبل از استفاده با پول واقعی:
1. Backtest کامل انجام دهید
2. با paper trading تست کنید
3. با سرمایه کم شروع کنید
4. همیشه Stop Loss تعیین کنید

**معامله در بازارهای مالی ریسک دارد. مسئولیت استفاده با خود شماست.**

---

**Happy Trading! 📈🏆**
