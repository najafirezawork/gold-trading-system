"""
Use Cases - موارد استفاده مختلف

این فایل شامل مثال‌های واقعی برای سناریوهای مختلف است.
"""

import logging
from datetime import datetime, timedelta

from data_layer import TwelveDataClient
from agents import SignalAgent, DecisionAgent
from config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# USE CASE 1: تحلیل روزانه صبحگاهی
# ============================================================

def daily_morning_analysis():
    """
    تحلیل صبحگاهی برای شروع روز معاملاتی.
    این را می‌توانید با cron job یا task scheduler اجرا کنید.
    """
    logger.info("\n" + "="*60)
    logger.info("📅 Daily Morning Analysis - " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info("="*60)
    
    client = TwelveDataClient()
    signal_agent = SignalAgent()
    decision_agent = DecisionAgent()
    
    try:
        # تحلیل روی daily timeframe
        data = client.get_time_series("XAU/USD", interval="1day", outputsize=50)
        
        signal = signal_agent.analyze(data)
        decision = decision_agent.analyze([signal])
        
        # نمایش نتیجه
        logger.info(f"\n🏆 Today's Outlook for Gold:")
        logger.info(f"  Current Price: ${data.data[0].close:.2f}")
        logger.info(f"  Signal: {signal.metadata['analysis']}")
        logger.info(f"  Decision: {decision.metadata['decision']}")
        logger.info(f"  Confidence: {decision.confidence:.2%}")
        
        # اگر سیگنال قوی بود
        if decision.metadata['decision'] in ['STRONG_BUY', 'STRONG_SELL']:
            logger.info(f"\n⚠️  STRONG SIGNAL DETECTED!")
            logger.info(f"  Action: Consider taking a position")
        
        return decision
        
    finally:
        client.close()


# ============================================================
# USE CASE 2: مقایسه چند timeframe
# ============================================================

def multi_timeframe_confluence():
    """
    بررسی همخوانی سیگنال‌ها در timeframe های مختلف.
    این یک روش قدرتمند برای validation است.
    """
    logger.info("\n" + "="*60)
    logger.info("📊 Multi-Timeframe Confluence Analysis")
    logger.info("="*60)
    
    client = TwelveDataClient()
    signal_agent = SignalAgent()
    
    timeframes = {
        "1h": "Short-term",
        "4h": "Medium-term",
        "1day": "Long-term"
    }
    
    results = {}
    
    try:
        for interval, description in timeframes.items():
            logger.info(f"\n🔍 Analyzing {description} ({interval})...")
            
            data = client.get_time_series("XAU/USD", interval=interval, outputsize=100)
            signal = signal_agent.analyze(data)
            
            results[interval] = {
                "description": description,
                "signal": signal.signal,
                "analysis": signal.metadata['analysis'],
                "confidence": signal.confidence
            }
            
            logger.info(f"  ✓ {signal.metadata['analysis']} (signal={signal.signal:.2f})")
        
        # بررسی همخوانی
        logger.info("\n" + "="*60)
        logger.info("📈 Confluence Check:")
        
        signals = [r['signal'] for r in results.values()]
        avg_signal = sum(signals) / len(signals)
        
        # همه سیگنال‌ها هم‌جهت هستند؟
        all_bullish = all(s > 0.2 for s in signals)
        all_bearish = all(s < -0.2 for s in signals)
        
        if all_bullish:
            logger.info("  ✅ BULLISH CONFLUENCE - All timeframes agree on uptrend")
            logger.info("     → High probability bullish setup")
        elif all_bearish:
            logger.info("  ✅ BEARISH CONFLUENCE - All timeframes agree on downtrend")
            logger.info("     → High probability bearish setup")
        else:
            logger.info("  ⚠️  MIXED SIGNALS - No clear confluence")
            logger.info("     → Wait for better setup")
        
        logger.info(f"  Average Signal: {avg_signal:.2f}")
        logger.info("="*60)
        
        return results
        
    finally:
        client.close()


# ============================================================
# USE CASE 3: استراتژی Swing Trading
# ============================================================

def swing_trading_setup():
    """
    شناسایی فرصت‌های swing trading (نگهداری چند روزه).
    """
    logger.info("\n" + "="*60)
    logger.info("🎯 Swing Trading Setup Finder")
    logger.info("="*60)
    
    client = TwelveDataClient()
    signal_agent = SignalAgent()
    decision_agent = DecisionAgent()
    
    try:
        # تحلیل روی 4h برای swing trading
        data = client.get_time_series("XAU/USD", interval="4h", outputsize=100)
        
        signal = signal_agent.analyze(data)
        indicators = signal.metadata['indicators']
        
        logger.info(f"\n📊 Current Market Conditions:")
        logger.info(f"  Price: ${data.data[0].close:.2f}")
        logger.info(f"  RSI: {indicators['rsi']:.2f}")
        logger.info(f"  Price vs SMA(20): {((data.data[0].close / indicators['sma_20']) - 1) * 100:+.2f}%")
        logger.info(f"  Price vs SMA(50): {((data.data[0].close / indicators['sma_50']) - 1) * 100:+.2f}%")
        
        # بررسی شرایط swing trade
        rsi = indicators['rsi']
        price = data.data[0].close
        sma_20 = indicators['sma_20']
        sma_50 = indicators['sma_50']
        
        logger.info(f"\n🎯 Swing Trade Opportunities:")
        
        # شرایط خرید
        if rsi < 40 and price > sma_50 and sma_20 > sma_50:
            logger.info("  ✅ BULLISH SETUP DETECTED:")
            logger.info("     • RSI oversold but trend is up (price > SMA50)")
            logger.info("     • Golden cross in place (SMA20 > SMA50)")
            logger.info("     → Consider LONG position")
            logger.info("     → Stop Loss: Below recent low")
            logger.info("     → Target: Recent high or resistance")
        
        # شرایط فروش
        elif rsi > 60 and price < sma_50 and sma_20 < sma_50:
            logger.info("  ✅ BEARISH SETUP DETECTED:")
            logger.info("     • RSI overbought but trend is down (price < SMA50)")
            logger.info("     • Death cross in place (SMA20 < SMA50)")
            logger.info("     → Consider SHORT position")
            logger.info("     → Stop Loss: Above recent high")
            logger.info("     → Target: Recent low or support")
        
        else:
            logger.info("  ⏳ NO CLEAR SETUP - Wait for better opportunity")
            
            if rsi > 70:
                logger.info("     • Market overbought - wait for pullback")
            elif rsi < 30:
                logger.info("     • Market oversold - wait for reversal confirmation")
            else:
                logger.info("     • Market in neutral zone - wait for breakout")
        
        logger.info("="*60)
        
    finally:
        client.close()


# ============================================================
# USE CASE 4: Risk Management Calculator
# ============================================================

def calculate_position_size(account_size: float, risk_percent: float = 1.0):
    """
    محاسبه اندازه position بر اساس مدیریت ریسک.
    
    Args:
        account_size: میزان سرمایه (دلار)
        risk_percent: درصد ریسک هر معامله (پیش‌فرض: 1%)
    """
    logger.info("\n" + "="*60)
    logger.info("💰 Position Size Calculator")
    logger.info("="*60)
    
    client = TwelveDataClient()
    signal_agent = SignalAgent()
    
    try:
        data = client.get_time_series("XAU/USD", interval="1h", outputsize=100)
        signal = signal_agent.analyze(data)
        
        current_price = data.data[0].close
        atr = signal.metadata['indicators']['atr']
        
        # محاسبه stop loss بر اساس ATR
        stop_loss_distance = atr * 2  # 2x ATR
        
        # محاسبه ریسک
        risk_amount = account_size * (risk_percent / 100)
        
        # محاسبه تعداد واحد
        position_size = risk_amount / stop_loss_distance
        position_value = position_size * current_price
        
        logger.info(f"\n📊 Market Info:")
        logger.info(f"  Current Price: ${current_price:.2f}")
        logger.info(f"  ATR (volatility): ${atr:.2f}")
        
        logger.info(f"\n💼 Account Info:")
        logger.info(f"  Account Size: ${account_size:,.2f}")
        logger.info(f"  Risk per Trade: {risk_percent}% (${risk_amount:,.2f})")
        
        logger.info(f"\n🎯 Position Sizing:")
        logger.info(f"  Stop Loss Distance: ${stop_loss_distance:.2f} (2x ATR)")
        logger.info(f"  Position Size: {position_size:.4f} units")
        logger.info(f"  Position Value: ${position_value:,.2f}")
        logger.info(f"  Stop Loss Level: ${current_price - stop_loss_distance:.2f}")
        logger.info(f"  Take Profit (2:1): ${current_price + (stop_loss_distance * 2):.2f}")
        
        logger.info(f"\n📈 Trade Plan:")
        if signal.signal > 0.3:
            logger.info(f"  Direction: LONG")
            logger.info(f"  Entry: ${current_price:.2f}")
            logger.info(f"  Stop Loss: ${current_price - stop_loss_distance:.2f}")
            logger.info(f"  Take Profit: ${current_price + (stop_loss_distance * 2):.2f}")
        elif signal.signal < -0.3:
            logger.info(f"  Direction: SHORT")
            logger.info(f"  Entry: ${current_price:.2f}")
            logger.info(f"  Stop Loss: ${current_price + stop_loss_distance:.2f}")
            logger.info(f"  Take Profit: ${current_price - (stop_loss_distance * 2):.2f}")
        else:
            logger.info(f"  ⏳ No trade - Signal not strong enough")
        
        logger.info("="*60)
        
    finally:
        client.close()


# ============================================================
# USE CASE 5: Scheduled Alert System
# ============================================================

def create_alert_system():
    """
    سیستم هشدار برای سیگنال‌های قوی.
    این را می‌توانید با scheduler مثل APScheduler اجرا کنید.
    """
    logger.info("\n" + "="*60)
    logger.info("🔔 Alert System Check")
    logger.info("="*60)
    
    client = TwelveDataClient()
    signal_agent = SignalAgent()
    decision_agent = DecisionAgent()
    
    try:
        data = client.get_time_series("XAU/USD", interval="1h", outputsize=100)
        signal = signal_agent.analyze(data)
        decision = decision_agent.analyze([signal])
        
        # بررسی شرایط هشدار
        alerts = []
        
        # هشدار 1: سیگنال قوی
        if decision.metadata['decision'] in ['STRONG_BUY', 'STRONG_SELL']:
            alerts.append({
                "type": "STRONG_SIGNAL",
                "message": f"Strong {decision.metadata['decision']} signal detected!",
                "priority": "HIGH"
            })
        
        # هشدار 2: RSI اشباع
        rsi = signal.metadata['indicators']['rsi']
        if rsi < 30:
            alerts.append({
                "type": "OVERSOLD",
                "message": f"RSI oversold at {rsi:.2f}",
                "priority": "MEDIUM"
            })
        elif rsi > 70:
            alerts.append({
                "type": "OVERBOUGHT",
                "message": f"RSI overbought at {rsi:.2f}",
                "priority": "MEDIUM"
            })
        
        # هشدار 3: تغییر ناگهانی قیمت
        price_change = ((data.data[0].close / data.data[10].close) - 1) * 100
        if abs(price_change) > 1:  # بیش از 1% تغییر در 10 ساعت
            alerts.append({
                "type": "PRICE_MOVE",
                "message": f"Significant price move: {price_change:+.2f}%",
                "priority": "MEDIUM"
            })
        
        # نمایش هشدارها
        if alerts:
            logger.info(f"\n🔔 {len(alerts)} Alert(s) Detected:")
            for i, alert in enumerate(alerts, 1):
                logger.info(f"\n  Alert #{i} [{alert['priority']}]:")
                logger.info(f"  Type: {alert['type']}")
                logger.info(f"  Message: {alert['message']}")
            
            logger.info(f"\n💡 Current Status:")
            logger.info(f"  Price: ${data.data[0].close:.2f}")
            logger.info(f"  Signal: {signal.metadata['analysis']}")
            logger.info(f"  Decision: {decision.metadata['decision']}")
            
            # اینجا می‌توانید alert را به Telegram، Email یا ... ارسال کنید
            # send_telegram_alert(alerts)
            # send_email_alert(alerts)
        else:
            logger.info("\n✅ No alerts - Market conditions normal")
        
        logger.info("="*60)
        
        return alerts
        
    finally:
        client.close()


# ============================================================
# Main - اجرای مثال‌ها
# ============================================================

if __name__ == "__main__":
    print("\n🚀 Gold Trading System - Use Cases\n")
    print("انتخاب کنید:")
    print("1. Daily Morning Analysis")
    print("2. Multi-Timeframe Confluence")
    print("3. Swing Trading Setup")
    print("4. Position Size Calculator")
    print("5. Alert System Check")
    print()
    
    choice = input("شماره (1-5): ").strip()
    
    if choice == "1":
        daily_morning_analysis()
    elif choice == "2":
        multi_timeframe_confluence()
    elif choice == "3":
        swing_trading_setup()
    elif choice == "4":
        account = float(input("Account Size ($): "))
        risk = float(input("Risk per trade (%): "))
        calculate_position_size(account, risk)
    elif choice == "5":
        create_alert_system()
    else:
        print("❌ Invalid choice")
