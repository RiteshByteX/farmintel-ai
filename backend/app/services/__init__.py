"""
FarmIntel AI - Services Package
Core services for ML prediction, training, weather, and data management
"""

from app.services.ml_service import MLService, ml_service
from app.services.train_service import TrainService, train_service
from app.services.weather_service import WeatherService, weather_service
from app.services.data_service import DataService, data_service
from app.services.pdf_service import PDFService, pdf_service
from app.services.csv_service import CSVService, csv_service

__all__ = [
    # ML Service
    'MLService',
    'ml_service',
    
    # Training Service
    'TrainService',
    'train_service',
    
    # Weather Service
    'WeatherService',
    'weather_service',
    
    # Data Service
    'DataService',
    'data_service',
    
    # PDF Service
    'PDFService',
    'pdf_service',
    
    # CSV Service
    'CSVService',
    'csv_service'
]