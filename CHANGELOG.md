# Changelog

تمامی تغییرات مهم پروژه در این فایل مستند می‌شود.

## [2.0.0] - 2025-01-26

### ✨ New Features

#### Backtesting Module
- **Complete Backtesting Framework**
  - `BacktestEngine`: موتور اصلی backtesting با پشتیبانی کامل
  - `BaseStrategy`: کلاس abstract برای ساخت استراتژی‌های سفارشی
  - `Trade Model`: مدل کامل برای معاملات با محاسبه P&L
  - `BacktestResult`: نتایج جامع با metrics حرفه‌ای
  - `PerformanceMetrics`: محاسبه Sharpe, Sortino, Max Drawdown

- **Pre-built Strategies**
  - `SimpleMAStrategy`: Moving Average Crossover
  - `RSIStrategy`: RSI با stop loss/take profit
  - `SignalAgentStrategy`: استفاده از Signal Agent در backtesting

- **Advanced Features**
  - Stop Loss و Take Profit support
  - Commission calculation
  - Equity curve tracking
  - Integration با Signal Agent
  - JSON export برای نتایج

#### Docker Support
- **Complete Containerization**
  - `Dockerfile`: Python 3.13-slim base image
  - `docker-compose.yml`: Service orchestration
  - `.dockerignore`: Optimized build context
  - `docker-run.ps1`: PowerShell script (Windows)
  - `docker-run.sh`: Bash script (Linux/Mac)

- **Production Ready**
  - Volume mounts برای logs و results
  - Environment variable support
  - Port exposure (8000) برای web dashboard آینده
  - Health checks ready
  - Commented PostgreSQL و Redis configs

#### Documentation
- **New Documentation Files**
  - `BACKTESTING.md`: راهنمای جامع 200+ خط
  - `DOCKER.md`: راهنمای Docker deployment 300+ خط
  - `QUICKSTART.md`: راهنمای شروع سریع

- **Updated Documentation**
  - `README.md`: اضافه شدن Docker و Backtesting sections
  - بهبود structure و navigation
  - لینک‌های بین مستندات

#### Examples & Tests
- **New Examples**
  - `examples/backtest_examples.py`: 4 مثال کامل backtesting
  - مقایسه استراتژی‌ها
  - ذخیره نتایج در JSON
  - منوی تعاملی

- **New Tests**
  - `test_backtesting.py`: test suite جامع
  - تست Trade model
  - تست PerformanceMetrics
  - تست BacktestEngine
  - تست BaseStrategy

### 🔧 Improvements
- بهبود ساختار پروژه
- اضافه شدن type hints کامل‌تر
- بهبود error handling
- بهبود logging

### 📚 Documentation Updates
- مستندات Docker کامل
- مستندات Backtesting با مثال‌های واقعی
- Quick start guide
- Best practices برای backtesting

---

## [1.0.0] - 2025-10-26

### ✨ Added

#### Core System
- **Data Layer** با اتصال به Twelve Data API
  - `TwelveDataClient` برای ارتباط با API
  - `MarketData` و `OHLCV` models با Pydantic
  - Error handling با `TwelveDataAPIError`
  - Context manager support

#### Agent System
- **Base Agent Architecture**
  - `BaseAgent` کلاس پایه برای همه agents
  - `AgentOutput` فرمت استاندارد خروجی
  - `AgentType` enum برای انواع agents
  - Enable/Disable functionality

- **Signal Agent** (Technical Analysis)
  - تحلیل تکنیکال کامل با 6 اندیکاتور
  - RSI, MACD, Bollinger Bands
  - Moving Averages (SMA, EMA)
  - ATR برای volatility
  - وزن‌دهی هوشمند سیگنال‌ها

- **Decision Agent**
  - Aggregation چند agent با confidence weighting
  - 5 سطح تصمیم: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
  - تنظیم پویای thresholds
  - توضیحات کامل برای هر تصمیم

#### Configuration
- **Settings Management**
  - استفاده از Pydantic Settings
  - پشتیبانی از `.env` files
  - Type-safe configuration
  - تنظیمات قابل سفارشی‌سازی

#### Examples & Documentation
- **Examples**
  - `main.py`: مثال اصلی و ساده
  - `quick_start.py`: شروع سریع
  - `examples/advanced_usage.py`: کاربردهای پیشرفته
  - `examples/use_cases.py`: 5 use case واقعی

- **Documentation**
  - `README.md`: مستندات اصلی
  - `DEVELOPER_GUIDE.md`: راهنمای کامل توسعه‌دهنده
  - `API_REFERENCE.md`: مرجع کامل API
  - این `CHANGELOG.md`

#### Testing
- `test_system.py` برای تست سریع تمام اجزا
- تست imports, config, data layer, agents, indicators

#### Development Tools
- `.gitignore` برای Python projects
- `requirements.txt` با تمام dependencies
- Logging سیستماتیک در تمام ماژول‌ها

### 🎨 Features

- **Clean Architecture**: معماری تمیز بر اساس SOLID principles
- **Type Safety**: Type hints در همه جا
- **Error Handling**: مدیریت خطای جامع
- **Extensibility**: قابل توسعه برای ML و sentiment agents
- **Modularity**: ماژولار و قابل نگهداری
- **Documentation**: مستندات کامل و به روز

### 🔧 Technical Details

#### Design Patterns Used
- **Strategy Pattern**: برای agent strategies
- **Template Method**: در BaseAgent
- **Dependency Injection**: در constructors
- **Context Manager**: برای API client

#### Code Quality
- رعایت PEP 8 style guide
- Docstrings برای تمام کلاس‌ها و متدها
- Type hints everywhere
- Error handling with custom exceptions
- Logging با Python logging module

#### Dependencies
```
requests==2.31.0
pandas==2.1.0
numpy==1.24.3
python-dotenv==1.0.0
pydantic==2.4.2
pydantic-settings==2.0.3
```

### 📊 Indicators Implemented
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Average True Range (ATR)

### 🎯 Use Cases
1. Daily Morning Analysis
2. Multi-Timeframe Confluence
3. Swing Trading Setup Finder
4. Position Size Calculator
5. Alert System

### 🔒 Security
- API keys در `.env` (not committed)
- `.gitignore` برای sensitive files
- Input validation در API client

### 🚀 Future Roadmap

#### Version 1.1.0 (Planned)
- [ ] ML Agent با scikit-learn
- [ ] Backtesting module
- [ ] Performance metrics

#### Version 1.2.0 (Planned)
- [ ] Real-time streaming data
- [ ] WebSocket support
- [ ] Multi-symbol support

#### Version 2.0.0 (Planned)
- [ ] Web dashboard (FastAPI + React)
- [ ] Database integration
- [ ] User authentication
- [ ] Portfolio management
- [ ] Risk management tools

### 📝 Notes

این اولین نسخه پایدار پروژه است که شامل:
- ✅ Data layer کامل و تست شده
- ✅ Signal agent با 6 اندیکاتور
- ✅ Decision agent با aggregation هوشمند
- ✅ معماری قابل توسعه
- ✅ مستندات جامع
- ✅ مثال‌های کاربردی

پروژه آماده استفاده برای:
- تحلیل تکنیکال طلا
- تصمیم‌گیری معاملاتی
- توسعه agent های جدید (ML, Sentiment, etc.)

---

**Contributors**: Your Name
**License**: Open Source
**Repository**: TBD
