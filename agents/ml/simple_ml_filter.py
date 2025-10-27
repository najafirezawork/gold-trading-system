"""
Simple ML Filter Agent
=======================

هدف: فیلتر کردن سیگنال‌های بد، نه تولید سیگنال!

این agent فقط می‌گوید:
- ✅ این سیگنال technical قابل اعتماد است
- ❌ این سیگنال technical مشکوک است - رد کن

خیلی ساده، خیلی سریع، بدون over-engineering!
"""

from typing import Optional
import numpy as np
from dataclasses import dataclass

from agents.base.agent import BaseAgent, AgentOutput, AgentType
from data_layer.models import MarketData


@dataclass
class MLFilterOutput:
    """خروجی ML Filter"""
    should_take_trade: bool  # True = OK, False = Reject
    filter_confidence: float  # 0 to 1
    filter_reason: str


class SimpleMLFilter(BaseAgent):
    """
    ML Filter ساده
    
    Logic:
    - If technical signal is strong (confidence > 0.7) → Always approve
    - If technical signal is weak (confidence < 0.4) → Always reject  
    - If medium (0.4-0.7) → Use simple heuristics
    
    NO COMPLEX ML! Just simple rules + optional lightweight model
    """
    
    def __init__(self):
        super().__init__(agent_type=AgentType.ML, name="Simple ML Filter")
        
        # Thresholds
        self.strong_signal_threshold = 0.7
        self.weak_signal_threshold = 0.4
    
    def analyze(self, market_data: MarketData, technical_signal: AgentOutput) -> AgentOutput:
        """
        فیلتر کردن سیگنال technical
        
        Args:
            market_data: داده‌های بازار
            technical_signal: سیگنال از Technical Agent
        
        Returns:
            AgentOutput with approval/rejection
        """
        # Extract technical signal details
        tech_confidence = technical_signal.confidence
        tech_signal_strength = abs(technical_signal.signal)
        
        # Rule 1: Strong signals always pass
        if tech_confidence >= self.strong_signal_threshold:
            return self._approve_signal(
                technical_signal,
                confidence=0.9,
                reason="Strong technical signal - approved"
            )
        
        # Rule 2: Very weak signals always rejected
        if tech_confidence < self.weak_signal_threshold:
            return self._reject_signal(
                technical_signal,
                confidence=0.8,
                reason="Weak technical signal - rejected"
            )
        
        # Rule 3: Medium signals - use simple heuristics
        filter_score = self._evaluate_medium_signal(market_data, technical_signal)
        
        if filter_score > 0.5:
            return self._approve_signal(
                technical_signal,
                confidence=filter_score,
                reason=f"Medium signal approved (score={filter_score:.2f})"
            )
        else:
            return self._reject_signal(
                technical_signal,
                confidence=1.0 - filter_score,
                reason=f"Medium signal rejected (score={filter_score:.2f})"
            )
    
    def _evaluate_medium_signal(self, market_data: MarketData, tech_signal: AgentOutput) -> float:
        """
        ارزیابی ساده سیگنال‌های متوسط
        
        Simple heuristics:
        - Check if multiple indicators agree
        - Check trend alignment
        - Check volatility (avoid high volatility periods)
        
        Returns:
            Score 0-1 (>0.5 = approve)
        """
        score = 0.5  # Start neutral
        
        metadata = tech_signal.metadata
        
        # Check number of reasons (more reasons = more confidence)
        reasons = metadata.get('reasons', [])
        if len(reasons) >= 3:
            score += 0.15
        elif len(reasons) >= 2:
            score += 0.1
        
        # Check risk/reward ratio
        rr_ratio = metadata.get('risk_reward_ratio', 1.0)
        if rr_ratio >= 2.0:
            score += 0.15
        elif rr_ratio >= 1.5:
            score += 0.1
        
        # Check trend alignment (from metadata)
        if "Uptrend" in str(reasons) or "Downtrend" in str(reasons):
            score += 0.1
        
        # Check RSI extreme (from metadata)
        indicators = metadata.get('indicators', {})
        rsi = indicators.get('rsi', 50)
        if rsi < 30 or rsi > 70:
            score += 0.1  # Extreme RSI adds confidence
        
        return min(1.0, max(0.0, score))
    
    def _approve_signal(self, tech_signal: AgentOutput, confidence: float, reason: str) -> AgentOutput:
        """Approve the signal"""
        return AgentOutput(
            agent_type=self.agent_type,
            signal=tech_signal.signal,  # Pass through original signal
            confidence=confidence,
            metadata={
                'filter_decision': 'APPROVE',
                'filter_reason': reason,
                'original_signal': tech_signal.signal,
                'original_confidence': tech_signal.confidence,
                'technical_metadata': tech_signal.metadata
            }
        )
    
    def _reject_signal(self, tech_signal: AgentOutput, confidence: float, reason: str) -> AgentOutput:
        """Reject the signal"""
        return AgentOutput(
            agent_type=self.agent_type,
            signal=0.0,  # Neutralize signal
            confidence=confidence,
            metadata={
                'filter_decision': 'REJECT',
                'filter_reason': reason,
                'original_signal': tech_signal.signal,
                'original_confidence': tech_signal.confidence
            }
        )
