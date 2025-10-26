"""
Decision agent for making final trading decisions.
"""

import logging
from typing import List, Dict, Any
from enum import Enum

from agents.base import BaseAgent, AgentOutput, AgentType
from config import settings


logger = logging.getLogger(__name__)


class TradingDecision(Enum):
    """Trading decision types."""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class DecisionAgent(BaseAgent):
    """
    Decision-making agent that aggregates signals from multiple agents.
    
    This agent takes outputs from various analysis agents (Signal, ML, etc.)
    and makes a final trading decision with reasoning.
    """
    
    def __init__(self, name: str = "Decision Agent"):
        """Initialize the decision agent."""
        super().__init__(AgentType.DECISION, name)
        self.strong_threshold = settings.strong_signal_threshold
        self.medium_threshold = settings.medium_signal_threshold
    
    def analyze(self, agent_outputs: List[AgentOutput]) -> AgentOutput:
        """
        Aggregate multiple agent outputs and make a final decision.
        
        Args:
            agent_outputs: List of AgentOutput from various agents
            
        Returns:
            AgentOutput with final decision
        """
        if not self.enabled:
            logger.warning(f"Agent {self.name} is disabled")
            return AgentOutput(
                agent_type=self.agent_type,
                signal=0.0,
                confidence=0.0,
                metadata={"status": "disabled"}
            )
        
        if not agent_outputs:
            logger.warning("No agent outputs to analyze")
            return AgentOutput(
                agent_type=self.agent_type,
                signal=0.0,
                confidence=0.0,
                metadata={"error": "no_inputs"}
            )
        
        logger.info(f"Analyzing outputs from {len(agent_outputs)} agents")
        
        # Filter out disabled agents or invalid outputs
        valid_outputs = [
            output for output in agent_outputs
            if output.signal is not None and output.confidence > 0
        ]
        
        if not valid_outputs:
            logger.warning("No valid agent outputs")
            return AgentOutput(
                agent_type=self.agent_type,
                signal=0.0,
                confidence=0.0,
                metadata={"error": "no_valid_inputs"}
            )
        
        # Calculate weighted average signal
        final_signal, final_confidence = self._aggregate_signals(valid_outputs)
        
        # Make decision
        decision = self._make_decision(final_signal, final_confidence)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(valid_outputs, final_signal, final_confidence, decision)
        
        metadata = {
            "decision": decision.value,
            "agent_contributions": [
                {
                    "agent": output.agent_type.value,
                    "signal": output.signal,
                    "confidence": output.confidence
                }
                for output in valid_outputs
            ],
            "reasoning": reasoning
        }
        
        logger.info(f"Final decision: {decision.value} (signal={final_signal:.2f}, confidence={final_confidence:.2f})")
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=final_signal,
            confidence=final_confidence,
            metadata=metadata
        )
    
    def _aggregate_signals(self, outputs: List[AgentOutput]) -> tuple[float, float]:
        """
        Aggregate signals from multiple agents using confidence-weighted average.
        
        Args:
            outputs: List of valid AgentOutput objects
            
        Returns:
            Tuple of (aggregated_signal, aggregated_confidence)
        """
        total_weight = 0.0
        weighted_signal = 0.0
        confidences = []
        
        for output in outputs:
            # Weight by confidence
            weight = output.confidence
            weighted_signal += output.signal * weight
            total_weight += weight
            confidences.append(output.confidence)
        
        # Calculate final signal
        if total_weight > 0:
            final_signal = weighted_signal / total_weight
        else:
            final_signal = 0.0
        
        # Calculate final confidence (average of confidences, but penalize disagreement)
        avg_confidence = sum(confidences) / len(confidences)
        
        # Calculate signal agreement (how much agents agree)
        signal_variance = sum((output.signal - final_signal) ** 2 for output in outputs) / len(outputs)
        agreement_factor = max(0.5, 1.0 - signal_variance)
        
        final_confidence = avg_confidence * agreement_factor
        
        return final_signal, final_confidence
    
    def _make_decision(self, signal: float, confidence: float) -> TradingDecision:
        """
        Make a trading decision based on signal and confidence.
        
        Args:
            signal: Aggregated signal (-1 to 1)
            confidence: Confidence level (0 to 1)
            
        Returns:
            TradingDecision enum
        """
        # Only make strong decisions if confidence is high
        if confidence >= self.strong_threshold:
            if signal >= 0.5:
                return TradingDecision.STRONG_BUY
            elif signal <= -0.5:
                return TradingDecision.STRONG_SELL
        
        # Medium confidence decisions
        if confidence >= self.medium_threshold:
            if signal >= 0.2:
                return TradingDecision.BUY
            elif signal <= -0.2:
                return TradingDecision.SELL
        
        # Default to HOLD if uncertain
        return TradingDecision.HOLD
    
    def _generate_reasoning(
        self,
        outputs: List[AgentOutput],
        signal: float,
        confidence: float,
        decision: TradingDecision
    ) -> str:
        """Generate human-readable reasoning for the decision."""
        
        reasoning_parts = []
        
        # Summary
        reasoning_parts.append(
            f"Decision: {decision.value} based on analysis of {len(outputs)} agent(s)."
        )
        
        # Signal strength
        signal_strength = "strong" if abs(signal) > 0.6 else "moderate" if abs(signal) > 0.3 else "weak"
        signal_direction = "bullish" if signal > 0 else "bearish" if signal < 0 else "neutral"
        reasoning_parts.append(
            f"Overall signal is {signal_strength} {signal_direction} ({signal:.2f})."
        )
        
        # Confidence
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        reasoning_parts.append(f"Confidence level is {confidence_level} ({confidence:.2f}).")
        
        # Agent contributions
        for output in outputs:
            agent_name = output.agent_type.value
            agent_signal = "buy" if output.signal > 0.2 else "sell" if output.signal < -0.2 else "neutral"
            reasoning_parts.append(
                f"- {agent_name.capitalize()} agent suggests {agent_signal} "
                f"(signal={output.signal:.2f}, confidence={output.confidence:.2f})"
            )
        
        return " ".join(reasoning_parts)
    
    def set_thresholds(self, strong: float, medium: float):
        """
        Update decision thresholds.
        
        Args:
            strong: Threshold for strong signals (0-1)
            medium: Threshold for medium signals (0-1)
        """
        self.strong_threshold = max(0.0, min(1.0, strong))
        self.medium_threshold = max(0.0, min(1.0, medium))
        logger.info(f"Updated thresholds: strong={self.strong_threshold}, medium={self.medium_threshold}")
