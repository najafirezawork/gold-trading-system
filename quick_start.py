"""
Quick Start Example - استفاده ساده و سریع

این مثال نحوه استفاده ساده از سیستم را نشان می‌دهد.
"""

from main import TradingSystem


def quick_start():
    """مثال استفاده سریع"""
    
    print("="*60)
    print("🏆 Gold Trading Signal System - Quick Start")
    print("="*60)
    print()
    
    # ایجاد سیستم
    system = TradingSystem()
    
    # اجرای تحلیل برای طلا
    print("📊 در حال تحلیل طلا (XAU/USD)...")
    print()
    
    result = system.run_analysis(
        symbol="XAU/USD",    # نماد طلا
        interval="1h",       # بازه زمانی 1 ساعته
        outputsize=100       # 100 کندل
    )
    
    # بستن اتصال
    system.close()
    
    print()
    print("="*60)
    print("✅ تحلیل کامل شد!")
    print("="*60)


if __name__ == "__main__":
    quick_start()
