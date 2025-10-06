from pymongo import MongoClient
from flask import g, current_app

def get_db():
    """Get database connection"""
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client.get_database()
        g.mongo_client = client
    return g.db

def close_db(e=None):
    """Close database connection"""
    client = g.pop('mongo_client', None)
    if client is not None:
        client.close()

def init_db(app):
    """Initialize database"""
    app.teardown_appcontext(close_db)
    
    # Create indexes
    with app.app_context():
        db = get_db()
        
        # Historical data indexes
        db.historical_data.create_index([('symbol', 1), ('timestamp', -1)])
        db.historical_data.create_index([('timestamp', -1)])
        
        # Forecasts indexes
        db.forecasts.create_index([('forecast_id', 1)], unique=True)
        db.forecasts.create_index([('symbol', 1), ('created_at', -1)])
        
        # Model metadata indexes
        db.model_metadata.create_index([('model_type', 1), ('symbol', 1)])
        db.model_metadata.create_index([('trained_at', -1)])