import pytest
import numpy as np
from app.utils.metrics import (
    calculate_rmse,
    calculate_mae,
    calculate_mape,
    calculate_r2,
    calculate_directional_accuracy,
    calculate_all_metrics
)
from app.utils.validators import (
    validate_symbol,
    validate_horizon,
    validate_model_type
)

class TestMetrics:
    """Test metric calculation functions"""
    
    def test_calculate_rmse(self):
        y_true = np.array([100, 105, 103, 108, 110])
        y_pred = np.array([102, 104, 105, 107, 109])
        
        rmse = calculate_rmse(y_true, y_pred)
        assert rmse > 0
        assert isinstance(rmse, (float, np.floating))
    
    def test_calculate_mae(self):
        y_true = np.array([100, 105, 103, 108, 110])
        y_pred = np.array([102, 104, 105, 107, 109])
        
        mae = calculate_mae(y_true, y_pred)
        assert mae > 0
        assert isinstance(mae, (float, np.floating))
    
    def test_calculate_mape(self):
        y_true = np.array([100, 105, 103, 108, 110])
        y_pred = np.array([102, 104, 105, 107, 109])
        
        mape = calculate_mape(y_true, y_pred)
        assert mape >= 0
        assert mape < 100  # Should be a reasonable percentage
    
    def test_calculate_mape_zero_handling(self):
        y_true = np.array([0, 105, 103, 108, 110])
        y_pred = np.array([102, 104, 105, 107, 109])
        
        # Should handle zeros without error
        mape = calculate_mape(y_true, y_pred)
        assert mape >= 0
    
    def test_calculate_r2(self):
        y_true = np.array([100, 105, 103, 108, 110])
        y_pred = np.array([102, 104, 105, 107, 109])
        
        r2 = calculate_r2(y_true, y_pred)
        assert -1 <= r2 <= 1  # R² should be in this range
    
    def test_calculate_directional_accuracy(self):
        y_true = np.array([100, 105, 103, 108, 110])
        y_pred = np.array([100, 106, 102, 109, 111])
        
        acc = calculate_directional_accuracy(y_true, y_pred)
        assert 0 <= acc <= 100
    
    def test_calculate_all_metrics(self):
        y_true = np.array([100, 105, 103, 108, 110])
        y_pred = np.array([102, 104, 105, 107, 109])
        
        metrics = calculate_all_metrics(y_true, y_pred)
        
        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert 'mape' in metrics
        assert 'r2_score' in metrics
        assert 'directional_accuracy' in metrics

class TestValidators:
    """Test validation functions"""
    
    def test_validate_symbol(self):
        assert validate_symbol('aapl') == 'AAPL'
        assert validate_symbol('BTC-USD') == 'BTC-USD'
    
    def test_validate_symbol_invalid(self):
        with pytest.raises(ValueError):
            validate_symbol('')
        
        with pytest.raises(ValueError):
            validate_symbol(None)
    
    def test_validate_horizon(self):
        valid_horizons = {'1hr': 1, '24hrs': 24}
        
        assert validate_horizon('1hr', valid_horizons) == '1hr'
        assert validate_horizon('24hrs', valid_horizons) == '24hrs'
    
    def test_validate_horizon_invalid(self):
        valid_horizons = {'1hr': 1, '24hrs': 24}
        
        with pytest.raises(ValueError):
            validate_horizon('invalid', valid_horizons)
    
    def test_validate_model_type(self):
        available = ['arima', 'lstm', 'gru']
        
        assert validate_model_type('arima', available) == 'arima'
        assert validate_model_type('lstm', available) == 'lstm'
    
    def test_validate_model_type_invalid(self):
        available = ['arima', 'lstm']
        
        with pytest.raises(ValueError):
            validate_model_type('invalid', available)