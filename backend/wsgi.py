"""
FarmIntel AI - WSGI Entry Point for Production
Use this file for deploying with Gunicorn, uWSGI, or Waitress
"""

import os
import sys
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app factory
from app import create_app

# Create application instance for production
# Set to 'production' to use production configuration
app = create_app(config_name='production')

# For Gunicorn (Heroku, DigitalOcean, etc.)
# Usage: gunicorn wsgi:app

# For Waitress (Windows production)
# Usage: waitress-serve --port=5000 wsgi:app

if __name__ == '__main__':
    # This runs when executed directly (for testing)
    # For production, use a proper WSGI server
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("="*60)
    print("🌾 FarmIntel AI - Production Server")
    print("="*60)
    print(f"Starting production server on {host}:{port}")
    print("For production deployment, use:")
    print("  - Gunicorn: gunicorn wsgi:app")
    print("  - Waitress: waitress-serve --port=5000 wsgi:app")
    print("  - uWSGI: uwsgi --http :5000 --wsgi-file wsgi.py --callable app")
    print("="*60)
    
    # Use Waitress for Windows production (more stable)
    try:
        from waitress import serve
        serve(app, host=host, port=port)
    except ImportError:
        # Fallback to Flask development server (not recommended for production)
        app.run(host=host, port=port, debug=False)