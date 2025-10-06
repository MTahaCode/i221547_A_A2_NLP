import pytest
import json

class TestInstrumentsRoutes:
    """Test instruments API routes"""
    
    def test_get_instruments(self, client):
        response = client.get('/api/instruments/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) > 0
    
    def test_get_instrument_info(self, client):
        response = client.get('/api/instruments/AAPL/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['name'] == 'Apple Inc.'
    
    def test_get_instrument_info_invalid(self, client):
        response = client.get('/api/instruments/INVALID/info')
        assert response.status_code == 500

class TestForecastsRoutes:
    """Test forecasts API routes"""
    
    def test_create_forecast_missing_fields(self, client):
        response = client.post('/api/forecast', 
                              json={'symbol': 'AAPL'})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Missing required field' in data['message']
    
    def test_create_forecast_invalid_model(self, client):
        response = client.post('/api/forecast',
                              json={
                                  'symbol': 'AAPL',
                                  'horizon': '24hrs',
                                  'model_type': 'invalid_model'
                              })
        assert response.status_code == 400
    
    def test_get_forecast_not_found(self, client):
        response = client.get('/api/forecast/nonexistent-id')
        assert response.status_code == 404

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'