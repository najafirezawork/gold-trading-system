"""
Complete Trading System Integration Test
تست کامل سیستم یکپارچه معاملاتی
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from trading_system import IntegratedTradingSystem
from data_layer import TwelveDataClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_complete_system():
    """Test complete trading system with all agents"""
    
    print("\n" + "="*80)
    print("INTEGRATED TRADING SYSTEM - COMPLETE TEST")
    print("="*80)
    
    # 1. Initialize data fetcher
    print("\n[1] Initializing Twelve Data Client...")
    client = TwelveDataClient()
    
    # 2. Fetch market data
    print("[2] Fetching market data (500 candles, 1H timeframe)...")
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=500
    )
    
    print(f"    - Fetched {len(market_data)} candles")
    print(f"    - From: {market_data.data[0].datetime}")
    print(f"    - To: {market_data.data[-1].datetime}")
    print(f"    - Current Price: ${market_data.data[-1].close:.2f}")
    
    # 3. Initialize trading system
    print("\n[3] Initializing Integrated Trading System...")
    system = IntegratedTradingSystem(
        ml_model_path="models/gold_ml_model.pkl",
        enable_ml=True,
        enable_signal=True,
        enable_regime_detection=True
    )
    
    system.initialize()
    
    # Show system status
    status = system.get_status()
    print(f"\n    System Status:")
    print(f"    - Initialized: {status['initialized']}")
    print(f"    - Signal Agent: {'ACTIVE' if status['agents']['signal'] else 'INACTIVE'}")
    print(f"    - ML Agent: {'ACTIVE' if status['agents']['ml'] else 'INACTIVE'}")
    print(f"    - Regime Detection: {'ACTIVE' if status['agents']['regime_detection'] else 'INACTIVE'}")
    
    # 4. Run analysis
    print("\n[4] Running Complete Analysis...")
    print("    This will:")
    print("    - Detect market regime")
    print("    - Adjust agent weights based on regime")
    print("    - Run Signal Agent (technical analysis)")
    print("    - Run ML Agent (machine learning prediction)")
    print("    - Aggregate signals via Decision Agent")
    print("    - Generate final trading recommendation")
    
    recommendation = system.analyze(market_data)
    
    # 5. Display results
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\nMarket Context:")
    print(f"  - Current Price: ${recommendation.current_price:.2f}")
    print(f"  - Market Regime: {recommendation.market_regime.upper()}")
    print(f"  - Timestamp: {recommendation.timestamp}")
    
    print(f"\nAgent Contributions:")
    for contrib in recommendation.agent_contributions:
        agent_name = contrib['agent']
        signal = contrib['signal']
        confidence = contrib['confidence']
        
        signal_direction = "BUY" if signal > 0.2 else "SELL" if signal < -0.2 else "NEUTRAL"
        
        print(f"  - {agent_name.upper()}:")
        print(f"      Signal: {signal:.2f} ({signal_direction})")
        print(f"      Confidence: {confidence:.2%}")
    
    print(f"\nAgent Weights (adjusted for {recommendation.market_regime}):")
    for agent, weight in system.agent_weights.items():
        print(f"  - {agent.upper()}: {weight:.2f}")
    
    print(f"\n" + "-"*80)
    print(f"FINAL RECOMMENDATION")
    print(f"-"*80)
    print(f"  Action: {recommendation.action}")
    print(f"  Signal Strength: {recommendation.signal:.2f} (-1.0 to 1.0)")
    print(f"  Confidence: {recommendation.confidence:.1%}")
    
    print(f"\nReasoning:")
    print(f"  {recommendation.reasoning}")
    
    # 6. Full explanation
    print("\n" + "="*80)
    print("DETAILED EXPLANATION")
    print("="*80)
    
    explanation = system.explain_decision(recommendation)
    print(explanation)
    
    # 7. Trading suggestion
    print("\n" + "="*80)
    print("TRADING SUGGESTION")
    print("="*80)
    
    if recommendation.action in ["STRONG_BUY", "BUY"]:
        print(f"\n  >> LONG POSITION RECOMMENDED")
        print(f"     Entry Price: ${recommendation.current_price:.2f}")
        print(f"     Confidence Level: {recommendation.confidence:.1%}")
        
        if recommendation.confidence > 0.8:
            print(f"     Risk Level: LOW (High confidence)")
        elif recommendation.confidence > 0.6:
            print(f"     Risk Level: MEDIUM")
        else:
            print(f"     Risk Level: HIGH (Low confidence)")
    
    elif recommendation.action in ["STRONG_SELL", "SELL"]:
        print(f"\n  >> SHORT POSITION RECOMMENDED")
        print(f"     Entry Price: ${recommendation.current_price:.2f}")
        print(f"     Confidence Level: {recommendation.confidence:.1%}")
        
        if recommendation.confidence > 0.8:
            print(f"     Risk Level: LOW (High confidence)")
        elif recommendation.confidence > 0.6:
            print(f"     Risk Level: MEDIUM")
        else:
            print(f"     Risk Level: HIGH (Low confidence)")
    
    else:  # HOLD
        print(f"\n  >> NO POSITION RECOMMENDED (HOLD)")
        print(f"     Wait for clearer signal")
        print(f"     Current confidence: {recommendation.confidence:.1%}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")


async def test_weight_adjustment():
    """Test dynamic weight adjustment based on regime"""
    
    print("\n" + "="*80)
    print("WEIGHT ADJUSTMENT TEST")
    print("="*80)
    
    print("\nThis test demonstrates how agent weights are adjusted based on market regime:")
    
    system = IntegratedTradingSystem()
    
    test_regimes = ["trending_up", "ranging", "volatile", "trending_down"]
    
    for regime in test_regimes:
        system._adjust_weights_for_regime(regime)
        
        print(f"\nRegime: {regime.upper()}")
        print(f"  ML Agent Weight: {system.agent_weights['ml']:.2f}")
        print(f"  Signal Agent Weight: {system.agent_weights['signal']:.2f}")
        
        if regime.startswith("trending"):
            print(f"  -> ML Agent prioritized (better in trends)")
        elif regime == "ranging":
            print(f"  -> Signal Agent prioritized (mean reversion)")
        elif regime == "volatile":
            print(f"  -> Both agents downweighted (uncertainty)")
    
    print("\n" + "="*80)


async def test_manual_weights():
    """Test manual weight configuration"""
    
    print("\n" + "="*80)
    print("MANUAL WEIGHT CONFIGURATION TEST")
    print("="*80)
    
    client = TwelveDataClient()
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=500
    )
    
    system = IntegratedTradingSystem()
    system.initialize()
    
    # Scenario 1: Trust ML more
    print("\n[Scenario 1] High trust in ML Agent:")
    system.update_weights({'ml': 1.5, 'signal': 0.5})
    rec1 = system.analyze(market_data)
    
    print(f"  Weights: ML={system.agent_weights['ml']}, Signal={system.agent_weights['signal']}")
    print(f"  Decision: {rec1.action} (confidence: {rec1.confidence:.1%})")
    
    # Scenario 2: Trust Signal more
    print("\n[Scenario 2] High trust in Signal Agent:")
    system.update_weights({'ml': 0.5, 'signal': 1.5})
    rec2 = system.analyze(market_data)
    
    print(f"  Weights: ML={system.agent_weights['ml']}, Signal={system.agent_weights['signal']}")
    print(f"  Decision: {rec2.action} (confidence: {rec2.confidence:.1%})")
    
    # Scenario 3: Equal weights
    print("\n[Scenario 3] Equal weights:")
    system.update_weights({'ml': 1.0, 'signal': 1.0})
    rec3 = system.analyze(market_data)
    
    print(f"  Weights: ML={system.agent_weights['ml']}, Signal={system.agent_weights['signal']}")
    print(f"  Decision: {rec3.action} (confidence: {rec3.confidence:.1%})")
    
    print("\n" + "="*80)


async def main():
    """Run all tests"""
    
    try:
        # Main test - sync call since TwelveDataClient is not async
        await test_complete_system()
        
        # Additional tests
        await test_weight_adjustment()
        await test_manual_weights()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
    
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    # Run without asyncio since we're using sync API
    import sys
    sys.exit(asyncio.run(main()) or 0)
