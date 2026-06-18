"""
FarmIntel AI - Models Package
Database schemas and data models for the application
"""

from app.models.disease_model import DiseaseModel, PredictionResult
from app.models.history_model import HistoryModel, ScanRecord
from app.models.schemas import (
    DetectionRequest,
    DetectionResponse,
    TreatmentRequest,
    TreatmentResponse,
    WeatherRequest,
    WeatherResponse,
    HistoryRequest,
    HistoryResponse,
    ReportRequest,
    ReportResponse,
    UserSchema,
    DiseaseSchema,
    ValidationError,
    NotFoundError,
    APIError
)

__all__ = [
    # Disease Model
    'DiseaseModel',
    'PredictionResult',
    
    # History Model
    'HistoryModel',
    'ScanRecord',
    
    # Request/Response Schemas
    'DetectionRequest',
    'DetectionResponse',
    'TreatmentRequest',
    'TreatmentResponse',
    'WeatherRequest',
    'WeatherResponse',
    'HistoryRequest',
    'HistoryResponse',
    'ReportRequest',
    'ReportResponse',
    
    # Utility Schemas
    'UserSchema',
    'DiseaseSchema',
    
    # Error Classes
    'ValidationError',
    'NotFoundError',
    'APIError'
]