# 🏛️ تحلیل معماری سیستم

## 📐 نمای معماری کلی

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface Layer                        │
│            (CLI, API, Web Dashboard, Monitoring)               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│               API/Service Layer (Orchestration)                 │
│  • main.py - Entry Points                                       │
│  • Exception Handling                                           │
│  • Request Validation                                           │
└──────────────────────────────┬──────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
    ┌───▼───┐            ┌──────▼─────┐         ┌───▼──┐
    │Agents │            │Backtesting │         │Config│
    │Layer  │            │Engine      │         │Layer │
    └───┬───┘            └──────┬─────┘         └───┬──┘
        │                       │                    │
    ┌───┴────────────────────┬──┴────┐          ┌───▼──────────┐
    │                        │       │          │  Settings    │
    │  ┌────────────────┐    │   ┌──▼──┐       │  • API Key   │
    │  │Meta Agent      │    │   │Strat│       │  • Symbols   │
    │  │(Orchestrator)  │    │   │egies│       │  • Parameters│
    │  └────────────────┘    │   └─────┘       └──────────────┘
    │   ▲   ▲      ▲   ▲     │
    │   │   │      │   │     │
    │ ┌─┴─┬─┴──┬──┬┴─┬─┴─┐   │
    │ │Sig│ ML │Deci│Risk│   │
    │ │nal│    │sion│Mgmt│   │
    │ └───┴────┴────┴────┘   │
    │                        │
    └────────────┬───────────┘
                 │
┌────────────────┴──────────────────┐
│  Technical Analysis & ML Layer      │
│  • 7 Technical Indicators           │
│  • Feature Engineering (70+)        │
│  • ML Models (RF, XGBoost, Ens)     │
│  • Model Training & Prediction      │
└────────────────┬──────────────────┘
                 │
┌────────────────┴──────────────────┐
│      Data Layer & Caching          │
│  • Twelve Data API Client          │
│  • OHLCV Data Models               │
│  • Validation & Normalization      │
│  • Caching (in-memory/disk)        │
└────────────────┬──────────────────┘
                 │
┌────────────────┴──────────────────┐
│      External APIs & Services      │
│  • Twelve Data API (Real-time)     │
│  • Potential: Broker APIs          │
│  • Potential: Alert Services       │
└────────────────────────────────────┘
```

---

## 🔧 جزئیات هر لایه

### 1. Agent Layer

#### BaseAgent (Base Class)
```python
class BaseAgent(ABC):
    ├── agent_type: AgentType
    ├── name: str
    ├── enabled: bool
    └── analyze(data) → AgentOutput: abstract
```

#### Signal Agent
```
┌─────────────────────────────┐
│    Signal Agent (7 Indicators)│
├─────────────────────────────┤
│ Input: MarketData (200 OHLCV)│
│ Process:                     │
│  ├─ SMA(20,50)             │
│  ├─ EMA(12,26)             │
│  ├─ RSI(14)                │
│  ├─ MACD(12,26,9)          │
│  ├─ Bollinger(20,2)        │
│  ├─ ATR(14)                │
│  └─ Fibonacci(H,L)         │
│                             │
│ Output:                      │
│  ├─ signal: -1 to +1       │
│  ├─ confidence: 0 to 1     │
│  └─ indicators metadata     │
└─────────────────────────────┘
```

#### ML Agent
```
70+ Features → Feature Selection → ML Models
    │            ├─ Select top 20-30
    ├─ Price      └─ Remove correlated
    ├─ Moving Avg
    ├─ Momentum    ML Models:
    ├─ Volatility  ├─ RandomForest
    ├─ Patterns    ├─ XGBoost
    └─ Support/Res └─ Ensemble

Output:
├─ prob_up: 0-1 (احتمال صعود)
├─ prob_down: 0-1 (احتمال نزول)
├─ trend_strength: 0-1
├─ volatility: 0-1
└─ momentum: -1 to +1
```

#### Decision Agent
```
Inputs from:
├─ Signal Agent (signal, confidence)
├─ ML Agent (probabilities)
└─ Risk Agent (position size)

Logic:
├─ Weight signals: σᵢ = wₛ*Sₛ + wₘ*Sₘ
├─ Aggregate: Σ = Σᵢ / n
├─ Apply thresholds
│   ├─ > 0.6: STRONG_BUY
│   ├─ 0.3-0.6: BUY
│   ├─ -0.3-0.3: HOLD
│   ├─ -0.6--0.3: SELL
│   └─ < -0.6: STRONG_SELL
└─ Calculate confidence

Output:
├─ decision: BUY/SELL/HOLD
├─ confidence: 0-1
└─ reasoning: str
```

### 2. Data Layer

#### Client (TwelveDataClient)
```python
class TwelveDataClient:
    ├── __init__(api_key)
    ├── get_time_series()  # دریافت OHLCV
    ├── _validate_response()
    ├── _handle_errors()
    └── __enter__/__exit__  # Context Manager
```

#### Models (Pydantic)
```python
class OHLCV:
    ├── datetime: datetime
    ├── open: float
    ├── high: float
    ├── low: float
    ├── close: float
    └── volume: float

class MarketData:
    ├── symbol: str
    ├── interval: str
    ├── data: List[OHLCV]
    ├── meta: Optional[dict]
    └── __len__(), to_dict()
```

### 3. Technical Indicators

#### TechnicalIndicators Class
```python
class TechnicalIndicators:
    @staticmethod
    ├── calculate_sma(prices, period)
    ├── calculate_ema(prices, period)
    ├── calculate_rsi(prices, period)
    ├── calculate_macd(prices, fast, slow, signal)
    ├── calculate_bollinger_bands(prices, period, std)
    ├── calculate_atr(highs, lows, closes, period)
    ├── calculate_fibonacci_retracements(high, low)
    └── get_fibonacci_signal(price, levels)
```

#### محاسبات ریاضی

**SMA (Simple Moving Average)**
```
SMA = Σ(prices[-period:]) / period
```

**EMA (Exponential Moving Average)**
```
Multiplier = 2 / (period + 1)
EMA_t = price_t * M + EMA_(t-1) * (1 - M)
```

**RSI (Relative Strength Index)**
```
RS = avg_gain / avg_loss
RSI = 100 - (100 / (1 + RS))
```

**MACD**
```
MACD = EMA12 - EMA26
Signal = EMA9(MACD)
Histogram = MACD - Signal
```

**Bollinger Bands**
```
Middle = SMA(20)
Upper = Middle + (2 * StdDev)
Lower = Middle - (2 * StdDev)
```

**ATR (Average True Range)**
```
TR = max(H-L, |H-C_prev|, |L-C_prev|)
ATR = avg(TR[-period:])
```

**Fibonacci**
```
diff = high - low
levels = {
    "0": low,
    "23.6": low + diff * 0.236,
    "38.2": low + diff * 0.382,
    "50": low + diff * 0.5,
    "61.8": low + diff * 0.618,  # φ (phi)
    "78.6": low + diff * 0.786,
    "100": high
}
```

### 4. Machine Learning Layer

#### Feature Engineering

```
Total Features: 70+

Category 1: Price Features (10)
├── Close, Open, High, Low
├── Returns (1-day, 5-day, 20-day)
├── High-Low Range
├── Volatility (std dev)
└── Price Ratios

Category 2: Moving Averages (15)
├── SMA(5,10,20,50)
├── EMA(5,10,20)
├── SMA Crossovers
├── EMA Crossovers
└── MA Slopes

Category 3: Momentum (20)
├── RSI(14)
├── MACD, MACD Signal
├── Stochastic %K, %D
├── Rate of Change
├── Momentum Divergence
└── Acceleration

Category 4: Volatility (15)
├── ATR(14)
├── Bollinger Bands Width
├── Bollinger %B
├── Historical Volatility
├── Volatility Ratio
└── Keltner Channels

Category 5: Pattern Recognition (10)
├── Higher Highs/Lows
├── Support/Resistance Breaks
├── Fibonacci Levels Distance
├── Channel Width
└── Trend Strength
```

#### ML Models

**Model 1: RandomForest**
```
- Trees: 100
- Max Depth: 15
- Min Samples Split: 5
- Feature Selection: top 25
- Out-of-bag Score
```

**Model 2: XGBoost**
```
- Estimators: 100
- Max Depth: 6
- Learning Rate: 0.1
- Subsample: 0.8
- Colsample: 0.8
- Objective: binary:logistic
```

**Model 3: Ensemble**
```
Ensemble = (RF * 0.4) + (XGBoost * 0.4) + (LR * 0.2)
├── RF: Tree-based
├── XGBoost: Gradient Boost
└── LR: Linear Regression
```

### 5. Backtesting Engine

#### Strategy Pattern
```python
class BaseStrategy(ABC):
    ├── on_candle(candle)
    ├── should_buy()
    ├── should_sell()
    └── position_size()

# Implementations:
├── SMACrossoverStrategy
├── RSIStrategy
├── MACDDivergenceStrategy
├── BollingerBreakoutStrategy
└── MultiIndicatorStrategy
```

#### BacktestEngine
```
Run Flow:
1. Load Historical Data
2. For each candle:
   a. Update indicators
   b. Check strategy signals
   c. Execute trades
   d. Update equity
3. Calculate Metrics
4. Generate Report
```

#### Metrics Calculation

```python
class PerformanceMetrics:
    ├── total_return = (final_equity - initial) / initial
    ├── win_rate = wins / total_trades
    ├── sharpe_ratio = avg_return / std_return * √252
    ├── sortino_ratio = avg_return / downside_std * √252
    ├── max_drawdown = (peak - trough) / peak
    ├── profit_factor = gross_profit / gross_loss
    ├── payoff_ratio = avg_win / avg_loss
    └── cumulative_returns = equity_curve
```

---

## 🎯 Data Flow

### سناریو: تحلیل و تصمیم‌گیری

```
1. دریافت داده
   └─→ API Call: get_time_series("XAU/USD", "1h", 200)
   └─→ Response: 200 OHLCV candles

2. تحلیل Signal Agent
   ├─→ Extract: closes, highs, lows
   ├─→ Calculate: 7 indicators
   ├─→ Generate signal: 0.25
   └─→ Confidence: 67%

3. تحلیل ML Agent
   ├─→ Engineer: 70+ features
   ├─→ Select: top 25 features
   ├─→ Predict: 3 models
   └─→ Ensemble: prob_up=65%

4. Decision Agent
   ├─→ Weight: 0.4*signal + 0.4*ml + 0.2*risk
   ├─→ Aggregate: 0.52
   ├─→ Threshold: > 0.3 → BUY
   └─→ Final: BUY, confidence 70%

5. Action
   ├─→ Execute: BUY order
   ├─→ Position: 1000 shares
   ├─→ Stop Loss: -2%
   └─→ Take Profit: +5%
```

---

## 🔍 Design Patterns استفاده شده

### 1. Strategy Pattern
```python
# Interface
class BaseStrategy(ABC):
    @abstractmethod
    def on_candle(self, candle): pass

# Implementations
class SMACrossover(BaseStrategy):
    def on_candle(self, candle):
        # SMA logic
        pass

class RSIBased(BaseStrategy):
    def on_candle(self, candle):
        # RSI logic
        pass
```

### 2. Factory Pattern
```python
def create_agent(agent_type: str):
    if agent_type == "signal":
        return SignalAgent()
    elif agent_type == "ml":
        return MLAgent()
    elif agent_type == "decision":
        return DecisionAgent()
```

### 3. Observer Pattern
```python
class BacktestEngine:
    def __init__(self):
        self.observers = []
    
    def notify_trade(self, trade):
        for observer in self.observers:
            observer.on_trade(trade)
```

### 4. Context Manager
```python
class TwelveDataClient:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        pass
```

### 5. Singleton Pattern
```python
@dataclass
class Settings:
    """محیط‌های تنظیمات (یکتا)"""
    api_key: str
    symbol: str
    interval: str
```

### 6. Template Method Pattern
```python
class BaseAgent(ABC):
    def analyze(self, data):
        # Template
        if not self.enabled:
            return self._disabled_output()
        
        indicators = self._calculate_indicators(data)
        signal = self._generate_signal(indicators)
        return self._create_output(signal)
    
    @abstractmethod
    def _calculate_indicators(self, data): pass
    
    @abstractmethod
    def _generate_signal(self, indicators): pass
```

---

## 📊 Class Relationships

```
┌──────────────────────────────────────────────┐
│              BaseAgent (Abstract)             │
│  ├── agent_type: AgentType                   │
│  ├── name: str                               │
│  └── analyze(data) → AgentOutput             │
└────────────┬────────────────────────────────┘
             │
    ┌────────┼────────┬─────────┐
    │        │        │         │
    ▼        ▼        ▼         ▼
┌────────┐ ┌────┐ ┌───────┐ ┌────────┐
│Signal  │ │ ML │ │Decision│ │ Risk   │
│Agent   │ │Agent│ │Agent  │ │Agent   │
└────────┘ └────┘ └───────┘ └────────┘
    │        │        │         │
    └────────┼────────┼─────────┘
             │        │
        ┌────▼────┬───▼─────┐
        │          │         │
        ▼          ▼         ▼
    ┌────────────────────────────┐
    │     Meta Agent             │
    │   (Orchestrator)           │
    │  • Coordinate agents       │
    │  • Aggregate signals       │
    │  • Make decisions          │
    └────────────────────────────┘
```

---

## ⚡ Performance Considerations

### Time Complexity

```
Signal Agent Analysis:
├── SMA calculation: O(n)
├── EMA calculation: O(n)
├── RSI calculation: O(n)
├── MACD calculation: O(n)
├── Bollinger Bands: O(n)
├── ATR calculation: O(n)
└── Fibonacci: O(1)

Total: O(n) where n = number of candles (200)
Average: 50-100ms per analysis
```

### Space Complexity

```
Signal Agent:
├── Input data: 200 candles × 5 values = 1 KB
├── Indicators cache: 7 × float = 56 bytes
└── Output: ~500 bytes

Total: ~2 KB per analysis
Memory efficient ✅
```

### ML Agent

```
Time: 100-500ms (includes feature engineering)
Space: ~10 MB (model file + features)
Bottleneck: Feature engineering & model loading
```

---

## 🔐 Error Handling

```python
# Validation Errors
class InsufficientDataError(Exception):
    """داده ناکافی برای تحلیل"""
    pass

# API Errors
class APIError(Exception):
    """خطای API"""
    pass

# Model Errors
class ModelPredictionError(Exception):
    """خطای پیش‌بینی"""
    pass
```

---

## 📈 Scalability

### Horizontal Scaling
```
Multiple Symbols:
├── XAU/USD → Agent 1
├── EURUSD → Agent 2
├── USDJPY → Agent 3
└── Load Balancer
```

### Vertical Scaling
```
More Data:
├── 200 → 500 candles (no perf impact)
├── Add new indicators (linear time)
└── Multi-processing for ML
```

---

**نتیجه**: معماری قابل توسعه، قابل اعتماد، و بهینه شده برای معاملات سریع
