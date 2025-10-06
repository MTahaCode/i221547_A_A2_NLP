import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app import create_app
from app.models.database import get_db

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://admin:admin123@localhost:27017/fintech_test?authSource=admin'
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_price_data():
    """Generate sample price data for testing"""
    np.random.seed(42)
    n_points = 100
    base_price = 100
    prices = base_price + np.cumsum(np.random.randn(n_points) * 2)
    return prices

@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data"""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    data = []
    for date in dates:
        close = 100 + np.random.randn() * 10
        high = close + abs(np.random.randn() * 2)
        low = close - abs(np.random.randn() * 2)
        open_price = low + (high - low) * np.random.rand()
        volume = np.random.randint(1000, 10000)
        
        data.append({
            'timestamp': date.isoformat(),
            'open': float(open_price),
            'high': float(high),
            'low': float(low),
            'close': float(close),
            'volume': float(volume)
        })
    
    return data

@pytest.fixture
def cleanup_db(app):
    """Clean up test database after tests"""
    yield
    with app.app_context():
        db = get_db()
        db.historical_data.delete_many({'symbol': {'$regex': '^TEST'}})
        db.forecasts.delete_many({'symbol': {'$regex': '^TEST'}})
        db.model_metadata.delete_many({'symbol': {'$regex': '^TEST'}})