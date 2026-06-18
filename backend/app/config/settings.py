"""
FarmIntel AI - Application Configuration
Centralized configuration management for the backend
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with default settings"""
    
    # ========================================
    # Flask Core Settings
    # ========================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'farmintel-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = False
    ENV = os.getenv('FLASK_ENV', 'development')
    
    # ========================================
    # Server Settings
    # ========================================
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # ========================================
    # File Upload Settings
    # ========================================
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    # ========================================
    # Database / Storage Settings
    # ========================================
    DATABASE_FOLDER = 'database'
    HISTORY_FILE = os.path.join(DATABASE_FOLDER, 'history.json')
    USERS_FILE = os.path.join(DATABASE_FOLDER, 'users.json')
    
    # ========================================
    # Reports Settings
    # ========================================
    REPORTS_FOLDER = 'reports'
    PDF_FOLDER = os.path.join(REPORTS_FOLDER, 'pdf')
    CSV_FOLDER = os.path.join(REPORTS_FOLDER, 'csv')
    
    # ========================================
    # AI/ML Model Settings
    # ========================================
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/plant_disease_model.h5')
    MODEL_METADATA_PATH = os.getenv('MODEL_METADATA_PATH', 'models/model_metadata.json')
    IMG_SIZE = (224, 224)  # Image size for model input
    BATCH_SIZE = 32
    CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for predictions
    
    # ========================================
    # Model Training Settings
    # ========================================
    EPOCHS = 50
    LEARNING_RATE = 0.001
    VALIDATION_SPLIT = 0.2
    TEST_SPLIT = 0.1
    RANDOM_SEED = 42
    
    # Data augmentation settings
    AUGMENTATION = {
        'rotation_range': 40,
        'width_shift_range': 0.2,
        'height_shift_range': 0.2,
        'shear_range': 0.2,
        'zoom_range': 0.2,
        'horizontal_flip': True,
        'fill_mode': 'nearest'
    }
    
    # ========================================
    # Weather API Settings
    # ========================================
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    WEATHER_API_BASE_URL = 'https://api.openweathermap.org/data/2.5'
    WEATHER_API_TIMEOUT = 10  # seconds
    
    # ========================================
    # CORS Settings
    # ========================================
    CORS_ORIGINS = [
        'http://localhost:5500',
        'http://127.0.0.1:5500',
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://localhost:3000',
        'http://127.0.0.1:3000'
    ]
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
    
    # ========================================
    # Logging Settings
    # ========================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ========================================
    # App Information
    # ========================================
    APP_NAME = 'FarmIntel AI'
    APP_VERSION = '1.0.0'
    APP_DESCRIPTION = 'AI-powered crop disease detection and farm advisory system'
    APP_AUTHOR = 'FarmIntel AI Team'
    
    @classmethod
    def is_allowed_file(cls, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def get_model_config(cls):
        """Get model configuration as dictionary"""
        return {
            'model_path': cls.MODEL_PATH,
            'img_size': cls.IMG_SIZE,
            'batch_size': cls.BATCH_SIZE,
            'confidence_threshold': cls.CONFIDENCE_THRESHOLD
        }


class DevelopmentConfig(Config):
    """Development configuration - used for local development"""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # More permissive CORS for development
    CORS_ORIGINS = Config.CORS_ORIGINS + ['*']
    
    # Lower log level for development
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def init_app(cls, app):
        """Initialize app for development"""
        # Create required directories
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.DATABASE_FOLDER, exist_ok=True)
        os.makedirs(cls.REPORTS_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(cls.LOG_FILE), exist_ok=True)


class ProductionConfig(Config):
    """Production configuration - used for deployment"""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Production must have a real secret key
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Stricter CORS for production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    # Higher log level for production
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def validate(cls):
        """Validate production configuration"""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")


class TestingConfig(Config):
    """Testing configuration - used for unit tests"""
    
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    
    # Use in-memory database for tests
    DATABASE_FOLDER = ':memory:'
    
    # Smaller file size limit for tests
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB