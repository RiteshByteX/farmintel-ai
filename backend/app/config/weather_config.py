"""
FarmIntel AI - Weather API Configuration
Settings for OpenWeatherMap and weather-related services
"""

import os
from dotenv import load_dotenv

load_dotenv()


class WeatherConfig:
    """Configuration for weather API and weather-related services"""
    
    # ========================================
    # API Settings
    # ========================================
    
    # OpenWeatherMap API
    API_KEY = os.getenv('WEATHER_API_KEY', '855806ebd3b87344f662c768d28f2b1c')
    API_BASE_URL = os.getenv('WEATHER_API_BASE_URL', 'https://api.openweathermap.org/data/2.5')
    API_VERSION = '2.5'
    
    # Request settings
    REQUEST_TIMEOUT = int(os.getenv('WEATHER_API_TIMEOUT', 10))
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # ========================================
    # Location Settings
    # ========================================
    
    DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'Chandigarh')
    DEFAULT_COUNTRY = os.getenv('DEFAULT_COUNTRY', 'IN')
    DEFAULT_UNITS = os.getenv('WEATHER_UNITS', 'metric')  # metric, imperial, standard
    DEFAULT_LANGUAGE = os.getenv('WEATHER_LANGUAGE', 'en')
    
    # Supported cities in India
    SUPPORTED_CITIES = [
        'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad',
        'Chennai', 'Kolkata', 'Surat', 'Pune', 'Jaipur', 'Lucknow',
        'Nagpur', 'Indore', 'Bhopal', 'Visakhapatnam', 'Patna',
        'Vadodara', 'Ludhiana', 'Agra', 'Nashik', 'Ranchi',
        'Chandigarh', 'Mysore', 'Coimbatore', 'Kochi', 'Goa'
    ]
    
    # ========================================
    # Weather Data Settings
    # ========================================
    
    FETCH_CURRENT = True
    FETCH_FORECAST = True
    FORECAST_DAYS = 7
    FETCH_HOURLY = False
    FETCH_HISTORICAL = False
    
    # Update intervals (seconds)
    CURRENT_WEATHER_UPDATE_INTERVAL = 1800  # 30 minutes
    FORECAST_UPDATE_INTERVAL = 3600  # 1 hour
    
    # ========================================
    # Disease Risk Calculation Thresholds
    # ========================================
    
    # Temperature thresholds (°C)
    TEMP_OPTIMAL_MIN = 20
    TEMP_OPTIMAL_MAX = 30
    TEMP_WARNING_MIN = 15
    TEMP_WARNING_MAX = 35
    TEMP_CRITICAL_MIN = 10
    TEMP_CRITICAL_MAX = 38
    
    # Humidity thresholds (%)
    HUMIDITY_OPTIMAL_MAX = 60
    HUMIDITY_WARNING_MIN = 65
    HUMIDITY_WARNING_MAX = 80
    HUMIDITY_CRITICAL_MIN = 80
    
    # Wind speed thresholds (km/h)
    WIND_OPTIMAL_MAX = 15
    WIND_WARNING_MIN = 15
    WIND_CRITICAL_MIN = 25
    
    # Rainfall thresholds (mm)
    RAIN_WARNING_MIN = 5
    RAIN_CRITICAL_MIN = 20
    
    # Risk scoring weights
    RISK_WEIGHTS = {
        'temperature': 0.25,
        'humidity': 0.40,
        'wind_speed': 0.15,
        'rainfall': 0.20
    }
    
    # Risk levels
    RISK_LEVELS = {
        'low': {'min_score': 0, 'max_score': 30, 'color': '#10B981', 'message': 'Low risk. Conditions are favorable.'},
        'medium': {'min_score': 30, 'max_score': 60, 'color': '#F59E0B', 'message': 'Medium risk. Monitor crops regularly.'},
        'high': {'min_score': 60, 'max_score': 80, 'color': '#EF4444', 'message': 'High risk. Apply preventive measures.'},
        'critical': {'min_score': 80, 'max_score': 100, 'color': '#7F1D1D', 'message': 'CRITICAL risk! Immediate action required.'}
    }
    
    # ========================================
    # Disease-Specific Risk Factors
    # ========================================
    
    DISEASE_RISK_FACTORS = {
        'Late_Blight': {
            'name': 'Late Blight',
            'temp_min': 15,
            'temp_max': 22,
            'humidity_min': 85,
            'rain_required': True,
            'severity_multiplier': 1.5
        },
        'Early_Blight': {
            'name': 'Early Blight',
            'temp_min': 20,
            'temp_max': 30,
            'humidity_min': 70,
            'rain_required': False,
            'severity_multiplier': 1.2
        },
        'Powdery_Mildew': {
            'name': 'Powdery Mildew',
            'temp_min': 18,
            'temp_max': 28,
            'humidity_min': 40,
            'humidity_max': 60,
            'rain_required': False,
            'severity_multiplier': 1.3
        },
        'Downy_Mildew': {
            'name': 'Downy Mildew',
            'temp_min': 15,
            'temp_max': 25,
            'humidity_min': 85,
            'rain_required': True,
            'severity_multiplier': 1.4
        },
        'Rust': {
            'name': 'Rust',
            'temp_min': 15,
            'temp_max': 25,
            'humidity_min': 80,
            'rain_required': False,
            'severity_multiplier': 1.2
        },
        'Leaf_Spot': {
            'name': 'Leaf Spot',
            'temp_min': 18,
            'temp_max': 28,
            'humidity_min': 75,
            'rain_required': True,
            'severity_multiplier': 1.1
        },
        'Bacterial_Spot': {
            'name': 'Bacterial Spot',
            'temp_min': 20,
            'temp_max': 30,
            'humidity_min': 80,
            'rain_required': True,
            'severity_multiplier': 1.3
        },
        'Scab': {
            'name': 'Scab',
            'temp_min': 10,
            'temp_max': 20,
            'humidity_min': 75,
            'rain_required': True,
            'severity_multiplier': 1.2
        },
        'Cercospora': {
            'name': 'Cercospora Leaf Spot',
            'temp_min': 22,
            'temp_max': 30,
            'humidity_min': 80,
            'rain_required': True,
            'severity_multiplier': 1.1
        },
        'Northern_Leaf_Blight': {
            'name': 'Northern Leaf Blight',
            'temp_min': 18,
            'temp_max': 27,
            'humidity_min': 85,
            'rain_required': True,
            'severity_multiplier': 1.3
        }
    }
    
    # ========================================
    # Alert Messages
    # ========================================
    
    ALERT_MESSAGES = {
        'high_humidity': {
            'title': '⚠️ High Humidity Alert',
            'message': 'Humidity levels above {humidity}% create perfect conditions for fungal diseases. Apply preventive fungicide immediately.',
            'severity': 'high'
        },
        'extreme_temperature': {
            'title': '🌡️ Temperature Alert',
            'message': 'Extreme temperature ({temperature}°C) is stressing your plants. Consider protective measures.',
            'severity': 'high'
        },
        'rain_expected': {
            'title': '☔ Rain Expected',
            'message': 'Rain forecast in next 24 hours. Apply fungicide BEFORE rain for best protection.',
            'severity': 'warning'
        },
        'high_wind': {
            'title': '💨 High Wind Alert',
            'message': 'Wind speeds of {wind_speed} km/h may spread fungal spores. Consider wind barriers.',
            'severity': 'warning'
        },
        'spray_advisory_good': {
            'title': '✅ Good Spraying Conditions',
            'message': 'Perfect conditions for spraying today. Apply as scheduled.',
            'severity': 'success'
        },
        'spray_advisory_poor': {
            'title': '⚠️ Poor Spraying Conditions',
            'message': 'Not recommended to spray today. Wait for better conditions.',
            'severity': 'warning'
        },
        'disease_risk_critical': {
            'title': '🚨 CRITICAL Disease Risk',
            'message': 'Perfect conditions for disease outbreak! Immediate preventive action recommended.',
            'severity': 'critical'
        },
        'disease_risk_high': {
            'title': '⚠️ High Disease Risk',
            'message': 'Conditions favorable for disease development. Monitor crops closely.',
            'severity': 'high'
        },
        'disease_risk_medium': {
            'title': '📋 Medium Disease Risk',
            'message': 'Moderate risk. Regular monitoring recommended.',
            'severity': 'medium'
        },
        'disease_risk_low': {
            'title': '✅ Low Disease Risk',
            'message': 'Conditions are favorable. Continue regular monitoring.',
            'severity': 'low'
        }
    }
    
    # ========================================
    # Helper Methods
    # ========================================
    
    @classmethod
    def get_api_url(cls, endpoint='weather'):
        """Get full API URL for endpoint"""
        endpoints = {
            'weather': '/weather',
            'forecast': '/forecast',
            'air_pollution': '/air_pollution',
            'onecall': '/onecall'
        }
        return f"{cls.API_BASE_URL}{endpoints.get(endpoint, '/weather')}"
    
    @classmethod
    def get_request_params(cls, city=None, lat=None, lon=None):
        """Get default request parameters for API calls"""
        params = {
            'appid': cls.API_KEY,
            'units': cls.DEFAULT_UNITS,
            'lang': cls.DEFAULT_LANGUAGE
        }
        
        if city:
            params['q'] = f"{city},{cls.DEFAULT_COUNTRY}"
        elif lat is not None and lon is not None:
            params['lat'] = lat
            params['lon'] = lon
        else:
            params['q'] = f"{cls.DEFAULT_CITY},{cls.DEFAULT_COUNTRY}"
        
        return params
    
    @classmethod
    def is_api_configured(cls):
        """Check if weather API is properly configured"""
        return bool(cls.API_KEY) and cls.API_KEY != ''
    
    @classmethod
    def calculate_disease_risk(cls, temperature, humidity, wind_speed, rainfall):
        """
        Calculate overall disease risk based on weather conditions
        
        Returns:
            dict: Risk level, score, and message
        """
        risk_score = 0
        
        # Temperature factor
        if temperature < cls.TEMP_WARNING_MIN or temperature > cls.TEMP_WARNING_MAX:
            risk_score += 25
        elif temperature < cls.TEMP_OPTIMAL_MIN or temperature > cls.TEMP_OPTIMAL_MAX:
            risk_score += 15
        elif temperature < cls.TEMP_CRITICAL_MIN or temperature > cls.TEMP_CRITICAL_MAX:
            risk_score += 35
        
        # Humidity factor (most important)
        if humidity >= cls.HUMIDITY_CRITICAL_MIN:
            risk_score += 40
        elif humidity >= cls.HUMIDITY_WARNING_MIN:
            risk_score += 25
        elif humidity > cls.HUMIDITY_OPTIMAL_MAX:
            risk_score += 10
        
        # Wind speed factor
        if wind_speed >= cls.WIND_CRITICAL_MIN:
            risk_score += 15
        elif wind_speed >= cls.WIND_WARNING_MIN:
            risk_score += 8
        
        # Rainfall factor
        if rainfall >= cls.RAIN_CRITICAL_MIN:
            risk_score += 20
        elif rainfall >= cls.RAIN_WARNING_MIN:
            risk_score += 10
        
        # Determine risk level
        if risk_score >= cls.RISK_LEVELS['critical']['min_score']:
            risk_level = 'critical'
        elif risk_score >= cls.RISK_LEVELS['high']['min_score']:
            risk_level = 'high'
        elif risk_score >= cls.RISK_LEVELS['medium']['min_score']:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk': risk_level.upper(),
            'score': risk_score,
            'color': cls.RISK_LEVELS[risk_level]['color'],
            'message': cls.RISK_LEVELS[risk_level]['message']
        }
    
    @classmethod
    def get_alert_messages(cls, weather_data):
        """
        Generate alert messages based on weather data
        
        Returns:
            list: List of alert messages
        """
        alerts = []
        
        # High humidity alert
        if weather_data.get('humidity', 0) >= cls.HUMIDITY_CRITICAL_MIN:
            alert = cls.ALERT_MESSAGES['high_humidity'].copy()
            alert['message'] = alert['message'].format(humidity=weather_data.get('humidity'))
            alerts.append(alert)
        
        # Extreme temperature alert
        temp = weather_data.get('temperature', 25)
        if temp <= cls.TEMP_CRITICAL_MIN or temp >= cls.TEMP_CRITICAL_MAX:
            alert = cls.ALERT_MESSAGES['extreme_temperature'].copy()
            alert['message'] = alert['message'].format(temperature=temp)
            alerts.append(alert)
        
        # Rain alert
        if weather_data.get('rainfall', 0) > 0:
            alerts.append(cls.ALERT_MESSAGES['rain_expected'])
        
        # High wind alert
        wind = weather_data.get('wind_speed', 0)
        if wind >= cls.WIND_CRITICAL_MIN:
            alert = cls.ALERT_MESSAGES['high_wind'].copy()
            alert['message'] = alert['message'].format(wind_speed=wind)
            alerts.append(alert)
        
        return alerts
    
    @classmethod
    def get_spray_advisory(cls, temperature, humidity, wind_speed, rainfall):
        """
        Get spraying advisory based on weather conditions
        
        Returns:
            dict: Advisory message and status
        """
        # Check for poor conditions
        if wind_speed > cls.WIND_OPTIMAL_MAX:
            return {
                'status': 'poor',
                'message': cls.ALERT_MESSAGES['spray_advisory_poor']['message'],
                'recommendation': 'Wait for calmer conditions (wind speed <15 km/h)'
            }
        
        if rainfall > 0:
            return {
                'status': 'poor',
                'message': 'Rain expected. Apply fungicide BEFORE rain.',
                'recommendation': 'Apply preventive treatment before rain'
            }
        
        if temperature > cls.TEMP_OPTIMAL_MAX:
            return {
                'status': 'caution',
                'message': 'High temperature. Spray early morning or late evening.',
                'recommendation': 'Spray during cooler hours (early morning or dusk)'
            }
        
        if humidity > cls.HUMIDITY_WARNING_MIN:
            return {
                'status': 'caution',
                'message': 'High humidity present. Consider adding spreader-sticker.',
                'recommendation': 'Use appropriate adjuvants for better coverage'
            }
        
        # Good conditions
        return {
            'status': 'good',
            'message': cls.ALERT_MESSAGES['spray_advisory_good']['message'],
            'recommendation': 'Proceed with spraying as scheduled'
        }