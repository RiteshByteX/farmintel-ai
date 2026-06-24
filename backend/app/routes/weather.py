"""
Weather Routes - Weather data and disease risk forecasting endpoints
Handles current weather, forecasts, and disease risk calculations
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from app.controllers.weather_controller import WeatherController
from app.models.schemas import WeatherRequest, ValidationError

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/weather', methods=['GET'])
def get_weather():
    """
    Get current weather data for a location
    GET /api/weather?city=Chandigarh
    GET /api/weather?lat=30.7333&lon=76.7794
    GET /api/weather?pincode=160001
    
    Query Parameters:
        city: City name (e.g., Chandigarh, Mumbai, Delhi, Bangalore)
        lat: Latitude
        lon: Longitude
        pincode: Indian postal code
        
    Returns:
        JSON with weather data and disease risk analysis
    """
    try:
        # Get query parameters
        city = request.args.get('city')
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        pincode = request.args.get('pincode')
        
        # Convert lat/lon to float if provided
        if lat:
            lat = float(lat)
        if lon:
            lon = float(lon)
        
        # Validate request
        weather_request = WeatherRequest(city=city, lat=lat, lon=lon, pincode=pincode)
        weather_request.validate()
        
        # Get weather data
        if pincode:
            weather_data = WeatherController.get_weather_by_pincode(pincode)
        else:
            weather_data = WeatherController.get_weather(city=city, lat=lat, lon=lon)
        
        # Get air quality if coordinates available
        air_quality = None
        if lat and lon:
            air_quality = WeatherController.get_air_quality(lat, lon)
        
        return jsonify({
            'success': True,
            'location': {
                'city': weather_data.get('city'),
                'country': weather_data.get('country'),
                'coordinates': {
                    'lat': lat,
                    'lon': lon
                } if lat and lon else None
            },
            'current': {
                'temperature': weather_data.get('temperature'),
                'feels_like': weather_data.get('feels_like'),
                'humidity': weather_data.get('humidity'),
                'pressure': weather_data.get('pressure'),
                'wind_speed': weather_data.get('wind_speed'),
                'wind_direction': weather_data.get('wind_direction'),
                'rainfall': weather_data.get('rainfall'),
                'clouds': weather_data.get('clouds'),
                'condition': weather_data.get('condition'),
                'condition_main': weather_data.get('condition_main'),
                'weather_icon': weather_data.get('weather_icon'),
                'sunrise': weather_data.get('sunrise'),
                'sunset': weather_data.get('sunset')
            },
            'disease_risk': {
                'risk_level': weather_data.get('disease_risk'),
                'risk_score': weather_data.get('risk_score'),
                'risk_color': weather_data.get('risk_color'),
                'risk_message': weather_data.get('risk_message'),
                'disease_specific_risks': weather_data.get('disease_risks', [])
            },
            'alerts': weather_data.get('alerts', []),
            'spray_advisory': weather_data.get('spray_advisory'),
            'forecast': weather_data.get('forecast', []),
            'air_quality': air_quality,
            'is_mock': weather_data.get('is_mock', False),
            'timestamp': datetime.now().isoformat()
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': e.message,
            'field': e.field
        }), 400
    except Exception as e:
        current_app.logger.error(f"Weather API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching weather data'
        }), 500


@weather_bp.route('/weather/forecast', methods=['GET'])
def get_weather_forecast():
    """
    Get 7-day weather forecast
    GET /api/weather/forecast?city=Chandigarh
    GET /api/weather/forecast?lat=30.7333&lon=76.7794
    
    Query Parameters:
        city: City name
        lat: Latitude
        lon: Longitude
        days: Number of days (1-7, default 7)
        
    Returns:
        JSON with forecast data
    """
    try:
        city = request.args.get('city')
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        days = request.args.get('days', 7, type=int)
        
        # Limit days to 7
        days = min(days, 7)
        
        # Get forecast
        if city:
            weather_data = WeatherController.get_weather(city=city)
            forecast = weather_data.get('forecast', [])
        elif lat and lon:
            weather_data = WeatherController.get_weather(lat=float(lat), lon=float(lon))
            forecast = weather_data.get('forecast', [])
        else:
            weather_data = WeatherController.get_weather()
            forecast = weather_data.get('forecast', [])
        
        # Limit to requested days
        forecast = forecast[:days]
        
        return jsonify({
            'success': True,
            'location': city or WeatherController._get_city_from_config(),
            'days': len(forecast),
            'forecast': forecast,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Forecast error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching forecast data'
        }), 500


@weather_bp.route('/weather/risk', methods=['GET'])
def get_disease_risk():
    """
    Calculate disease risk based on weather conditions
    GET /api/weather/risk?city=Chandigarh
    GET /api/weather/risk?temp=28&humidity=85&wind=12&rain=2.4
    
    Query Parameters:
        city: City name (to get real weather)
        temp: Temperature (if not using city)
        humidity: Humidity (if not using city)
        wind: Wind speed (if not using city)
        rain: Rainfall (if not using city)
        
    Returns:
        JSON with disease risk analysis
    """
    try:
        # Check if custom parameters provided
        temp = request.args.get('temp', type=float)
        humidity = request.args.get('humidity', type=float)
        wind = request.args.get('wind', type=float)
        rain = request.args.get('rain', type=float)
        
        if temp is not None and humidity is not None:
            # Calculate risk from provided parameters
            from app.config.weather_config import WeatherConfig
            
            risk = WeatherConfig.calculate_disease_risk(temp, humidity, wind or 0, rain or 0)
            spray_advisory = WeatherConfig.get_spray_advisory(temp, humidity, wind or 0, rain or 0)
            alerts = WeatherConfig.get_alert_messages({
                'temperature': temp,
                'humidity': humidity,
                'wind_speed': wind or 0,
                'rainfall': rain or 0
            })
            
            return jsonify({
                'success': True,
                'conditions': {
                    'temperature': temp,
                    'humidity': humidity,
                    'wind_speed': wind,
                    'rainfall': rain
                },
                'disease_risk': {
                    'risk_level': risk['risk'],
                    'risk_score': risk['score'],
                    'risk_color': risk['color'],
                    'risk_message': risk['message']
                },
                'alerts': alerts,
                'spray_advisory': spray_advisory,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Get risk from city weather
            city = request.args.get('city', WeatherConfig.DEFAULT_CITY)
            weather_data = WeatherController.get_weather(city=city)
            
            return jsonify({
                'success': True,
                'location': city,
                'current_conditions': {
                    'temperature': weather_data.get('temperature'),
                    'humidity': weather_data.get('humidity'),
                    'wind_speed': weather_data.get('wind_speed'),
                    'rainfall': weather_data.get('rainfall')
                },
                'disease_risk': {
                    'risk_level': weather_data.get('disease_risk'),
                    'risk_score': weather_data.get('risk_score'),
                    'risk_color': weather_data.get('risk_color'),
                    'risk_message': weather_data.get('risk_message'),
                    'disease_specific': weather_data.get('disease_risks', [])
                },
                'alerts': weather_data.get('alerts', []),
                'spray_advisory': weather_data.get('spray_advisory'),
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        current_app.logger.error(f"Disease risk error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while calculating disease risk'
        }), 500


@weather_bp.route('/weather/alerts', methods=['GET'])
def get_weather_alerts():
    """
    Get weather alerts for a location
    GET /api/weather/alerts?city=Chandigarh
    
    Query Parameters:
        city: City name
        
    Returns:
        JSON with weather alerts
    """
    try:
        from app.config.weather_config import WeatherConfig
        city = request.args.get('city', WeatherConfig.DEFAULT_CITY)
        weather_data = WeatherController.get_weather(city=city)
        
        return jsonify({
            'success': True,
            'location': city,
            'alerts': weather_data.get('alerts', []),
            'total_alerts': len(weather_data.get('alerts', [])),
            'high_risk': weather_data.get('disease_risk') == 'HIGH',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Weather alerts error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching weather alerts'
        }), 500


@weather_bp.route('/weather/spray-advisory', methods=['GET'])
def get_spray_advisory():
    """
    Get spray advisory based on weather conditions
    GET /api/weather/spray-advisory?city=Chandigarh
    GET /api/weather/spray-advisory?temp=28&humidity=85&wind=12
    
    Query Parameters:
        city: City name (to get real weather)
        temp: Temperature (if not using city)
        humidity: Humidity (if not using city)
        wind: Wind speed (if not using city)
        
    Returns:
        JSON with spray advisory
    """
    try:
        from app.config.weather_config import WeatherConfig
        
        temp = request.args.get('temp', type=float)
        humidity = request.args.get('humidity', type=float)
        wind = request.args.get('wind', type=float)
        
        if temp is not None and humidity is not None:
            advisory = WeatherConfig.get_spray_advisory(temp, humidity, wind or 0, 0)
            
            return jsonify({
                'success': True,
                'conditions': {
                    'temperature': temp,
                    'humidity': humidity,
                    'wind_speed': wind
                },
                'advisory': advisory,
                'recommendation': advisory.get('recommendation'),
                'timestamp': datetime.now().isoformat()
            })
        else:
            city = request.args.get('city', WeatherConfig.DEFAULT_CITY)
            weather_data = WeatherController.get_weather(city=city)
            
            return jsonify({
                'success': True,
                'location': city,
                'current_conditions': {
                    'temperature': weather_data.get('temperature'),
                    'humidity': weather_data.get('humidity'),
                    'wind_speed': weather_data.get('wind_speed')
                },
                'advisory': weather_data.get('spray_advisory'),
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        current_app.logger.error(f"Spray advisory error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while getting spray advisory'
        }), 500


@weather_bp.route('/weather/cities', methods=['GET'])
def get_supported_cities():
    """
    Get list of supported cities
    GET /api/weather/cities
    
    Returns:
        JSON with list of supported cities
    """
    from app.config.weather_config import WeatherConfig
    
    return jsonify({
        'success': True,
        'total': len(WeatherConfig.SUPPORTED_CITIES),
        'cities': WeatherConfig.SUPPORTED_CITIES,
        'default_city': WeatherConfig.DEFAULT_CITY,
        'timestamp': datetime.now().isoformat()
    })


@weather_bp.route('/weather/health', methods=['GET'])
def weather_health():
    """
    Check weather service health
    GET /api/weather/health
    
    Returns:
        JSON with service status
    """
    from app.config.weather_config import WeatherConfig
    
    return jsonify({
        'success': True,
        'service': 'weather_api',
        'api_configured': WeatherConfig.is_api_configured(),
        'default_city': WeatherConfig.DEFAULT_CITY,
        'supported_cities': len(WeatherConfig.SUPPORTED_CITIES),
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


# Helper method to get city from config
@staticmethod
def _get_city_from_config():
    """Get default city from configuration"""
    from app.config.weather_config import WeatherConfig
    return WeatherConfig.DEFAULT_CITY