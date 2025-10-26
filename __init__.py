"""
Gold Trading Signal System

A modular, extensible, and clean trading signal system for gold analysis.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Agent-based trading signal system for gold (XAU/USD)"

# Quick imports for convenience
from data_layer import TwelveDataClient, MarketData
from agents import SignalAgent, DecisionAgent, TradingDecision
from config import settings

__all__ = [
    "TwelveDataClient",
    "MarketData",
    "SignalAgent",
    "DecisionAgent",
    "TradingDecision",
    "settings",
]
