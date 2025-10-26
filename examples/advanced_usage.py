"""
Advanced usage example demonstrating how to extend the system.

This shows how to:
1. Add custom agents in the future
2. Customize thresholds
3. Monitor multiple symbols
4. Save results
"""

import logging
from datetime import datetime
import json

from config import settings
from data_layer import TwelveDataClient
from agents import SignalAgent, DecisionAgent, AgentType, AgentOutput, BaseAgent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example: How to create a custom ML Agent (template for future)
class MLAgent(BaseAgent):
    """
    Placeholder for future ML-based agent.
    
    This demonstrates how to extend the system with new agents.
    """
    
    def __init__(self, name: str = "ML Agent"):
        super().__init__(AgentType.ML, name)
        # Initialize your ML model here
        # self.model = load_model('path/to/model')
    
    def analyze(self, data) -> AgentOutput:
        """
        Analyze using ML model.
        
        Args:
            data: MarketData object
            
        Returns:
            AgentOutput with ML predictions
        """
        if not self.enabled:
            return AgentOutput(
                agent_type=self.agent_type,
                signal=0.0,
                confidence=0.0,
                metadata={"status": "disabled"}
            )
        
        # TODO: Implement ML analysis
        # predictions = self.model.predict(data)
        # signal = self._convert_to_signal(predictions)
        
        # Placeholder implementation
        logger.info(f"{self.name}: ML analysis not yet implemented")
        
        return AgentOutput(
            agent_type=self.agent_type,
            signal=0.0,  # Replace with actual ML prediction
            confidence=0.5,
            metadata={
                "model_version": "1.0",
                "features_used": ["price", "volume", "indicators"],
                "note": "Placeholder - implement your ML model here"
            }
        )


class AdvancedTradingSystem:
    """Advanced trading system with enhanced features."""
    
    def __init__(self):
        """Initialize the advanced system."""
        self.client = TwelveDataClient()
        
        # Initialize all agents
        self.signal_agent = SignalAgent()
        self.ml_agent = MLAgent()
        self.decision_agent = DecisionAgent()
        
        # Customize decision thresholds if needed
        self.decision_agent.set_thresholds(strong=0.75, medium=0.55)
        
        logger.info("Advanced Trading System initialized")
    
    def analyze_multiple_timeframes(self, symbol: str = "XAU/USD"):
        """
        Analyze across multiple timeframes for confluence.
        
        Args:
            symbol: Trading symbol
        """
        timeframes = ["15min", "1h", "4h", "1day"]
        results = {}
        
        logger.info(f"\nMulti-timeframe analysis for {symbol}")
        logger.info("=" * 60)
        
        for timeframe in timeframes:
            try:
                logger.info(f"\nAnalyzing {timeframe} timeframe...")
                
                # Fetch data
                data = self.client.get_time_series(
                    symbol=symbol,
                    interval=timeframe,
                    outputsize=100
                )
                
                # Run signal agent
                signal_output = self.signal_agent.analyze(data)
                
                # Store results
                results[timeframe] = {
                    "signal": signal_output.signal,
                    "confidence": signal_output.confidence,
                    "analysis": signal_output.metadata.get("analysis", "N/A")
                }
                
                logger.info(f"  ✓ {timeframe}: {results[timeframe]['analysis']} "
                          f"(signal={signal_output.signal:.2f})")
                
            except Exception as e:
                logger.error(f"  ✗ Error analyzing {timeframe}: {e}")
                results[timeframe] = {"error": str(e)}
        
        # Check for confluence
        self._check_confluence(results)
        
        return results
    
    def _check_confluence(self, results: dict):
        """Check if signals agree across timeframes."""
        signals = [r["signal"] for r in results.values() if "signal" in r]
        
        if not signals:
            return
        
        avg_signal = sum(signals) / len(signals)
        agreement = all(s * avg_signal > 0 for s in signals if abs(s) > 0.2)
        
        logger.info("\n" + "=" * 60)
        if agreement and abs(avg_signal) > 0.3:
            logger.info(f"✓ CONFLUENCE DETECTED: Signals align across timeframes!")
            logger.info(f"  Average signal: {avg_signal:.2f}")
        else:
            logger.info(f"⚠ Mixed signals across timeframes (avg: {avg_signal:.2f})")
        logger.info("=" * 60)
    
    def save_results(self, result: AgentOutput, filename: str = None):
        """
        Save analysis results to file.
        
        Args:
            result: AgentOutput to save
            filename: Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{timestamp}.json"
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "decision": result.metadata.get("decision"),
            "signal": result.signal,
            "confidence": result.confidence,
            "reasoning": result.metadata.get("reasoning"),
            "agent_contributions": result.metadata.get("agent_contributions", [])
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filename}")
    
    def run_with_custom_agents(self, symbol: str = "XAU/USD"):
        """
        Run analysis with all available agents including custom ones.
        
        Args:
            symbol: Trading symbol
        """
        logger.info(f"\nRunning comprehensive analysis for {symbol}")
        
        # Fetch data
        data = self.client.get_time_series(
            symbol=symbol,
            interval="1h",
            outputsize=100
        )
        
        # Collect outputs from all agents
        agent_outputs = []
        
        # Signal Agent
        signal_output = self.signal_agent.analyze(data)
        agent_outputs.append(signal_output)
        logger.info(f"✓ Signal Agent: {signal_output.signal:.2f}")
        
        # ML Agent (when implemented)
        if settings.ml_agent_enabled:
            ml_output = self.ml_agent.analyze(data)
            agent_outputs.append(ml_output)
            logger.info(f"✓ ML Agent: {ml_output.signal:.2f}")
        
        # Make final decision
        decision = self.decision_agent.analyze(agent_outputs)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"FINAL DECISION: {decision.metadata['decision']}")
        logger.info(f"Signal: {decision.signal:.2f}, Confidence: {decision.confidence:.2f}")
        logger.info(f"{'='*60}\n")
        
        return decision
    
    def close(self):
        """Clean up resources."""
        self.client.close()


def example_1_basic():
    """Example 1: Basic usage with single analysis."""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 1: Basic Single Analysis")
    logger.info("="*60)
    
    system = AdvancedTradingSystem()
    decision = system.run_with_custom_agents("XAU/USD")
    system.save_results(decision)
    system.close()


def example_2_multi_timeframe():
    """Example 2: Multi-timeframe analysis."""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 2: Multi-Timeframe Analysis")
    logger.info("="*60)
    
    system = AdvancedTradingSystem()
    results = system.analyze_multiple_timeframes("XAU/USD")
    system.close()


def example_3_custom_thresholds():
    """Example 3: Using custom decision thresholds."""
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE 3: Custom Thresholds")
    logger.info("="*60)
    
    system = AdvancedTradingSystem()
    
    # Set conservative thresholds (higher confidence required)
    system.decision_agent.set_thresholds(strong=0.85, medium=0.65)
    logger.info("Using conservative thresholds (0.85/0.65)")
    
    decision = system.run_with_custom_agents("XAU/USD")
    system.close()


if __name__ == "__main__":
    # Run examples
    example_1_basic()
    
    # Uncomment to run other examples:
    # example_2_multi_timeframe()
    # example_3_custom_thresholds()
