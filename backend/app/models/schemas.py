from datetime import datetime
from typing import Optional, List, Dict

class OHLCVData:
    """Schema for OHLCV data"""
    
    def __init__(self, symbol: str, timestamp: datetime, open: float, 
                 high: float, low: float, close: float, volume: float):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }

class Forecast:
    """Schema for forecast data"""
    
    def __init__(self, forecast_id: str, symbol: str, model_type: str,
                 horizon: str, predictions: List[Dict], metrics: Dict):
        self.forecast_id = forecast_id
        self.symbol = symbol
        self.model_type = model_type
        self.horizon = horizon
        self.predictions = predictions
        self.metrics = metrics
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'forecast_id': self.forecast_id,
            'symbol': self.symbol,
            'model_type': self.model_type,
            'horizon': self.horizon,
            'created_at': self.created_at.isoformat(),
            'predictions': self.predictions,
            'metrics': self.metrics
        }