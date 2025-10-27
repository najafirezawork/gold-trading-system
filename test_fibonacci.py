"""
🧪 تست اندیکاتور فیبوناچی
تست سطح‌های حمایت و مقاومت فیبوناچی
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.signal.indicators import TechnicalIndicators


def test_fibonacci():
    """تست اندیکاتور فیبوناچی"""
    
    print("\n" + "="*80)
    print("  🔍 تست اندیکاتور فیبوناچی - سطح‌های حمایت و مقاومت")
    print("="*80 + "\n")
    
    indicators = TechnicalIndicators()
    
    # مثال 1: طلا از $4,000 به $4,500
    print("📊 مثال 1: صعود طلا از $4,000 به $4,500\n")
    
    high = 4500.0
    low = 4000.0
    
    fib_levels = indicators.calculate_fibonacci_retracements(high, low)
    
    print("سطح‌های فیبوناچی:")
    print("-" * 50)
    for level, price in sorted(fib_levels.items(), key=lambda x: float(x[0])):
        bar = "█" * int((float(level) / 100) * 30)
        print(f"  {level:>6}% → ${price:>8.2f}  {bar}")
    
    # بررسی قیمت‌های مختلف
    print("\n📍 تست قیمت‌های مختلف:\n")
    
    test_prices = [
        (4500, "نقطه بالا"),
        (4430, "نزدیک 61.8% (حمایت قوی)"),
        (4360, "نزدیک 50% (حمایت متوسط)"),
        (4290, "نزدیک 38.2% (حمایت ضعیف)"),
        (4220, "نزدیک 23.6% (حمایت ضعیفترین)"),
        (4000, "نقطه پایین"),
    ]
    
    for price, description in test_prices:
        signal = indicators.get_fibonacci_signal(price, fib_levels)
        
        print(f"💰 قیمت: ${price:.2f} ({description})")
        print(f"   ├─ نزدیکترین سطح: {signal['nearest_level']}%")
        print(f"   ├─ قیمت سطح: ${signal['nearest_price']:.2f}")
        print(f"   ├─ فاصله: ${signal['distance']:.2f}")
        print(f"   ├─ قدرت سیگنال: {signal['signal_strength']:.1%}")
        
        if signal['is_at_support']:
            print(f"   └─ ✅ در سطح حمایت!")
        else:
            print(f"   └─ ❌ دور از سطح حمایت")
        print()
    
    # مثال 2: سقوط طلا
    print("\n" + "="*80)
    print("  📉 مثال 2: سقوط طلا از $4,500 به $4,000\n")
    
    # درج‌انجام سقوط
    high = 4500.0
    low = 4000.0
    
    fib_levels_down = indicators.calculate_fibonacci_retracements(high, low)
    
    print("سطح‌های حمایت (از بالا به پایین):")
    print("-" * 50)
    
    descending_levels = sorted(fib_levels_down.items(), 
                              key=lambda x: float(x[0]), 
                              reverse=True)
    
    for level, price in descending_levels:
        if level == "100":
            print(f"  {level:>6}% → ${price:>8.2f}  ← نقطه شروع سقوط")
        elif level == "0":
            print(f"  {level:>6}% → ${price:>8.2f}  ← پایینترین سطح حمایت")
        else:
            print(f"  {level:>6}% → ${price:>8.2f}  ← سطح حمایت {level}%")
    
    # تحلیل سیناریو سقوط
    print("\n📋 سناریو سقوط تدریجی:\n")
    
    fall_sequence = [
        (4500, "شروع سقوط"),
        (4430, "اول حمایت (61.8%) - خیلی قوی"),
        (4360, "دوم حمایت (50%)"),
        (4290, "سوم حمایت (38.2%)"),
        (4220, "چهارم حمایت (23.6%)"),
        (4100, "زیر تمام سطح‌ها - بدون حمایت!"),
    ]
    
    for i, (price, description) in enumerate(fall_sequence, 1):
        signal = indicators.get_fibonacci_signal(price, fib_levels_down)
        
        status = "🟢 حمایت" if signal['is_at_support'] else "🔴 بدون حمایت"
        print(f"{i}. ${price:.2f} - {description}")
        print(f"   {status} (نزدیکترین: {signal['nearest_level']}% @ ${signal['nearest_price']:.2f})\n")
    
    # توصیه‌های عملی
    print("="*80)
    print("  💡 توصیه‌های عملی برای معامله‌گران\n")
    
    print("✅ خرید در سطح‌های فیبوناچی:")
    print("   1. 61.8% → قوی‌ترین حمایت (75% موفقیت)")
    print("   2. 50% → حمایت متوسط (60% موفقیت)")
    print("   3. 38.2% → حمایت ضعیف (45% موفقیت)\n")
    
    print("🛑 Stop Loss:")
    print("   • اگر قیمت زیر 23.6% سقوط کند = برگشتی نیست")
    print("   • Exit در 0% (نقطه پایین)\n")
    
    print("🎯 Target:")
    print("   • از 61.8% خرید → هدف: 100% (نقطه بالا)")
    print("   • Risk/Reward: خوب! (1:2+)\n")
    
    print("⚠️  تشخیص معکوس:")
    print("   • اگر قیمت تمام سطح‌ها را شکست → روند نزولی قوی")
    print("   • آنجا حتی فیبوناچی کار نمی‌کند!\n")
    
    print("="*80)
    print("  ✅ تست فیبوناچی کامل شد!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_fibonacci()
