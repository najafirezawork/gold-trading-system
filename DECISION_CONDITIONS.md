# 📋 شرایط تصمیم‌گیری - چه زمانی BUY/SELL می‌دهد؟

## 🎯 پارامترهای پیش‌فرض (کالیبره شده با مقیاس واقعی)

```python
ml_threshold = 0.65      # حداقل احتمال ML برای تصمیم
trend_threshold = 0.15   # حداقل قدرت ترند (کالیبره شده با range واقعی: 0-0.2)
```

**⚠️ نکته مهم:** 
- `trend_threshold = 0.15` به جای 0.5 استفاده می‌شه چون در داده‌های واقعی، `trend_strength` معمولاً بین 0 تا 0.2 هست.
- اگر 0.5 بذاری، هیچ وقت شرط برقرار نمی‌شه!

---

## ✅ شرط 1: Strong ML + Strong Trend → **BUY**

```python
if (ml_signal.prob_up > 0.65 AND 
    ml_signal.trend_strength > 0.15):
    → BUY (Strong)
```

### مثال:
```
ML Signals:
  prob_up: 0.72 (72%)          ✅ > 0.65
  trend_strength: 0.18 (18%)   ✅ > 0.15

Decision: BUY (Strong)
Confidence: 0.72 × 0.18 = 0.1296 (12.96%)
```

### توضیح:
- مدل ML با اطمینان بالا (>65%) می‌گه قیمت بالا میره
- **و همزمان** ترند قوی وجود داره (>15% از رنج واقعی)
- هر دو شرط باید برقرار باشه

---

## ❌ شرط 2: Strong ML + Strong Trend → **SELL**

```python
if (ml_signal.prob_down > 0.65 AND 
    ml_signal.trend_strength > 0.15):
    → SELL (Strong)
```

### مثال:
```
ML Signals:
  prob_down: 0.70 (70%)        ✅ > 0.65
  trend_strength: 0.20 (20%)   ✅ > 0.15

Decision: SELL (Strong)
Confidence: 0.70 × 0.20 = 0.14 (14%)
```

### توضیح:
- مدل ML با اطمینان بالا (>65%) می‌گه قیمت پایین میاد
- **و همزمان** ترند قوی وجود داره (>15% از رنج واقعی)
- هر دو شرط باید برقرار باشه

---

## 🔄 شرط 3: Technical + ML Momentum → **BUY**

```python
if (tech_signal.signal > 0.3 AND      # Technical bullish
    ml_signal.momentum > 0):           # ML momentum positive
    → BUY (Weak)
```

### مثال:
```
Technical Signal: +0.45 (bullish)     ✅ > 0.3
ML momentum: +0.05                     ✅ > 0

Decision: BUY (Weak)
Confidence: (tech_confidence + prob_up) / 2
```

### توضیح:
- اگر شرط 1 برقرار نبود (prob_up < 65% یا trend < 15%)
- **ولی** Technical Analysis می‌گه BUY
- **و** ML momentum مثبته (حتی اگر خیلی کم باشه)
- پس هر دو توافق دارن → BUY (با confidence کمتر)

---

## 🔄 شرط 4: Technical + ML Momentum → **SELL**

```python
if (tech_signal.signal < -0.3 AND     # Technical bearish
    ml_signal.momentum < 0):           # ML momentum negative
    → SELL (Weak)
```

### مثال:
```
Technical Signal: -0.45 (bearish)     ✅ < -0.3
ML momentum: -0.08                     ✅ < 0

Decision: SELL (Weak)
Confidence: (tech_confidence + prob_down) / 2
```

### توضیح:
- اگر شرط 2 برقرار نبود (prob_down < 65% یا trend < 15%)
- **ولی** Technical Analysis می‌گه SELL
- **و** ML momentum منفیه (حتی اگر خیلی کم باشه)
- پس هر دو توافق دارن → SELL (با confidence کمتر)

---

## ⚪ شرط 5: هیچ شرطی برقرار نباشد → **HOLD**

```python
else:
    → HOLD
```

### مثال:
```
ML Signals:
  prob_up: 0.45 (45%)          ❌ < 0.65
  prob_down: 0.55 (55%)        ❌ < 0.65
  trend_strength: 0.11 (11%)   ❌ < 0.15
  momentum: -0.01              ❌ نزدیک به 0

Technical Signal: -0.15        ❌ نه > 0.3 نه < -0.3

Decision: HOLD
Reason: "No clear signal from ML or Technical"
```

### چرا HOLD؟
- prob_up و prob_down هر دو ضعیف (<65%)
- trend_strength خیلی کم (<15%) → بازار رنج است
- momentum نزدیک به صفر → بی‌جهت
- Technical signal ضعیف → نه خریدار نه فروشنده

**این دقیقاً مثال واقعی‌ای بود که در تست دیدیم! ✅**

---

## ⚡ شرط اضافی: High Volatility Adjustment

```python
if ml_signal.volatility > 0.7:
    confidence *= 0.8  # کاهش 20% confidence
```

### مثال:
```
Original Decision: BUY, Confidence: 0.50
Volatility: 0.85 (85%)  ✅ > 0.7

Adjusted Confidence: 0.50 × 0.8 = 0.40 (40%)

Note: تصمیم تغییر نمی‌کنه، فقط confidence کم میشه
```

---

## 📊 جدول خلاصه (کالیبره شده با مقیاس واقعی)

| شرایط | Type | Action | Confidence |
|-------|------|--------|-----------|
| `prob_up > 65%` **AND** `trend > 15%` | **Strong** | **BUY** | `prob_up × trend_strength` |
| `prob_down > 65%` **AND** `trend > 15%` | **Strong** | **SELL** | `prob_down × trend_strength` |
| `tech > 0.3` **AND** `momentum > 0` | **Weak** | **BUY** | `(tech_conf + prob_up) / 2` |
| `tech < -0.3` **AND** `momentum < 0` | **Weak** | **SELL** | `(tech_conf + prob_down) / 2` |
| هیچ شرطی | - | **HOLD** | `0.5` |

---

## 🎯 مثال‌های واقعی

### مثال 1: BUY Signal - Strong (شرط 1)

```
Input:
  prob_up: 0.72
  prob_down: 0.28
  trend_strength: 0.18    # 18% - قوی در رنج واقعی
  momentum: 0.08

Check شرط 1:
  ✅ prob_up (0.72) > 0.65
  ✅ trend_strength (0.18) > 0.15

Output:
  Action: BUY (Strong)
  Confidence: 0.72 × 0.18 = 12.96%
  Reason: "Strong Buy: ML shows 72% UP probability | Trend strength: 0.18%"
```

### مثال 2: SELL Signal - Strong (شرط 2)

```
Input:
  prob_up: 0.25
  prob_down: 0.75
  trend_strength: 0.20    # 20% - خیلی قوی در رنج واقعی
  momentum: -0.10

Check شرط 2:
  ✅ prob_down (0.75) > 0.65
  ✅ trend_strength (0.20) > 0.15

Output:
  Action: SELL (Strong)
  Confidence: 0.75 × 0.20 = 15%
  Reason: "Strong Sell: ML shows 75% DOWN probability | Trend strength: 0.20%"
```

### مثال 3: BUY Signal - Weak (شرط 3)

```
Input:
  prob_up: 0.58
  prob_down: 0.42
  trend_strength: 0.08  ❌ کمتر از 0.15
  momentum: 0.02        ✅ مثبت (>0)
  tech_signal: 0.45
  tech_confidence: 0.70

Check شرط 1:
  ❌ prob_up (0.58) < 0.65
  ❌ trend_strength (0.08) < 0.15

Check شرط 3:
  ✅ tech_signal (0.45) > 0.3
  ✅ momentum (0.02) > 0

Output:
  Action: BUY (Weak)
  Confidence: (0.70 + 0.58) / 2 = 64%
  Reason: "Weak Buy: Technical bullish | ML momentum positive (+0.02)"
```

### مثال 4: HOLD - بازار رنج (مثال واقعی تست شما!)

```
Input:
  prob_up: 0.35
  prob_down: 0.65
  trend_strength: 0.11  ❌ خیلی ضعیف
  momentum: -0.003      ❌ نزدیک صفر
  tech_signal: -0.20    ❌ نه قوی

Check همه شروط:
  ❌ شرط 1: prob_up (0.35) < 0.65
  ❌ شرط 2: trend_strength (0.11) < 0.15
  ❌ شرط 3: tech_signal (-0.20) not > 0.3
  ❌ شرط 4: momentum (-0.003) not < 0 (تقریباً صفر)

Output:
  Action: HOLD
  Confidence: 50%
  Reason: "No clear signal | ML: 35% UP vs 65% DOWN | Trend too weak (11%)"
```

**این دقیقاً مثال واقعی بود که در تست دیدیم:**
- بازار رنج بود (`trend_strength: 0.11`)
- هیچ سیگنال قوی نبود
- سیستم درست HOLD داد ✅

---

## 🔧 تنظیمات قابل تغییر

### کاهش حساسیت (کمتر trade کردن - محافظه‌کارانه‌تر):

```python
decision_agent = SimpleDecisionAgent(
    ml_agent=ml_agent,
    signal_agent=signal_agent,
    ml_threshold=0.75,        # از 0.65 به 0.75 ✅
    trend_threshold=0.18      # از 0.15 به 0.18 ✅
)
```

**نتیجه:** فقط در سیگنال‌های قوی‌تر trade می‌کنه

### افزایش حساسیت (بیشتر trade کردن - تهاجمی‌تر):

```python
decision_agent = SimpleDecisionAgent(
    ml_agent=ml_agent,
    signal_agent=signal_agent,
    ml_threshold=0.55,        # از 0.65 به 0.55 ✅
    trend_threshold=0.10      # از 0.15 به 0.10 ✅
)
```

**نتیجه:** با سیگنال‌های ضعیف‌تر هم trade می‌کنه

---

## 💡 توصیه‌ها (بر اساس مقیاس واقعی)

### برای بازارهای Trending:
```python
ml_threshold = 0.60      # کمی کمتر
trend_threshold = 0.12   # معمولاً بازار ترند ضعیف‌تری داره
```

### برای بازارهای Volatile:
```python
ml_threshold = 0.75      # خیلی بیشتر
trend_threshold = 0.18   # بیشتر
```

### برای بازارهای Ranging (مثل تست شما!):
```python
ml_threshold = 0.70
trend_threshold = 0.20
# و بهتر اصلاً trade نکنی!
# سیستم خودش HOLD میده چون trend < 0.20
```

---

## 📉 چرا trend_strength در رنج 0-0.2 است؟

در محاسبه `trend_strength` در ML Agent:

```python
# از ADX استفاده می‌شه که معمولاً < 25 است
trend_strength = min(adx_14 / 100.0, 1.0)

# یا از تفاوت SMA
sma_diff = abs(sma_20 - sma_50) / current_price
trend_strength = min(sma_diff * 10, 1.0)
```

**در بازار طلا:**
- ADX معمولاً بین 10-25 است → trend_strength: 0.10-0.25
- بازارهای رنج: ADX < 20 → trend_strength < 0.20 ✅
- بازارهای ترنددار: ADX > 25 → trend_strength > 0.25

**پس threshold = 0.15 منطقی است:**
- بازار رنج: trend < 0.15 → HOLD
- بازار ترند ضعیف: 0.15 < trend < 0.20 → Trade با احتیاط
- بازار ترند قوی: trend > 0.20 → Trade با اعتماد

---

## 📈 نمودار تصمیم‌گیری

```
┌─────────────────────────────────────────┐
│  Start: Analyze Market Data            │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│  Get ML Signals + Technical Signals     │
└─────────────┬───────────────────────────┘
              │
              ↓
        ╔═════════════╗
        ║ شرط 1؟      ║  prob_up > 65% AND trend > 50%
        ╚══════╤══════╝
               │ YES → BUY
               │ NO
               ↓
        ╔═════════════╗
        ║ شرط 2؟      ║  prob_down > 65% AND trend > 50%
        ╚══════╤══════╝
               │ YES → SELL
               │ NO
               ↓
        ╔═════════════╗
        ║ شرط 3؟      ║  tech > 0.3 AND momentum > 0.2
        ╚══════╤══════╝
               │ YES → BUY
               │ NO
               ↓
        ╔═════════════╗
        ║ شرط 4؟      ║  tech < -0.3 AND momentum < -0.2
        ╚══════╤══════╝
               │ YES → SELL
               │ NO
               ↓
        ╔═════════════╗
        ║ شرط 5       ║  هیچ کدام
        ╚══════╤══════╝
               │
               ↓ HOLD
```

---

## 🎓 درس‌های کلیدی

1. **دو لایه تصمیم‌گیری:**
   - لایه 1: ML قوی + Trend قوی (conservative)
   - لایه 2: Technical + ML موافق‌اند (moderate)

2. **HOLD وقتی:**
   - سیگنال‌های ضعیف
   - سیگنال‌های متناقض
   - ترند ضعیف
   - نوسان خیلی بالا

3. **ترکیب signals:**
   - ML probability
   - Trend strength
   - Technical signal
   - Momentum

4. **Risk management:**
   - Confidence adjustment با volatility
   - Multiple conditions برای BUY/SELL
   - HOLD به عنوان default

---

این شرایط **محافظه‌کارانه** هستند و برای **کاهش false signals** طراحی شده‌اند.

---

# ✅ نسخه‌ی ساده و استاندارد

## Decision Logic Summary

ML Agent outputs probabilities and momentum signals.  
Technical Agent outputs a normalized signal [-1..+1].  
Decision Agent rules:

### Strong Buy
```python
if prob_up > 0.65 and trend_strength > 0.15:
    → BUY (Strong)
```

### Weak Buy
```python
if technical_signal > 0.30 and momentum > 0:
    → BUY (Weak)
```

### Strong Sell
```python
if prob_down > 0.65 and trend_strength > 0.15:
    → SELL (Strong)
```

### Weak Sell
```python
if technical_signal < -0.30 and momentum < 0:
    → SELL (Weak)
```

### Hold
```python
else:
    → HOLD
```

---

## Key Thresholds (Calibrated)

| Parameter | Value | Note |
|-----------|-------|------|
| `ml_threshold` | 0.65 | ML probability threshold |
| `trend_threshold` | 0.15 | Calibrated for real data range (0-0.2) |
| `tech_threshold` | ±0.30 | Technical signal threshold |
| `momentum_threshold` | 0 | Any positive/negative momentum |

---

## Why 0.15 instead of 0.50?

In real gold market data:
- `trend_strength` typically ranges from **0 to 0.2**
- Ranging market: trend < 0.15
- Trending market: trend > 0.15

Setting threshold to 0.50 would mean **no trades ever execute**! ❌

---

## Architecture

```
Market Data
    ↓
ML Agent (Signal Generator)
    → prob_up, prob_down, trend_strength, volatility, momentum
    ↓
Technical Agent
    → signal, confidence
    ↓
Decision Agent (BUY/SELL/HOLD)
```

**✅ ML Agent does NOT make trading decisions**  
**✅ ML Agent generates signals**  
**✅ Decision Agent makes final trading decisions**
