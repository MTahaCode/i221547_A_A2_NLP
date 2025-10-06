import os

class Config:
    """Application configuration"""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://admin:admin123@localhost:27017/fintech_forecasting?authSource=admin')
    MODEL_PATH = os.environ.get('MODEL_PATH', './trained_models')
    
    # Model configurations
    AVAILABLE_MODELS = ['arima', 'lstm', 'gru', 'transformer', 'ensemble']
    
    # Forecast horizon mappings (in hours)
    FORECAST_HORIZONS = {
        '1hr': 1,
        '3hrs': 3,
        '24hrs': 24,
        '72hrs': 72
    }
    
    # Data collection settings
    DATA_RETENTION_DAYS = 365
    
    # Flask settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True