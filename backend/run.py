"""
FarmIntel AI - Backend Server Entry Point
Run this file to start the Flask development server
"""

import os
import sys
from datetime import datetime

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app factory
from app import create_app

# Create the Flask application instance
app = create_app()


def print_banner():
    """Print beautiful startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   🌾  F A R M I N T E L   A I  🌾                                    ║
    ║                                                                       ║
    ║   AI-Powered Crop Disease Detection & Farm Advisory System           ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_startup_info():
    """Print startup information"""
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', True)
    env = app.config.get('ENV', 'development')
    
    print(f"\n{'='*70}")
    print(f"📋 APPLICATION INFORMATION")
    print(f"{'='*70}")
    print(f"   Name:        {app.config.get('APP_NAME', 'FarmIntel AI')}")
    print(f"   Version:     {app.config.get('APP_VERSION', '1.0.0')}")
    print(f"   Environment: {env}")
    print(f"   Debug Mode:  {debug}")
    print(f"   Started:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    print(f"🌐 SERVER URLs:")
    print(f"   Local:       http://localhost:{port}")
    print(f"   API Base:    http://localhost:{port}/api")
    print(f"   API Docs:    http://localhost:{port}/api/docs")
    print(f"   Health:      http://localhost:{port}/health")
    
    if host == '0.0.0.0':
        import socket
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"   Network:     http://{local_ip}:{port}")
        except:
            pass
    
    print(f"\n📡 API ENDPOINTS:")
    print(f"   POST   /api/upload      - Upload image for detection")
    print(f"   POST   /api/detect      - Detect disease from image")
    print(f"   POST   /api/treatment   - Get treatment recommendations")
    print(f"   GET    /api/weather     - Get weather data")
    print(f"   GET    /api/history     - Get scan history")
    print(f"   POST   /api/history     - Save to history")
    print(f"   DELETE /api/history/<id> - Delete history record")
    print(f"   POST   /api/report/pdf  - Generate PDF report")
    print(f"   POST   /api/report/csv  - Generate CSV report")
    print(f"   GET    /api/statistics  - Get application statistics")
    
    print(f"\n📁 DIRECTORIES:")
    print(f"   Uploads:     {app.config.get('UPLOAD_FOLDER', 'uploads')}")
    print(f"   Database:    database/")
    print(f"   Reports:     reports/")
    print(f"   Logs:        logs/")
    
    print(f"\n🤖 ML MODEL:")
    model_path = app.config.get('MODEL_PATH', 'models/plant_disease_model.h5')
    if os.path.exists(model_path):
        print(f"   Status:      ✅ Loaded")
        print(f"   Path:        {model_path}")
    else:
        print(f"   Status:      ⚠️ Not found (using mock mode)")
        print(f"   Path:        {model_path}")
        print(f"   Note:        Train model with python train_model.py")
    
    print(f"\n🌤️ WEATHER SERVICE:")
    if app.config.get('WEATHER_API_KEY'):
        print(f"   Status:      ✅ Configured")
        print(f"   API Key:     {'*' * 8}{app.config.get('WEATHER_API_KEY')[-4:]}")
    else:
        print(f"   Status:      ⚠️ Not configured (using mock data)")
        print(f"   Note:        Add WEATHER_API_KEY to .env file")
    
    print(f"\n{'='*70}")
    print("🚀 Server is running... Press CTRL+C to stop")
    print(f"{'='*70}\n")


def check_required_directories():
    """Check and create required directories"""
    required_dirs = [
        app.config.get('UPLOAD_FOLDER', 'uploads'),
        'database',
        'reports',
        'logs',
        'models'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")


def check_environment():
    """Check environment configuration"""
    warnings = []
    
    # Check for secret key
    if app.config.get('SECRET_KEY') == 'dev-secret-key':
        warnings.append("⚠️ Using default SECRET_KEY. Change this in production!")
    
    # Check for model
    model_path = app.config.get('MODEL_PATH', 'models/plant_disease_model.h5')
    if not os.path.exists(model_path):
        warnings.append(f"⚠️ Model not found at {model_path}. Train model with python train_model.py")
    
    # Check for weather API key (only warning in production)
    if app.config.get('ENV') == 'production' and not app.config.get('WEATHER_API_KEY'):
        warnings.append("⚠️ WEATHER_API_KEY not set. Weather features will use mock data.")
    
    # Print warnings
    if warnings:
        print("\n⚠️ WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
        print()


if __name__ == '__main__':
    # Get configuration
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    # Print banner
    print_banner()
    
    # Check and create directories
    check_required_directories()
    
    # Check environment
    check_environment()
    
    # Print startup info
    print_startup_info()
    
    # Run the application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down FarmIntel AI server...")
        print("   Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed to start server: {str(e)}")
        sys.exit(1)