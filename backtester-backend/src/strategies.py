# strategies.py
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, ROCIndicator
from ta.volatility import BollingerBands
from typing import Dict, Any
from dataclasses import asdict

from config import RbKnoxvilleConfig

class TradingStrategy(ABC):
    @abstractmethod
    def calculate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trading signals and indicators for the strategy."""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Return the parameters that should be included in the response."""
        pass

class MovingAverageStrategy(TradingStrategy):
    def __init__(self, ma_periods: Dict[str, int] = None):
        self.ma_periods = ma_periods or {"MA200": 200, "MA50": 50, "MA20": 20}

    def calculate_ma(self, data: pd.DataFrame, window: int) -> pd.Series:
        return data['Close'].rolling(window=window).mean()

    def calculate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        for ma_name, period in self.ma_periods.items():
            data[ma_name] = self.calculate_ma(data, period)

        last_row = data.iloc[-1]
        
        ma_values = [last_row[ma] for ma in sorted(self.ma_periods.keys(), reverse=True)]
        print(ma_values)
        buy_condition = all(ma_values[i] > ma_values[i+1] for i in range(len(ma_values)-1))
        buy_condition = buy_condition and (ma_values[-1] > last_row['Close'])
        
        sell_condition = all(ma_values[i] < ma_values[i+1] for i in range(len(ma_values)-1))
        sell_condition = sell_condition and (ma_values[-1] < last_row['Close'])

        return {
            "buy_signal": buy_condition,
            "sell_signal": sell_condition,
            **{ma_name: last_row[ma_name] for ma_name in self.ma_periods.keys()}
        }

    def get_parameters(self) -> Dict[str, Any]:
        return {ma_name: True for ma_name in self.ma_periods.keys()}


class RbKnoxvilleStrategy(TradingStrategy):
    def __init__(self, config: RbKnoxvilleConfig = None):
        self.config = config or RbKnoxvilleConfig()

    def calculate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Create a copy of the DataFrame to avoid the SettingWithCopyWarning
        data = data.copy()
        
        # Ensure we have enough bars of data
        data = data.tail(self.config.bars_back).reset_index(drop=False)
        
        # Calculate RSI
        rsi_indicator = RSIIndicator(
            close=data['Close'],
            window=self.config.rsi_period
        )
        data.loc[:, 'RSI'] = rsi_indicator.rsi()
        
        # Calculate Momentum (Rate of Change)
        momentum_indicator = ROCIndicator(
            close=data['Close'],
            window=self.config.momentum_period
        )
        data.loc[:, 'Momentum'] = momentum_indicator.roc()
        
        # Calculate Bollinger Bands
        bb_indicator = BollingerBands(
            close=data['Close'],
            window=self.config.momentum_period
        )
        data.loc[:, 'BB_high'] = bb_indicator.bollinger_hband()
        data.loc[:, 'BB_low'] = bb_indicator.bollinger_lband()
        
        last_row = data.iloc[-1]
        
        # Buy signal: RSI oversold + price below lower BB + positive momentum
        buy_signal = (
            last_row['RSI'] < self.config.rsi_oversold and 
            last_row['Close'] < last_row['BB_low'] and
            last_row['Momentum'] > 0
        )
        
        # Sell signal: RSI overbought + price above upper BB + negative momentum
        sell_signal = (
            last_row['RSI'] > self.config.rsi_overbought and 
            last_row['Close'] > last_row['BB_high'] and
            last_row['Momentum'] < 0
        )

        # Convert numpy.bool_ to Python bool for JSON serialization
        return {
            "buy_signal": bool(buy_signal),
            "sell_signal": bool(sell_signal),
            "RSI": float(last_row['RSI']),
            "Momentum": float(last_row['Momentum']),
            "BB_high": float(last_row['BB_high']),
            "BB_low": float(last_row['BB_low']),
            **{k: float(v) if isinstance(v, (np.float32, np.float64)) else v 
               for k, v in asdict(self.config).items()}
        }

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "RSI": True,
            "Momentum": True,
            "BB_high": True,
            "BB_low": True,
            "bars_back": True,
            "rsi_period": True,
            "momentum_period": True,
            "rsi_oversold": True,
            "rsi_overbought": True
        }
