import numpy as np
import uuid
from datetime import datetime, timedelta
from flask import g
from app.models.database import get_db
from app.services.data_service import DataService
from app.ml_models.arima_model import ARIMAForecaster
from app.ml_models.lstm_model import LSTMForecaster
from app.ml_models.gru_model import GRUForecaster
from app.ml_models.transformer_model import TransformerForecaster
from app.ml_models.ensemble import EnsembleForecaster
from app.utils.metrics import calculate_all_metrics
from flask import current_app

class ForecastService:
    """Service for generating and managing forecasts"""
    
    def __init__(self):
        self.data_service = DataService()
        
    def _get_model(self, model_type):
        """Initialize the appropriate model"""
        if model_type == 'arima':
            return ARIMAForecaster()
        elif model_type == 'lstm':
            return LSTMForecaster(epochs=50)
        elif model_type == 'gru':
            return GRUForecaster(epochs=50)
        elif model_type == 'transformer':
            return TransformerForecaster(epochs=50)
        elif model_type == 'ensemble':
            return EnsembleForecaster()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _horizon_to_steps(self, horizon):
        """Convert horizon string to number of steps"""
        horizons = current_app.config['FORECAST_HORIZONS']
        if horizon not in horizons:
            raise ValueError(f"Invalid horizon. Must be one of: {list(horizons.keys())}")
        return horizons[horizon]
    
    def generate_forecast(self, symbol, horizon, model_type):
        """Generate a forecast for the given parameters"""
        # Validate inputs
        if model_type not in current_app.config['AVAILABLE_MODELS']:
            raise ValueError(f"Invalid model type: {model_type}")
        
        steps = self._horizon_to_steps(horizon)
        
        # Get historical data
        historical_data = self.data_service.get_closing_prices(symbol, days=365)
        historical_array = np.array(historical_data)
        
        # Split data for validation
        train_size = int(len(historical_array) * 0.8)
        train_data = historical_array[:train_size]
        test_data = historical_array[train_size:]
        
        # Initialize and train model
        model = self._get_model(model_type)
        model.fit(train_data)
        
        # Generate predictions
        if model_type == 'arima':
            predictions, conf_int = model.predict(steps)
            confidence_lower = conf_int[:, 0].tolist()
            confidence_upper = conf_int[:, 1].tolist()
        elif model_type == 'ensemble':
            predictions, individual_preds = model.predict(historical_array, steps)
            confidence_lower = None
            confidence_upper = None
        else:
            predictions = model.predict(historical_array, steps)
            confidence_lower = None
            confidence_upper = None
        
        # Calculate metrics on validation set
        if len(test_data) >= steps:
            val_predictions = model.predict(train_data, len(test_data)) if model_type != 'arima' else model.predict(len(test_data))[0]
            metrics = calculate_all_metrics(test_data, val_predictions[:len(test_data)])
        else:
            metrics = {}
        
        # Generate timestamps for predictions
        last_timestamp = datetime.now()
        prediction_timestamps = [
            last_timestamp + timedelta(hours=i+1) for i in range(steps)
        ]
        
        # Format predictions
        formatted_predictions = []
        for i, (ts, pred) in enumerate(zip(prediction_timestamps, predictions)):
            pred_dict = {
                'timestamp': ts.isoformat(),
                'predicted_close': float(pred)
            }
            if confidence_lower is not None:
                pred_dict['confidence_lower'] = float(confidence_lower[i])
                pred_dict['confidence_upper'] = float(confidence_upper[i])
            formatted_predictions.append(pred_dict)
        
        # Save forecast to database
        forecast_id = str(uuid.uuid4())
        forecast_doc = {
            'forecast_id': forecast_id,
            'symbol': symbol,
            'model_type': model_type,
            'horizon': horizon,
            'created_at': datetime.now(),
            'predictions': formatted_predictions,
            'metrics': metrics,
            'model_params': model.get_params()
        }
        
        db = get_db()
        db.forecasts.insert_one(forecast_doc)
        
        # Save model metadata
        model_metadata = {
            'model_name': f"{model_type}_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'model_type': model_type,
            'symbol': symbol,
            'trained_at': datetime.now(),
            'parameters': model.get_params(),
            'performance': metrics
        }
        db.model_metadata.insert_one(model_metadata)
        
        # Return forecast (without _id)
        forecast_doc.pop('_id', None)
        forecast_doc['created_at'] = forecast_doc['created_at'].isoformat()
        
        return forecast_doc
    
    def get_forecast_by_id(self, forecast_id):
        """Retrieve a forecast by ID"""
        db = get_db()
        forecast = db.forecasts.find_one({'forecast_id': forecast_id})
        
        if forecast:
            forecast.pop('_id', None)
            forecast['created_at'] = forecast['created_at'].isoformat()
            return forecast
        
        return None
    
    def get_recent_forecasts(self, symbol, limit=10):
        """Get recent forecasts for a symbol"""
        db = get_db()
        cursor = db.forecasts.find(
            {'symbol': symbol}
        ).sort('created_at', -1).limit(limit)
        
        forecasts = []
        for forecast in cursor:
            forecast.pop('_id', None)
            forecast['created_at'] = forecast['created_at'].isoformat()
            forecasts.append(forecast)
        
        return forecasts
    
    def get_model_performance(self, symbol=None):
        """Get performance metrics for all models"""
        db = get_db()
        
        query = {'symbol': symbol} if symbol else {}
        cursor = db.model_metadata.find(query).sort('trained_at', -1)
        
        performance_data = {}
        for doc in cursor:
            model_type = doc['model_type']
            if model_type not in performance_data:
                performance_data[model_type] = {
                    'model_type': model_type,
                    'symbol': doc['symbol'],
                    'last_trained': doc['trained_at'].isoformat(),
                    'metrics': doc['performance'],
                    'parameters': doc['parameters']
                }
        
        return list(performance_data.values())