#!/usr/bin/env python3
"""
🎯 تست ML Agent به عنوان Continuous Signal Generator
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from agents.ml.ml_agent import MLAgent
from agents.ml.models import RandomForestModel
from data_layer.client import TwelveDataClient


def test_ml_signal_generator():
    """
    تست ML Agent با نقش جدید: Signal Generator
    """
    print(f"{'='*70}")
    print(f"🎯 ML Agent - Continuous Signal Generator Test")
    print(f"{'='*70}\n")
    
    # ایجاد agent
    print("1️⃣ Creating ML Agent...")
    agent = MLAgent(
        model=RandomForestModel(
            n_estimators=50,
            max_depth=6,
            min_samples_split=12,
            min_samples_leaf=6,
            max_features='sqrt'
        ),
        enable_feature_selection=True
    )
    print(f"✅ Agent: {agent.name}\n")
    
    # دریافت داده
    print("2️⃣ Fetching market data...")
    client = TwelveDataClient()
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=300
    )
    print(f"✅ Got {len(market_data.data)} candles\n")
    
    # Training
    print("3️⃣ Training model...")
    print(f"{'─'*70}")
    agent.train(
        market_data=market_data,
        val_split=0.2,
        save_model=False
    )
    print(f"{'─'*70}\n")
    
    # Analysis - Signal Generation
    print("4️⃣ Generating Signals...")
    print(f"{'─'*70}")
    
    signal = agent.analyze(market_data)
    
    print(f"\n📊 ML Agent Output (Continuous Signals):")
    print(f"{'='*70}")
    print(f"  prob_up:        {signal.prob_up:.4f}  ({signal.prob_up*100:.2f}%)")
    print(f"  prob_down:      {signal.prob_down:.4f}  ({signal.prob_down*100:.2f}%)")
    print(f"  trend_strength: {signal.trend_strength:.4f}  ({signal.trend_strength*100:.2f}%)")
    print(f"  volatility:     {signal.volatility:.4f}  ({signal.volatility*100:.2f}%)")
    print(f"  momentum:       {signal.momentum:+.4f}  ({signal.momentum*100:+.2f}%)")
    print(f"{'='*70}\n")
    
    # Interpretation
    print(f"💡 Interpretation:")
    print(f"{'─'*70}")
    
    if signal.momentum > 0.3:
        print(f"  🟢 Strong bullish momentum")
    elif signal.momentum > 0.1:
        print(f"  🟡 Moderate bullish momentum")
    elif signal.momentum < -0.3:
        print(f"  🔴 Strong bearish momentum")
    elif signal.momentum < -0.1:
        print(f"  🟡 Moderate bearish momentum")
    else:
        print(f"  ⚪ Neutral momentum")
    
    if signal.trend_strength > 0.6:
        print(f"  📈 Strong trend detected")
    elif signal.trend_strength > 0.4:
        print(f"  📊 Moderate trend")
    else:
        print(f"  📉 Weak trend / Ranging")
    
    if signal.volatility > 0.7:
        print(f"  ⚡ High volatility")
    elif signal.volatility > 0.4:
        print(f"  🌊 Moderate volatility")
    else:
        print(f"  💤 Low volatility")
    
    print(f"\n{'─'*70}")
    print(f"❌ NO BUY/SELL/HOLD HERE!")
    print(f"✅ These are pure signals for Decision Agent")
    print(f"{'─'*70}\n")
    
    # JSON Output
    print(f"📋 JSON Output Example:")
    print(f"{'─'*70}")
    
    import json
    output_dict = {
        "prob_up": round(signal.prob_up, 4),
        "prob_down": round(signal.prob_down, 4),
        "trend_strength": round(signal.trend_strength, 4),
        "volatility": round(signal.volatility, 4),
        "momentum": round(signal.momentum, 4)
    }
    
    print(json.dumps(output_dict, indent=2))
    print(f"{'─'*70}\n")
    
    print(f"✅ Test completed!\n")
    
    return signal


if __name__ == "__main__":
    try:
        test_ml_signal_generator()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
