"""
Base agent class for all trading agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents in the system."""
    SIGNAL = "signal"
    ML = "ml"
    SENTIMENT = "sentiment"
    DECISION = "decision"
    RISK = "risk"
    TECHNICAL = "technical"


class AgentOutput:
    """Standard output format for all agents."""
    
    def __init__(
        self,
        agent_type: AgentType,
        signal: Optional[float] = None,  # -1 to 1 scale
        confidence: float = 0.0,  # 0 to 1 scale
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent output.
        
        Args:
            agent_type: Type of the agent
            signal: Trading signal (-1: strong sell, 0: neutral, 1: strong buy)
            confidence: Confidence level of the signal (0 to 1)
            metadata: Additional information from the agent
        """
        self.agent_type = agent_type
        self.signal = signal
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def __repr__(self) -> str:
        return (
            f"AgentOutput(type={self.agent_type.value}, "
            f"signal={self.signal:.2f}, confidence={self.confidence:.2f})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_type": self.agent_type.value,
            "signal": self.signal,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """Base class for all trading agents."""
    
    def __init__(self, agent_type: AgentType, name: Optional[str] = None):
        """
        Initialize base agent.
        
        Args:
            agent_type: Type of the agent
            name: Optional name for the agent
        """
        self.agent_type = agent_type
        self.name = name or agent_type.value
        self.enabled = True
        logger.info(f"Initialized agent: {self.name}")
    
    @abstractmethod
    def analyze(self, data: Any) -> AgentOutput:
        """
        Analyze data and produce output.
        
        Args:
            data: Input data for analysis
            
        Returns:
            AgentOutput with signal and confidence
        """
        pass
    
    def enable(self):
        """Enable the agent."""
        self.enabled = True
        logger.info(f"Agent {self.name} enabled")
    
    def disable(self):
        """Disable the agent."""
        self.enabled = False
        logger.info(f"Agent {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if agent is enabled."""
        return self.enabled
    
    def __repr__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"{self.__class__.__name__}(name={self.name}, status={status})"
