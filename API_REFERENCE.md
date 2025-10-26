# API Reference

مستندات کامل API های موجود در سیستم.

## Data Layer API

### TwelveDataClient

کلاس اصلی برای ارتباط با Twelve Data API.

#### Constructor

```python
TwelveDataClient(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key` (str, optional): کلید API. اگر None باشد از settings استفاده می‌شود.

#### Methods

##### get_time_series()

دریافت داده‌های time series برای یک نماد.

```python
get_time_series(
    symbol: str,
    interval: str = "1h",
    outputsize: int = 100,
    timezone: str = "UTC"
) -> MarketData
```

**Parameters:**
- `symbol` (str): نماد معاملاتی (مثل "XAU/USD")
- `interval` (str): بازه زمانی (1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month)
- `outputsize` (int): تعداد نقاط داده
- `timezone` (str): منطقه زمانی

**Returns:**
- `MarketData`: شی حاوی داده‌های OHLCV

**Raises:**
- `TwelveDataAPIError`: در صورت خطا در API

**Example:**
```python
client = TwelveDataClient()
data = client.get_time_series("XAU/USD", interval="1h", outputsize=100)
print(f"Fetched {len(data)} candles")
```

##### get_quote()

دریافت قیمت لحظه‌ای.

```python
get_quote(symbol: str) -> Dict[str, Any]
```

**Example:**
```python
quote = client.get_quote("XAU/USD")
print(f"Current price: ${quote['close']}")
```

### MarketData

مدل داده برای نگهداری اطلاعات بازار.

#### Attributes

- `symbol` (str): نماد
- `interval` (str): بازه زمانی
- `data` (List[OHLCV]): لیست داده‌های OHLCV
- `meta` (dict, optional): اطلاعات متا

#### Methods

```python
def __len__(self) -> int
    """تعداد کندل‌ها"""

def to_dict(self) -> dict
    """تبدیل به dictionary"""
```

### OHLCV

مدل یک کندل.

#### Attributes

- `datetime` (datetime): زمان
- `open` (float): قیمت باز شدن
- `high` (float): بالاترین قیمت
- `low` (float): پایین‌ترین قیمت
- `close` (float): قیمت بسته شدن
- `volume` (float, optional): حجم

---

## Agents API

### BaseAgent

کلاس پایه برای همه agent ها.

#### Constructor

```python
BaseAgent(agent_type: AgentType, name: Optional[str] = None)
```

#### Methods

##### analyze()

متد اصلی برای تحلیل (باید در کلاس فرزند override شود).

```python
@abstractmethod
def analyze(self, data: Any) -> AgentOutput
```

##### enable() / disable()

فعال/غیرفعال کردن agent.

```python
agent.enable()
agent.disable()
```

##### is_enabled()

بررسی وضعیت agent.

```python
if agent.is_enabled():
    output = agent.analyze(data)
```

### AgentOutput

خروجی استاندارد همه agent ها.

#### Attributes

- `agent_type` (AgentType): نوع agent
- `signal` (float): سیگنال معاملاتی (-1 تا 1)
  - `-1`: فروش قوی (Strong Sell)
  - `0`: خنثی (Neutral)
  - `1`: خرید قوی (Strong Buy)
- `confidence` (float): میزان اطمینان (0 تا 1)
- `metadata` (dict): اطلاعات اضافی

#### Methods

```python
def to_dict(self) -> Dict[str, Any]
    """تبدیل به dictionary"""
```

**Example:**
```python
output = agent.analyze(data)
print(f"Signal: {output.signal:.2f}")
print(f"Confidence: {output.confidence:.2f}")
print(f"Type: {output.agent_type.value}")
```

### SignalAgent

Agent تحلیل تکنیکال.

#### Constructor

```python
SignalAgent(name: str = "Technical Signal Agent")
```

#### analyze()

تحلیل داده‌های بازار با اندیکاتورهای تکنیکال.

```python
def analyze(self, data: MarketData) -> AgentOutput
```

**Parameters:**
- `data` (MarketData): داده‌های بازار (حداقل 30 کندل)

**Returns:**
- `AgentOutput` با metadata حاوی:
  - `symbol`: نماد
  - `current_price`: قیمت فعلی
  - `indicators`: مقادیر اندیکاتورها
  - `analysis`: توضیح سیگنال

**Example:**
```python
signal_agent = SignalAgent()
market_data = client.get_time_series("XAU/USD")
output = signal_agent.analyze(market_data)

print(f"Analysis: {output.metadata['analysis']}")
print(f"RSI: {output.metadata['indicators']['rsi']:.2f}")
```

#### اندیکاتورهای استفاده شده

- **SMA(20, 50)**: Simple Moving Average
- **EMA(12)**: Exponential Moving Average
- **RSI(14)**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: با 2 std dev
- **ATR**: Average True Range

### DecisionAgent

Agent تصمیم‌گیری نهایی.

#### Constructor

```python
DecisionAgent(name: str = "Decision Agent")
```

#### analyze()

تجمیع خروجی‌های چند agent و تصمیم‌گیری نهایی.

```python
def analyze(self, agent_outputs: List[AgentOutput]) -> AgentOutput
```

**Parameters:**
- `agent_outputs` (List[AgentOutput]): لیست خروجی agent ها

**Returns:**
- `AgentOutput` با metadata حاوی:
  - `decision`: تصمیم نهایی (TradingDecision)
  - `agent_contributions`: سهم هر agent
  - `reasoning`: دلایل تصمیم

**Example:**
```python
decision_agent = DecisionAgent()

# جمع‌آوری خروجی agent ها
outputs = [
    signal_agent.analyze(data),
    ml_agent.analyze(data)
]

# تصمیم‌گیری
decision = decision_agent.analyze(outputs)
print(f"Decision: {decision.metadata['decision']}")
print(f"Reasoning: {decision.metadata['reasoning']}")
```

#### set_thresholds()

تنظیم آستانه‌های تصمیم‌گیری.

```python
def set_thresholds(self, strong: float, medium: float)
```

**Parameters:**
- `strong` (float): آستانه سیگنال قوی (0-1)
- `medium` (float): آستانه سیگنال متوسط (0-1)

**Example:**
```python
# تنظیمات محافظه‌کارانه
decision_agent.set_thresholds(strong=0.85, medium=0.65)
```

### TradingDecision

Enum برای تصمیمات معاملاتی.

```python
class TradingDecision(Enum):
    STRONG_BUY = "STRONG_BUY"      # خرید قوی
    BUY = "BUY"                    # خرید
    HOLD = "HOLD"                  # نگهداری
    SELL = "SELL"                  # فروش
    STRONG_SELL = "STRONG_SELL"    # فروش قوی
```

---

## Technical Indicators API

### TechnicalIndicators

کلاس استاتیک برای محاسبه اندیکاتورها.

#### calculate_sma()

محاسبه میانگین متحرک ساده.

```python
@staticmethod
def calculate_sma(prices: List[float], period: int) -> float
```

**Example:**
```python
from agents.signal import TechnicalIndicators

prices = [2640, 2645, 2650, 2648, 2652]
sma = TechnicalIndicators.calculate_sma(prices, period=5)
print(f"SMA(5): ${sma:.2f}")
```

#### calculate_ema()

محاسبه میانگین متحرک نمایی.

```python
@staticmethod
def calculate_ema(prices: List[float], period: int) -> float
```

#### calculate_rsi()

محاسبه شاخص قدرت نسبی.

```python
@staticmethod
def calculate_rsi(prices: List[float], period: int = 14) -> float
```

**Returns:**
- float: مقدار RSI بین 0 تا 100
  - `< 30`: oversold (اشباع فروش)
  - `> 70`: overbought (اشباع خرید)

#### calculate_macd()

محاسبه MACD.

```python
@staticmethod
def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> tuple[float, float, float]
```

**Returns:**
- tuple: (macd_line, signal_line, histogram)

#### calculate_bollinger_bands()

محاسبه باندهای بولینگر.

```python
@staticmethod
def calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    std_dev: float = 2.0
) -> tuple[float, float, float]
```

**Returns:**
- tuple: (upper_band, middle_band, lower_band)

#### calculate_atr()

محاسبه میانگین محدوده واقعی (نوسان).

```python
@staticmethod
def calculate_atr(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    period: int = 14
) -> float
```

---

## Config API

### Settings

تنظیمات سیستم با استفاده از Pydantic.

#### Attributes

##### API Configuration
- `twelve_data_api_key` (str): کلید API
- `twelve_data_base_url` (str): آدرس پایه API

##### Trading Configuration
- `default_symbol` (str): نماد پیش‌فرض ("XAU/USD")
- `default_interval` (str): بازه زمانی پیش‌فرض ("1h")
- `default_outputsize` (int): تعداد داده پیش‌فرض (100)

##### Agent Configuration
- `signal_agent_enabled` (bool): فعال بودن Signal Agent
- `ml_agent_enabled` (bool): فعال بودن ML Agent

##### Decision Thresholds
- `strong_signal_threshold` (float): آستانه سیگنال قوی (0.7)
- `medium_signal_threshold` (float): آستانه سیگنال متوسط (0.5)

#### Usage

```python
from config import settings

print(f"API Key: {settings.twelve_data_api_key}")
print(f"Default Symbol: {settings.default_symbol}")

# تغییر تنظیمات در runtime
settings.default_interval = "4h"
```

---

## Exceptions

### TwelveDataAPIError

Exception سفارشی برای خطاهای API.

```python
try:
    data = client.get_time_series("INVALID")
except TwelveDataAPIError as e:
    print(f"API Error: {e}")
```

---

## Complete Example

```python
from data_layer import TwelveDataClient
from agents import SignalAgent, DecisionAgent
from config import settings

# Initialize
client = TwelveDataClient()
signal_agent = SignalAgent()
decision_agent = DecisionAgent()

# Customize settings
decision_agent.set_thresholds(strong=0.8, medium=0.6)

# Fetch data
data = client.get_time_series(
    symbol="XAU/USD",
    interval="1h",
    outputsize=100
)

print(f"Fetched {len(data)} candles")
print(f"Current price: ${data.data[0].close:.2f}")

# Analyze
signal_output = signal_agent.analyze(data)
print(f"Signal: {signal_output.signal:.2f}")
print(f"Confidence: {signal_output.confidence:.2f}")
print(f"Analysis: {signal_output.metadata['analysis']}")

# Make decision
decision = decision_agent.analyze([signal_output])
print(f"Decision: {decision.metadata['decision']}")
print(f"Reasoning: {decision.metadata['reasoning']}")

# Cleanup
client.close()
```

---

## Type Hints Reference

```python
# Common types used in the system
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Custom types
MarketData: object containing OHLCV data
AgentOutput: standardized output from agents
TradingDecision: enum of trading decisions
```
