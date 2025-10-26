"""
Main entry point for the Gold Trading Signal System.

This example demonstrates how to use the system:
1. Fetch gold price data from Twelve Data API
2. Analyze data using Signal Agent
3. Make trading decision using Decision Agent
"""

import logging
import sys
from datetime import datetime

from config import settings
from data_layer import TwelveDataClient, TwelveDataAPIError
from agents import SignalAgent, DecisionAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('trading_system.log')
    ]
)

logger = logging.getLogger(__name__)


class TradingSystem:
    """
    Main trading system orchestrator.
    
    This class manages the data layer and multiple agents to provide
    trading signals and decisions.
    """
    
    def __init__(self):
        """Initialize the trading system."""
        logger.info("Initializing Trading System...")
        
        # Initialize data client
        self.data_client = TwelveDataClient()
        
        # Initialize agents
        self.signal_agent = SignalAgent()
        self.decision_agent = DecisionAgent()
        
        # Future: Add more agents here
        # self.ml_agent = MLAgent()
        # self.sentiment_agent = SentimentAgent()
        
        logger.info("Trading System initialized successfully")
    
    def run_analysis(self, symbol: str = None, interval: str = None, outputsize: int = None):
        """
        Run complete analysis pipeline.
        
        Args:
            symbol: Trading symbol (default: from config)
            interval: Time interval (default: from config)
            outputsize: Number of data points (default: from config)
        """
        symbol = symbol or settings.default_symbol
        interval = interval or settings.default_interval
        outputsize = outputsize or settings.default_outputsize
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting analysis for {symbol} at {datetime.now()}")
        logger.info(f"Interval: {interval}, Data points: {outputsize}")
        logger.info(f"{'='*60}\n")
        
        try:
            # Step 1: Fetch market data
            logger.info("Step 1: Fetching market data...")
            market_data = self.data_client.get_time_series(
                symbol=symbol,
                interval=interval,
                outputsize=outputsize
            )
            logger.info(f"✓ Fetched {len(market_data)} data points")
            
            # Display current price
            current_price = market_data.data[0].close
            logger.info(f"Current Price: ${current_price:.2f}\n")
            
            # Step 2: Run Signal Agent analysis
            logger.info("Step 2: Running technical analysis...")
            signal_output = self.signal_agent.analyze(market_data)
            
            if signal_output.signal is not None:
                logger.info(f"✓ Signal Agent Analysis:")
                logger.info(f"  - Signal: {signal_output.signal:.2f}")
                logger.info(f"  - Confidence: {signal_output.confidence:.2f}")
                logger.info(f"  - Analysis: {signal_output.metadata.get('analysis', 'N/A')}")
                
                # Display key indicators
                indicators = signal_output.metadata.get('indicators', {})
                logger.info(f"\n  Key Indicators:")
                logger.info(f"    • RSI: {indicators.get('rsi', 0):.2f}")
                logger.info(f"    • SMA(20): ${indicators.get('sma_20', 0):.2f}")
                logger.info(f"    • SMA(50): ${indicators.get('sma_50', 0):.2f}")
                logger.info(f"    • EMA(12): ${indicators.get('ema_12', 0):.2f}")
                
                macd = indicators.get('macd', {})
                logger.info(f"    • MACD: {macd.get('macd_line', 0):.4f}")
                logger.info(f"    • MACD Signal: {macd.get('signal_line', 0):.4f}\n")
            
            # Step 3: Collect all agent outputs
            agent_outputs = [signal_output]
            
            # Future: Add more agent outputs here
            # if settings.ml_agent_enabled:
            #     ml_output = self.ml_agent.analyze(market_data)
            #     agent_outputs.append(ml_output)
            
            # Step 4: Make final decision
            logger.info("Step 3: Making trading decision...")
            decision_output = self.decision_agent.analyze(agent_outputs)
            
            # Display decision
            logger.info(f"✓ Final Decision:")
            logger.info(f"  - Decision: {decision_output.metadata['decision']}")
            logger.info(f"  - Signal: {decision_output.signal:.2f}")
            logger.info(f"  - Confidence: {decision_output.confidence:.2f}")
            logger.info(f"\n  Reasoning:")
            logger.info(f"  {decision_output.metadata['reasoning']}\n")
            
            logger.info(f"{'='*60}")
            logger.info("Analysis completed successfully")
            logger.info(f"{'='*60}\n")
            
            return decision_output
            
        except TwelveDataAPIError as e:
            logger.error(f"API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return None
    
    def close(self):
        """Clean up resources."""
        self.data_client.close()
        logger.info("Trading System shut down")


def main():
    """Main function."""
    try:
        # Create trading system
        system = TradingSystem()
        
        # Run analysis for Gold (XAU/USD)
        result = system.run_analysis(
            symbol="XAU/USD",
            interval="1h",
            outputsize=100
        )
        
        if result:
            logger.info("Trading signal generated successfully!")
        else:
            logger.warning("Failed to generate trading signal")
        
        # Clean up
        system.close()
        
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
