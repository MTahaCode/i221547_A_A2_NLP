from flask import Blueprint, jsonify, request
from app.services.forecast_service import ForecastService
import uuid

forecasts_bp = Blueprint('forecasts', __name__)
forecast_service = ForecastService()

@forecasts_bp.route('/forecast', methods=['POST'])
def create_forecast():
    """Generate a new forecast"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['symbol', 'horizon', 'model_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        symbol = data['symbol']
        horizon = data['horizon']
        model_type = data['model_type']
        
        # Generate forecast
        forecast_result = forecast_service.generate_forecast(
            symbol=symbol,
            horizon=horizon,
            model_type=model_type
        )
        
        return jsonify({
            'status': 'success',
            'data': forecast_result
        }), 201
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@forecasts_bp.route('/forecast/<forecast_id>', methods=['GET'])
def get_forecast(forecast_id):
    """Retrieve a saved forecast"""
    try:
        forecast = forecast_service.get_forecast_by_id(forecast_id)
        
        if forecast is None:
            return jsonify({
                'status': 'error',
                'message': 'Forecast not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': forecast
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@forecasts_bp.route('/forecasts/<symbol>', methods=['GET'])
def get_forecasts_by_symbol(symbol):
    """Get recent forecasts for a symbol"""
    try:
        limit = int(request.args.get('limit', 10))
        forecasts = forecast_service.get_recent_forecasts(symbol, limit=limit)
        
        return jsonify({
            'status': 'success',
            'data': forecasts,
            'count': len(forecasts)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@forecasts_bp.route('/models/performance', methods=['GET'])
def get_model_performance():
    """Get performance metrics for all models"""
    try:
        symbol = request.args.get('symbol')
        performance = forecast_service.get_model_performance(symbol)
        
        return jsonify({
            'status': 'success',
            'data': performance
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500