"""
Schemas - Data validation schemas for API requests and responses
Defines data structures for all API endpoints
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


# ========================================
# Enums
# ========================================

class ReportType(str, Enum):
    """Report type enumeration"""
    SUMMARY = 'summary'
    DETAILED = 'detailed'
    WEATHER = 'weather'
    HISTORY = 'history'


class DateRange(str, Enum):
    """Date range enumeration"""
    TODAY = 'today'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'
    ALL = 'all'


class SeverityLevel(str, Enum):
    """Severity level enumeration"""
    SEVERE = 'Severe'
    MODERATE = 'Moderate'
    MILD = 'Mild'
    LOW = 'Low'


class DiseaseRisk(str, Enum):
    """Disease risk level enumeration"""
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'
    CRITICAL = 'Critical'


# ========================================
# Request Schemas
# ========================================

@dataclass
class DetectionRequest:
    """
    Request schema for disease detection endpoint
    """
    image_path: Optional[str] = None
    base64_image: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.image_path and not self.base64_image:
            raise ValidationError("Either image_path or base64_image is required")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DetectionRequest':
        """Create from dictionary"""
        return cls(
            image_path=data.get('image_path'),
            base64_image=data.get('base64_image')
        )


@dataclass
class TreatmentRequest:
    """
    Request schema for treatment lookup endpoint
    """
    disease_name: str
    confidence: float = 0.0
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.disease_name:
            raise ValidationError("disease_name is required")
        if not 0 <= self.confidence <= 100:
            raise ValidationError("confidence must be between 0 and 100")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TreatmentRequest':
        """Create from dictionary"""
        return cls(
            disease_name=data.get('disease_name', ''),
            confidence=data.get('confidence', 0.0)
        )


@dataclass
class WeatherRequest:
    """
    Request schema for weather data endpoint
    """
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    pincode: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate the request data"""
        has_city = self.city is not None and self.city.strip()
        has_coords = self.lat is not None and self.lon is not None
        has_pincode = self.pincode is not None and self.pincode.strip()
        
        if not (has_city or has_coords or has_pincode):
            raise ValidationError("Either city, lat/lon, or pincode is required")
        
        if self.lat is not None and (self.lat < -90 or self.lat > 90):
            raise ValidationError("lat must be between -90 and 90")
        
        if self.lon is not None and (self.lon < -180 or self.lon > 180):
            raise ValidationError("lon must be between -180 and 180")
        
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WeatherRequest':
        """Create from dictionary"""
        return cls(
            city=data.get('city'),
            lat=data.get('lat'),
            lon=data.get('lon'),
            pincode=data.get('pincode')
        )


@dataclass
class HistoryRequest:
    """
    Request schema for history endpoint
    """
    limit: int = 50
    offset: int = 0
    sort_by: str = 'timestamp'
    sort_order: str = 'desc'
    
    def validate(self) -> bool:
        """Validate the request data"""
        if self.limit < 1 or self.limit > 1000:
            raise ValidationError("limit must be between 1 and 1000")
        if self.offset < 0:
            raise ValidationError("offset must be non-negative")
        if self.sort_order not in ['asc', 'desc']:
            raise ValidationError("sort_order must be 'asc' or 'desc'")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HistoryRequest':
        """Create from dictionary"""
        return cls(
            limit=data.get('limit', 50),
            offset=data.get('offset', 0),
            sort_by=data.get('sort_by', 'timestamp'),
            sort_order=data.get('sort_order', 'desc')
        )


@dataclass
class HistorySearchRequest:
    """
    Request schema for history search endpoint
    """
    query: str
    field: str = 'disease'
    limit: int = 50
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.query:
            raise ValidationError("query is required")
        if self.limit < 1 or self.limit > 1000:
            raise ValidationError("limit must be between 1 and 1000")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HistorySearchRequest':
        """Create from dictionary"""
        return cls(
            query=data.get('query', ''),
            field=data.get('field', 'disease'),
            limit=data.get('limit', 50)
        )


@dataclass
class ReportRequest:
    """
    Request schema for report generation endpoint
    """
    report_type: ReportType = ReportType.DETAILED
    date_range: DateRange = DateRange.ALL
    format: str = 'pdf'
    history_ids: Optional[List[int]] = None
    detection_data: Optional[Dict] = None
    
    def validate(self) -> bool:
        """Validate the request data"""
        if self.format not in ['pdf', 'csv']:
            raise ValidationError("format must be 'pdf' or 'csv'")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportRequest':
        """Create from dictionary"""
        return cls(
            report_type=data.get('report_type', ReportType.DETAILED),
            date_range=data.get('date_range', DateRange.ALL),
            format=data.get('format', 'pdf'),
            history_ids=data.get('history_ids'),
            detection_data=data.get('detection_data')
        )


@dataclass
class LoginRequest:
    """
    Request schema for login endpoint
    """
    email: str
    password: str
    remember_me: bool = False
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.email:
            raise ValidationError("email is required")
        if not self.password:
            raise ValidationError("password is required")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LoginRequest':
        """Create from dictionary"""
        return cls(
            email=data.get('email', ''),
            password=data.get('password', ''),
            remember_me=data.get('remember_me', False)
        )


@dataclass
class SignupRequest:
    """
    Request schema for signup endpoint
    """
    name: str
    email: str
    password: str
    mobile: Optional[str] = None
    location: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate the request data"""
        if not self.name:
            raise ValidationError("name is required")
        if not self.email:
            raise ValidationError("email is required")
        if not self.password:
            raise ValidationError("password is required")
        if len(self.password) < 6:
            raise ValidationError("password must be at least 6 characters")
        return True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SignupRequest':
        """Create from dictionary"""
        return cls(
            name=data.get('name', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            mobile=data.get('mobile'),
            location=data.get('location')
        )


# ========================================
# Response Schemas
# ========================================

@dataclass
class BaseResponse:
    """
    Base response schema for all API responses
    """
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DetectionResponse(BaseResponse):
    """
    Response schema for disease detection endpoint
    """
    disease: Optional[str] = None
    confidence: Optional[float] = None
    severity: Optional[str] = None
    severity_color: Optional[str] = None
    class_index: Optional[int] = None
    class_name: Optional[str] = None
    confidence_level: Optional[str] = None
    is_healthy: Optional[bool] = None
    crop: Optional[str] = None
    symptoms: Optional[str] = None
    causes: Optional[str] = None
    season: Optional[str] = None
    treatment: Optional[Dict] = None
    top_predictions: Optional[List[Dict]] = None
    
    @classmethod
    def success_response(cls, prediction_result: Any, treatment: Dict = None) -> 'DetectionResponse':
        """Create success response from prediction result"""
        return cls(
            success=True,
            disease=prediction_result.disease_name,
            confidence=prediction_result.confidence,
            severity=prediction_result.severity,
            class_index=prediction_result.class_index,
            class_name=prediction_result.class_name,
            confidence_level=prediction_result.confidence_level,
            is_healthy=prediction_result.is_healthy,
            treatment=treatment,
            top_predictions=prediction_result.top_predictions,
            message="Detection completed successfully"
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'DetectionResponse':
        """Create error response"""
        return cls(
            success=False,
            error=error_message
        )


@dataclass
class TreatmentResponse(BaseResponse):
    """
    Response schema for treatment recommendations endpoint
    """
    disease: Optional[str] = None
    confidence: Optional[float] = None
    severity: Optional[str] = None
    urgency: Optional[str] = None
    chemical_name: Optional[str] = None
    chemical_dosage: Optional[str] = None
    chemical_frequency: Optional[str] = None
    chemical_method: Optional[str] = None
    chemical_precautions: Optional[str] = None
    chemical_products: List[str] = field(default_factory=list)
    organic_name: Optional[str] = None
    organic_dosage: Optional[str] = None
    organic_frequency: Optional[str] = None
    organic_method: Optional[str] = None
    organic_precautions: Optional[str] = None
    organic_alternative: Optional[str] = None
    cultural_practices: List[str] = field(default_factory=list)
    cultural_spacing: Optional[str] = None
    cultural_watering: Optional[str] = None
    cultural_soil: Optional[str] = None
    prevention_tips: List[str] = field(default_factory=list)
    affected_area: Optional[str] = None
    health_status: Optional[str] = None
    
    @classmethod
    def success_response(cls, treatment_data: Dict) -> 'TreatmentResponse':
        """Create success response from treatment data"""
        return cls(
            success=True,
            **treatment_data,
            message="Treatment recommendations retrieved successfully"
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'TreatmentResponse':
        """Create error response"""
        return cls(
            success=False,
            error=error_message
        )


@dataclass
class WeatherResponse(BaseResponse):
    """
    Response schema for weather data endpoint
    """
    city: Optional[str] = None
    country: Optional[str] = None
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[int] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None
    rainfall: Optional[float] = None
    clouds: Optional[int] = None
    condition: Optional[str] = None
    condition_main: Optional[str] = None
    weather_icon: Optional[str] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    disease_risk: Optional[str] = None
    risk_score: Optional[int] = None
    risk_color: Optional[str] = None
    risk_message: Optional[str] = None
    alerts: List[Dict] = field(default_factory=list)
    spray_advisory: Dict = field(default_factory=dict)
    disease_risks: List[Dict] = field(default_factory=list)
    forecast: List[Dict] = field(default_factory=list)
    is_mock: bool = False
    
    @classmethod
    def success_response(cls, weather_data: Dict) -> 'WeatherResponse':
        """Create success response from weather data"""
        return cls(
            success=True,
            **weather_data,
            message="Weather data retrieved successfully"
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'WeatherResponse':
        """Create error response"""
        return cls(
            success=False,
            error=error_message
        )


@dataclass
class HistoryResponse(BaseResponse):
    """
    Response schema for history endpoints
    """
    total: Optional[int] = None
    count: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    history: List[Dict] = field(default_factory=list)
    
    @classmethod
    def success_response(cls, history_data: List[Dict], total: int = None, 
                         offset: int = 0, limit: int = None) -> 'HistoryResponse':
        """Create success response"""
        return cls(
            success=True,
            total=total or len(history_data),
            count=len(history_data),
            offset=offset,
            limit=limit,
            history=history_data,
            message="History retrieved successfully"
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'HistoryResponse':
        """Create error response"""
        return cls(
            success=False,
            error=error_message
        )


@dataclass
class ReportResponse(BaseResponse):
    """
    Response schema for report generation endpoint
    """
    report_url: Optional[str] = None
    file_size: Optional[int] = None
    file_name: Optional[str] = None
    
    @classmethod
    def success_response(cls, file_name: str, file_size: int = None) -> 'ReportResponse':
        """Create success response"""
        return cls(
            success=True,
            file_name=file_name,
            file_size=file_size,
            message="Report generated successfully"
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'ReportResponse':
        """Create error response"""
        return cls(
            success=False,
            error=error_message
        )


@dataclass
class LoginResponse(BaseResponse):
    """
    Response schema for login endpoint
    """
    user: Optional[Dict] = None
    token: Optional[str] = None
    
    @classmethod
    def success_response(cls, user: Dict, token: str = None) -> 'LoginResponse':
        """Create success response"""
        return cls(
            success=True,
            user=user,
            token=token,
            message="Login successful"
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'LoginResponse':
        """Create error response"""
        return cls(
            success=False,
            error=error_message
        )


@dataclass
class StatisticsResponse(BaseResponse):
    """
    Response schema for statistics endpoint
    """
    total_scans: int = 0
    diseased_count: int = 0
    healthy_count: int = 0
    disease_rate: float = 0
    avg_confidence: float = 0
    severity_breakdown: Dict = field(default_factory=dict)
    disease_breakdown: Dict = field(default_factory=dict)
    most_common_disease: Optional[str] = None
    most_common_severity: Optional[str] = None
    last_scan: Optional[str] = None
    first_scan: Optional[str] = None
    scans_by_month: Dict = field(default_factory=dict)
    recovery_rate: float = 0
    
    @classmethod
    def success_response(cls, stats: Dict) -> 'StatisticsResponse':
        """Create success response from statistics data"""
        return cls(
            success=True,
            **stats,
            message="Statistics retrieved successfully"
        )
    
    @classmethod
    def error_response(cls, error_message: str) -> 'StatisticsResponse':
        """Create error response"""
        return cls(
            success=False,
            error=error_message
        )


# ========================================
# Utility Schemas
# ========================================

@dataclass
class UserSchema:
    """
    User data schema for storage and transfer
    """
    id: int
    name: str
    email: str
    role: str = 'user'
    plan: str = 'basic'
    avatar: Optional[str] = None
    mobile: Optional[str] = None
    location: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'plan': self.plan,
            'avatar': self.avatar,
            'mobile': self.mobile,
            'location': self.location,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        import json
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserSchema':
        """Create from dictionary"""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            plan=data.get('plan', 'basic'),
            avatar=data.get('avatar'),
            mobile=data.get('mobile'),
            location=data.get('location'),
            created_at=data.get('created_at', datetime.now().isoformat()),
            last_login=data.get('last_login')
        )


@dataclass
class DiseaseSchema:
    """
    Disease information schema for library and responses
    """
    id: int
    name: str
    crop: str
    symptoms: str
    causes: str
    treatment: str
    prevention: str
    severity: str
    season: str
    organic_treatment: Optional[str] = None
    image_icon: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'crop': self.crop,
            'symptoms': self.symptoms,
            'causes': self.causes,
            'treatment': self.treatment,
            'organic_treatment': self.organic_treatment,
            'prevention': self.prevention,
            'severity': self.severity,
            'season': self.season,
            'image_icon': self.image_icon
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DiseaseSchema':
        """Create from dictionary"""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            crop=data.get('crop', ''),
            symptoms=data.get('symptoms', ''),
            causes=data.get('causes', ''),
            treatment=data.get('treatment', ''),
            organic_treatment=data.get('organic_treatment'),
            prevention=data.get('prevention', ''),
            severity=data.get('severity', 'Moderate'),
            season=data.get('season', ''),
            image_icon=data.get('image_icon')
        )


# ========================================
# Error Classes
# ========================================

class ValidationError(Exception):
    """
    Exception raised for validation errors in request data
    """
    def __init__(self, message: str, field: str = None, code: str = 'VALIDATION_ERROR'):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        result = {
            'error': 'ValidationError',
            'code': self.code,
            'message': self.message
        }
        if self.field:
            result['field'] = self.field
        return result


class NotFoundError(Exception):
    """
    Exception raised when requested resource is not found
    """
    def __init__(self, message: str, resource_type: str = None, resource_id: Any = None):
        self.message = message
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        result = {
            'error': 'NotFoundError',
            'code': 'RESOURCE_NOT_FOUND',
            'message': self.message
        }
        if self.resource_type:
            result['resource_type'] = self.resource_type
        if self.resource_id:
            result['resource_id'] = self.resource_id
        return result


class AuthenticationError(Exception):
    """
    Exception raised for authentication failures
    """
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'error': 'AuthenticationError',
            'code': 'AUTH_FAILED',
            'message': self.message
        }


class APIError(Exception):
    """
    Generic API error with status code
    """
    def __init__(self, message: str, status_code: int = 500, details: Dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'error': 'APIError',
            'code': 'INTERNAL_ERROR',
            'message': self.message,
            'status_code': self.status_code,
            'details': self.details
        }


# ========================================
# Helper Functions
# ========================================

def validate_request(data: Dict, schema_class) -> Any:
    """
    Validate request data against a schema
    
    Args:
        data: Request data dictionary
        schema_class: Schema class to validate against
        
    Returns:
        Validated schema instance
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        schema = schema_class.from_dict(data)
        schema.validate()
        return schema
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid request data: {str(e)}")


def create_success_response(data: Any, message: str = "Success") -> Dict:
    """
    Create a standardized success response
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Dictionary with standardized format
    """
    return {
        'success': True,
        'message': message,
        'data': data if hasattr(data, 'to_dict') else data,
        'timestamp': datetime.now().isoformat()
    }


def create_error_response(error: Exception, status_code: int = 400) -> Dict:
    """
    Create a standardized error response
    
    Args:
        error: Exception object
        status_code: HTTP status code
        
    Returns:
        Dictionary with standardized error format
    """
    if hasattr(error, 'to_dict'):
        error_dict = error.to_dict()
    else:
        error_dict = {
            'error': type(error).__name__,
            'message': str(error)
        }
    
    return {
        'success': False,
        'error': error_dict,
        'timestamp': datetime.now().isoformat()
    }, status_code