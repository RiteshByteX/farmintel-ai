"""
FarmIntel AI - Routes Package
API endpoint blueprints and route registration
"""

from flask import Blueprint

# Import all route blueprints
from app.routes.api import api_bp
from app.routes.detect import detect_bp
from app.routes.treatment import treatment_bp
from app.routes.weather import weather_bp
from app.routes.history import history_bp
from app.routes.reports import reports_bp

__all__ = [
    'api_bp',
    'detect_bp',
    'treatment_bp',
    'weather_bp',
    'history_bp',
    'reports_bp'
]


def register_routes(app):
    """
    Register all route blueprints with the Flask app
    
    Args:
        app: Flask application instance
    """
    # Register all blueprints with their URL prefixes
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(detect_bp, url_prefix='/api')
    app.register_blueprint(treatment_bp, url_prefix='/api')
    app.register_blueprint(weather_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
    
    # Log registered routes
    app.logger.info("All API routes registered successfully")
    
    # Print all registered routes for debugging
    if app.debug:
        print("\n📋 Registered API Routes:")
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api'):
                methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                print(f"   {methods:10} {rule.rule}")
        print()