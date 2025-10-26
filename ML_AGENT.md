# ML Agent Documentation

## Overview

ML Agent از Machine Learning برای پیش‌بینی جهت حرکت قیمت طلا استفاده می‌کند.

## Features

### 1. Feature Engineering (70+ Features)
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ATR
- **Moving Averages**: SMA, EMA با periods مختلف (5, 10, 20, 50)
- **Price Patterns**: Doji, Hammer, Engulfing patterns
- **Statistical**: Volatility, Momentum, Z-score
- **Time-based**: Hour, day of week, cyclical encoding

### 2. ML Models
- **Random Forest**: 100 trees, max_depth=10
- **XGBoost**: 100 estimators, max_depth=6
- **Ensemble**: Voting از multiple models

### 3. Prediction
- **Binary Classification**: UP (1) یا DOWN (0)
- **Probability**: احتمال هر کلاس
- **Confidence**: میزان اطمینان پیش‌بینی

## Usage

### Training

```python
from data_layer.client import TwelveDataClient
from agents.ml.ml_agent import MLAgent

# دریافت داده تاریخی
client = TwelveDataClient(api_key="your_key")
market_data = client.get_time_series("XAU/USD", "1h", 2000)

# ساخت و training
ml_agent = MLAgent(
    confidence_threshold=0.6,
    model_path="models/gold_ml_model.pkl"
)

metrics = ml_agent.train(
    market_data=market_data,
    val_split=0.2,
    save_model=True
)
```

### Prediction

```python
# بارگذاری model
ml_agent = MLAgent(model_path="models/gold_ml_model.pkl")
ml_agent.load_model()

# پیش‌بینی
market_data = client.get_time_series("XAU/USD", "1h", 200)
output = ml_agent.analyze(market_data)

print(f"Recommendation: {output.recommendation}")  # BUY, SELL, HOLD
print(f"Confidence: {output.confidence:.1%}")
```

### با Decision Agent

```python
from agents.signal.signal_agent import SignalAgent
from agents.decision.decision_agent import DecisionAgent
from agents.base.base_agent import AgentOutput, AgentType

# تحلیل با هر دو agent
ml_output = ml_agent.analyze(market_data)
signal_output = signal_agent.analyze(market_data)

# تبدیل به format Decision Agent
agent_outputs = [
    AgentOutput(
        agent_type=AgentType.ML,
        signal=1.0 if ml_output.recommendation == "BUY" else -1.0 if ml_output.recommendation == "SELL" else 0.0,
        confidence=ml_output.confidence,
        metadata={'source': 'ML Agent'}
    ),
    AgentOutput(
        agent_type=AgentType.SIGNAL,
        signal=1.0 if signal_output.recommendation == "BUY" else -1.0,
        confidence=signal_output.confidence,
        metadata={'source': 'Signal Agent'}
    )
]

# تصمیم نهایی
decision_output = decision_agent.analyze(agent_outputs)
print(f"Final Decision: {decision_output.metadata['decision']}")
```

## Model Performance

### Typical Metrics (1h timeframe, 2000 candles)

- **Validation Accuracy**: 55-60%
- **Precision**: 55-58%
- **Recall**: 52-57%
- **F1 Score**: 53-58%

### High Confidence Trades (confidence >= 60%)
- **Accuracy**: 60-65%
- **Count**: ~30-40% of all predictions

## Feature Importance

### Top Features (معمولاً)

1. **close_sma_20_ratio**: نسبت قیمت فعلی به SMA(20)
2. **rsi_14**: RSI 14-period
3. **bb_position**: موقعیت در Bollinger Bands
4. **momentum_20**: Momentum 20-period
5. **macd_hist**: MACD Histogram
6. **atr_14**: Average True Range
7. **volatility_20**: Volatility 20-period
8. **volume_ratio**: نسبت volume به میانگین

## Best Practices

### 1. Training Data
- حداقل **1500-2000 candles** برای training
- استفاده از timeframe مناسب (1h یا 4h توصیه می‌شود)
- بروزرسانی model هر **1-2 هفته**

### 2. Confidence Threshold
- **0.5**: تمام signalها (accuracy ~55%)
- **0.6**: Balanced (accuracy ~60%, 40% trades)
- **0.7**: Conservative (accuracy ~65%, 20% trades)

### 3. Combination با Technical Analysis
ML Agent بهتر است با Signal Agent ترکیب شود:
- ML برای **direction** (جهت)
- Technical برای **entry/exit** (ورود/خروج)
- Decision Agent برای **final decision**

## Limitations

1. **Accuracy**: 55-60% است، نه 80-90%
2. **Market Regime**: در بازارهای ranging بهتر عمل می‌کند
3. **Overfitting**: باید با validation set بررسی شود
4. **Features**: نیاز به update با تغییر market conditions

## Files

```
agents/ml/
├── __init__.py
├── ml_agent.py           # Main ML Agent
├── feature_engineer.py   # Feature extraction
└── models.py             # ML models (RandomForest, XGBoost, Ensemble)
```

## Examples

```
examples/
├── test_ml_agent.py      # Full example با training و usage
└── test_ml_quick.py      # Quick tests
```

## Dependencies

```
scikit-learn>=1.3.0
xgboost>=2.0.0
pandas>=2.0.0
numpy>=1.22.0
```

Install:
```bash
pip install scikit-learn xgboost
```
