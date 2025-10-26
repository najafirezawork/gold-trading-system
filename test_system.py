"""
Simple Tests - تست‌های ساده

برای تست سریع عملکرد سیستم.
برای تست‌های کامل، باید از pytest استفاده کنید.
"""

import sys
from datetime import datetime


def test_imports():
    """تست import کردن تمام ماژول‌ها"""
    print("Testing imports...")
    try:
        from config import settings
        from data_layer import TwelveDataClient, MarketData, OHLCV
        from agents import SignalAgent, DecisionAgent, AgentType, AgentOutput
        from agents.signal import TechnicalIndicators
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_config():
    """تست تنظیمات"""
    print("\nTesting configuration...")
    try:
        from config import settings
        
        assert settings.twelve_data_api_key, "API key not set"
        assert settings.default_symbol == "XAU/USD"
        assert settings.default_interval == "1h"
        
        print(f"✅ Config loaded successfully")
        print(f"   - API Key: {settings.twelve_data_api_key[:10]}...")
        print(f"   - Default Symbol: {settings.default_symbol}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_data_layer():
    """تست لایه دیتا"""
    print("\nTesting data layer...")
    try:
        from data_layer import TwelveDataClient
        
        client = TwelveDataClient()
        
        # تست دریافت داده
        print("  Fetching data from API...")
        data = client.get_time_series("XAU/USD", interval="1h", outputsize=10)
        
        assert len(data) == 10, f"Expected 10 data points, got {len(data)}"
        assert data.symbol == "XAU/USD"
        assert data.data[0].close > 0
        
        print(f"✅ Data layer working")
        print(f"   - Fetched {len(data)} candles")
        print(f"   - Current price: ${data.data[0].close:.2f}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Data layer test failed: {e}")
        return False


def test_signal_agent():
    """تست Signal Agent"""
    print("\nTesting Signal Agent...")
    try:
        from data_layer import TwelveDataClient
        from agents import SignalAgent
        
        client = TwelveDataClient()
        agent = SignalAgent()
        
        # دریافت داده
        data = client.get_time_series("XAU/USD", interval="1h", outputsize=100)
        
        # تحلیل
        print("  Running technical analysis...")
        output = agent.analyze(data)
        
        assert output.signal is not None
        assert -1 <= output.signal <= 1, f"Signal out of range: {output.signal}"
        assert 0 <= output.confidence <= 1, f"Confidence out of range: {output.confidence}"
        
        print(f"✅ Signal Agent working")
        print(f"   - Signal: {output.signal:.2f}")
        print(f"   - Confidence: {output.confidence:.2f}")
        print(f"   - Analysis: {output.metadata['analysis']}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Signal Agent test failed: {e}")
        return False


def test_decision_agent():
    """تست Decision Agent"""
    print("\nTesting Decision Agent...")
    try:
        from data_layer import TwelveDataClient
        from agents import SignalAgent, DecisionAgent
        
        client = TwelveDataClient()
        signal_agent = SignalAgent()
        decision_agent = DecisionAgent()
        
        # دریافت و تحلیل
        data = client.get_time_series("XAU/USD", interval="1h", outputsize=100)
        signal_output = signal_agent.analyze(data)
        
        # تصمیم‌گیری
        print("  Making trading decision...")
        decision = decision_agent.analyze([signal_output])
        
        assert decision.signal is not None
        assert decision.metadata['decision'] is not None
        assert 'reasoning' in decision.metadata
        
        print(f"✅ Decision Agent working")
        print(f"   - Decision: {decision.metadata['decision']}")
        print(f"   - Signal: {decision.signal:.2f}")
        print(f"   - Confidence: {decision.confidence:.2f}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Decision Agent test failed: {e}")
        return False


def test_technical_indicators():
    """تست اندیکاتورهای تکنیکال"""
    print("\nTesting Technical Indicators...")
    try:
        from agents.signal import TechnicalIndicators
        
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        highs = [p + 1 for p in prices]
        lows = [p - 1 for p in prices]
        
        # SMA
        sma = TechnicalIndicators.calculate_sma(prices, 5)
        assert sma > 0
        
        # EMA
        ema = TechnicalIndicators.calculate_ema(prices, 5)
        assert ema > 0
        
        # RSI
        rsi = TechnicalIndicators.calculate_rsi(prices, 5)
        assert 0 <= rsi <= 100
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(prices, 5)
        assert upper > middle > lower
        
        print(f"✅ Technical Indicators working")
        print(f"   - SMA: {sma:.2f}")
        print(f"   - EMA: {ema:.2f}")
        print(f"   - RSI: {rsi:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Technical Indicators test failed: {e}")
        return False


def test_full_pipeline():
    """تست کل pipeline"""
    print("\nTesting full pipeline...")
    try:
        from main import TradingSystem
        
        system = TradingSystem()
        
        print("  Running full analysis...")
        result = system.run_analysis(
            symbol="XAU/USD",
            interval="1h",
            outputsize=50
        )
        
        assert result is not None
        assert result.metadata['decision'] is not None
        
        print(f"✅ Full pipeline working")
        print(f"   - Final decision: {result.metadata['decision']}")
        
        system.close()
        return True
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return False


def run_all_tests():
    """اجرای تمام تست‌ها"""
    print("="*60)
    print("🧪 Running Tests...")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Data Layer", test_data_layer),
        ("Signal Agent", test_signal_agent),
        ("Decision Agent", test_decision_agent),
        ("Technical Indicators", test_technical_indicators),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # خلاصه نتایج
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
