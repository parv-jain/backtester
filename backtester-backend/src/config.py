# config.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class StrategyConfig:
    """Base configuration class for trading strategies"""
    bars_back: int = 200  # Default to studying last 200 days

@dataclass
class RbKnoxvilleConfig(StrategyConfig):
    """Configuration specific to RbKnoxville strategy"""
    rsi_period: int = 14      # RSI calculation period
    momentum_period: int = 20  # Recovery period for momentum calculation
    rsi_oversold: int = 30    # RSI oversold threshold
    rsi_overbought: int = 70  # RSI overbought threshold
