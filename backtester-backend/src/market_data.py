# market_data.py
from typing import Optional
import pandas as pd
import yfinance as yf

class MarketDataProvider:
    @staticmethod
    def get_period_for_bars(bars_back: int) -> str:
        """
        Convert number of bars to valid yfinance period string.
        
        Args:
            bars_back (int): Number of trading days to look back
            
        Returns:
            str: Valid yfinance period string
        """
        # Trading days approximations:
        # 1 month ≈ 20-22 trading days
        # 1 year = 252 trading days
        if bars_back <= 5:
            return "5d"
        elif bars_back <= 20:
            return "1mo"
        elif bars_back <= 60:
            return "3mo"
        elif bars_back <= 120:
            return "6mo"
        elif bars_back <= 252:
            return "1y"
        elif bars_back <= 504:
            return "2y"
        elif bars_back <= 1260:
            return "5y"
        else:
            return "10y"

    @staticmethod
    def get_data(symbol: str, market: str, bars_back: int = 200) -> Optional[pd.DataFrame]:
        try:
            ticker = f"{symbol}.NS" if market == "India" else symbol
            
            # Get appropriate period based on bars_back
            period = MarketDataProvider.get_period_for_bars(bars_back)
            
            # Download data
            data = yf.download(ticker, period=period)
            
            if data.empty:
                return None
                
            # Ensure we have enough data
            if len(data) < bars_back:
                # If we don't have enough data, try getting maximum available
                data = yf.download(ticker, period="max")
                
            # Return the requested number of bars, or all available if less
            return data.tail(min(bars_back, len(data)))
            
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {symbol}: {str(e)}")