"""
خلاصه فیبوناچی - نمایش سریع
"""

from agents.signal.indicators import TechnicalIndicators

print("\n" + "="*70)
print("  🔍 فیبوناچی اندیکاتور - خلاصه سریع")
print("="*70)

ind = TechnicalIndicators()

# مثال
high = 4500.0
low = 4000.0
fib = ind.calculate_fibonacci_retracements(high, low)

print(f"\n💰 محدوده قیمت: ${low:.0f} تا ${high:.0f}")
print(f"📊 دامنه: ${high-low:.0f}\n")

print("سطح‌های فیبوناچی:")
for level in ['0', '23.6', '38.2', '50.0', '61.8', '78.6', '100']:
    price = fib[level]
    if level == '61.8':
        print(f'  {level:>5}% → ${price:>8.2f}  ⭐ نسبت طلایی')
    elif level == '50.0':
        print(f'  50.0% → ${price:>8.2f}  ═ نقطه میانی')
    elif level in ['0', '100']:
        print(f'  {level:>5}% → ${price:>8.2f}  ◆ نقطه انتهایی')
    else:
        print(f'  {level:>5}% → ${price:>8.2f}')

print("\n" + "="*70)

# تست موقعیت
test_price = 4310.0
signal = ind.get_fibonacci_signal(test_price, fib)

print(f"\n📍 قیمت فعلی: ${test_price:.2f}")
print(f"  └─ نزدیکترین سطح: {signal['nearest_level']}% @ ${signal['nearest_price']:.2f}")
print(f"  └─ در حمایت: {'✅ بله' if signal['is_at_support'] else '❌ خیر'}")

print("\n" + "="*70)
print("  ✅ فیبوناچی آماده برای استفاده است!")
print("="*70 + "\n")
