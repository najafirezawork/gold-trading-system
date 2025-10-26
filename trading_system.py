"""
Integrated Trading System
سیستم یکپارچه معاملاتی که همه agents را ترکیب می‌کند
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

from agents.base import AgentOutput, AgentType
from agents.signal.signal_agent import SignalAgent
from agents.ml import MLAgent
from agents.decision.decision_agent import DecisionAgent
from data_layer.models import MarketData
from backtesting.regime_detector import MarketRegimeDetector, MarketRegime


logger = logging.getLogger(__name__)


@dataclass
class TradingRecommendation:
    """توصیه نهایی برای معامله"""
    action: str  # BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
    confidence: float  # 0 to 1
    signal: float  # -1 to 1
    reasoning: str
    agent_contributions: List[Dict[str, Any]]
    market_regime: str
    current_price: float
    timestamp: datetime


class IntegratedTradingSystem:
    """
    سیستم یکپارچه معاملاتی
    
    ترکیب همه agents:
    - Signal Agent (technical analysis)
    - ML Agent (machine learning predictions)
    - Market Regime Detection
    - Decision Agent (final decision)
    
    Example:
        >>> system = IntegratedTradingSystem()
        >>> system.initialize()
        >>> recommendation = system.analyze(market_data)
        >>> print(recommendation.action)  # STRONG_BUY
    """
    
    def __init__(
        self,
        ml_model_path: Optional[str] = None,
        enable_ml: bool = True,
        enable_signal: bool = True,
        enable_regime_detection: bool = True,
        agent_weights: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            ml_model_path: مسیر model آموزش دیده ML Agent
            enable_ml: فعال/غیرفعال کردن ML Agent
            enable_signal: فعال/غیرفعال کردن Signal Agent
            enable_regime_detection: فعال/غیرفعال کردن تشخیص regime
            agent_weights: وزن هر agent {agent_name: weight}
        """
        self.ml_model_path = ml_model_path or "models/gold_ml_model.pkl"
        self.enable_ml = enable_ml
        self.enable_signal = enable_signal
        self.enable_regime_detection = enable_regime_detection
        
        # Default weights (می‌توان بر اساس market regime تغییر دهیم)
        self.agent_weights = agent_weights or {
            'ml': 1.0,
            'signal': 1.0
        }
        
        # Initialize components
        self.signal_agent: Optional[SignalAgent] = None
        self.ml_agent: Optional[MLAgent] = None
        self.regime_detector: Optional[MarketRegimeDetector] = None
        self.decision_agent = DecisionAgent()
        
        self.initialized = False
        
        logger.info("Integrated Trading System created")
    
    def initialize(self):
        """Initialize all agents"""
        logger.info("Initializing trading system...")
        
        # Signal Agent
        if self.enable_signal:
            logger.info("Initializing Signal Agent...")
            self.signal_agent = SignalAgent()
        
        # ML Agent
        if self.enable_ml:
            logger.info("Initializing ML Agent...")
            self.ml_agent = MLAgent(model_path=self.ml_model_path)
            
            # Load trained model
            try:
                self.ml_agent.load_model()
                logger.info("ML Agent model loaded successfully")
            except FileNotFoundError:
                logger.warning(f"ML model not found at {self.ml_model_path}. ML Agent disabled.")
                self.enable_ml = False
        
        # Regime Detector
        if self.enable_regime_detection:
            logger.info("Initializing Regime Detector...")
            self.regime_detector = MarketRegimeDetector()
        
        self.initialized = True
        logger.info("Trading system initialized successfully")
    
    def analyze(self, market_data: MarketData) -> TradingRecommendation:
        """
        تحلیل کامل و تولید توصیه معاملاتی
        
        Args:
            market_data: داده‌های بازار
        
        Returns:
            TradingRecommendation با جزئیات کامل
        """
        if not self.initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        logger.info(f"Analyzing market data: {len(market_data)} candles")
        
        # 1. Market Regime Detection
        regime = self._detect_regime(market_data)
        logger.info(f"Market regime: {regime}")
        
        # 2. Update agent weights based on regime
        self._adjust_weights_for_regime(regime)
        
        # 3. Collect signals from all agents
        agent_outputs = []
        
        # Signal Agent
        if self.enable_signal and self.signal_agent:
            signal_output = self._analyze_with_signal_agent(market_data)
            agent_outputs.append(signal_output)
        
        # ML Agent
        if self.enable_ml and self.ml_agent:
            ml_output = self._analyze_with_ml_agent(market_data)
            agent_outputs.append(ml_output)
        
        # 4. Decision Agent - final decision
        if not agent_outputs:
            raise RuntimeError("No agents enabled or all agents failed")
        
        decision_output = self.decision_agent.analyze(agent_outputs)
        
        # 5. Build recommendation
        recommendation = TradingRecommendation(
            action=decision_output.metadata['decision'],
            confidence=decision_output.confidence,
            signal=decision_output.signal,
            reasoning=decision_output.metadata['reasoning'],
            agent_contributions=decision_output.metadata['agent_contributions'],
            market_regime=regime,
            current_price=float(market_data.data[-1].close),
            timestamp=market_data.data[-1].datetime
        )
        
        logger.info(f"Final recommendation: {recommendation.action} (confidence: {recommendation.confidence:.2f})")
        
        return recommendation
    
    def _detect_regime(self, market_data: MarketData) -> str:
        """تشخیص market regime"""
        if not self.enable_regime_detection or not self.regime_detector:
            return "unknown"
        
        # استفاده از 100 کندل اخیر برای تشخیص regime
        lookback_data = market_data.data[-100:] if len(market_data.data) > 100 else market_data.data
        
        regime_analysis = self.regime_detector.detect(lookback_data)
        
        logger.info(
            f"Regime: {regime_analysis.regime}, "
            f"Confidence: {regime_analysis.confidence:.1%}, "
            f"ADX: {regime_analysis.adx:.1f}"
        )
        
        return regime_analysis.regime
    
    def _adjust_weights_for_regime(self, regime: str):
        """
        تنظیم وزن agents بر اساس market regime
        
        - Trending: ML Agent وزن بیشتری دارد
        - Ranging: Signal Agent وزن بیشتری دارد (mean reversion)
        - Volatile: کاهش confidence کلی
        """
        if regime == "trending_up" or regime == "trending_down":
            # ML در trend بهتر عمل می‌کند
            self.agent_weights['ml'] = 1.3
            self.agent_weights['signal'] = 0.8
        
        elif regime == "ranging":
            # Technical indicators در ranging بهتر هستند
            self.agent_weights['ml'] = 0.8
            self.agent_weights['signal'] = 1.3
        
        elif regime == "volatile":
            # در volatile، هر دو را کم‌وزن می‌کنیم
            self.agent_weights['ml'] = 0.7
            self.agent_weights['signal'] = 0.7
        
        else:
            # Default
            self.agent_weights['ml'] = 1.0
            self.agent_weights['signal'] = 1.0
        
        logger.debug(f"Agent weights adjusted for {regime}: {self.agent_weights}")
    
    def _analyze_with_signal_agent(self, market_data: MarketData) -> AgentOutput:
        """تحلیل با Signal Agent"""
        logger.debug("Running Signal Agent...")
        
        signal_output = self.signal_agent.analyze(market_data)
        
        # اعمال وزن
        weight = self.agent_weights.get('signal', 1.0)
        
        weighted_output = AgentOutput(
            agent_type=AgentType.SIGNAL,
            signal=signal_output.signal,
            confidence=signal_output.confidence * weight,
            metadata={
                'source': 'Signal Agent',
                'weight': weight,
                'original_confidence': signal_output.confidence
            }
        )
        
        logger.debug(f"Signal Agent: signal={signal_output.signal:.2f}, confidence={signal_output.confidence:.2f}")
        
        return weighted_output
    
    def _analyze_with_ml_agent(self, market_data: MarketData) -> AgentOutput:
        """تحلیل با ML Agent"""
        logger.debug("Running ML Agent...")
        
        ml_output = self.ml_agent.analyze(market_data)
        
        # تبدیل recommendation به signal
        if ml_output.recommendation == "BUY":
            signal = 1.0
        elif ml_output.recommendation == "SELL":
            signal = -1.0
        else:  # HOLD
            signal = 0.0
        
        # اعمال وزن
        weight = self.agent_weights.get('ml', 1.0)
        
        weighted_output = AgentOutput(
            agent_type=AgentType.ML,
            signal=signal,
            confidence=ml_output.confidence * weight,
            metadata={
                'source': 'ML Agent',
                'weight': weight,
                'original_confidence': ml_output.confidence,
                'recommendation': ml_output.recommendation,
                'prediction': ml_output.metadata.get('prediction'),
                'probabilities': {
                    'up': ml_output.metadata.get('probability_up'),
                    'down': ml_output.metadata.get('probability_down')
                }
            }
        )
        
        logger.debug(
            f"ML Agent: recommendation={ml_output.recommendation}, "
            f"confidence={ml_output.confidence:.2f}"
        )
        
        return weighted_output
    
    def get_status(self) -> Dict[str, Any]:
        """وضعیت فعلی سیستم"""
        return {
            'initialized': self.initialized,
            'agents': {
                'signal': self.enable_signal and self.signal_agent is not None,
                'ml': self.enable_ml and self.ml_agent is not None,
                'regime_detection': self.enable_regime_detection and self.regime_detector is not None
            },
            'weights': self.agent_weights,
            'ml_model_path': self.ml_model_path
        }
    
    def update_weights(self, weights: Dict[str, float]):
        """
        بروزرسانی دستی وزن agents
        
        Args:
            weights: {agent_name: weight}
        """
        self.agent_weights.update(weights)
        logger.info(f"Agent weights updated: {self.agent_weights}")
    
    def explain_decision(self, recommendation: TradingRecommendation) -> str:
        """
        توضیح تفصیلی تصمیم
        
        Returns:
            String با توضیح کامل
        """
        explanation = []
        
        explanation.append(f"="*80)
        explanation.append(f"TRADING DECISION EXPLANATION")
        explanation.append(f"="*80)
        explanation.append(f"")
        explanation.append(f"Time: {recommendation.timestamp}")
        explanation.append(f"Current Price: ${recommendation.current_price:.2f}")
        explanation.append(f"Market Regime: {recommendation.market_regime.upper()}")
        explanation.append(f"")
        explanation.append(f"FINAL DECISION: {recommendation.action}")
        explanation.append(f"Confidence: {recommendation.confidence:.1%}")
        explanation.append(f"Signal Strength: {recommendation.signal:.2f} (-1 to 1)")
        explanation.append(f"")
        explanation.append(f"REASONING:")
        explanation.append(f"{recommendation.reasoning}")
        explanation.append(f"")
        explanation.append(f"AGENT CONTRIBUTIONS:")
        
        for contrib in recommendation.agent_contributions:
            agent_name = contrib['agent']
            signal = contrib['signal']
            confidence = contrib['confidence']
            
            signal_dir = "BUY" if signal > 0.2 else "SELL" if signal < -0.2 else "NEUTRAL"
            
            explanation.append(
                f"  - {agent_name.upper()}: {signal_dir} "
                f"(signal={signal:.2f}, confidence={confidence:.2f})"
            )
        
        explanation.append(f"")
        explanation.append(f"AGENT WEIGHTS:")
        for agent, weight in self.agent_weights.items():
            explanation.append(f"  - {agent}: {weight:.2f}")
        
        explanation.append(f"")
        explanation.append(f"="*80)
        
        return "\n".join(explanation)
