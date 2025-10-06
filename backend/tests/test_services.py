import pytest
from app.services.data_service import DataService
from app.services.forecast_service import ForecastService

class TestDataService:
    """Test data service functionality"""
    
    def test_get_available_instruments(self):
        service = DataService()
        instruments = service.get_available_instruments()
        
        assert len(instruments) > 0
        assert any(i['symbol'] == 'BTC-USD' for i in instruments)
        assert any(i['symbol'] == 'AAPL' for i in instruments)
    
    def test_get_instrument_info(self):
        service = DataService()
        info = service.get_instrument_info('AAPL')
        
        assert info['name'] == 'Apple Inc.'
        assert info['type'] == 'stock'
    
    def test_get_instrument_info_invalid(self):
        service = DataService()
        with pytest.raises(ValueError, match="Unknown instrument"):
            service.get_instrument_info('INVALID')
    
    def test_format_ohlcv_data(self):
        service = DataService()
        from datetime import datetime
        
        data = [{
            'timestamp': datetime(2024, 1, 1),
            'open': 100.0,
            'high': 105.0,
            'low': 98.0,
            'close': 103.0,
            'volume': 1000000.0
        }]
        
        formatted = service._format_ohlcv_data(data)
        
        assert len(formatted) == 1
        assert formatted[0]['open'] == 100.0
        assert 'timestamp' in formatted[0]

class TestForecastService:
    """Test forecast service functionality"""
    
    def test_horizon_to_steps(self, app):
        with app.app_context():
            service = ForecastService()
            
            assert service._horizon_to_steps('1hr') == 1
            assert service._horizon_to_steps('3hrs') == 3
            assert service._horizon_to_steps('24hrs') == 24
            assert service._horizon_to_steps('72hrs') == 72
    
    def test_horizon_to_steps_invalid(self, app):
        with app.app_context():
            service = ForecastService()
            with pytest.raises(ValueError, match="Invalid horizon"):
                service._horizon_to_steps('invalid')
    
    def test_get_model(self, app):
        with app.app_context():
            service = ForecastService()
            
            arima = service._get_model('arima')
            assert isinstance(arima, ARIMAForecaster)
            
            lstm = service._get_model('lstm')
            assert isinstance(lstm, LSTMForecaster)
    
    def test_get_model_invalid(self, app):
        with app.app_context():
            service = ForecastService()
            with pytest.raises(ValueError, match="Unknown model type"):
                service._get_model('invalid_model')