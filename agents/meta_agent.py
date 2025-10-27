"""
Meta-Agent Orchestrator
========================

نقش: تصمیم‌گیر نهایی!

این orchestrator همه agents رو هماهنگ می‌کنه:
1. Enhanced Technical Agent → سیگنال قوی technical
2. Simple ML Filter → فیلتر سیگنال‌های بد
3. Risk Management Agent → بررسی ریسک و position sizing

Final Decision Logic:
- اگر Technical سیگنال قوی بده (confidence >0.7) → ادامه
- اگر ML Filter رد کرد → VETO
- اگه Risk Agent رد کرد → VETO
- اگر همه OK بودن → معامله با weighted confidence
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
import numpy as np

from agents.base import BaseAgent, AgentOutput, AgentType
from agents.technical.enhanced_technical_agent import EnhancedTechnicalAgent
from agents.ml.simple_ml_filter import SimpleMLFilter
from agents.risk.risk_management_agent import RiskManagementAgent
from data_layer.models import MarketData


@dataclass
class MetaDecision:
    """تصمیم نهایی Meta-Agent"""
    final_signal: float  # -1 to 1
    final_confidence: float  # 0 to 1
    action: str  # "BUY", "SELL", "HOLD"
    position_size: float
    stop_loss: float
    take_profit: float
    reasoning_chain: List[str]  # دلیل هر agent
    veto_reasons: List[str]  # اگر reject شد چرا؟
    warnings: List[str]


class MetaAgentOrchestrator:
    """
    Meta-Agent Orchestrator
    
    Architecture:
    Technical Agent (50%) → ML Filter (20%) → Risk Agent (30%) → Final Decision
    
    Veto Power:
    - ML Filter can veto if confidence < 0.4
    - Risk Agent can veto for any risk violation
    - Technical Agent must have minimum confidence 0.5
    """
    
    def __init__(
        self,
        account_balance: float = 10000.0,
        min_technical_confidence: float = 0.5,
        ml_filter_veto_threshold: float = 0.4
    ):
        """
        Initialize Meta-Agent
        
        Args:
            account_balance: مبلغ اولیه حساب
            min_technical_confidence: حداقل confidence برای Technical
            ml_filter_veto_threshold: threshold برای veto توسط ML
        """
        # Initialize all agents
        self.technical_agent = EnhancedTechnicalAgent()
        self.ml_filter = SimpleMLFilter()
        self.risk_agent = RiskManagementAgent(account_balance=account_balance)
        
        # Settings
        self.min_technical_confidence = min_technical_confidence
        self.ml_filter_veto_threshold = ml_filter_veto_threshold
        
        # Weights for final decision (must sum to 1.0)
        self.weights = {
            'technical': 0.50,
            'ml_filter': 0.20,
            'risk': 0.30
        }
    
    def get_decision(self, market_data: MarketData) -> MetaDecision:
        """
        تصمیم‌گیری نهایی بر اساس همه agents
        
        Pipeline:
        1. Technical Agent generates signal
        2. ML Filter evaluates signal
        3. Risk Agent checks constraints and position sizing
        4. Meta combines all outputs with weighted voting
        
        Args:
            market_data: داده‌های بازار
        
        Returns:
            MetaDecision with final action
        """
        reasoning_chain = []
        veto_reasons = []
        warnings = []
        
        # ========================================
        # STEP 1: Technical Analysis
        # ========================================
        tech_output = self.technical_agent.analyze(market_data)
        
        reasoning_chain.append(
            f"Technical: Signal={tech_output.signal:.2f}, "
            f"Confidence={tech_output.confidence:.2f}, "
            f"Reasons={tech_output.metadata.get('reasons', [])}"
        )
        
        # Check minimum technical confidence
        if tech_output.confidence < self.min_technical_confidence:
            veto_reasons.append(
                f"Technical confidence too low: {tech_output.confidence:.2f} < {self.min_technical_confidence}"
            )
            return self._create_hold_decision(reasoning_chain, veto_reasons, warnings)
        
        # If no clear signal, hold
        if abs(tech_output.signal) < 0.1:
            veto_reasons.append("No clear technical signal")
            return self._create_hold_decision(reasoning_chain, veto_reasons, warnings)
        
        # ========================================
        # STEP 2: ML Filter
        # ========================================
        ml_output = self.ml_filter.analyze(market_data, tech_output)
        
        filter_decision = ml_output.metadata.get('filter_decision', 'UNKNOWN')
        filter_reason = ml_output.metadata.get('filter_reason', '')
        
        reasoning_chain.append(
            f"ML Filter: {filter_decision}, "
            f"Confidence={ml_output.confidence:.2f}, "
            f"Reason={filter_reason}"
        )
        
        # ML Filter veto
        if filter_decision == 'REJECT':
            veto_reasons.append(f"ML Filter rejected: {filter_reason}")
            return self._create_hold_decision(reasoning_chain, veto_reasons, warnings)
        
        # ========================================
        # STEP 3: Risk Management
        # ========================================
        # Get SL and TP from technical analysis
        tech_metadata = tech_output.metadata
        stop_loss = tech_metadata.get('stop_loss', 0.0)
        take_profit = tech_metadata.get('take_profit', 0.0)
        
        risk_output = self.risk_agent.analyze(
            market_data=market_data,
            signal_output=ml_output,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        risk_decision = risk_output.metadata.get('risk_decision', 'UNKNOWN')
        risk_warnings = risk_output.metadata.get('warnings', [])
        rejection_reasons = risk_output.metadata.get('rejection_reasons', [])
        
        reasoning_chain.append(
            f"Risk: {risk_decision}, "
            f"Position Size={risk_output.metadata.get('position_size', 0):.4f}, "
            f"R/R={risk_output.metadata.get('risk_reward_ratio', 0):.2f}"
        )
        
        warnings.extend(risk_warnings)
        
        # Risk veto
        if risk_decision == 'REJECTED':
            veto_reasons.extend(rejection_reasons)
            return self._create_hold_decision(reasoning_chain, veto_reasons, warnings)
        
        # ========================================
        # STEP 4: Meta Decision (Weighted Voting)
        # ========================================
        final_signal = self._calculate_weighted_signal(
            tech_output, ml_output, risk_output
        )
        
        final_confidence = self._calculate_weighted_confidence(
            tech_output, ml_output, risk_output
        )
        
        # Determine action
        if final_signal > 0.3:
            action = "BUY"
        elif final_signal < -0.3:
            action = "SELL"
        else:
            action = "HOLD"
            veto_reasons.append(f"Weak final signal: {final_signal:.2f}")
        
        # Extract position details
        position_size = risk_output.metadata.get('position_size', 0.0)
        
        return MetaDecision(
            final_signal=final_signal,
            final_confidence=final_confidence,
            action=action,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reasoning_chain=reasoning_chain,
            veto_reasons=veto_reasons,
            warnings=warnings
        )
    
    def _calculate_weighted_signal(
        self,
        tech_output: AgentOutput,
        ml_output: AgentOutput,
        risk_output: AgentOutput
    ) -> float:
        """
        محاسبه سیگنال نهایی با weighted voting
        
        Formula:
        Final Signal = (Tech × 0.5) + (ML × 0.2) + (Risk × 0.3)
        """
        weighted_signal = (
            tech_output.signal * self.weights['technical'] +
            ml_output.signal * self.weights['ml_filter'] +
            risk_output.signal * self.weights['risk']
        )
        
        return np.clip(weighted_signal, -1.0, 1.0)
    
    def _calculate_weighted_confidence(
        self,
        tech_output: AgentOutput,
        ml_output: AgentOutput,
        risk_output: AgentOutput
    ) -> float:
        """
        محاسبه confidence نهایی با weighted voting
        
        اگر یکی از agents confidence پایین داشت، نهایی هم پایین میره
        """
        # Weighted average
        weighted_conf = (
            tech_output.confidence * self.weights['technical'] +
            ml_output.confidence * self.weights['ml_filter'] +
            risk_output.confidence * self.weights['risk']
        )
        
        # Penalty for disagreement
        # اگه agents با هم مخالف باشن، confidence کم میشه
        signals = [tech_output.signal, ml_output.signal, risk_output.signal]
        signal_std = np.std([s for s in signals if abs(s) > 0.1])
        
        if signal_std > 0.5:  # High disagreement
            weighted_conf *= 0.8
        
        return np.clip(weighted_conf, 0.0, 1.0)
    
    def _create_hold_decision(
        self,
        reasoning_chain: List[str],
        veto_reasons: List[str],
        warnings: List[str]
    ) -> MetaDecision:
        """Create a HOLD decision"""
        return MetaDecision(
            final_signal=0.0,
            final_confidence=0.0,
            action="HOLD",
            position_size=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            reasoning_chain=reasoning_chain,
            veto_reasons=veto_reasons,
            warnings=warnings
        )
    
    def update_balance(self, new_balance: float):
        """Update risk agent balance after trade"""
        self.risk_agent.update_balance(new_balance)
    
    def get_status(self) -> Dict:
        """Get current status of all agents"""
        return {
            'account_balance': self.risk_agent.current_balance,
            'current_drawdown': self.risk_agent._calculate_current_drawdown(),
            'open_positions': len(self.risk_agent.open_positions),
            'peak_balance': self.risk_agent.peak_balance,
            'weights': self.weights
        }
