# app.py
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

from strategies import MovingAverageStrategy, RbKnoxvilleStrategy
from config import RbKnoxvilleConfig
from scanner import StockScanner
from market_data import MarketDataProvider

app = Flask(__name__)
CORS(app)

# Initialize strategies with configurations
STRATEGIES = {
    "moving-average": MovingAverageStrategy(),
    "rb-knoxville": RbKnoxvilleStrategy(RbKnoxvilleConfig())
}

@app.route('/api/scan', methods=['POST'])
def scan():
    try:
        data = request.json
        symbols = data.get('symbols', [])
        market = data.get('market')
        strategy_name = data.get('strategyName')

        if not all([symbols, market, strategy_name]):
            return jsonify({"error": "Missing required parameters: symbols, market, strategyName"}), 400

        if strategy_name not in STRATEGIES:
            return jsonify({"error": "Invalid strategy name"}), 400
        if market not in ['India', 'US']:
            return jsonify({"error": "Invalid market"}), 400

        strategy = STRATEGIES[strategy_name]
        scanner = StockScanner(MarketDataProvider(), strategy)
        results = [scanner.scan_stock(symbol, market) for symbol in symbols]
        
        # Ensure all values are JSON serializable
        for result in results:
            for key, value in result.items():
                if isinstance(value, (np.integer, np.floating)):
                    result[key] = float(value)
                elif isinstance(value, np.bool_):
                    result[key] = bool(value)
        
        return jsonify(results)

    except Exception as e:
        app.logger.error(f"Error in scan endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
