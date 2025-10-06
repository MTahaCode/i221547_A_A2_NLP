# ============================================
# backend/tests/__init__.py
# ============================================
"""Test suite for FinTech Forecasting Application"""

# ============================================
# backend/tests/conftest.py
# ============================================
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

# ============================================
# backend/tests/test_models.py
# ============================================
import pytest
import numpy as np
from app.ml_models.arima_model import ARIMAForecaster
from app.ml_models.lstm_model import LSTMForecaster
from app.ml_models.gru_model import GRUForecaster
from app.ml_models.transformer_model import TransformerForecaster
from app.ml_models.ensemble import EnsembleForecaster

class TestARIMAModel:
    """Test ARIMA forecasting model"""
    
    def test_arima_initialization(self):
        model = ARIMAForecaster(order=(5, 1, 2))
        assert model.order == (5, 1, 2)
        assert model.fitted_model is None
    
    def test_arima_fit(self, sample_price_data):
        model = ARIMAForecaster()
        model.fit(sample_price_data)
        assert model.fitted_model is not None
    
    def test_arima_predict(self, sample_price_data):
        model = ARIMAForecaster()
        model.fit(sample_price_data)
        predictions, conf_int = model.predict(steps=10)
        
        assert len(predictions) == 10
        assert conf_int.shape == (10, 2)
        assert np.all(conf_int[:, 0] <= predictions)  # lower bound <= prediction
        assert np.all(predictions <= conf_int[:, 1])  # prediction <= upper bound
    
    def test_arima_predict_before_fit(self):
        model = ARIMAForecaster()
        with pytest.raises(ValueError, match="Model must be fitted"):
            model.predict(10)
    
    def test_arima_get_params(self, sample_price_data):
        model = ARIMAForecaster()
        model.fit(sample_price_data)
        params = model.get_params()
        
        assert 'order' in params
        assert 'aic' in params
        assert 'bic' in params
        assert params['aic'] is not None

class TestLSTMModel:
    """Test LSTM forecasting model"""
    
    def test_lstm_initialization(self):
        model = LSTMForecaster(sequence_length=30, hidden_size=32, epochs=5)
        assert model.sequence_length == 30
        assert model.hidden_size == 32
        assert model.epochs == 5
    
    def test_lstm_fit(self, sample_price_data):
        model = LSTMForecaster(sequence_length=30, epochs=5)
        model.fit(sample_price_data)
        assert model.model is not None
        assert model.scaler is not None
    
    def test_lstm_predict(self, sample_price_data):
        model = LSTMForecaster(sequence_length=30, epochs=5)
        model.fit(sample_price_data)
        predictions = model.predict(sample_price_data, steps=10)
        
        assert len(predictions) == 10
        assert np.all(predictions > 0)  # Prices should be positive
    
    def test_lstm_predict_before_fit(self, sample_price_data):
        model = LSTMForecaster()
        with pytest.raises(ValueError, match="Model must be fitted"):
            model.predict(sample_price_data, 10)
    
    def test_lstm_prepare_data(self, sample_price_data):
        model = LSTMForecaster(sequence_length=30)
        X, y = model.prepare_data(sample_price_data)
        
        assert X.shape[0] == len(sample_price_data) - 30
        assert X.shape[1] == 30
        assert len(y) == len(sample_price_data) - 30

class TestGRUModel:
    """Test GRU forecasting model"""
    
    def test_gru_initialization(self):
        model = GRUForecaster(sequence_length=30, hidden_size=32, epochs=5)
        assert model.sequence_length == 30
        assert model.hidden_size == 32
    
    def test_gru_fit_and_predict(self, sample_price_data):
        model = GRUForecaster(sequence_length=30, epochs=5)
        model.fit(sample_price_data)
        predictions = model.predict(sample_price_data, steps=10)
        
        assert len(predictions) == 10
        assert model.model is not None

class TestTransformerModel:
    """Test Transformer forecasting model"""
    
    def test_transformer_initialization(self):
        model = TransformerForecaster(sequence_length=30, d_model=32, epochs=5)
        assert model.sequence_length == 30
        assert model.d_model == 32
    
    def test_transformer_fit_and_predict(self, sample_price_data):
        model = TransformerForecaster(sequence_length=30, d_model=32, epochs=5)
        model.fit(sample_price_data)
        predictions = model.predict(sample_price_data, steps=10)
        
        assert len(predictions) == 10

class TestEnsembleModel:
    """Test Ensemble forecasting model"""
    
    def test_ensemble_initialization(self):
        model = EnsembleForecaster()
        assert len(model.models) == 4  # arima, lstm, gru, transformer
        assert 'arima' in model.models
        assert 'lstm' in model.models
    
    def test_ensemble_with_custom_weights(self):
        weights = {'arima': 0.4, 'lstm': 0.3, 'gru': 0.2, 'transformer': 0.1}
        model = EnsembleForecaster(weights=weights)
        assert model.weights == weights
    
    def test_ensemble_fit(self, sample_price_data):
        model = EnsembleForecaster()
        # Use small epochs for testing
        model.models['lstm'].epochs = 5
        model.models['gru'].epochs = 5
        model.models['transformer'].epochs = 5
        
        model.fit(sample_price_data)
        assert len(model.fitted_models) > 0
    
    def test_ensemble_predict(self, sample_price_data):
        model = EnsembleForecaster()
        model.models['lstm'].epochs = 5
        model.models['gru'].epochs = 5
        model.models['transformer'].epochs = 5
        
        model.fit(sample_price_data)
        predictions, individual = model.predict(sample_price_data, steps=10)
        
        assert len(predictions) == 10
        assert isinstance(individual, dict)
        assert len(individual) > 0
    
    def test_ensemble_update_weights(self):
        model = EnsembleForecaster()
        performance = {'arima': 10.0, 'lstm': 5.0, 'gru': 8.0}
        new_weights = model.update_weights(performance)
        
        assert 'arima' in new_weights
        assert sum(new_weights.values()) == pytest.approx(1.0, rel=1e-5)
        assert new_weights['lstm'] > new_weights['arima']  # Bett