"""
Simple test: ML Agent with Decision Agent
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from data_layer.client import TwelveDataClient
from agents.ml import MLAgent
from agents.signal.signal_agent import SignalAgent
from agents.decision.decision_agent import DecisionAgent
from agents.base import AgentOutput, AgentType


def main():
    print("="*80)
    print("ML AGENT + DECISION AGENT TEST")
    print("="*80)
    
    # Fetch data
    client = TwelveDataClient(api_key="e2527b8bfdac451094f85f9aa826bc65")
    market_data = client.get_time_series("XAU/USD", "1h", 200)
    
    if not market_data:
        print("Failed to fetch data")
        return
    
    print(f"\nFetched {len(market_data)} candles")
    print(f"Current price: ${market_data.data[-1].close:.2f}")
    
    # ML Agent
    print("\n1. ML Agent Analysis...")
    ml_agent = MLAgent(model_path="models/test_model.pkl")
    ml_agent.load_model()
    ml_output = ml_agent.analyze(market_data)
    
    print(f"   Recommendation: {ml_output.recommendation}")
    print(f"   Confidence: {ml_output.confidence:.1%}")
    
    # Signal Agent
    print("\n2. Signal Agent Analysis...")
    signal_agent = SignalAgent()
    signal_output = signal_agent.analyze(market_data)
    
    # تبدیل signal به recommendation
    signal_rec = "BUY" if signal_output.signal > 0.2 else "SELL" if signal_output.signal < -0.2 else "HOLD"
    
    print(f"   Recommendation: {signal_rec}")
    print(f"   Signal: {signal_output.signal:.2f}")
    print(f"   Confidence: {signal_output.confidence:.2f}")
    
    # Decision Agent
    print("\n3. Decision Agent (combining both)...")
    
    agent_outputs = [
        AgentOutput(
            agent_type=AgentType.ML,
            signal=1.0 if ml_output.recommendation == "BUY" else -1.0 if ml_output.recommendation == "SELL" else 0.0,
            confidence=ml_output.confidence,
            metadata={'source': 'ML Agent'}
        ),
        signal_output  # SignalAgent already returns AgentOutput
    ]
    
    decision_agent = DecisionAgent()
    decision_output = decision_agent.analyze(agent_outputs)
    
    print(f"   Decision: {decision_output.metadata['decision']}")
    print(f"   Signal: {decision_output.signal:.2f}")
    print(f"   Confidence: {decision_output.confidence:.2f}")
    
    # Final
    print("\n" + "="*80)
    print("FINAL RECOMMENDATION")
    print("="*80)
    
    decision = decision_output.metadata['decision']
    
    if 'BUY' in decision:
        print(f"ACTION: BUY")
        print(f"Strength: {'STRONG' if 'STRONG' in decision else 'MODERATE'}")
    elif 'SELL' in decision:
        print(f"ACTION: SELL")
        print(f"Strength: {'STRONG' if 'STRONG' in decision else 'MODERATE'}")
    else:
        print(f"ACTION: HOLD")
        print(f"Reason: Low confidence or mixed signals")
    
    print(f"\nReasoning: {decision_output.metadata['reasoning']}")
    print("="*80)


if __name__ == "__main__":
    main()
