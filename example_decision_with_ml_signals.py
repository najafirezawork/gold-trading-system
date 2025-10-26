#!/usr/bin/env python3
"""
🧠 مثال: نحوه استفاده از ML Signals در Decision Agent

این فایل نشان می‌دهد چطور Decision Agent باید از ML Signals استفاده کند.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from agents.ml.ml_agent import MLAgent
from agents.signal.signal_agent import SignalAgent
from agents.ml.models import RandomForestModel
from data_layer.client import TwelveDataClient


class SimpleDecisionAgent:
    """
    🧠 Decision Agent ساده
    
    این agent از signals مختلف استفاده می‌کند و تصمیم می‌گیرد.
    """
    
    def __init__(
        self,
        ml_agent: MLAgent,
        signal_agent: SignalAgent,
        ml_threshold: float = 0.65,
        trend_threshold: float = 0.15
    ):
        """
        Initialize Decision Agent
        
        Args:
            ml_agent: ML Agent برای دریافت سیگنال‌های ML
            signal_agent: Signal Agent برای دریافت سیگنال‌های Technical
            ml_threshold: حداقل احتمال ML برای تصمیم (default: 0.65)
            trend_threshold: حداقل قدرت ترند برای تصمیم (default: 0.15 - کالیبره شده با مقیاس واقعی)
        """
        self.ml_agent = ml_agent
        self.signal_agent = signal_agent
        self.ml_threshold = ml_threshold
        self.trend_threshold = trend_threshold
        self.ml_agent = ml_agent
        self.signal_agent = signal_agent
        self.ml_threshold = ml_threshold
        self.trend_threshold = trend_threshold
    
    def decide(self, market_data):
        """
        تصمیم‌گیری بر اساس ترکیب signals
        
        Returns:
            dict: {
                "action": "BUY" | "SELL" | "HOLD",
                "confidence": float,
                "reason": str,
                "signals": dict
            }
        """
        # ========================================
        # 1️⃣ دریافت ML Signals
        # ========================================
        ml_signal = self.ml_agent.analyze(market_data)
        
        print(f"\n🤖 ML Signals:")
        print(f"   prob_up:        {ml_signal.prob_up:.2%}")
        print(f"   prob_down:      {ml_signal.prob_down:.2%}")
        print(f"   trend_strength: {ml_signal.trend_strength:.2%}")
        print(f"   volatility:     {ml_signal.volatility:.2%}")
        print(f"   momentum:       {ml_signal.momentum:+.2%}")
        
        # ========================================
        # 2️⃣ دریافت Technical Signals
        # ========================================
        tech_signal = self.signal_agent.analyze(market_data)
        
        print(f"\n📊 Technical Signals:")
        print(f"   signal:         {tech_signal.signal:+.2f}")
        print(f"   confidence:     {tech_signal.confidence:.2%}")
        
        # تبدیل signal به recommendation برای نمایش
        if tech_signal.signal > 0.3:
            tech_recommendation = "BUY"
        elif tech_signal.signal < -0.3:
            tech_recommendation = "SELL"
        else:
            tech_recommendation = "HOLD"
        
        print(f"   interpretation: {tech_recommendation}")
        
        # ========================================
        # 3️⃣ Decision Logic
        # ========================================
        print(f"\n🧠 Decision Process:")
        print(f"{'─'*60}")
        
        action = "HOLD"
        confidence = 0.5
        reasons = []
        
        # Strategy 1: Strong ML Signal + Strong Trend (قوی)
        if (ml_signal.prob_up > self.ml_threshold and 
            ml_signal.trend_strength > self.trend_threshold):
            
            action = "BUY"
            confidence = ml_signal.prob_up * ml_signal.trend_strength
            reasons.append(f"Strong Buy: ML shows {ml_signal.prob_up:.0%} UP probability")
            reasons.append(f"Trend strength: {ml_signal.trend_strength:.2%}")
            
            print(f"   ✅ Condition met: Strong bullish ML + Trend")
        
        elif (ml_signal.prob_down > self.ml_threshold and 
              ml_signal.trend_strength > self.trend_threshold):
            
            action = "SELL"
            confidence = ml_signal.prob_down * ml_signal.trend_strength
            reasons.append(f"Strong Sell: ML shows {ml_signal.prob_down:.0%} DOWN probability")
            reasons.append(f"Trend strength: {ml_signal.trend_strength:.2%}")
            
            print(f"   ✅ Condition met: Strong bearish ML + Trend")
        
        # Strategy 2: Technical + ML Momentum Agreement (متوسط)
        elif tech_recommendation == "BUY" and ml_signal.momentum > 0:
            action = "BUY"
            confidence = (tech_signal.confidence + ml_signal.prob_up) / 2
            reasons.append("Weak Buy: Technical bullish")
            reasons.append(f"ML momentum positive ({ml_signal.momentum:+.3f})")
            
            print(f"   ✅ Condition met: Technical + ML agree (bullish)")
        
        elif tech_recommendation == "SELL" and ml_signal.momentum < 0:
            action = "SELL"
            confidence = (tech_signal.confidence + ml_signal.prob_down) / 2
            reasons.append("Weak Sell: Technical bearish")
            reasons.append(f"ML momentum negative ({ml_signal.momentum:+.3f})")
            
            print(f"   ✅ Condition met: Technical + ML agree (bearish)")
        
        # No clear signal
        else:
            reasons.append("No clear signal from ML or Technical")
            reasons.append(f"ML: {ml_signal.prob_up:.0%} UP vs {ml_signal.prob_down:.0%} DOWN")
            reasons.append(f"Trend strength too weak ({ml_signal.trend_strength:.0%})")
            
            print(f"   ⚠️ No condition met: Holding position")
        
        # Risk adjustment based on volatility
        if ml_signal.volatility > 0.7:
            confidence *= 0.8  # کاهش confidence در نوسان بالا
            reasons.append(f"⚡ High volatility ({ml_signal.volatility:.0%}) - reduced confidence")
            print(f"   ⚠️ High volatility: Confidence reduced")
        
        print(f"{'─'*60}\n")
        
        # ========================================
        # 4️⃣ Final Decision
        # ========================================
        decision = {
            "action": action,
            "confidence": confidence,
            "reason": " | ".join(reasons),
            "signals": {
                "ml": {
                    "prob_up": ml_signal.prob_up,
                    "prob_down": ml_signal.prob_down,
                    "trend_strength": ml_signal.trend_strength,
                    "volatility": ml_signal.volatility,
                    "momentum": ml_signal.momentum
                },
                "technical": {
                    "signal": tech_signal.signal,
                    "confidence": tech_signal.confidence,
                    "interpretation": tech_recommendation
                }
            }
        }
        
        return decision


def example_decision_flow():
    """
    مثال کامل: از ML Signal تا Decision
    """
    print(f"{'='*70}")
    print(f"🧠 Decision Agent - Using ML Signals Example")
    print(f"{'='*70}\n")
    
    # 1. Setup agents
    print("1️⃣ Setting up agents...")
    
    ml_agent = MLAgent(
        model=RandomForestModel(
            n_estimators=50,
            max_depth=6,
            min_samples_split=12,
            min_samples_leaf=6,
            max_features='sqrt'
        ),
        enable_feature_selection=True
    )
    
    signal_agent = SignalAgent()
    
    print(f"✅ ML Agent: {ml_agent.name}")
    print(f"✅ Signal Agent: {signal_agent.name}")
    
    # 2. Get data
    print(f"\n2️⃣ Fetching market data...")
    client = TwelveDataClient()
    market_data = client.get_time_series("XAU/USD", "1h", 500)
    print(f"✅ Got {len(market_data.data)} candles")
    
    # 3. Train ML Agent
    print(f"\n3️⃣ Training ML Agent...")
    print(f"{'─'*70}")
    ml_agent.train(market_data, val_split=0.2, save_model=False)
    print(f"{'─'*70}")
    
    # 4. Create Decision Agent
    print(f"\n4️⃣ Creating Decision Agent...")
    decision_agent = SimpleDecisionAgent(
        ml_agent=ml_agent,
        signal_agent=signal_agent,
        ml_threshold=0.65,
        trend_threshold=0.5
    )
    print(f"✅ Decision Agent ready")
    
    # 5. Make Decision
    print(f"\n5️⃣ Making Trading Decision...")
    print(f"{'='*70}")
    
    decision = decision_agent.decide(market_data)
    
    # 6. Display Result
    print(f"\n{'='*70}")
    print(f"📋 FINAL DECISION")
    print(f"{'='*70}")
    print(f"  🎯 Action:     {decision['action']}")
    print(f"  📊 Confidence: {decision['confidence']:.2%}")
    print(f"  💡 Reason:     {decision['reason']}")
    print(f"{'='*70}\n")
    
    # 7. Explain the flow
    print(f"📖 Flow Summary:")
    print(f"{'─'*70}")
    print(f"  1. Market Data → ML Agent")
    print(f"     ↓ ML generates continuous signals (NO decision)")
    print(f"  2. ML Signals → Decision Agent")
    print(f"     ↓ Decision Agent analyzes signals")
    print(f"  3. Market Data → Signal Agent")
    print(f"     ↓ Signal Agent provides technical signals")
    print(f"  4. Technical Signals → Decision Agent")
    print(f"     ↓ Decision Agent combines all signals")
    print(f"  5. Decision Agent → Trading Action (BUY/SELL/HOLD)")
    print(f"{'─'*70}\n")
    
    print(f"✅ Example completed!\n")


if __name__ == "__main__":
    try:
        example_decision_flow()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
