# راهنمای توسعه‌دهنده (Developer Guide)

## معماری سیستم

سیستم بر اساس معماری Agent-Based طراحی شده که به راحتی قابل توسعه است.

### ساختار کلی

```
┌─────────────────────────────────────────────────────────┐
│                    Trading System                        │
│                                                          │
│  ┌──────────────┐      ┌────────────────────────────┐  │
│  │  Data Layer  │─────▶│     Agent System           │  │
│  │              │      │                            │  │
│  │ • API Client │      │  ┌──────────────────────┐  │  │
│  │ • Data Models│      │  │   Signal Agent       │  │  │
│  └──────────────┘      │  │  (Technical Analysis)│  │  │
│                        │  └──────────────────────┘  │  │
│                        │                            │  │
│                        │  ┌──────────────────────┐  │  │
│                        │  │   ML Agent           │  │  │
│                        │  │  (Future: ML Models) │  │  │
│                        │  └──────────────────────┘  │  │
│                        │                            │  │
│                        │  ┌──────────────────────┐  │  │
│                        │  │  Decision Agent      │  │  │
│                        │  │  (Aggregates All)    │  │  │
│                        │  └──────────────────────┘  │  │
│                        └────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## چگونه Agent جدید اضافه کنیم؟

### مرحله 1: ایجاد Agent Class

در فولدر `agents/` یک پوشه جدید بسازید (مثلاً `ml/` یا `sentiment/`):

```python
# agents/ml/ml_agent.py

from agents.base import BaseAgent, AgentOutput, AgentType
from data_layer import MarketData

class MLAgent(BaseAgent):
    """Agent based on Machine Learning predictions."""
    
    def __init__(self, model_path: str = None):
        super().__init__(AgentType.ML, "ML Agent")
        # Load your model
        self.model = self._load_model(model_path)
    
    def analyze(self, data: MarketData) -> AgentOutput:
        """Analyze using ML model."""
        if not self.enabled:
            return AgentOutput(
                agent_type=self.agent_type,
                signal=0.0,
                confidence=0.0,
                metadata={"status": "disabled"}
            )
        
        # Prepare features
        features = self._prepare_features(data)
        
        # Get prediction
        prediction = self.model.predict(features)
        signal = self._convert_prediction_to_signal(prediction)
        confidence = self._calculate_confidence(prediction)
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=signal,
            confidence=confidence,
            metadata={
                "model_version": "1.0",
                "prediction": prediction,
                "features": features
            }
        )
    
    def _prepare_features(self, data: MarketData):
        """Extract features from market data."""
        # Implement feature engineering
        pass
    
    def _convert_prediction_to_signal(self, prediction):
        """Convert model output to -1 to 1 signal."""
        # Implement conversion logic
        pass
    
    def _calculate_confidence(self, prediction):
        """Calculate confidence from model output."""
        # Implement confidence calculation
        pass
    
    def _load_model(self, path):
        """Load ML model."""
        # Implement model loading
        pass
```

### مرحله 2: افزودن AgentType جدید

در `agents/base/agent.py` در enum AgentType:

```python
class AgentType(Enum):
    SIGNAL = "signal"
    ML = "ml"              # ✓ Already added
    SENTIMENT = "sentiment"  # Add new type
    NEWS = "news"           # Add new type
    DECISION = "decision"
```

### مرحله 3: استفاده از Agent جدید

```python
from agents.ml import MLAgent
from agents import DecisionAgent

# Initialize agents
signal_agent = SignalAgent()
ml_agent = MLAgent(model_path="models/gold_predictor.pkl")
decision_agent = DecisionAgent()

# Fetch data
market_data = client.get_time_series("XAU/USD")

# Analyze with all agents
outputs = [
    signal_agent.analyze(market_data),
    ml_agent.analyze(market_data)
]

# Make final decision
decision = decision_agent.analyze(outputs)
```

## اصول کد تمیز که رعایت شده

### 1. Single Responsibility Principle (SRP)
- هر کلاس یک مسئولیت دارد
- `TwelveDataClient`: فقط ارتباط با API
- `SignalAgent`: فقط تحلیل تکنیکال
- `DecisionAgent`: فقط تصمیم‌گیری

### 2. Open/Closed Principle (OCP)
- سیستم برای توسعه باز و برای تغییر بسته است
- Agent های جدید بدون تغییر کد قبلی اضافه می‌شوند
- از طریق inheritance از `BaseAgent`

### 3. Dependency Inversion Principle (DIP)
- وابستگی به abstractions نه concrete classes
- همه agents از `BaseAgent` ارث می‌برند
- `DecisionAgent` با `AgentOutput` کار می‌کند نه با agent مشخص

### 4. Interface Segregation
- Interfaces کوچک و مشخص
- `BaseAgent.analyze()` متد واحد برای همه
- `AgentOutput` فرمت استاندارد خروجی

### 5. کپسوله‌سازی (Encapsulation)
- متدهای داخلی با `_` مشخص شده‌اند
- داده‌های حساس در config جدا شده
- API key در `.env` نگهداری می‌شود

### 6. مدیریت خطا (Error Handling)
- Exception های سفارشی: `TwelveDataAPIError`
- Logging مناسب در تمام سطوح
- Graceful degradation (اگر agent خاموش باشد)

### 7. تست‌پذیری (Testability)
- Dependency injection در constructors
- متدهای کوچک و قابل تست
- Mock کردن API client آسان است

## پترن‌های طراحی استفاده شده

### 1. Strategy Pattern
هر Agent یک استراتژی تحلیل مختلف است:
```python
# Different strategies for analysis
signal_agent = SignalAgent()    # Technical strategy
ml_agent = MLAgent()            # ML strategy
sentiment_agent = SentimentAgent()  # Sentiment strategy
```

### 2. Factory Pattern (آماده برای استفاده)
```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str):
        if agent_type == "signal":
            return SignalAgent()
        elif agent_type == "ml":
            return MLAgent()
        # ...
```

### 3. Observer Pattern (برای آینده)
می‌توان برای real-time updates استفاده کرد.

## نکات مهم برای توسعه

### Configuration Management
- همه تنظیمات در `config/settings.py`
- از environment variables استفاده کنید
- برای production از `.env.production` استفاده کنید

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# در هر متد مهم
logger.info("Starting analysis...")
logger.warning("Low confidence signal")
logger.error("API connection failed")
```

### Type Hints
همیشه type hints استفاده کنید:
```python
def analyze(self, data: MarketData) -> AgentOutput:
    pass
```

### Docstrings
برای تمام کلاس‌ها و متدهای public:
```python
def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index.
    
    Args:
        prices: List of closing prices
        period: RSI period (default: 14)
        
    Returns:
        RSI value between 0 and 100
    """
```

## تست کردن

### Unit Tests (آینده)
```python
# tests/test_signal_agent.py
import unittest
from agents import SignalAgent
from data_layer import MarketData, OHLCV

class TestSignalAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SignalAgent()
    
    def test_analyze_with_valid_data(self):
        # Create mock data
        data = self._create_mock_data()
        
        # Analyze
        result = self.agent.analyze(data)
        
        # Assertions
        self.assertIsNotNone(result.signal)
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 1)
```

## Performance Optimization

### Caching (آینده)
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(symbol: str, interval: str):
    return client.get_time_series(symbol, interval)
```

### Async Operations (آینده)
```python
import asyncio

async def analyze_async(self, data):
    # Async analysis
    pass
```

## نکات امنیتی

1. **هرگز API key را commit نکنید**
2. از `.gitignore` برای `.env` استفاده کنید
3. برای production از secrets management استفاده کنید
4. Input validation در همه جا
5. Rate limiting برای API calls

## مثال: اضافه کردن Sentiment Agent

```python
# agents/sentiment/sentiment_agent.py

from agents.base import BaseAgent, AgentOutput, AgentType
import requests

class SentimentAgent(BaseAgent):
    """Analyzes market sentiment from news and social media."""
    
    def __init__(self, news_api_key: str):
        super().__init__(AgentType.SENTIMENT, "Sentiment Agent")
        self.api_key = news_api_key
    
    def analyze(self, data) -> AgentOutput:
        """Analyze sentiment from news."""
        if not self.enabled:
            return self._disabled_output()
        
        # Fetch news
        news = self._fetch_gold_news()
        
        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(news)
        
        # Convert to signal (-1 to 1)
        signal = self._normalize_sentiment(sentiment_score)
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=signal,
            confidence=0.6,
            metadata={
                "news_count": len(news),
                "sentiment_score": sentiment_score
            }
        )
    
    def _fetch_gold_news(self):
        """Fetch gold-related news."""
        # Implement news fetching
        pass
    
    def _analyze_sentiment(self, news):
        """Analyze sentiment of news articles."""
        # Implement sentiment analysis
        pass
```

## Resources

- [Twelve Data API Docs](https://twelvedata.com/docs)
- [Technical Analysis Library](https://technical-analysis-library-in-python.readthedocs.io/)
- Clean Code by Robert C. Martin
- Design Patterns by Gang of Four

## توسعه‌های آینده پیشنهادی

1. **Backtesting Module**: تست استراتژی روی داده‌های تاریخی
2. **Real-time Streaming**: دریافت real-time data
3. **Portfolio Management**: مدیریت چند نماد
4. **Risk Management**: محاسبه position size و stop loss
5. **Web Dashboard**: داشبورد تحت وب برای نمایش
6. **Database Integration**: ذخیره‌سازی نتایج در دیتابیس
7. **Notification System**: ارسال اعلان‌ها (email, SMS, Telegram)

## سوالات متداول

**Q: چطور می‌توانم نماد دیگری غیر از طلا تحلیل کنم؟**
```python
system.run_analysis(symbol="BTC/USD", interval="1h")
```

**Q: چطور threshold های تصمیم‌گیری را تغییر دهم؟**
```python
decision_agent.set_thresholds(strong=0.8, medium=0.6)
```

**Q: چطور agent خاصی را غیرفعال کنم؟**
```python
signal_agent.disable()
# یا
if not signal_agent.is_enabled():
    pass
```

**Q: چطور نتایج را ذخیره کنم؟**
```python
from examples.advanced_usage import AdvancedTradingSystem

system = AdvancedTradingSystem()
result = system.run_with_custom_agents()
system.save_results(result, "my_analysis.json")
```
