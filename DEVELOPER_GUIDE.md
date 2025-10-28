# 👨‍💻 Developer Guide - Gold Trading System

**Version:** 2.1.0  
**Last Updated:** October 28, 2025

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Development Workflow](#development-workflow)
6. [Testing Guidelines](#testing-guidelines)
7. [Common Development Tasks](#common-development-tasks)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

---

## Getting Started

### Prerequisites

Before starting development, ensure you have:

- **Python 3.13+** installed
- **Git** for version control
- **Docker** (optional, for containerized development)
- **VS Code** or **PyCharm** (recommended IDEs)
- **Twelve Data API Key** (get free key at https://twelvedata.com/)

### Quick Start (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/najafirezawork/gold-trading-system.git
cd gold-trading-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your TWELVE_DATA_API_KEY

# 5. Run tests to verify setup
python test_signal_agent.py

# 6. Run the main application
python main.py
```

---

## Development Environment Setup

### IDE Configuration

#### VS Code Setup

**Recommended Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "visualstudioexptteam.vscodeintellicode"
  ]
}
```

**Settings (.vscode/settings.json):**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

#### PyCharm Setup

1. **Configure Python Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Add your virtual environment

2. **Enable Type Checking:**
   - Settings → Editor → Inspections
   - Enable "Python → Type Checking"

3. **Configure Code Style:**
   - Settings → Editor → Code Style → Python
   - Set line length to 88 (Black standard)

### Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
TWELVE_DATA_API_KEY=your_api_key_here

# Trading Configuration
SYMBOL=XAU/USD
INTERVAL=1h
INITIAL_CAPITAL=10000

# System Configuration
LOG_LEVEL=INFO
ENABLE_CACHING=true
CACHE_TTL=300

# ML Configuration
ML_MODEL_PATH=./models/gold_ml_model.pkl
FEATURE_COUNT=70

# Backtesting Configuration
BACKTEST_START_DATE=2023-01-01
BACKTEST_END_DATE=2024-12-31
```

---

## Project Structure

```
gold-trading-system/
│
├── agents/                      # Agent implementations
│   ├── base/                    # Base agent classes
│   │   ├── __init__.py
│   │   └── agent.py            # BaseAgent, AgentOutput, AgentType
│   ├── signal/                  # Technical analysis agent
│   │   ├── __init__.py
│   │   ├── signal_agent.py     # Main signal agent
│   │   └── indicators.py       # Technical indicators
│   ├── ml/                      # Machine learning agent
│   │   ├── __init__.py
│   │   ├── ml_agent.py         # ML prediction agent
│   │   ├── feature_engineer.py # Feature extraction
│   │   ├── feature_selector.py # Feature selection
│   │   └── models.py           # ML model wrappers
│   ├── decision/                # Decision making agent
│   │   ├── __init__.py
│   │   └── decision_agent.py   # Signal aggregation
│   ├── risk/                    # Risk management
│   │   └── risk_management_agent.py
│   └── meta_agent.py            # Main orchestrator
│
├── data_layer/                  # Data access layer
│   ├── __init__.py
│   ├── client.py               # API client (Twelve Data)
│   └── models.py               # Data models (OHLCV, MarketData)
│
├── backtesting/                 # Backtesting engine
│   ├── __init__.py
│   ├── engine.py               # Backtest execution engine
│   ├── strategy.py             # Base strategy interface
│   ├── strategies.py           # Simple strategies
│   ├── advanced_strategies.py  # Advanced strategies
│   ├── metrics.py              # Performance metrics
│   ├── models.py               # Trade, BacktestResult models
│   └── regime_detector.py      # Market regime detection
│
├── config/                      # Configuration management
│   ├── __init__.py
│   └── settings.py             # Pydantic settings
│
├── models/                      # Trained ML models
│   └── gold_ml_model.pkl       # Serialized model
│
├── results/                     # Test and backtest results
│   ├── signal_agent_test_results.json
│   ├── signal_agent_test_report.html
│   └── backtest_results.json
│
├── tests/                       # Test files
│   ├── test_signal_agent.py
│   ├── test_fibonacci.py
│   └── show_fibonacci.py
│
├── docs/                        # Documentation
│   ├── SYSTEM_ARCHITECTURE.md  # System architecture
│   ├── DEVELOPER_GUIDE.md      # This file
│   ├── API_REFERENCE.md        # API documentation
│   └── DEPLOYMENT_GUIDE.md     # Deployment instructions
│
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker compose configuration
└── README.md                    # Project readme
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

#### Formatting

- **Line Length:** 88 characters (Black default)
- **Indentation:** 4 spaces
- **Quotes:** Double quotes for strings
- **Imports:** Grouped and sorted (isort)

```python
# Good
from typing import List, Optional
import pandas as pd
from agents.base import BaseAgent, AgentOutput

# Bad
from agents.base import *
import pandas as pd, numpy as np
```

#### Naming Conventions

```python
# Classes: PascalCase
class SignalAgent:
    pass

# Functions/Methods: snake_case
def calculate_moving_average(prices, period):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_TIMEOUT = 30

# Private: Leading underscore
def _internal_helper(self):
    pass

# Variables: snake_case
current_price = 1234.56
indicator_values = []
```

#### Type Hints

**Always use type hints** for function signatures:

```python
from typing import List, Optional, Dict, Any

def calculate_rsi(
    prices: List[float],
    period: int = 14
) -> Optional[float]:
    """
    Calculate Relative Strength Index.
    
    Args:
        prices: List of price values
        period: RSI period (default: 14)
    
    Returns:
        RSI value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    # Implementation
    return rsi_value
```

#### Docstrings

Use **Google-style docstrings**:

```python
def analyze_market(
    data: MarketData,
    lookback: int = 200
) -> AgentOutput:
    """
    Analyze market data and generate trading signal.
    
    This function processes OHLCV data, calculates technical indicators,
    and produces a trading signal with confidence score.
    
    Args:
        data: Market data containing OHLCV candles
        lookback: Number of periods to analyze (default: 200)
    
    Returns:
        AgentOutput containing:
            - signal: Trading signal (-1 to 1)
            - confidence: Confidence score (0 to 1)
            - metadata: Additional analysis details
    
    Raises:
        ValueError: If data is insufficient or invalid
        APIError: If external API call fails
    
    Example:
        >>> data = client.get_time_series("XAU/USD", "1h", 200)
        >>> output = analyze_market(data)
        >>> print(f"Signal: {output.signal:.2f}")
        Signal: 0.25
    """
    pass
```

### Code Quality Tools

#### Black (Code Formatter)

```bash
# Format all Python files
black .

# Check formatting without modifying
black --check .
```

#### isort (Import Sorter)

```bash
# Sort imports
isort .

# Check import order
isort --check-only .
```

#### Pylint (Linter)

```bash
# Lint entire project
pylint agents/ data_layer/ backtesting/

# Lint specific file
pylint agents/signal/signal_agent.py
```

#### mypy (Type Checker)

```bash
# Check type hints
mypy agents/ data_layer/ backtesting/
```

---

## Development Workflow

### Git Workflow

We use **Git Flow** branching model:

```
main (production)
  │
  ├─ develop (development)
  │   │
  │   ├─ feature/new-indicator
  │   ├─ feature/ml-improvements
  │   └─ bugfix/api-timeout
  │
  └─ hotfix/critical-bug
```

#### Creating a Feature Branch

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/add-new-indicator

# Make changes and commit
git add .
git commit -m "feat: Add Stochastic Oscillator indicator"

# Push to remote
git push origin feature/add-new-indicator
```

#### Commit Message Convention

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(signal): Add Stochastic Oscillator indicator"
git commit -m "fix(ml): Resolve feature scaling issue"
git commit -m "docs(api): Update API reference documentation"
git commit -m "test(backtest): Add tests for new strategy"
```

### Pull Request Process

1. **Create PR** from feature branch to `develop`
2. **Fill PR template** with description and checklist
3. **Ensure CI passes** (tests, linting)
4. **Request review** from at least one team member
5. **Address feedback** and update PR
6. **Merge** after approval (squash and merge)

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings

## Testing
Describe testing performed

## Screenshots (if applicable)
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_indicators.py
│   ├── test_signal_agent.py
│   └── test_ml_agent.py
├── integration/             # Integration tests
│   ├── test_api_client.py
│   └── test_agent_pipeline.py
└── e2e/                     # End-to-end tests
    └── test_trading_flow.py
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from agents.signal import SignalAgent
from data_layer.models import MarketData, OHLCV

def test_signal_agent_basic():
    """Test basic signal agent functionality."""
    # Arrange
    agent = SignalAgent()
    data = create_test_market_data()
    
    # Act
    output = agent.analyze(data)
    
    # Assert
    assert -1 <= output.signal <= 1
    assert 0 <= output.confidence <= 1
    assert output.agent_type.value == "signal"

def test_signal_agent_insufficient_data():
    """Test error handling with insufficient data."""
    agent = SignalAgent()
    data = create_test_market_data(count=5)  # Too few candles
    
    with pytest.raises(ValueError, match="Insufficient data"):
        agent.analyze(data)

@pytest.mark.parametrize("rsi_value,expected_signal", [
    (25, 0.5),   # Oversold → Buy
    (75, -0.5),  # Overbought → Sell
    (50, 0.0),   # Neutral → Hold
])
def test_rsi_signal_generation(rsi_value, expected_signal):
    """Test RSI-based signal generation."""
    agent = SignalAgent()
    # Mock RSI value
    agent._mock_rsi = rsi_value
    
    output = agent.analyze(create_test_market_data())
    
    assert abs(output.signal - expected_signal) < 0.1
```

#### Integration Test Example

```python
def test_full_analysis_pipeline():
    """Test complete analysis pipeline."""
    # Arrange
    client = TwelveDataClient()
    signal_agent = SignalAgent()
    ml_agent = MLAgent()
    decision_agent = DecisionAgent()
    
    # Act
    data = client.get_time_series("XAU/USD", "1h", 200)
    signal_output = signal_agent.analyze(data)
    ml_output = ml_agent.analyze(data)
    decision = decision_agent.analyze([signal_output, ml_output])
    
    # Assert
    assert decision.signal is not None
    assert decision.confidence > 0
    assert "decision" in decision.metadata
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_signal_agent.py

# Run with coverage
python -m pytest --cov=agents --cov-report=html

# Run with verbose output
python -m pytest -v

# Run only fast tests (skip slow)
python -m pytest -m "not slow"
```

### Test Coverage Goals

- **Minimum:** 80% overall coverage
- **Critical paths:** 95% coverage
- **New code:** 100% coverage

```bash
# Generate coverage report
pytest --cov=agents --cov=data_layer --cov-report=html
open htmlcov/index.html
```

---

## Common Development Tasks

### Adding a New Technical Indicator

**Step 1:** Implement the indicator calculation

```python
# In agents/signal/indicators.py
class TechnicalIndicators:
    @staticmethod
    def calculate_stochastic(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> tuple[float, float]:
        """
        Calculate Stochastic Oscillator.
        
        Returns:
            (%K, %D) tuple
        """
        # Implementation
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        current_close = closes[-1]
        
        k = 100 * (current_close - lowest_low) / (highest_high - lowest_low)
        d = sum([k for _ in range(3)]) / 3  # Simplified
        
        return k, d
```

**Step 2:** Integrate in Signal Agent

```python
# In agents/signal/signal_agent.py
def _calculate_indicators(self, data: MarketData) -> dict:
    indicators = {}
    
    # Existing indicators...
    
    # New indicator
    k, d = TechnicalIndicators.calculate_stochastic(
        highs=data.high,
        lows=data.low,
        closes=data.close,
        period=14
    )
    indicators['stochastic_k'] = k
    indicators['stochastic_d'] = d
    
    return indicators
```

**Step 3:** Update signal generation logic

```python
def _generate_signal(self, indicators: dict) -> tuple[float, float]:
    # Existing logic...
    
    # Add stochastic contribution
    stoch_signal = 0.0
    if indicators['stochastic_k'] < 20:
        stoch_signal = 0.3  # Oversold
    elif indicators['stochastic_k'] > 80:
        stoch_signal = -0.3  # Overbought
    
    # Update combined signal
    combined_signal = (
        existing_signal * 0.7 +
        stoch_signal * 0.3
    )
    
    return combined_signal, confidence
```

**Step 4:** Add tests

```python
# In tests/test_indicators.py
def test_stochastic_calculation():
    highs = [100, 102, 101, 103, 104]
    lows = [95, 96, 97, 98, 99]
    closes = [98, 99, 100, 101, 102]
    
    k, d = TechnicalIndicators.calculate_stochastic(
        highs, lows, closes, period=5
    )
    
    assert 0 <= k <= 100
    assert 0 <= d <= 100
```

### Adding a New Agent

**Step 1:** Create agent class

```python
# In agents/sentiment/sentiment_agent.py
from agents.base import BaseAgent, AgentType, AgentOutput

class SentimentAgent(BaseAgent):
    """Analyze market sentiment from news and social media."""
    
    def __init__(self):
        super().__init__(AgentType.SENTIMENT, name="sentiment_agent")
        self.sentiment_api = SentimentAPI()
    
    def analyze(self, data: MarketData) -> AgentOutput:
        """
        Analyze sentiment and generate signal.
        
        Args:
            data: Market data (used for timestamp)
        
        Returns:
            AgentOutput with sentiment-based signal
        """
        if not self.enabled:
            return self._disabled_output()
        
        # Fetch sentiment data
        sentiment_score = self.sentiment_api.get_sentiment(
            symbol=data.symbol,
            timestamp=data.data[-1].datetime
        )
        
        # Convert to signal
        signal = self._sentiment_to_signal(sentiment_score)
        confidence = abs(sentiment_score)
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=signal,
            confidence=confidence,
            metadata={
                "sentiment_score": sentiment_score,
                "source": "twitter,reddit,news"
            }
        )
    
    def _sentiment_to_signal(self, score: float) -> float:
        """Convert sentiment score to trading signal."""
        return max(-1.0, min(1.0, score))
```

**Step 2:** Register in Meta Agent

```python
# In agents/meta_agent.py
from agents.sentiment import SentimentAgent

class MetaAgent:
    def __init__(self):
        self.agents = [
            SignalAgent(),
            MLAgent(),
            SentimentAgent(),  # Add new agent
            DecisionAgent()
        ]
```

**Step 3:** Add tests

```python
# In tests/test_sentiment_agent.py
def test_sentiment_agent():
    agent = SentimentAgent()
    data = create_test_market_data()
    
    output = agent.analyze(data)
    
    assert output.agent_type == AgentType.SENTIMENT
    assert -1 <= output.signal <= 1
```

### Training ML Models

```python
# scripts/train_model.py
from agents.ml import MLAgent
from data_layer import TwelveDataClient

def train_and_save_model():
    """Train ML model and save to disk."""
    # Fetch historical data
    client = TwelveDataClient()
    data = client.get_time_series("XAU/USD", "1h", 5000)
    
    # Prepare features and labels
    agent = MLAgent()
    X, y = agent.prepare_training_data(data)
    
    # Train model
    agent.train(X, y)
    
    # Save model
    agent.save_model("models/gold_ml_model.pkl")
    
    # Evaluate
    metrics = agent.evaluate(X_test, y_test)
    print(f"Model Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")

if __name__ == "__main__":
    train_and_save_model()
```

---

## Troubleshooting

### Common Issues

#### 1. API Rate Limit Exceeded

**Problem:** `APIError: Rate limit exceeded (8 calls/minute)`

**Solution:**
```python
# Increase delay between calls
client = TwelveDataClient(rate_limit_delay=10)

# Or use caching
client = TwelveDataClient(enable_cache=True, cache_ttl=300)
```

#### 2. Insufficient Data for Indicators

**Problem:** `ValueError: Insufficient data for indicator calculation`

**Solution:**
```python
# Ensure minimum data points
MIN_DATA_POINTS = 200
data = client.get_time_series("XAU/USD", "1h", MIN_DATA_POINTS)

if len(data) < MIN_DATA_POINTS:
    raise ValueError(f"Need {MIN_DATA_POINTS} data points, got {len(data)}")
```

#### 3. Model Loading Errors

**Problem:** `ModelNotFoundError: ML model file not found`

**Solution:**
```bash
# Download pre-trained model
wget https://example.com/models/gold_ml_model.pkl -O models/gold_ml_model.pkl

# Or train new model
python scripts/train_model.py
```

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or via environment
# LOG_LEVEL=DEBUG python main.py
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile code
profiler = cProfile.Profile()
profiler.enable()

# Your code here
agent.analyze(data)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

---

## Contributing

### Contribution Workflow

1. **Fork** the repository
2. **Create** feature branch
3. **Make** changes with tests
4. **Ensure** all checks pass
5. **Submit** pull request
6. **Address** review feedback
7. **Merge** (maintainers only)

### Code Review Checklist

**For Authors:**
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests passing
- [ ] No linting errors
- [ ] Performance considered
- [ ] Security reviewed

**For Reviewers:**
- [ ] Code is readable and maintainable
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Tests are adequate
- [ ] Documentation is clear
- [ ] No security issues
- [ ] Performance is acceptable

### Communication Channels

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions and ideas
- **Pull Requests:** Code contributions and reviews

---

## Additional Resources

### Documentation

- [System Architecture](SYSTEM_ARCHITECTURE.md) - Comprehensive architecture guide
- [API Reference](API_REFERENCE.md) - Detailed API documentation
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions

### External Resources

- [Python Official Docs](https://docs.python.org/3/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Twelve Data API](https://twelvedata.com/docs)
- [Technical Analysis Tutorial](https://www.investopedia.com/technical-analysis-4689657)

---

**Happy Coding! 🚀**

For questions or support, please open an issue on GitHub.
