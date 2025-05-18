# scanner.py
import numpy as np

from market_data import MarketDataProvider
from strategies import TradingStrategy
from typing import Dict, Any

class StockScanner:
    def __init__(self, market_data_provider: MarketDataProvider, strategy: TradingStrategy):
        self.market_data_provider = market_data_provider
        self.strategy = strategy

    def scan_stock(self, symbol: str, market: str) -> Dict[str, Any]:
        try:
            bars_back = (
                self.strategy.config.bars_back 
                if hasattr(self.strategy, 'config') 
                else 200
            )
            
            data = self.market_data_provider.get_data(symbol, market, bars_back)
            if data is None or data.empty:
                raise ValueError("No data available")

            last_row = data.iloc[-1]
            strategy_results = self.strategy.calculate_signals(data)
            parameters = self.strategy.get_parameters()

            # Ensure all numeric values are Python native types
            response = {
                "symbol": symbol,
                "buy_signal": bool(strategy_results["buy_signal"]),
                "sell_signal": bool(strategy_results["sell_signal"]),
                "last_price": float(last_row['Close']),
                "volume": float(last_row['Volume']),
                "date": last_row.name.isoformat()
            }

            # Add strategy-specific parameters
            for param, include in parameters.items():
                if include and param in strategy_results:
                    value = strategy_results[param]
                    # Convert numpy types to Python native types
                    if isinstance(value, (np.integer, np.floating)):
                        value = float(value)
                    elif isinstance(value, np.bool_):
                        value = bool(value)
                    response[param] = value

            return response

        except Exception as e:
            return {
                "symbol": symbol,
                "error": f"Failed to scan stock: {str(e)}"
            }
