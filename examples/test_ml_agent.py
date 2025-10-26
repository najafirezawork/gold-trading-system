"""
Example: ML Agent Training and Usage
Train ML model and use with Decision Agent
"""

import sys
from pathlib import Path

# اضافه کردن root directory به path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from data_layer.client import TwelveDataClient
from agents.ml.ml_agent import MLAgent
from agents.ml.models import RandomForestModel, XGBoostModel, EnsembleModel
from agents.signal.signal_agent import SignalAgent
from agents.decision.decision_agent import DecisionAgent


def train_ml_model():
    """
    بخش 1: Train ML Model
    """
    print("="*80)
    print("PART 1: TRAINING ML MODEL")
    print("="*80)
    
    # دریافت داده تاریخی
    print("\nFetching historical data...")
    client = TwelveDataClient(api_key="e2527b8bfdac451094f85f9aa826bc65")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=2000  # 2000 candles برای training
    )
    
    if not market_data:
        print("Failed to fetch data")
        return None
    
    print(f"Fetched {len(market_data)} candles")
    print(f"Period: {market_data.data[0].datetime} to {market_data.data[-1].datetime}")
    
    # ساخت ML Agent
    print("\nCreating ML Agent with Ensemble model (RandomForest + XGBoost)...")
    
    ml_agent = MLAgent(
        model=EnsembleModel([
            RandomForestModel(n_estimators=100, max_depth=10),
            XGBoostModel(n_estimators=100, max_depth=6)
        ]),
        confidence_threshold=0.6,
        model_path="models/gold_ml_model.pkl"
    )
    
    # Training
    metrics = ml_agent.train(
        market_data=market_data,
        val_split=0.2,
        save_model=True
    )
    
    # Backtest
    print("\nBacktesting predictions on historical data...")
    backtest_results = ml_agent.backtest_predictions(
        market_data=market_data,
        window_size=100
    )
    
    return ml_agent


def test_ml_agent_standalone():
    """
    بخش 2: Test ML Agent به تنهایی
    """
    print("\n" + "="*80)
    print("PART 2: TESTING ML AGENT (STANDALONE)")
    print("="*80)
    
    # دریافت داده جدید
    print("\nFetching current market data...")
    client = TwelveDataClient(api_key="e2527b8bfdac451094f85f9aa826bc65")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=200  # 200 candles برای context
    )
    
    if not market_data:
        print("Failed to fetch data")
        return
    
    print(f"Fetched {len(market_data)} candles")
    
    # بارگذاری model
    print("\nLoading trained model...")
    ml_agent = MLAgent(model_path="models/gold_ml_model.pkl")
    ml_agent.load_model()
    
    # Prediction
    print("\nAnalyzing current market...")
    output = ml_agent.analyze(market_data)
    
    print(f"\n{'='*60}")
    print(f"ML AGENT PREDICTION")
    print(f"{'='*60}")
    print(f"Recommendation: {output.recommendation}")
    print(f"Confidence: {output.confidence:.1%}")
    print(f"Reason: {output.reason}")
    print(f"\nMetadata:")
    for key, value in output.metadata.items():
        print(f"  {key}: {value}")
    print(f"{'='*60}")
    
    # توضیح prediction
    print("\nDetailed Prediction Explanation:")
    explanation = ml_agent.explain_prediction(market_data)
    
    print(f"\nPrediction: {explanation['prediction']} (0=DOWN, 1=UP)")
    print(f"Probabilities:")
    print(f"  UP: {explanation['probabilities']['up']:.1%}")
    print(f"  DOWN: {explanation['probabilities']['down']:.1%}")
    
    print(f"\nTop 5 Important Features:")
    for i, (feature, importance) in enumerate(list(explanation['top_features']['importance'].items())[:5], 1):
        value = explanation['top_features']['current_values'].get(feature, 'N/A')
        if isinstance(value, float):
            print(f"  {i}. {feature}: {value:.4f} (importance: {importance:.4f})")
        else:
            print(f"  {i}. {feature}: {value} (importance: {importance:.4f})")


def test_ml_with_decision_agent():
    """
    بخش 3: ML Agent + Signal Agent + Decision Agent
    """
    print("\n" + "="*80)
    print("PART 3: ML AGENT + SIGNAL AGENT + DECISION AGENT")
    print("="*80)
    
    # دریافت داده
    print("\nFetching market data...")
    client = TwelveDataClient(api_key="e2527b8bfdac451094f85f9aa826bc65")
    
    market_data = client.get_time_series(
        symbol="XAU/USD",
        interval="1h",
        outputsize=200
    )
    
    if not market_data:
        print("Failed to fetch data")
        return
    
    print(f"Fetched {len(market_data)} candles")
    
    # ساخت agents
    print("\nInitializing agents...")
    
    # ML Agent
    ml_agent = MLAgent(model_path="models/gold_ml_model.pkl")
    ml_agent.load_model()
    
    # Signal Agent
    signal_agent = SignalAgent()
    
    # Decision Agent
    decision_agent = DecisionAgent()
    
    # تحلیل
    print("\nAnalyzing with ML Agent...")
    ml_output = ml_agent.analyze(market_data)
    
    print("\nAnalyzing with Signal Agent...")
    signal_output = signal_agent.analyze(market_data)
    
    print("\nMaking final decision...")
    
    # تبدیل outputs به format مورد نیاز Decision Agent
    from agents.base import AgentOutput as BaseAgentOutput, AgentType
    
    agent_outputs = [
        BaseAgentOutput(
            agent_type=AgentType.ML,
            signal=1.0 if ml_output.recommendation == "BUY" else -1.0 if ml_output.recommendation == "SELL" else 0.0,
            confidence=ml_output.confidence,
            metadata={'source': 'ML Agent', 'raw_output': ml_output.metadata}
        ),
        BaseAgentOutput(
            agent_type=AgentType.SIGNAL,
            signal=1.0 if signal_output.recommendation == "BUY" else -1.0 if signal_output.recommendation == "SELL" else 0.0,
            confidence=signal_output.confidence,
            metadata={'source': 'Signal Agent', 'raw_output': signal_output.metadata}
        )
    ]
    
    decision_output = decision_agent.analyze(agent_outputs)
    
    # نمایش نتایج
    print(f"\n{'='*80}")
    print(f"COMBINED ANALYSIS RESULTS")
    print(f"{'='*80}")
    
    print(f"\nML Agent:")
    print(f"  Recommendation: {ml_output.recommendation}")
    print(f"  Confidence: {ml_output.confidence:.1%}")
    print(f"  Reason: {ml_output.reason}")
    
    print(f"\nSignal Agent:")
    print(f"  Recommendation: {signal_output.recommendation}")
    print(f"  Confidence: {signal_output.confidence:.1%}")
    print(f"  Reason: {signal_output.reason}")
    
    print(f"\nDecision Agent (Final):")
    print(f"  Decision: {decision_output.metadata['decision']}")
    print(f"  Signal: {decision_output.signal:.2f}")
    print(f"  Confidence: {decision_output.confidence:.2f}")
    print(f"  Reasoning: {decision_output.metadata['reasoning']}")
    
    print(f"\n{'='*80}")
    
    # توصیه نهایی
    decision = decision_output.metadata['decision']
    
    if decision in ['STRONG_BUY', 'BUY']:
        print("\nFINAL RECOMMENDATION: BUY")
        print("Both ML and technical signals suggest upward movement.")
    elif decision in ['STRONG_SELL', 'SELL']:
        print("\nFINAL RECOMMENDATION: SELL")
        print("Both ML and technical signals suggest downward movement.")
    else:
        print("\nFINAL RECOMMENDATION: HOLD")
        print("Mixed signals or low confidence. Better to wait.")
    
    print(f"{'='*80}\n")


def main():
    """
    Main function - اجرای همه بخش‌ها
    """
    
    # انتخاب: کدام بخش را اجرا کنیم؟
    print("Choose option:")
    print("1. Train ML Model (takes 2-3 minutes)")
    print("2. Test ML Agent (standalone)")
    print("3. Test ML + Signal + Decision Agents")
    print("4. Run all")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        train_ml_model()
    
    elif choice == '2':
        test_ml_agent_standalone()
    
    elif choice == '3':
        test_ml_with_decision_agent()
    
    elif choice == '4':
        # همه را اجرا کن
        ml_agent = train_ml_model()
        
        if ml_agent:
            test_ml_agent_standalone()
            test_ml_with_decision_agent()
    
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
