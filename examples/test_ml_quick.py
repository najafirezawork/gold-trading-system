"""
Quick test for ML Agent
تست سریع برای بررسی ML Agent
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from data_layer.client import TwelveDataClient
from agents.ml.ml_agent import MLAgent
from agents.ml.feature_engineer import FeatureEngineer


def test_feature_engineer():
    """Test 1: Feature Engineering"""
    print("\n" + "="*60)
    print("TEST 1: FEATURE ENGINEERING")
    print("="*60)
    
    # دریافت داده
    client = TwelveDataClient(api_key="e2527b8bfdac451094f85f9aa826bc65")
    market_data = client.get_time_series("XAU/USD", "1h", 500)
    
    if not market_data:
        print("Failed to fetch data")
        return False
    
    print(f"Fetched {len(market_data)} candles")
    
    # Feature extraction
    engineer = FeatureEngineer()
    df = engineer.extract_features(market_data)
    
    print(f"\nFeatures extracted:")
    print(f"  Samples: {len(df)}")
    print(f"  Features: {len(df.columns) - 2}")  # -2 for target columns
    print(f"\nSample features:")
    print(df.head())
    
    print(f"\nTarget distribution:")
    print(df['target'].value_counts())
    
    return True


def test_ml_training():
    """Test 2: ML Model Training"""
    print("\n" + "="*60)
    print("TEST 2: ML MODEL TRAINING")
    print("="*60)
    
    # دریافت داده
    client = TwelveDataClient(api_key="e2527b8bfdac451094f85f9aa826bc65")
    market_data = client.get_time_series("XAU/USD", "1h", 1000)
    
    if not market_data:
        print("Failed to fetch data")
        return False
    
    print(f"Fetched {len(market_data)} candles")
    
    # ساخت و training
    ml_agent = MLAgent(
        confidence_threshold=0.6,
        model_path="models/test_model.pkl"
    )
    
    metrics = ml_agent.train(
        market_data=market_data,
        val_split=0.2,
        save_model=True
    )
    
    print(f"\nTraining completed successfully!")
    print(f"Validation accuracy: {metrics.get('ensemble_val_accuracy', 'N/A')}")
    
    return True


def test_ml_prediction():
    """Test 3: ML Prediction"""
    print("\n" + "="*60)
    print("TEST 3: ML PREDICTION")
    print("="*60)
    
    # دریافت داده
    client = TwelveDataClient(api_key="e2527b8bfdac451094f85f9aa826bc65")
    market_data = client.get_time_series("XAU/USD", "1h", 200)
    
    if not market_data:
        print("Failed to fetch data")
        return False
    
    print(f"Fetched {len(market_data)} candles")
    
    # بارگذاری model
    ml_agent = MLAgent(model_path="models/test_model.pkl")
    
    try:
        ml_agent.load_model()
    except FileNotFoundError:
        print("Model not found. Running training first...")
        if not test_ml_training():
            return False
        ml_agent.load_model()
    
    # Prediction
    output = ml_agent.analyze(market_data)
    
    print(f"\nPrediction:")
    print(f"  Recommendation: {output.recommendation}")
    print(f"  Confidence: {output.confidence:.1%}")
    print(f"  Reason: {output.reason}")
    
    # Explanation
    explanation = ml_agent.explain_prediction(market_data)
    
    print(f"\nTop 3 Features:")
    for i, (feature, importance) in enumerate(list(explanation['top_features']['importance'].items())[:3], 1):
        print(f"  {i}. {feature}: importance={importance:.4f}")
    
    return True


def main():
    """Run all tests"""
    print("="*60)
    print("ML AGENT QUICK TESTS")
    print("="*60)
    
    tests = [
        ("Feature Engineering", test_feature_engineer),
        ("ML Training", test_ml_training),
        ("ML Prediction", test_ml_prediction)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print(f"\nERROR in {test_name}: {e}")
            results[test_name] = "ERROR"
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results.items():
        symbol = "OK" if result == "PASS" else "FAIL"
        print(f"{symbol} {test_name}: {result}")
    print("="*60)


if __name__ == "__main__":
    main()
