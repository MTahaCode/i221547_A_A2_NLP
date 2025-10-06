import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from flask import g
from app.models.database import get_db
from app.models.schemas import OHLCVData

class DataService:
    """Service for managing financial data"""
    
    AVAILABLE_INSTRUMENTS = {
        'BTC-USD': {'name': 'Bitcoin', 'type': 'crypto'},
        'ETH-USD': {'name': 'Ethereum', 'type': 'crypto'},
        'AAPL': {'name': 'Apple Inc.', 'type': 'stock'},
        'GOOGL': {'name': 'Alphabet Inc.', 'type': 'stock'},
        'MSFT': {'name': 'Microsoft Corp.', 'type': 'stock'},
        'TSLA': {'name': 'Tesla Inc.', 'type': 'stock'},
        'EURUSD=X': {'name': 'EUR/USD', 'type': 'forex'},
        'JPY=X': {'name': 'USD/JPY', 'type': 'forex'}
    }
    
    def get_available_instruments(self):
        """Get list of available instruments"""
        return [
            {
                'symbol': symbol,
                'name': info['name'],
                'type': info['type']
            }
            for symbol, info in self.AVAILABLE_INSTRUMENTS.items()
        ]
    
    def get_instrument_info(self, symbol):
        """Get information about an instrument"""
        if symbol not in self.AVAILABLE_INSTRUMENTS:
            raise ValueError(f"Unknown instrument: {symbol}")
        
        return self.AVAILABLE_INSTRUMENTS[symbol]
    
    def fetch_from_yfinance(self, symbol, days=365, interval='1h'):
        """Fetch data from Yahoo Finance"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        return df
    
    def save_historical_data(self, symbol, df):
        """Save historical data to MongoDB"""
        db = get_db()
        collection = db.historical_data
        
        records = []
        for idx, row in df.iterrows():
            record = {
                'symbol': symbol,
                'timestamp': idx.to_pydatetime(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': float(row['Volume']),
                'source': 'yfinance'
            }
            records.append(record)
        
        if records:
            # Use update_one with upsert to avoid duplicates
            for record in records:
                collection.update_one(
                    {
                        'symbol': record['symbol'],
                        'timestamp': record['timestamp']
                    },
                    {'$set': record},
                    upsert=True
                )
        
        return len(records)
    
    def get_historical_data(self, symbol, days=365, interval='1h', use_cache=True):
        """Get historical data (from cache or fetch new)"""
        db = get_db()
        collection = db.historical_data
        
        # Try to get from database first
        if use_cache:
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor = collection.find({
                'symbol': symbol,
                'timestamp': {'$gte': cutoff_date}
            }).sort('timestamp', 1)
            
            data = list(cursor)
            
            if data and len(data) > 100:  # Minimum data points
                return self._format_ohlcv_data(data)
        
        # Fetch new data if not in cache
        df = self.fetch_from_yfinance(symbol, days=days, interval=interval)
        self.save_historical_data(symbol, df)
        
        # Retrieve saved data
        cursor = collection.find({'symbol': symbol}).sort('timestamp', 1).limit(days * 24)
        data = list(cursor)
        
        return self._format_ohlcv_data(data)
    
    def _format_ohlcv_data(self, data):
        """Format MongoDB data to API response"""
        return [
            {
                'timestamp': record['timestamp'].isoformat(),
                'open': record['open'],
                'high': record['high'],
                'low': record['low'],
                'close': record['close'],
                'volume': record['volume']
            }
            for record in data
        ]
    
    def get_closing_prices(self, symbol, days=365):
        """Get only closing prices as numpy array"""
        data = self.get_historical_data(symbol, days=days)
        return [point['close'] for point in data]