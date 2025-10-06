from flask import Blueprint, jsonify, request
from app.services.data_service import DataService
from datetime import datetime, timedelta

instruments_bp = Blueprint('instruments', __name__)
data_service = DataService()

@instruments_bp.route('/', methods=['GET'])
def get_instruments():
    """Get list of available instruments"""
    try:
        instruments = data_service.get_available_instruments()
        return jsonify({
            'status': 'success',
            'data': instruments
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@instruments_bp.route('/<symbol>/historical', methods=['GET'])
def get_historical_data(symbol):
    """Get historical OHLCV data for an instrument"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 365))
        interval = request.args.get('interval', '1h')
        
        # Fetch data
        data = data_service.get_historical_data(symbol, days=days, interval=interval)
        
        return jsonify({
            'status': 'success',
            'data': data,
            'count': len(data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@instruments_bp.route('/<symbol>/info', methods=['GET'])
def get_instrument_info(symbol):
    """Get instrument metadata"""
    try:
        info = data_service.get_instrument_info(symbol)
        return jsonify({
            'status': 'success',
            'data': info
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500