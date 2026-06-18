"""
FarmIntel AI - Flask Application Factory
Initializes and configures the Flask application
"""

import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime


def create_app(config_object=None):
    """
    Application factory pattern
    
    Args:
        config_object: Configuration object or path
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'farmintel-secret-key-2024'),
            DEBUG=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
            UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
            MAX_CONTENT_LENGTH=int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)),
            MODEL_PATH=os.environ.get('MODEL_PATH', 'models/plant_disease_model.h5'),
            WEATHER_API_KEY=os.environ.get('WEATHER_API_KEY', ''),
            WEATHER_API_BASE_URL='https://api.openweathermap.org/data/2.5',
            ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
            HISTORY_FILE='database/history.json',
            APP_NAME='FarmIntel AI',
            APP_VERSION='1.0.0',
            APP_DESCRIPTION='AI-powered crop disease detection and farm advisory system'
        )
    
    # Configure CORS (no wildcard for production)
    CORS(app, origins=[
        'http://localhost:5500',
        'http://127.0.0.1:5500', 
        'http://localhost:5000',
        'http://127.0.0.1:5000'
    ])
    
    # Create required directories
    _create_directories(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register request/response handlers
    _register_request_handlers(app)
    
    # Register blueprints (routes)
    _register_blueprints(app)
    
    # Initialize services
    _init_services(app)
    
    return app


def _create_directories(app):
    """Create required directories for the application"""
    directories = [
        app.config.get('UPLOAD_FOLDER', 'uploads'),
        'database',
        'reports',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create history file if not exists
    history_file = app.config.get('HISTORY_FILE', 'database/history.json')
    if not os.path.exists(history_file):
        with open(history_file, 'w') as f:
            json.dump([], f)
    
    app.logger.info("✅ Directories created successfully")


def _register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({
            'success': False,
            'error': 'Payload Too Large',
            'message': 'File size exceeds the maximum allowed limit'
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500


def _register_request_handlers(app):
    """Register before/after request handlers"""
    
    @app.before_request
    def before_request():
        """Log incoming requests"""
        app.logger.info(f"{request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response


def _register_blueprints(app):
    """Register all route blueprints"""
    from app.routes import register_routes
    register_routes(app)
    
    app.logger.info("✅ Routes registered successfully")


def _init_services(app):
    """Initialize application services"""
    # Initialize ML service
    try:
        from app.services.ml_service import ml_service
        ml_service.load_model()
        app.logger.info("✅ ML Service initialized")
    except Exception as e:
        app.logger.warning(f"⚠️ ML Service initialization failed: {e}")
    
    # Initialize weather service
    try:
        from app.services.weather_service import weather_service
        app.logger.info("✅ Weather Service initialized")
    except Exception as e:
        app.logger.warning(f"⚠️ Weather Service initialization failed: {e}")
    
    app.logger.info("✅ All services initialized")


# Create application instance
app = create_app()


if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("\n" + "="*60)
    print("🌾 FarmIntel AI Backend Server")
    print("="*60)
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📁 Upload folder: {app.config.get('UPLOAD_FOLDER', 'uploads')}")
    print(f"🤖 Model: {app.config.get('MODEL_PATH', 'Not configured')}")
    print("="*60)
    print("\n✅ Server starting...\n")
    
    app.run(host=host, port=port, debug=debug)