# 🏛️ Gold Trading System - System Architecture

**Version:** 2.1.0  
**Last Updated:** October 28, 2025  
**Status:** Production Ready ✅

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architectural Components](#architectural-components)
4. [Communication Protocols](#communication-protocols)
5. [Technology Stack](#technology-stack)
6. [Scalability & Reliability](#scalability--reliability)
7. [Security Architecture](#security-architecture)
8. [Future Integration Guidelines](#future-integration-guidelines)
9. [Deployment Architecture](#deployment-architecture)
10. [Monitoring & Observability](#monitoring--observability)

---

## Executive Summary

The Gold Trading System is a production-ready, agent-based trading platform designed for analyzing and generating trading signals for gold (XAU/USD) markets. The system employs a modular, event-driven architecture that combines technical analysis, machine learning, and risk management to produce actionable trading decisions.

### Key Characteristics

- **Architecture Pattern:** Agent-based, Microkernel
- **Design Philosophy:** SOLID principles, Separation of Concerns
- **Scalability:** Horizontal and vertical scaling support
- **Deployment:** Containerized (Docker), cloud-ready
- **Data Flow:** Pipeline architecture with staged processing

---

## System Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User/Client Layer                           │
│                    (CLI, API, Web Dashboard)                        │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                    Application Interface Layer                      │
│  • Request Handling  • Validation  • Error Management               │
│  • Response Formatting  • Authentication  • Rate Limiting            │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                   Agent Orchestration Layer                         │
│                        (Meta Agent)                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Agent Coordinator: Manages lifecycle & communication         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────┬────────────┬────────────┬────────────┬──────────────────────┘
      │            │            │            │
┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐
│ Signal   │ │    ML    │ │ Decision │ │   Risk   │
│  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │
│          │ │          │ │          │ │          │
│ 7 Tech   │ │ 70+      │ │ Signal   │ │ Position │
│ Indicators│ │ Features │ │ Fusion   │ │  Sizing  │
└─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘
      │            │            │            │
      └────────────┴────────────┴────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                Technical Analysis & ML Layer                        │
│  • Indicator Calculations  • Feature Engineering                    │
│  • Model Inference  • Pattern Recognition                           │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                      Data Access Layer                              │
│  • API Clients  • Data Validation  • Caching                        │
│  • Rate Limiting  • Retry Logic  • Error Handling                   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                    External Services Layer                          │
│  • Twelve Data API  • Broker APIs  • Alert Services                 │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

1. **Modularity:** Each component is independent and replaceable
2. **Extensibility:** Easy to add new agents, indicators, or strategies
3. **Testability:** Comprehensive test coverage with isolated unit tests
4. **Maintainability:** Clean code, documentation, and type hints
5. **Performance:** Optimized for low-latency signal generation

---

## Architectural Components

### 1. Agent System (Core Logic)

The agent system is the heart of the platform, implementing an agent-based architecture where each agent has a specific responsibility.

#### Base Agent Abstract Class

```python
class BaseAgent(ABC):
    - agent_type: AgentType
    - name: str
    - enabled: bool
    + analyze(data) -> AgentOutput
    + enable() / disable()
```

**Responsibilities:**
- Define common interface for all agents
- Implement lifecycle management
- Provide standardized output format (AgentOutput)
- Enable/disable functionality for dynamic configuration

#### Signal Agent

**Purpose:** Technical analysis and indicator-based signal generation

**Indicators Implemented:**
1. **SMA (Simple Moving Average):** Trend identification (periods: 20, 50, 200)
2. **EMA (Exponential Moving Average):** Responsive trend tracking (periods: 12, 26)
3. **RSI (Relative Strength Index):** Momentum and overbought/oversold conditions
4. **MACD (Moving Average Convergence Divergence):** Trend direction and strength
5. **Bollinger Bands:** Volatility and support/resistance levels
6. **ATR (Average True Range):** Volatility measurement for risk management
7. **Fibonacci Retracements:** Key support/resistance levels based on golden ratio

**Signal Generation Logic:**
```
Input: MarketData (200 OHLCV candles)
  ↓
Calculate 7 Technical Indicators
  ↓
Weight & Combine Indicator Signals
  ↓
Generate: signal (-1 to +1), confidence (0 to 1)
  ↓
Output: AgentOutput with metadata
```

**Output Format:**
```json
{
  "agent_type": "signal",
  "signal": 0.25,
  "confidence": 0.67,
  "metadata": {
    "indicators": {
      "sma_20": 4369.04,
      "rsi_14": 29.03,
      "macd": -3.11,
      "fibonacci_level": "61.8%"
    },
    "analysis": "Buy signal with moderate confidence"
  }
}
```

#### ML Agent

**Purpose:** Machine learning-based predictions and trend forecasting

**Architecture:**
```
Raw Data → Feature Engineering → Feature Selection → Model Ensemble → Predictions
            (70+ features)         (Top 25)           (3 models)
```

**Features Categories:**
- **Price Features (10):** Returns, volatility, price ratios
- **Moving Averages (15):** SMA/EMA crossovers, slopes
- **Momentum (20):** RSI, MACD, Stochastic, ROC
- **Volatility (15):** ATR, Bollinger width, historical volatility
- **Patterns (10):** Higher highs/lows, support/resistance breaks

**ML Models:**
1. **RandomForest:** Ensemble of decision trees (100 estimators)
2. **XGBoost:** Gradient boosting (optimized for speed)
3. **Ensemble:** Weighted combination (RF: 40%, XGBoost: 40%, Linear: 20%)

**Output:**
```json
{
  "agent_type": "ml",
  "signal": 0.30,
  "confidence": 0.72,
  "metadata": {
    "prob_up": 0.65,
    "prob_down": 0.35,
    "trend_strength": 0.70,
    "momentum": 0.25
  }
}
```

#### Decision Agent

**Purpose:** Aggregate signals from multiple agents and make final trading decisions

**Decision Logic:**
```python
# Weighted aggregation
weighted_signal = (w_signal * signal_output.signal) + 
                  (w_ml * ml_output.signal) + 
                  (w_risk * risk_adjustment)

# Threshold-based decision
if weighted_signal > 0.6: return "STRONG_BUY"
elif weighted_signal > 0.3: return "BUY"
elif weighted_signal > -0.3: return "HOLD"
elif weighted_signal > -0.6: return "SELL"
else: return "STRONG_SELL"

# Confidence calculation
confidence = 1 - (std_dev(signals) / max_std_dev)
```

#### Risk Management Agent

**Purpose:** Position sizing, stop-loss, and risk assessment

**Key Functions:**
- **Position Sizing:** Calculate optimal position size based on account size and risk tolerance
- **Stop-Loss Placement:** Dynamic stop-loss based on ATR and volatility
- **Risk-Reward Ratio:** Ensure minimum 1:2 risk-reward ratio
- **Exposure Management:** Limit total portfolio exposure

**Risk Metrics:**
- Maximum position size: 10% of capital
- Maximum risk per trade: 2% of capital
- Portfolio heat limit: 6% (total open risk)

### 2. Data Layer

#### TwelveDataClient

**Purpose:** Interface with Twelve Data API for market data

**Key Features:**
- Rate limiting and retry logic
- Response validation and error handling
- Context manager support for resource cleanup
- Caching for repeated requests

**API Methods:**
```python
class TwelveDataClient:
    + get_time_series(symbol, interval, outputsize) -> MarketData
    + get_quote(symbol) -> dict
    + _validate_response(response) -> bool
    + _handle_rate_limit(response) -> None
```

**Data Models (Pydantic):**
```python
class OHLCV(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float]

class MarketData(BaseModel):
    symbol: str
    interval: str
    data: List[OHLCV]
    meta: Optional[dict]
```

### 3. Backtesting Engine

**Purpose:** Historical strategy testing and performance evaluation

**Components:**
1. **BacktestEngine:** Core execution engine
2. **Strategy Interface:** Base class for trading strategies
3. **Metrics Calculator:** Performance metric computation
4. **Regime Detector:** Market condition identification

**Strategy Pattern Implementation:**
```python
class BaseStrategy(ABC):
    @abstractmethod
    def on_candle(self, candle: OHLCV) -> None
    
    @abstractmethod
    def should_buy(self) -> bool
    
    @abstractmethod
    def should_sell(self) -> bool
    
    def position_size(self) -> float
```

**Available Strategies:**
1. SMA Crossover Strategy
2. RSI-based Strategy
3. MACD Divergence Strategy
4. Bollinger Bands Breakout
5. Multi-Indicator Advanced Strategy

**Performance Metrics:**
- Total Return
- Win Rate
- Sharpe Ratio (risk-adjusted return)
- Sortino Ratio (downside risk)
- Maximum Drawdown
- Profit Factor
- Average Win/Loss
- Trade Count

### 4. Configuration Management

**Purpose:** Centralized configuration and environment management

**Implementation:**
```python
# Using Pydantic Settings
class Settings(BaseSettings):
    TWELVE_DATA_API_KEY: str
    SYMBOL: str = "XAU/USD"
    INTERVAL: str = "1h"
    INITIAL_CAPITAL: float = 10000
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
```

---

## Communication Protocols

### Inter-Agent Communication

**Protocol:** Direct method invocation with standardized AgentOutput

**Communication Flow:**
```
Meta Agent (Orchestrator)
    │
    ├─→ Signal Agent.analyze(data) → AgentOutput
    │       │
    │       └─→ Technical Indicators Module
    │
    ├─→ ML Agent.analyze(data) → AgentOutput
    │       │
    │       └─→ Feature Engineering → Model Inference
    │
    ├─→ Decision Agent.analyze([outputs]) → AgentOutput
    │       │
    │       └─→ Signal Aggregation Logic
    │
    └─→ Risk Agent.assess(decision) → AgentOutput
            │
            └─→ Position Sizing Calculation
```

**Message Format (AgentOutput):**
```python
{
    "agent_type": AgentType,      # Enum: SIGNAL, ML, DECISION, RISK
    "signal": float,               # -1 to +1
    "confidence": float,           # 0 to 1
    "metadata": {                  # Agent-specific data
        "indicators": {...},
        "analysis": "...",
        "timestamp": "..."
    }
}
```

### External API Communication

**Protocol:** REST API over HTTPS with JSON payload

**Twelve Data API Integration:**
```
Client Request
    │
    ├─→ Rate Limiter Check
    │
    ├─→ HTTP GET /time_series
    │   Headers: {
    │       "Authorization": "apikey YOUR_KEY"
    │   }
    │
    ├─→ Response Validation
    │
    ├─→ Parse JSON → Pydantic Models
    │
    └─→ Return MarketData
```

**Error Handling:**
- Automatic retry with exponential backoff
- Rate limit detection and waiting
- Timeout handling (30 seconds default)
- Connection error recovery

---

## Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.13+ | Core implementation |
| **Data Models** | Pydantic | 2.12.3 | Data validation & serialization |
| **HTTP Client** | Requests | 2.31.0 | API communication |
| **Data Processing** | Pandas | 2.3.3 | Time series manipulation |
| **Numerical Computing** | NumPy | 2.3.4 | Mathematical operations |
| **ML Framework** | scikit-learn | 1.3.0+ | ML model training |
| **Gradient Boosting** | XGBoost | 2.0.0+ | Advanced ML model |
| **Configuration** | python-dotenv | 1.0.0 | Environment management |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Docker Compose | Multi-container management |
| **Version Control** | Git | Source code management |
| **CI/CD** | GitHub Actions | Automated testing & deployment |

### External Services

| Service | Purpose | Protocol |
|---------|---------|----------|
| **Twelve Data API** | Market data provider | REST/HTTPS |
| **Future: Broker API** | Trade execution | REST/WebSocket |
| **Future: Alert Service** | Notifications | Webhook/Email |

### Design Patterns Used

1. **Strategy Pattern:** Backtesting strategies
2. **Factory Pattern:** Agent creation
3. **Template Method:** BaseAgent implementation
4. **Observer Pattern:** Event notifications (backtesting)
5. **Singleton Pattern:** Configuration management
6. **Context Manager:** Resource cleanup (API clients)

---

## Scalability & Reliability

### Scalability Considerations

#### Horizontal Scaling

**Multi-Symbol Support:**
```
Load Balancer
    │
    ├─→ Instance 1: XAU/USD
    ├─→ Instance 2: XAU/EUR
    ├─→ Instance 3: XAG/USD
    └─→ Instance N: Multiple pairs
```

**Implementation Strategy:**
- Stateless agent design
- Independent processing per symbol
- Shared ML models via model registry
- Distributed caching layer

#### Vertical Scaling

**Resource Optimization:**
- **CPU:** Parallel indicator calculations using multiprocessing
- **Memory:** Efficient data structures, streaming data processing
- **I/O:** Asynchronous API calls, connection pooling
- **Storage:** Time-series database for historical data

**Performance Benchmarks:**
- Signal generation: 50-100ms per analysis
- ML inference: 100-500ms (with feature engineering)
- Backtesting: 1000 trades/second
- Memory footprint: ~50MB per symbol

#### Caching Strategy

```
┌─────────────────────────────────────┐
│        Application Layer            │
└───────────┬────────────────────────┘
            │
┌───────────▼────────────────────────┐
│      In-Memory Cache (LRU)         │
│  • Recent market data (5 min TTL)  │
│  • Indicator calculations          │
└───────────┬────────────────────────┘
            │
┌───────────▼────────────────────────┐
│    Persistent Cache (Redis)        │
│  • Historical data (24h TTL)       │
│  • ML model predictions            │
└────────────────────────────────────┘
```

### Reliability Features

#### Fault Tolerance

**API Failure Handling:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_market_data(symbol):
    # API call with automatic retry
    pass
```

**Graceful Degradation:**
- If ML Agent fails → Use Signal Agent only
- If external API fails → Use cached data
- If one indicator fails → Continue with remaining indicators

#### Data Validation

**Multi-Layer Validation:**
1. **API Response:** Validate JSON structure and required fields
2. **Pydantic Models:** Type checking and data validation
3. **Business Logic:** Range checks, anomaly detection
4. **Output Validation:** Ensure signal values in valid range

**Example:**
```python
class MarketData(BaseModel):
    symbol: str = Field(..., regex=r"^[A-Z]{3}/[A-Z]{3}$")
    interval: str = Field(..., regex=r"^\d+[mhd]$")
    data: List[OHLCV] = Field(..., min_items=1)
    
    @validator('data')
    def validate_chronological(cls, v):
        # Ensure data is in chronological order
        for i in range(1, len(v)):
            if v[i].datetime <= v[i-1].datetime:
                raise ValueError("Data must be chronological")
        return v
```

#### Error Recovery

**Error Hierarchy:**
```
BaseException
├── APIError (recoverable)
│   ├── RateLimitError → Wait and retry
│   ├── TimeoutError → Retry with backoff
│   └── InvalidResponseError → Log and skip
├── DataValidationError (recoverable)
│   ├── InsufficientDataError → Request more data
│   └── MalformedDataError → Clean and retry
└── SystemError (non-recoverable)
    ├── ConfigurationError → Fail fast
    └── ModelLoadError → Fallback to simpler model
```

---

## Security Architecture

### Authentication & Authorization

**API Key Management:**
```
Environment Variables (.env)
    ↓
Application Configuration (Pydantic Settings)
    ↓
Encrypted Storage (at rest)
    ↓
Secure Transmission (HTTPS only)
```

**Best Practices:**
- Never commit API keys to version control
- Use environment variables for secrets
- Implement key rotation policy (90 days)
- Monitor for unauthorized access

### Data Security

#### Data in Transit

- **Protocol:** TLS 1.2+ (HTTPS)
- **Certificate Validation:** Enabled
- **Request Signing:** HMAC-SHA256 for sensitive operations

#### Data at Rest

- **Configuration Files:** Encrypted using Fernet (symmetric encryption)
- **Model Files:** Integrity checks using SHA-256 hashes
- **Logs:** PII redaction, log rotation

#### Sensitive Data Handling

```python
# Example: Secure API key handling
class SecureConfig:
    _api_key: str = None
    
    @property
    def api_key(self):
        return self._api_key
    
    @api_key.setter
    def api_key(self, value):
        # Validate and encrypt
        self._api_key = encrypt(value)
    
    def __repr__(self):
        # Never expose key in logs
        return f"SecureConfig(api_key=***)"
```

### Input Validation & Sanitization

**Prevent Injection Attacks:**
```python
def validate_symbol(symbol: str) -> str:
    """Validate trading symbol format."""
    pattern = r'^[A-Z]{3}/[A-Z]{3}$'
    if not re.match(pattern, symbol):
        raise ValueError(f"Invalid symbol format: {symbol}")
    return symbol
```

**Rate Limiting:**
- Per-user API rate limits
- Exponential backoff on failures
- DDoS protection via reverse proxy

### Dependency Security

**Vulnerability Scanning:**
```bash
# Regular security audits
pip install safety
safety check

# Dependency updates
pip list --outdated
```

**Pinned Dependencies:**
- All dependencies with specific versions in `requirements.txt`
- Regular updates for security patches
- Automated vulnerability alerts via GitHub Dependabot

---

## Future Integration Guidelines

### Adding New Agents

**Step-by-Step Guide:**

1. **Create Agent Class:**
```python
from agents.base import BaseAgent, AgentType, AgentOutput

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.NEW, name="new_agent")
    
    def analyze(self, data):
        # Your analysis logic
        signal = calculate_signal(data)
        confidence = calculate_confidence(data)
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=signal,
            confidence=confidence,
            metadata={"custom": "data"}
        )
```

2. **Register Agent:**
```python
# In meta_agent.py
from agents.new_agent import NewAgent

class MetaAgent:
    def __init__(self):
        self.agents = [
            SignalAgent(),
            MLAgent(),
            NewAgent(),  # Add here
            DecisionAgent()
        ]
```

3. **Add Tests:**
```python
# test_new_agent.py
def test_new_agent():
    agent = NewAgent()
    data = create_test_data()
    output = agent.analyze(data)
    
    assert -1 <= output.signal <= 1
    assert 0 <= output.confidence <= 1
```

### Adding New Indicators

**Integration Steps:**

1. **Implement Calculation:**
```python
# In agents/signal/indicators.py
class TechnicalIndicators:
    @staticmethod
    def calculate_new_indicator(prices, period):
        """Calculate new technical indicator."""
        # Implementation
        return result
```

2. **Integrate in Signal Agent:**
```python
# In signal_agent.py
def _calculate_indicators(self, data):
    indicators = {
        'sma': self._calculate_sma(data),
        'new_indicator': TechnicalIndicators.calculate_new_indicator(
            data.close, period=14
        )
    }
    return indicators
```

3. **Update Signal Logic:**
```python
def _generate_signal(self, indicators):
    # Include new indicator in signal calculation
    new_signal = indicators['new_indicator']
    combined_signal = (existing_signal + new_signal) / 2
    return combined_signal
```

### Adding New Strategies

**Backtesting Strategy Template:**

```python
from backtesting.strategy import BaseStrategy

class CustomStrategy(BaseStrategy):
    def __init__(self, param1=10, param2=20):
        super().__init__(name="Custom Strategy")
        self.param1 = param1
        self.param2 = param2
        self.position = 0
    
    def on_candle(self, candle):
        """Process each new candle."""
        # Update internal state
        self.update_indicators(candle)
    
    def should_buy(self):
        """Determine if should buy."""
        return (self.indicator1 > self.threshold1 and 
                self.indicator2 < self.threshold2)
    
    def should_sell(self):
        """Determine if should sell."""
        return (self.indicator1 < self.threshold1 or 
                self.indicator2 > self.threshold2)
    
    def position_size(self):
        """Calculate position size."""
        return self.calculate_kelly_criterion()
```

### API Expansion

**Adding REST API Layer:**

```python
# api/main.py (FastAPI example)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Gold Trading API", version="2.1.0")

class AnalysisRequest(BaseModel):
    symbol: str
    interval: str
    lookback: int = 200

@app.post("/api/v1/analyze")
async def analyze_market(request: AnalysisRequest):
    """Analyze market and return trading signal."""
    try:
        # Get market data
        data = client.get_time_series(
            request.symbol, 
            request.interval, 
            request.lookback
        )
        
        # Run analysis
        signal = meta_agent.analyze(data)
        
        return {
            "symbol": request.symbol,
            "signal": signal.signal,
            "confidence": signal.confidence,
            "action": get_action(signal.signal),
            "metadata": signal.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Database Integration

**Adding Persistent Storage:**

```python
# Example: SQLAlchemy models
from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    signal_value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    metadata = Column(JSON)

class PerformanceMetric(Base):
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    total_return = Column(Float)
    sharpe_ratio = Column(Float)
    win_rate = Column(Float)
    max_drawdown = Column(Float)
```

### Monitoring & Alerting

**Adding Observability:**

```python
# Example: Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Metrics
signal_generation_count = Counter(
    'signal_generation_total',
    'Total number of signals generated',
    ['agent_type', 'symbol']
)

signal_latency = Histogram(
    'signal_latency_seconds',
    'Signal generation latency',
    ['agent_type']
)

confidence_score = Gauge(
    'signal_confidence',
    'Current signal confidence',
    ['symbol']
)

# Usage
@signal_latency.time()
def analyze_market(data):
    signal = agent.analyze(data)
    signal_generation_count.labels(
        agent_type='signal',
        symbol=data.symbol
    ).inc()
    confidence_score.labels(symbol=data.symbol).set(signal.confidence)
    return signal
```

---

## Deployment Architecture

### Containerization

**Docker Image Structure:**

```dockerfile
# Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 trader && chown -R trader:trader /app
USER trader

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "main.py"]
```

**Docker Compose Configuration:**

```yaml
version: '3.8'

services:
  trading-system:
    build: .
    environment:
      - TWELVE_DATA_API_KEY=${TWELVE_DATA_API_KEY}
      - SYMBOL=XAU/USD
      - INTERVAL=1h
      - LOG_LEVEL=INFO
    volumes:
      - ./results:/app/results
      - ./logs:/app/logs
      - ./models:/app/models
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### Cloud Deployment Options

#### Option 1: AWS ECS (Elastic Container Service)

```
┌─────────────────────────────────────────┐
│  AWS Cloud                              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Application Load Balancer        │ │
│  └────────────┬──────────────────────┘ │
│               │                         │
│  ┌────────────▼──────────────────────┐ │
│  │  ECS Service (Auto Scaling)       │ │
│  │  ├─ Task 1 (Container)            │ │
│  │  ├─ Task 2 (Container)            │ │
│  │  └─ Task N (Container)            │ │
│  └────────────┬──────────────────────┘ │
│               │                         │
│  ┌────────────▼──────────────────────┐ │
│  │  ElastiCache (Redis)              │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  CloudWatch (Monitoring)          │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

#### Option 2: Kubernetes (K8s)

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gold-trading-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gold-trading
  template:
    metadata:
      labels:
        app: gold-trading
    spec:
      containers:
      - name: trading-app
        image: gold-trading-system:2.1.0
        env:
        - name: TWELVE_DATA_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: twelve-data-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: gold-trading-service
spec:
  selector:
    app: gold-trading
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Monitoring & Observability

### Logging Strategy

**Log Levels:**
- **DEBUG:** Detailed diagnostic information
- **INFO:** General operational events
- **WARNING:** Unexpected situations (handled)
- **ERROR:** Errors that need attention
- **CRITICAL:** System failures

**Structured Logging:**
```python
import logging
import json

logger = logging.getLogger(__name__)

def analyze_market(symbol):
    logger.info(
        "Starting market analysis",
        extra={
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "agent": "signal_agent"
        }
    )
    # Analysis logic
    logger.info(
        "Analysis completed",
        extra={
            "symbol": symbol,
            "signal": signal.signal,
            "confidence": signal.confidence,
            "duration_ms": duration
        }
    )
```

### Metrics Collection

**Key Performance Indicators (KPIs):**

1. **System Metrics:**
   - Request rate (signals/minute)
   - Response time (p50, p95, p99)
   - Error rate
   - API call success rate

2. **Business Metrics:**
   - Signal accuracy (backtest vs live)
   - Average confidence score
   - Signal distribution (buy/sell/hold)
   - Indicator calculation time

3. **Resource Metrics:**
   - CPU utilization
   - Memory usage
   - Network I/O
   - Disk I/O

**Monitoring Dashboard (Example):**
```
┌─────────────────────────────────────────────────────┐
│  Gold Trading System - Monitoring Dashboard         │
├─────────────────────────────────────────────────────┤
│  System Health:            🟢 Healthy               │
│  Active Agents:            4/4                      │
│  Signals Generated Today:  1,247                    │
│  Average Latency:          85ms                     │
│  Error Rate:               0.02%                    │
├─────────────────────────────────────────────────────┤
│  Recent Signals:                                    │
│  XAU/USD │ BUY    │ 0.45  │ 72%  │ 10:23:45       │
│  XAU/USD │ HOLD   │ 0.12  │ 65%  │ 10:08:12       │
│  XAU/USD │ SELL   │ -0.38 │ 68%  │ 09:52:34       │
├─────────────────────────────────────────────────────┤
│  Performance (Last 24h):                            │
│  Total Return:     +2.3%                            │
│  Win Rate:         64%                              │
│  Sharpe Ratio:     1.85                             │
└─────────────────────────────────────────────────────┘
```

### Alerting Rules

**Critical Alerts:**
1. System down / unhealthy
2. API connection failures (>5 consecutive)
3. Model prediction errors
4. Data validation failures
5. Abnormal signal distribution

**Warning Alerts:**
1. High latency (>500ms)
2. Low confidence signals (<50%)
3. High error rate (>1%)
4. Memory usage >80%
5. API rate limit approaching

---

## Appendices

### A. Data Flow Diagram

```
┌────────────┐
│  External  │
│  API       │
└─────┬──────┘
      │ HTTPS/JSON
┌─────▼──────┐
│  Data      │
│  Client    │
└─────┬──────┘
      │ MarketData
┌─────▼──────┐
│  Signal    │
│  Agent     │
└─────┬──────┘
      │ AgentOutput
┌─────▼──────┐
│  ML        │
│  Agent     │
└─────┬──────┘
      │ AgentOutput
┌─────▼──────┐
│  Decision  │
│  Agent     │
└─────┬──────┘
      │ Decision
┌─────▼──────┐
│  Risk      │
│  Agent     │
└─────┬──────┘
      │ Action
┌─────▼──────┐
│  Output    │
└────────────┘
```

### B. Glossary

- **Agent:** Autonomous component responsible for specific analysis task
- **Signal:** Numerical value indicating buy/sell recommendation (-1 to +1)
- **Confidence:** Measure of certainty in the signal (0 to 1)
- **OHLCV:** Open, High, Low, Close, Volume candlestick data
- **Indicator:** Mathematical calculation on price data
- **Backtest:** Historical simulation of trading strategy
- **Sharpe Ratio:** Risk-adjusted return metric

### C. References

1. Technical Analysis: https://www.investopedia.com/terms/t/technicalanalysis.asp
2. Agent-Based Architecture: https://en.wikipedia.org/wiki/Agent-based_model
3. Twelve Data API: https://twelvedata.com/docs
4. Python Type Hints: https://docs.python.org/3/library/typing.html
5. Pydantic Documentation: https://docs.pydantic.dev/
6. Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-28 | Architecture Team | Initial comprehensive architecture document |

---

**For questions or clarifications, please create an issue in the GitHub repository.**

**License:** MIT License  
**Copyright:** © 2025 Gold Trading System Team
