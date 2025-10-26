"""
Simple example of using the Integrated Trading System
مثال ساده استفاده از سیستم یکپارچه
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from trading_system import IntegratedTradingSystem
from data_layer import TwelveDataClient


def simple_example():
    """Simple usage example"""
    
    print("\n" + "="*70)
    print("INTEGRATED TRADING SYSTEM - SIMPLE EXAMPLE")
    print("="*70)
    
    # 1. Fetch data
    print("\n[1] Fetching market data...")
    client = TwelveDataClient()
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=500
    )
    print(f"    Fetched {len(market_data)} candles")
    print(f"    Current Price: ${market_data.data[-1].close:.2f}")
    
    # 2. Initialize system
    print("\n[2] Initializing trading system...")
    system = IntegratedTradingSystem()
    system.initialize()
    
    status = system.get_status()
    print(f"    Signal Agent: {'✓' if status['agents']['signal'] else '✗'}")
    print(f"    ML Agent: {'✓' if status['agents']['ml'] else '✗'}")
    print(f"    Regime Detection: {'✓' if status['agents']['regime_detection'] else '✗'}")
    
    # 3. Get recommendation
    print("\n[3] Analyzing market and generating recommendation...")
    recommendation = system.analyze(market_data)
    
    # 4. Display results
    print("\n" + "="*70)
    print("TRADING RECOMMENDATION")
    print("="*70)
    
    print(f"\nMarket Information:")
    print(f"  Symbol: XAU/USD (Gold)")
    print(f"  Current Price: ${recommendation.current_price:.2f}")
    print(f"  Market Regime: {recommendation.market_regime.upper()}")
    print(f"  Timestamp: {recommendation.timestamp}")
    
    print(f"\nRecommendation:")
    print(f"  Action: {recommendation.action}")
    print(f"  Signal: {recommendation.signal:.2f} (-1.0 to 1.0)")
    print(f"  Confidence: {recommendation.confidence:.1%}")
    
    # Trading suggestion
    if recommendation.confidence > 0.7:
        risk_level = "LOW"
    elif recommendation.confidence > 0.5:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    print(f"  Risk Level: {risk_level}")
    
    if recommendation.action in ["STRONG_BUY", "BUY"]:
        print(f"\n  → Consider LONG position")
    elif recommendation.action in ["STRONG_SELL", "SELL"]:
        print(f"\n  → Consider SHORT position")
    else:
        print(f"\n  → HOLD - Wait for clearer signal")
    
    print(f"\nReasoning:")
    for line in recommendation.reasoning.split('.'):
        if line.strip():
            print(f"  • {line.strip()}")
    
    print(f"\nAgent Contributions:")
    for contrib in recommendation.agent_contributions:
        agent = contrib['agent']
        signal = contrib['signal']
        confidence = contrib['confidence']
        
        direction = "BUY" if signal > 0.2 else "SELL" if signal < -0.2 else "NEUTRAL"
        
        print(f"  • {agent.upper()}: {direction} (confidence: {confidence:.1%})")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    simple_example()
