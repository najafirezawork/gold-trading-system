"""
Configuration settings for the trading system.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    twelve_data_api_key: str = Field(..., alias="TWELVE_DATA_API_KEY")
    twelve_data_base_url: str = "https://api.twelvedata.com"
    
    # Trading Configuration
    default_symbol: str = "XAU/USD"  # Gold
    default_interval: str = "1h"
    default_outputsize: int = 100
    
    # Agent Configuration
    signal_agent_enabled: bool = True
    ml_agent_enabled: bool = False  # For future use
    
    # Decision Thresholds
    strong_signal_threshold: float = 0.7
    medium_signal_threshold: float = 0.5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
