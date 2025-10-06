from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.models.database import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from app.routes.instruments import instruments_bp
    from app.routes.forecasts import forecasts_bp
    
    app.register_blueprint(instruments_bp, url_prefix='/api/instruments')
    app.register_blueprint(forecasts_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return {'status': 'healthy', 'message': 'API is running'}, 200
    
    return app