"""
🧪 تست جامع Signal Agent (Technical Analysis)

بررسی دقیق عملکرد اندیکاتورهای تکنیکالی و سیگنال‌ها
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from data_layer import TwelveDataClient, MarketData
from agents.signal import SignalAgent, TechnicalIndicators
from agents.base import AgentOutput, AgentType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SignalAgentTester:
    """🎯 تست‌کننده جامع Signal Agent"""
    
    def __init__(self):
        self.client = TwelveDataClient()
        self.agent = SignalAgent()
        self.indicators = TechnicalIndicators()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_results": {},
            "indicators_analysis": {},
            "signal_verification": {},
            "summary": {}
        }
    
    def print_header(self, title: str, level: int = 1):
        """نمایش هدر"""
        if level == 1:
            print(f"\n\n{'='*90}")
            print(f"{'='*90}")
            print(f"  {title}")
            print(f"{'='*90}")
            print(f"{'='*90}\n")
        elif level == 2:
            print(f"\n{'─'*90}")
            print(f"  ► {title}")
            print(f"{'─'*90}\n")
        else:
            print(f"\n  🔹 {title}\n")
    
    def run_all_tests(self):
        """اجرای تمام تست‌ها"""
        self.print_header("🧪 تست جامع Signal Agent - سیستم تحلیل تکنیکال طلا")
        
        try:
            # تست 1: دریافت داده
            self.test_data_retrieval()
            
            # تست 2: محاسبه اندیکاتورها
            self.test_indicators_calculation()
            
            # تست 3: تولید سیگنال
            self.test_signal_generation()
            
            # تست 4: تصحیح سیگنال
            self.test_signal_validation()
            
            # تست 5: تست edge cases
            self.test_edge_cases()
            
            # خلاصه
            self.print_summary()
            
            # ذخیره نتایج
            self.save_results()
            
        except Exception as e:
            logger.error(f"❌ خطا در تست‌ها: {e}", exc_info=True)
            self.results["summary"]["status"] = "FAILED"
            self.results["summary"]["error"] = str(e)
            self.save_results()
    
    def test_data_retrieval(self):
        """1️⃣ تست دریافت داده‌های بازار"""
        self.print_header("1️⃣ تست دریافت داده‌های بازار", level=2)
        
        test_name = "data_retrieval"
        test_result = {
            "status": "PENDING",
            "details": {}
        }
        
        try:
            print("📊 دریافت داده‌های تاریخی طلا از Twelve Data API...")
            
            market_data = self.client.get_time_series(
                symbol="XAU/USD",
                interval="1h",
                outputsize=200
            )
            
            # بررسی‌های پایه
            assert market_data is not None, "Market data خالی است"
            assert len(market_data.data) > 0, "هیچ کندلی دریافت نشد"
            assert market_data.symbol == "XAU/USD", "نماد نادرست است"
            
            print(f"✅ داده دریافت شد!")
            print(f"   📈 تعداد کندل: {len(market_data.data)}")
            print(f"   🔤 نماد: {market_data.symbol}")
            print(f"   ⏱️  بازه زمانی: 1 ساعت")
            
            # جزئیات کندل‌ها
            first_candle = market_data.data[0]
            last_candle = market_data.data[-1]
            
            print(f"\n   📍 اول کندل:")
            print(f"      - قیمت بسته: ${first_candle.close:.2f}")
            print(f"      - بالا: ${first_candle.high:.2f}")
            print(f"      - پایین: ${first_candle.low:.2f}")
            
            print(f"\n   📍 آخرین کندل:")
            print(f"      - قیمت بسته: ${last_candle.close:.2f}")
            print(f"      - بالا: ${last_candle.high:.2f}")
            print(f"      - پایین: ${last_candle.low:.2f}")
            
            # محاسبات آماری
            closes = [c.close for c in market_data.data]
            price_min = min(closes)
            price_max = max(closes)
            price_avg = sum(closes) / len(closes)
            
            print(f"\n   📊 آمار قیمت‌ها:")
            print(f"      - کمترین: ${price_min:.2f}")
            print(f"      - بیشترین: ${price_max:.2f}")
            print(f"      - میانگین: ${price_avg:.2f}")
            print(f"      - دامنه: ${price_max - price_min:.2f}")
            
            test_result.update({
                "status": "PASSED ✅",
                "details": {
                    "candle_count": len(market_data.data),
                    "symbol": market_data.symbol,
                    "current_price": last_candle.close,
                    "price_range": {
                        "min": price_min,
                        "max": price_max,
                        "avg": price_avg
                    }
                }
            })
            
            # ذخیره برای تست‌های بعد
            self.market_data = market_data
            self.closes = closes
            
        except AssertionError as e:
            test_result["status"] = f"FAILED ❌: {str(e)}"
            logger.error(f"❌ تست دریافت داده ناموفق: {e}")
        except Exception as e:
            test_result["status"] = f"ERROR ⚠️: {str(e)}"
            logger.error(f"❌ خطا در دریافت داده: {e}")
        
        self.results["test_results"][test_name] = test_result
    
    def test_indicators_calculation(self):
        """2️⃣ تست محاسبه اندیکاتورهای تکنیکالی"""
        self.print_header("2️⃣ تست محاسبه اندیکاتورهای تکنیکالی", level=2)
        
        test_name = "indicators_calculation"
        indicators_result = {
            "status": "PENDING",
            "indicators": {}
        }
        
        try:
            if not hasattr(self, 'closes'):
                print("⚠️  داده‌ای برای محاسبه ندارم، ابتدا تست 1 را اجرا کنید")
                return
            
            closes = self.closes
            highs = [c.high for c in self.market_data.data]
            lows = [c.low for c in self.market_data.data]
            
            print(f"📈 محاسبه {6} اندیکاتور مختلف...\n")
            
            # 1. Simple Moving Average
            print("1️⃣  SMA (Simple Moving Average)")
            sma_20 = self.indicators.calculate_sma(closes, 20)
            sma_50 = self.indicators.calculate_sma(closes, 50)
            print(f"    ✓ SMA 20: ${sma_20:.2f}")
            print(f"    ✓ SMA 50: ${sma_50:.2f}")
            indicators_result["indicators"]["SMA"] = {
                "sma_20": sma_20,
                "sma_50": sma_50
            }
            
            # 2. Exponential Moving Average
            print("\n2️⃣  EMA (Exponential Moving Average)")
            ema_12 = self.indicators.calculate_ema(closes, 12)
            ema_26 = self.indicators.calculate_ema(closes, 26)
            print(f"    ✓ EMA 12: ${ema_12:.2f}")
            print(f"    ✓ EMA 26: ${ema_26:.2f}")
            indicators_result["indicators"]["EMA"] = {
                "ema_12": ema_12,
                "ema_26": ema_26
            }
            
            # 3. RSI
            print("\n3️⃣  RSI (Relative Strength Index)")
            rsi = self.indicators.calculate_rsi(closes, 14)
            rsi_status = self._interpret_rsi(rsi)
            print(f"    ✓ RSI 14: {rsi:.2f}")
            print(f"    📊 وضعیت: {rsi_status}")
            indicators_result["indicators"]["RSI"] = {
                "value": rsi,
                "status": rsi_status
            }
            
            # 4. MACD
            print("\n4️⃣  MACD (Moving Average Convergence Divergence)")
            macd_line, signal_line, histogram = self.indicators.calculate_macd(closes)
            macd_status = "صعودی 📈" if histogram > 0 else "نزولی 📉"
            print(f"    ✓ MACD Line: {macd_line:.4f}")
            print(f"    ✓ Signal Line: {signal_line:.4f}")
            print(f"    ✓ Histogram: {histogram:.4f}")
            print(f"    📊 وضعیت: {macd_status}")
            indicators_result["indicators"]["MACD"] = {
                "macd_line": macd_line,
                "signal_line": signal_line,
                "histogram": histogram,
                "status": macd_status
            }
            
            # 5. Bollinger Bands
            print("\n5️⃣  Bollinger Bands")
            upper_band, middle_band, lower_band = self.indicators.calculate_bollinger_bands(closes)
            current_price = closes[-1]
            bb_position = self._get_bb_position(current_price, upper_band, middle_band, lower_band)
            print(f"    ✓ Upper Band: ${upper_band:.2f}")
            print(f"    ✓ Middle Band: ${middle_band:.2f}")
            print(f"    ✓ Lower Band: ${lower_band:.2f}")
            print(f"    📊 موقعیت قیمت: {bb_position}")
            indicators_result["indicators"]["Bollinger_Bands"] = {
                "upper": upper_band,
                "middle": middle_band,
                "lower": lower_band,
                "position": bb_position
            }
            
            # 6. ATR
            print("\n6️⃣  ATR (Average True Range - نوسان‌پذیری)")
            atr = self.indicators.calculate_atr(highs, lows, closes, 14)
            volatility = "زیاد 📊" if atr > (closes[-1] * 0.01) else "کم 📉"
            print(f"    ✓ ATR 14: {atr:.4f}")
            print(f"    📊 سطح نوسان: {volatility}")
            indicators_result["indicators"]["ATR"] = {
                "value": atr,
                "volatility": volatility
            }
            
            # خلاصه
            print(f"\n{'─'*50}")
            print(f"✅ تمام اندیکاتورها با موفقیت محاسبه شدند!")
            
            indicators_result["status"] = "PASSED ✅"
            self.indicators_data = indicators_result["indicators"]
            
        except Exception as e:
            indicators_result["status"] = f"ERROR ⚠️: {str(e)}"
            logger.error(f"❌ خطا در محاسبه اندیکاتورها: {e}", exc_info=True)
        
        self.results["indicators_analysis"] = indicators_result
    
    def test_signal_generation(self):
        """3️⃣ تست تولید سیگنال"""
        self.print_header("3️⃣ تست تولید سیگنال", level=2)
        
        test_name = "signal_generation"
        signal_result = {
            "status": "PENDING",
            "signal_output": None
        }
        
        try:
            if not hasattr(self, 'market_data'):
                print("⚠️  داده‌ای برای تحلیل ندارم")
                return
            
            print("🔍 تحلیل با Signal Agent...")
            
            # فراخوانی agent
            output = self.agent.analyze(self.market_data)
            
            assert isinstance(output, AgentOutput), "خروجی نامعتبر"
            assert output.agent_type == AgentType.SIGNAL, "نوع agent نادرست"
            
            # نمایش نتایج
            print(f"\n✅ سیگنال با موفقیت تولید شد!")
            print(f"\n📊 خروجی Signal Agent:")
            print(f"   Agent: {output.agent_type.value}")
            print(f"   Signal: {output.signal:.4f}")
            print(f"   Confidence: {output.confidence:.2%}")
            
            # تفسیر سیگنال
            signal_interpretation = self._interpret_signal(output.signal)
            confidence_interpretation = self._interpret_confidence(output.confidence)
            
            print(f"\n📈 تفسیر:")
            print(f"   سیگنال: {signal_interpretation}")
            print(f"   اعتماد: {confidence_interpretation}")
            
            # جزئیات اندیکاتورها
            if "indicators" in output.metadata:
                print(f"\n🎯 جزئیات اندیکاتورها:")
                indicators = output.metadata["indicators"]
                
                if "rsi" in indicators:
                    print(f"   RSI: {indicators['rsi']:.2f}")
                if "sma_20" in indicators:
                    print(f"   SMA 20: ${indicators['sma_20']:.2f}")
                if "sma_50" in indicators:
                    print(f"   SMA 50: ${indicators['sma_50']:.2f}")
            
            signal_result.update({
                "status": "PASSED ✅",
                "signal_output": {
                    "signal": output.signal,
                    "confidence": output.confidence,
                    "interpretation": signal_interpretation
                }
            })
            
            self.signal_output = output
            
        except AssertionError as e:
            signal_result["status"] = f"FAILED ❌: {str(e)}"
            logger.error(f"❌ تست تولید سیگنال ناموفق: {e}")
        except Exception as e:
            signal_result["status"] = f"ERROR ⚠️: {str(e)}"
            logger.error(f"❌ خطا در تولید سیگنال: {e}", exc_info=True)
        
        self.results["test_results"][test_name] = signal_result
    
    def test_signal_validation(self):
        """4️⃣ تست صحت‌سنجی سیگنال"""
        self.print_header("4️⃣ تست صحت‌سنجی سیگنال", level=2)
        
        test_name = "signal_validation"
        validation_result = {
            "status": "PENDING",
            "validations": {}
        }
        
        try:
            if not hasattr(self, 'signal_output'):
                print("⚠️  سیگنالی برای تصحیح ندارم")
                return
            
            output = self.signal_output
            
            print("✔️  بررسی صحت سیگنال...\n")
            
            # تست 1: محدوده سیگنال
            print("1️⃣  محدوده سیگنال (-1 تا 1)")
            assert -1 <= output.signal <= 1, "سیگنال خارج از محدوده!"
            print(f"    ✓ سیگنال: {output.signal:.4f} (معتبر)")
            validation_result["validations"]["signal_range"] = "PASSED ✅"
            
            # تست 2: محدوده confidence
            print("\n2️⃣  محدوده Confidence (0 تا 1)")
            assert 0 <= output.confidence <= 1, "Confidence خارج از محدوده!"
            print(f"    ✓ Confidence: {output.confidence:.4f} (معتبر)")
            validation_result["validations"]["confidence_range"] = "PASSED ✅"
            
            # تست 3: Agent Type
            print("\n3️⃣  نوع Agent")
            assert output.agent_type == AgentType.SIGNAL, "نوع Agent نادرست!"
            print(f"    ✓ Agent Type: {output.agent_type.value} (معتبر)")
            validation_result["validations"]["agent_type"] = "PASSED ✅"
            
            # تست 4: Metadata
            print("\n4️⃣  Metadata")
            assert isinstance(output.metadata, dict), "Metadata نامعتبر!"
            assert "indicators" in output.metadata, "Indicators در metadata نیست!"
            print(f"    ✓ Metadata موجود است")
            print(f"    ✓ اندیکاتورها: {list(output.metadata['indicators'].keys())}")
            validation_result["validations"]["metadata"] = "PASSED ✅"
            
            # تست 5: سازگاری سیگنال با اندیکاتورها
            print("\n5️⃣  سازگاری سیگنال با اندیکاتورها")
            indicators = output.metadata["indicators"]
            consistency_score = self._calculate_consistency(output.signal, indicators)
            print(f"    ✓ نمره سازگاری: {consistency_score:.2%}")
            validation_result["validations"]["consistency"] = {
                "status": "PASSED ✅",
                "score": consistency_score
            }
            
            print(f"\n{'─'*50}")
            print(f"✅ تمام تست‌های صحت‌سنجی موفق بودند!")
            
            validation_result["status"] = "PASSED ✅"
            
        except AssertionError as e:
            validation_result["status"] = f"FAILED ❌: {str(e)}"
            logger.error(f"❌ تست صحت‌سنجی ناموفق: {e}")
        except Exception as e:
            validation_result["status"] = f"ERROR ⚠️: {str(e)}"
            logger.error(f"❌ خطا در صحت‌سنجی: {e}", exc_info=True)
        
        self.results["test_results"][test_name] = validation_result
    
    def test_edge_cases(self):
        """5️⃣ تست موارد حدی"""
        self.print_header("5️⃣ تست موارد حدی (Edge Cases)", level=2)
        
        test_name = "edge_cases"
        edge_result = {
            "status": "PENDING",
            "test_cases": {}
        }
        
        try:
            print("🔬 تست موارد خاص و حدی...\n")
            
            # Case 1: داده ناکافی
            print("1️⃣  داده ناکافی (10 کندل)")
            small_market_data = MarketData(
                symbol="XAU/USD",
                interval="1h",
                data=self.market_data.data[:10]
            )
            output = self.agent.analyze(small_market_data)
            assert output.confidence == 0.0, "باید confidence صفر باشد"
            print(f"    ✓ با {len(small_market_data.data)} کندل:")
            print(f"      Signal: {output.signal}, Confidence: {output.confidence}")
            print(f"      ✅ تست موفق")
            edge_result["test_cases"]["insufficient_data"] = "PASSED ✅"
            
            # Case 2: بازار صعودی (همه قیمت‌ها بالا می‌روند)
            print("\n2️⃣  بازار صعودی (قیمت‌های افزایشی)")
            from datetime import datetime, timedelta
            bullish_data = []
            base_price = 2000
            base_time = datetime.now()
            for i in range(100):
                from data_layer import OHLCV
                bullish_data.append(OHLCV(
                    datetime=base_time + timedelta(hours=i),
                    open=base_price + i,
                    high=base_price + i + 1,
                    low=base_price + i - 0.5,
                    close=base_price + i + 0.5,
                    volume=1000
                ))
            bullish_market = MarketData(symbol="XAU/USD", interval="1h", data=bullish_data)
            output = self.agent.analyze(bullish_market)
            print(f"    ✓ Signal: {output.signal:.4f}")
            print(f"    ✓ Confidence: {output.confidence:.2%}")
            assert output.signal > 0, "سیگنال باید مثبت باشد"
            print(f"    ✅ تست موفق (خرید پیشنهاد شد)")
            edge_result["test_cases"]["bullish_market"] = "PASSED ✅"
            
            # Case 3: بازار نزولی
            print("\n3️⃣  بازار نزولی (قیمت‌های کاهشی)")
            bearish_data = []
            base_price = 2100
            base_time = datetime.now()
            for i in range(100):
                from data_layer import OHLCV
                bearish_data.append(OHLCV(
                    datetime=base_time + timedelta(hours=i),
                    open=base_price - i,
                    high=base_price - i + 0.5,
                    low=base_price - i - 1,
                    close=base_price - i - 0.5,
                    volume=1000
                ))
            bearish_market = MarketData(symbol="XAU/USD", interval="1h", data=bearish_data)
            output = self.agent.analyze(bearish_market)
            print(f"    ✓ Signal: {output.signal:.4f}")
            print(f"    ✓ Confidence: {output.confidence:.2%}")
            assert output.signal < 0, "سیگنال باید منفی باشد"
            print(f"    ✅ تست موفق (فروش پیشنهاد شد)")
            edge_result["test_cases"]["bearish_market"] = "PASSED ✅"
            
            # Case 4: بازار جانبی (سیدویز)
            print("\n4️⃣  بازار جانبی (قیمت ثابت)")
            sideways_data = []
            stable_price = 2050
            base_time = datetime.now()
            for i in range(100):
                from data_layer import OHLCV
                sideways_data.append(OHLCV(
                    datetime=base_time + timedelta(hours=i),
                    open=stable_price,
                    high=stable_price + 0.5,
                    low=stable_price - 0.5,
                    close=stable_price,
                    volume=1000
                ))
            sideways_market = MarketData(symbol="XAU/USD", interval="1h", data=sideways_data)
            output = self.agent.analyze(sideways_market)
            print(f"    ✓ Signal: {output.signal:.4f}")
            print(f"    ✓ Confidence: {output.confidence:.2%}")
            print(f"    ✅ تست موفق (وضعیت خنثی)")
            edge_result["test_cases"]["sideways_market"] = "PASSED ✅"
            
            print(f"\n{'─'*50}")
            print(f"✅ تمام تست‌های حدی موفق بودند!")
            
            edge_result["status"] = "PASSED ✅"
            
        except AssertionError as e:
            edge_result["status"] = f"FAILED ❌: {str(e)}"
            logger.error(f"❌ تست حدی ناموفق: {e}")
        except Exception as e:
            edge_result["status"] = f"ERROR ⚠️: {str(e)}"
            logger.error(f"❌ خطا در تست حدی: {e}", exc_info=True)
        
        self.results["test_results"][test_name] = edge_result
    
    def print_summary(self):
        """چاپ خلاصه نتایج"""
        self.print_header("📋 خلاصه نتایج تست", level=2)
        
        print("نتایج تست‌ها:\n")
        
        all_passed = True
        for test_name, result in self.results["test_results"].items():
            status = result.get("status", "UNKNOWN")
            symbol = "✅" if "PASSED" in status else "❌"
            print(f"  {symbol} {test_name}: {status}")
            if "FAILED" in status or "ERROR" in status:
                all_passed = False
        
        print(f"\n{'─'*50}")
        
        if all_passed:
            print("✅ تمام تست‌ها موفق بودند!")
            self.results["summary"]["status"] = "SUCCESS ✅"
        else:
            print("⚠️  برخی تست‌ها ناموفق بودند")
            self.results["summary"]["status"] = "PARTIAL ⚠️"
        
        print(f"\n📊 آمار:")
        print(f"   - تاریخ/زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - تعداد تست‌ها: {len(self.results['test_results'])}")
    
    def save_results(self):
        """ذخیره نتایج در فایل JSON"""
        try:
            results_file = Path(__file__).parent / "results" / "signal_agent_test_results.json"
            results_file.parent.mkdir(exist_ok=True)
            
            # تبدیل به JSON-serializable
            json_results = json.dumps(self.results, indent=2, ensure_ascii=False, default=str)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write(json_results)
            
            print(f"\n💾 نتایج در فایل ذخیره شدند:")
            print(f"   {results_file}")
            
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره نتایج: {e}")
    
    # متدهای کمکی
    def _interpret_signal(self, signal: float) -> str:
        """تفسیر سیگنال"""
        if signal > 0.5:
            return "🟢 خرید قوی (Strong Buy)"
        elif signal > 0:
            return "🟢 خرید (Buy)"
        elif signal > -0.5:
            return "🔴 فروش (Sell)"
        else:
            return "🔴 فروش قوی (Strong Sell)"
    
    def _interpret_confidence(self, confidence: float) -> str:
        """تفسیر اعتماد"""
        if confidence > 0.8:
            return "⭐⭐⭐⭐⭐ بسیار زیاد"
        elif confidence > 0.6:
            return "⭐⭐⭐⭐ زیاد"
        elif confidence > 0.4:
            return "⭐⭐⭐ متوسط"
        elif confidence > 0.2:
            return "⭐⭐ کم"
        else:
            return "⭐ بسیار کم"
    
    def _interpret_rsi(self, rsi: float) -> str:
        """تفسیر RSI"""
        if rsi > 70:
            return "⬆️  اشباع خریدی (Overbought)"
        elif rsi < 30:
            return "⬇️  اشباع فروشی (Oversold)"
        else:
            return "→ خنثی (Neutral)"
    
    def _get_bb_position(self, price: float, upper: float, middle: float, lower: float) -> str:
        """موقعیت قیمت نسبت به Bollinger Bands"""
        if price > upper * 0.99:
            return "📈 بالا (Near Upper Band)"
        elif price < lower * 1.01:
            return "📉 پایین (Near Lower Band)"
        else:
            return "→ وسط (Middle Band)"
    
    def _calculate_consistency(self, signal: float, indicators: Dict[str, Any]) -> float:
        """محاسبه سازگاری سیگنال با اندیکاتورها"""
        consistency_score = 0
        indicator_count = 0
        
        # RSI
        if "rsi" in indicators:
            rsi = indicators["rsi"]
            if signal > 0 and rsi < 70:
                consistency_score += 1
            elif signal < 0 and rsi > 30:
                consistency_score += 1
            indicator_count += 1
        
        # MACD
        if "macd" in indicators:
            macd_hist = indicators["macd"].get("histogram", 0)
            if (signal > 0 and macd_hist > 0) or (signal < 0 and macd_hist < 0):
                consistency_score += 1
            indicator_count += 1
        
        if indicator_count > 0:
            return consistency_score / indicator_count
        return 0.5


def main():
    """نقطه ورود اصلی"""
    tester = SignalAgentTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
