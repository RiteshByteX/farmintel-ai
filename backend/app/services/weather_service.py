"""
Weather Service - Weather API Integration Service
Handles fetching weather data from OpenWeatherMap API and calculating disease risks
"""

import requests
import json
from datetime import datetime, timedelta
from flask import current_app
from typing import Dict, Any, Optional, List
import random
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service for fetching and processing weather data
    Integrates with OpenWeatherMap API and provides disease risk calculations
    """
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        'critical': {'min_score': 80, 'color': '#7F1D1D', 'level': 'Critical'},
        'high': {'min_score': 60, 'color': '#EF4444', 'level': 'High'},
        'medium': {'min_score': 40, 'color': '#F59E0B', 'level': 'Medium'},
        'low': {'min_score': 0, 'color': '#10B981', 'level': 'Low'}
    }
    
    # Temperature thresholds (°C)
    TEMP_THRESHOLDS = {
        'critical_min': 5,
        'warning_min': 10,
        'optimal_min': 20,
        'optimal_max': 30,
        'warning_max': 35,
        'critical_max': 38
    }
    
    # Humidity thresholds (%)
    HUMIDITY_THRESHOLDS = {
        'critical': 85,
        'high': 75,
        'medium': 65,
        'optimal': 60
    }
    
    # Wind thresholds (km/h)
    WIND_THRESHOLDS = {
        'critical': 25,
        'high': 20,
        'medium': 15
    }
    
    # Rain thresholds (mm)
    RAIN_THRESHOLDS = {
        'critical': 20,
        'high': 10,
        'medium': 5
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize weather service
        
        Args:
            api_key: OpenWeatherMap API key
        """
        # Store api_key directly without using current_app
        self._api_key = api_key
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        self.timeout = 10
        self.units = 'metric'
        self.lang = 'en'
        
        # Cache for weather data
        self._cache = {}
        self._cache_duration = 1800  # 30 minutes
        
        # Supported cities
        self.supported_cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad',
            'Chennai', 'Kolkata', 'Surat', 'Pune', 'Jaipur', 'Lucknow',
            'Nagpur', 'Indore', 'Bhopal', 'Visakhapatnam', 'Patna',
            'Vadodara', 'Ludhiana', 'Agra', 'Nashik', 'Ranchi',
            'Chandigarh', 'Mysore', 'Coimbatore', 'Kochi', 'Goa'
        ]
        
        # Don't access current_app here!
        if self._api_key:
            print("✅ Weather API configured with provided key")
        else:
            print("⚠️ Weather API key not provided - will try config later")

    @property
    def api_key(self):
        """Lazy load API key from config when needed"""
        if self._api_key:
            return self._api_key
        
        # Try environment variable
        import os
        self._api_key = os.environ.get('WEATHER_API_KEY', '')
        
        if self._api_key:
            return self._api_key
        
        # Try Flask config (only if in app context)
        try:
            from flask import current_app
            self._api_key = current_app.config.get('WEATHER_API_KEY', '')
        except (RuntimeError, ImportError):
            pass
        
        return self._api_key
    
    def is_configured(self) -> bool:
        """Check if weather API is properly configured"""
        return bool(self.api_key) and self.api_key != ''
    
    def get_current_weather(self, city: str = None, lat: float = None, lon: float = None, 
                            include_forecast: bool = False) -> Dict:
        """
        Get current weather data for a location
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            include_forecast: Whether to include forecast data
            
        Returns:
            Dictionary with weather data
        """
        # Check cache
        cache_key = city or f"{lat},{lon}" or "default"
        if cache_key in self._cache:
            cached_data, cache_time = self._cache[cache_key]
            if (datetime.now() - cache_time).seconds < self._cache_duration:
                logger.info(f"Returning cached weather for {cache_key}")
                return cached_data
        
        try:
            if self.is_configured():
                weather_data = self._fetch_from_api(city, lat, lon)
            else:
                logger.warning("Weather API not configured, using mock data")
                weather_data = self._get_mock_weather(city or 'Mumbai')
            
            # Add forecast if requested
            if include_forecast:
                weather_data['forecast'] = self.get_forecast(city, lat, lon)
            
            # Cache the result
            self._cache[cache_key] = (weather_data, datetime.now())
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            return self._get_mock_weather(city or 'Mumbai')
    
    def _fetch_from_api(self, city: str = None, lat: float = None, lon: float = None) -> Dict:
        """
        Fetch weather data from OpenWeatherMap API
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            
        Returns:
            Parsed weather data
        """
        # Build URL and params
        if city:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{city},IN",
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang
            }
        elif lat is not None and lon is not None:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang
            }
        else:
            # Default to Mumbai
            url = f"{self.base_url}/weather"
            params = {
                'q': "Mumbai,IN",
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang
            }
        
        # Make request
        response = requests.get(url, params=params, timeout=self.timeout)
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Parse response
        weather_condition = data.get('weather', [{}])[0]
        main_data = data.get('main', {})
        wind_data = data.get('wind', {})
        sys_data = data.get('sys', {})
        
        # Calculate rainfall
        rainfall = 0
        if 'rain' in data:
            rainfall = data['rain'].get('1h', 0) or data['rain'].get('3h', 0) / 3 or 0
        
        # Calculate wind speed in km/h (convert from m/s)
        wind_speed_kmh = wind_data.get('speed', 2.5) * 3.6
        
        weather_data = {
            'success': True,
            'city': data.get('name', city or 'Unknown'),
            'country': sys_data.get('country', 'IN'),
            'temperature': round(main_data.get('temp', 25), 1),
            'feels_like': round(main_data.get('feels_like', 25), 1),
            'temp_min': round(main_data.get('temp_min', 20), 1),
            'temp_max': round(main_data.get('temp_max', 30), 1),
            'humidity': main_data.get('humidity', 65),
            'pressure': main_data.get('pressure', 1013),
            'wind_speed': round(wind_speed_kmh, 1),
            'wind_direction': wind_data.get('deg', 0),
            'wind_gust': round(wind_data.get('gust', 0) * 3.6, 1) if wind_data.get('gust') else 0,
            'rainfall': round(rainfall, 1),
            'clouds': data.get('clouds', {}).get('all', 0),
            'condition': weather_condition.get('description', 'Unknown'),
            'condition_main': weather_condition.get('main', 'Clear'),
            'weather_icon': weather_condition.get('icon', '01d'),
            'weather_id': weather_condition.get('id', 800),
            'sunrise': datetime.fromtimestamp(sys_data.get('sunrise', 0)).strftime('%I:%M %p'),
            'sunset': datetime.fromtimestamp(sys_data.get('sunset', 0)).strftime('%I:%M %p'),
            'timestamp': datetime.now().isoformat(),
            'is_mock': False
        }
        
        # Calculate additional metrics
        weather_data['disease_risk'] = self._calculate_disease_risk(weather_data)
        weather_data['spray_advisory'] = self._get_spray_advisory(weather_data)
        weather_data['alerts'] = self._get_weather_alerts(weather_data)
        weather_data['disease_risks'] = self._calculate_disease_specific_risks(weather_data)
        weather_data['heat_index'] = self._calculate_heat_index(
            weather_data['temperature'], weather_data['humidity']
        )
        weather_data['dew_point'] = self._calculate_dew_point(
            weather_data['temperature'], weather_data['humidity']
        )
        
        return weather_data
    
    def get_forecast(self, city: str = None, lat: float = None, lon: float = None, days: int = 7) -> List[Dict]:
        """
        Get weather forecast for a location
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            days: Number of days (max 7)
            
        Returns:
            List of forecast data
        """
        days = min(days, 7)  # Limit to 7 days
        
        try:
            if self.is_configured():
                return self._fetch_forecast_from_api(city, lat, lon, days)
            else:
                return self._get_mock_forecast(city or 'Mumbai', days)
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            return self._get_mock_forecast(city or 'Mumbai', days)
    
    def _fetch_forecast_from_api(self, city: str = None, lat: float = None, lon: float = None, days: int = 7) -> List[Dict]:
        """
        Fetch forecast from OpenWeatherMap API
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            days: Number of days
            
        Returns:
            List of forecast data
        """
        # Build URL
        if city:
            url = f"{self.base_url}/forecast"
            params = {
                'q': f"{city},IN",
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang,
                'cnt': days * 8  # 8 readings per day (every 3 hours)
            }
        elif lat is not None and lon is not None:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang,
                'cnt': days * 8
            }
        else:
            url = f"{self.base_url}/forecast"
            params = {
                'q': "Mumbai,IN",
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang,
                'cnt': days * 8
            }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        
        if response.status_code != 200:
            raise Exception(f"Forecast API returned status {response.status_code}")
        
        data = response.json()
        
        # Process forecast data
        forecast_by_day = {}
        
        for item in data.get('list', []):
            dt = datetime.fromtimestamp(item.get('dt', 0))
            day_key = dt.strftime('%Y-%m-%d')
            
            if day_key not in forecast_by_day:
                forecast_by_day[day_key] = {
                    'date': day_key,
                    'day_name': dt.strftime('%A'),
                    'temps': [],
                    'temp_mins': [],
                    'temp_maxs': [],
                    'humidities': [],
                    'conditions': [],
                    'icons': [],
                    'rain': 0,
                    'wind_speeds': []
                }
            
            forecast_by_day[day_key]['temps'].append(item.get('main', {}).get('temp', 25))
            forecast_by_day[day_key]['temp_mins'].append(item.get('main', {}).get('temp_min', 25))
            forecast_by_day[day_key]['temp_maxs'].append(item.get('main', {}).get('temp_max', 25))
            forecast_by_day[day_key]['humidities'].append(item.get('main', {}).get('humidity', 65))
            forecast_by_day[day_key]['conditions'].append(
                item.get('weather', [{}])[0].get('description', 'Unknown')
            )
            forecast_by_day[day_key]['icons'].append(
                item.get('weather', [{}])[0].get('icon', '01d')
            )
            forecast_by_day[day_key]['wind_speeds'].append(
                item.get('wind', {}).get('speed', 2.5) * 3.6  # Convert to km/h
            )
            
            if 'rain' in item:
                forecast_by_day[day_key]['rain'] += item['rain'].get('3h', 0)
        
        # Calculate daily averages
        forecast = []
        for day_key, day_data in list(forecast_by_day.items())[:days]:
            avg_temp = sum(day_data['temps']) / len(day_data['temps'])
            min_temp = min(day_data['temp_mins'])
            max_temp = max(day_data['temp_maxs'])
            avg_humidity = sum(day_data['humidities']) / len(day_data['humidities'])
            avg_wind = sum(day_data['wind_speeds']) / len(day_data['wind_speeds'])
            
            # Get most common condition and icon
            condition = max(set(day_data['conditions']), key=day_data['conditions'].count)
            icon = max(set(day_data['icons']), key=day_data['icons'].count)
            
            risk = self._calculate_risk_from_conditions(avg_temp, avg_humidity, day_data['rain'], avg_wind)
            
            forecast.append({
                'date': day_data['date'],
                'day': day_data['day_name'][:3],
                'full_day': day_data['day_name'],
                'temperature': round(avg_temp, 1),
                'temp_min': round(min_temp, 1),
                'temp_max': round(max_temp, 1),
                'humidity': round(avg_humidity, 1),
                'condition': condition,
                'weather_icon': icon,
                'rainfall': round(day_data['rain'], 1),
                'wind_speed': round(avg_wind, 1),
                'disease_risk': risk['risk'],
                'risk_color': risk['color'],
                'risk_score': risk['score']
            })
        
        return forecast
    
    def _calculate_disease_risk(self, weather_data: Dict) -> Dict:
        """
        Calculate disease risk based on weather conditions
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            Risk assessment dictionary
        """
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        wind = weather_data.get('wind_speed', 10)
        rain = weather_data.get('rainfall', 0)
        
        return self._calculate_risk_from_conditions(temp, humidity, rain, wind)
    
    def _calculate_risk_from_conditions(self, temp: float, humidity: float, rain: float, wind: float = 0) -> Dict:
        """
        Calculate risk from weather conditions
        
        Args:
            temp: Temperature in Celsius
            humidity: Humidity percentage
            rain: Rainfall in mm
            wind: Wind speed in km/h
            
        Returns:
            Risk assessment dictionary
        """
        risk_score = 0
        factors = []
        
        # Temperature factor
        if temp <= self.TEMP_THRESHOLDS['critical_min'] or temp >= self.TEMP_THRESHOLDS['critical_max']:
            risk_score += 30
            factors.append(f"extreme_temperature_{temp}°C")
        elif temp <= self.TEMP_THRESHOLDS['warning_min'] or temp >= self.TEMP_THRESHOLDS['warning_max']:
            risk_score += 20
            factors.append(f"temperature_stress_{temp}°C")
        elif temp < self.TEMP_THRESHOLDS['optimal_min'] or temp > self.TEMP_THRESHOLDS['optimal_max']:
            risk_score += 10
            factors.append(f"suboptimal_temperature_{temp}°C")
        
        # Humidity factor (most important for fungal diseases)
        if humidity >= self.HUMIDITY_THRESHOLDS['critical']:
            risk_score += 40
            factors.append(f"critical_humidity_{humidity}%")
        elif humidity >= self.HUMIDITY_THRESHOLDS['high']:
            risk_score += 30
            factors.append(f"high_humidity_{humidity}%")
        elif humidity >= self.HUMIDITY_THRESHOLDS['medium']:
            risk_score += 15
            factors.append(f"moderate_humidity_{humidity}%")
        
        # Wind factor
        if wind >= self.WIND_THRESHOLDS['critical']:
            risk_score += 15
            factors.append(f"high_wind_{wind}km/h")
        elif wind >= self.WIND_THRESHOLDS['high']:
            risk_score += 8
            factors.append(f"moderate_wind_{wind}km/h")
        
        # Rain factor
        if rain >= self.RAIN_THRESHOLDS['critical']:
            risk_score += 25
            factors.append(f"heavy_rain_{rain}mm")
        elif rain >= self.RAIN_THRESHOLDS['high']:
            risk_score += 15
            factors.append(f"moderate_rain_{rain}mm")
        elif rain > 0:
            risk_score += 8
            factors.append(f"light_rain_{rain}mm")
        
        # Determine risk level
        risk_score = min(risk_score, 100)  # Cap at 100
        
        if risk_score >= self.RISK_THRESHOLDS['critical']['min_score']:
            risk = self.RISK_THRESHOLDS['critical']['level']
            color = self.RISK_THRESHOLDS['critical']['color']
            message = '🚨 CRITICAL: Perfect conditions for disease outbreak! Immediate preventive action required.'
        elif risk_score >= self.RISK_THRESHOLDS['high']['min_score']:
            risk = self.RISK_THRESHOLDS['high']['level']
            color = self.RISK_THRESHOLDS['high']['color']
            message = '⚠️ High disease risk detected. Apply preventive fungicide immediately.'
        elif risk_score >= self.RISK_THRESHOLDS['medium']['min_score']:
            risk = self.RISK_THRESHOLDS['medium']['level']
            color = self.RISK_THRESHOLDS['medium']['color']
            message = '📋 Medium disease risk. Monitor crops regularly.'
        else:
            risk = self.RISK_THRESHOLDS['low']['level']
            color = self.RISK_THRESHOLDS['low']['color']
            message = '✅ Low disease risk. Conditions are favorable.'
        
        return {
            'risk': risk,
            'score': risk_score,
            'color': color,
            'message': message,
            'factors': factors
        }
    
    def _calculate_disease_specific_risks(self, weather_data: Dict) -> List[Dict]:
        """
        Calculate risks for specific diseases
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            List of disease-specific risk assessments
        """
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        rain = weather_data.get('rainfall', 0)
        
        disease_factors = {
            'Late Blight': {
                'temp_min': 15, 'temp_max': 22, 'humidity_min': 85,
                'message': 'Cool, wet conditions favor Late Blight'
            },
            'Early Blight': {
                'temp_min': 20, 'temp_max': 30, 'humidity_min': 70,
                'message': 'Warm, humid conditions favor Early Blight'
            },
            'Powdery Mildew': {
                'temp_min': 18, 'temp_max': 28, 'humidity_min': 40, 'humidity_max': 60,
                'message': 'Moderate temperatures with low humidity favor Powdery Mildew'
            },
            'Downy Mildew': {
                'temp_min': 15, 'temp_max': 25, 'humidity_min': 85,
                'message': 'Cool, wet conditions favor Downy Mildew'
            },
            'Rust': {
                'temp_min': 15, 'temp_max': 25, 'humidity_min': 80,
                'message': 'Humid conditions with moderate temperatures favor Rust'
            },
            'Leaf Spot': {
                'temp_min': 18, 'temp_max': 28, 'humidity_min': 75,
                'message': 'Warm, humid conditions favor Leaf Spot'
            },
            'Bacterial Spot': {
                'temp_min': 20, 'temp_max': 30, 'humidity_min': 80,
                'message': 'Warm, wet conditions favor Bacterial Spot'
            },
            'Anthracnose': {
                'temp_min': 22, 'temp_max': 28, 'humidity_min': 85,
                'message': 'Warm, wet conditions favor Anthracnose'
            },
            'Scab': {
                'temp_min': 10, 'temp_max': 20, 'humidity_min': 75,
                'message': 'Cool, wet conditions favor Scab'
            }
        }
        
        risks = []
        
        for disease, factors in disease_factors.items():
            temp_ok = factors['temp_min'] <= temp <= factors['temp_max']
            humidity_ok = humidity >= factors['humidity_min']
            
            if 'humidity_max' in factors:
                humidity_ok = humidity_ok and humidity <= factors['humidity_max']
            
            if temp_ok and humidity_ok:
                risk = 'High'
                risk_score = 80
                if rain > 0 and 'rain' in str(factors).lower():
                    risk_score = 90
            elif temp_ok or humidity_ok:
                risk = 'Medium'
                risk_score = 50
            else:
                risk = 'Low'
                risk_score = 20
            
            risks.append({
                'disease': disease,
                'risk': risk,
                'risk_score': risk_score,
                'message': factors.get('message', f"{risk} risk of {disease}"),
                'temp_optimal': temp_ok,
                'humidity_optimal': humidity_ok
            })
        
        # Sort by risk (High first)
        risk_order = {'High': 3, 'Medium': 2, 'Low': 1}
        risks.sort(key=lambda x: risk_order.get(x['risk'], 0), reverse=True)
        
        return risks[:7]  # Return top 7
    
    def _get_spray_advisory(self, weather_data: Dict) -> Dict:
        """
        Get spray advisory based on weather conditions
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            Spray advisory dictionary
        """
        wind = weather_data.get('wind_speed', 10)
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        rain = weather_data.get('rainfall', 0)
        
        if wind > self.WIND_THRESHOLDS['critical']:
            return {
                'status': 'poor',
                'severity': 'high',
                'message': '⚠️ Not recommended today. Wind speed too high.',
                'recommendation': f'Wait for calmer conditions (wind speed <{self.WIND_THRESHOLDS["high"]} km/h)'
            }
        elif rain > 0:
            return {
                'status': 'poor',
                'severity': 'warning',
                'message': '☔ Rain expected. Apply fungicide BEFORE rain.',
                'recommendation': 'Apply preventive treatment before rain. Allow 2-4 hours to dry.'
            }
        elif temp > self.TEMP_THRESHOLDS['warning_max']:
            return {
                'status': 'caution',
                'severity': 'warning',
                'message': f'🌡️ High temperature ({temp}°C). Spray early morning or late evening.',
                'recommendation': 'Spray during cooler hours (6-9 AM or 5-7 PM)'
            }
        elif humidity > self.HUMIDITY_THRESHOLDS['high']:
            return {
                'status': 'caution',
                'severity': 'info',
                'message': f'💧 High humidity ({humidity}%). Consider adding spreader-sticker.',
                'recommendation': 'Use appropriate adjuvants for better coverage and penetration'
            }
        elif wind > self.WIND_THRESHOLDS['medium']:
            return {
                'status': 'caution',
                'severity': 'info',
                'message': f'💨 Moderate wind ({wind} km/h). Use caution when spraying.',
                'recommendation': 'Use drift-reducing nozzles. Spray in calm conditions.'
            }
        else:
            return {
                'status': 'good',
                'severity': 'success',
                'message': '✅ Perfect conditions for spraying today.',
                'recommendation': 'Proceed with spraying as scheduled'
            }
    
    def _get_weather_alerts(self, weather_data: Dict) -> List[Dict]:
        """
        Generate weather alerts based on conditions
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            List of alerts
        """
        alerts = []
        
        humidity = weather_data.get('humidity', 0)
        temp = weather_data.get('temperature', 25)
        wind = weather_data.get('wind_speed', 0)
        rain = weather_data.get('rainfall', 0)
        
        # Humidity alerts
        if humidity >= self.HUMIDITY_THRESHOLDS['critical']:
            alerts.append({
                'type': 'humidity',
                'title': '⚠️ Critical High Humidity Alert',
                'message': f'Humidity levels at {humidity}% create perfect conditions for fungal diseases.',
                'recommendation': 'Apply preventive fungicide IMMEDIATELY. Improve air circulation.',
                'severity': 'critical'
            })
        elif humidity >= self.HUMIDITY_THRESHOLDS['high']:
            alerts.append({
                'type': 'humidity',
                'title': '⚠️ High Humidity Alert',
                'message': f'Humidity at {humidity}%. High risk for fungal diseases.',
                'recommendation': 'Apply preventive fungicide. Avoid overhead irrigation.',
                'severity': 'high'
            })
        
        # Temperature alerts
        if temp >= self.TEMP_THRESHOLDS['critical_max']:
            alerts.append({
                'type': 'temperature',
                'title': '🌡️ Extreme Heat Warning',
                'message': f'Temperature reached {temp}°C. Extreme heat stress on crops.',
                'recommendation': 'Provide shade, increase irrigation, avoid midday work.',
                'severity': 'critical'
            })
        elif temp <= self.TEMP_THRESHOLDS['critical_min']:
            alerts.append({
                'type': 'temperature',
                'title': '❄️ Frost Warning',
                'message': f'Temperature dropped to {temp}°C. Frost risk for sensitive crops.',
                'recommendation': 'Cover plants, use row covers, irrigate before frost.',
                'severity': 'critical'
            })
        elif temp >= self.TEMP_THRESHOLDS['warning_max']:
            alerts.append({
                'type': 'temperature',
                'title': '🌡️ High Temperature Alert',
                'message': f'Temperature at {temp}°C. Heat stress may affect crop growth.',
                'recommendation': 'Water early morning or evening. Provide temporary shade.',
                'severity': 'high'
            })
        elif temp <= self.TEMP_THRESHOLDS['warning_min']:
            alerts.append({
                'type': 'temperature',
                'title': '🥶 Cold Stress Alert',
                'message': f'Temperature at {temp}°C. Cold stress may slow growth.',
                'recommendation': 'Use row covers, delay planting, avoid excess moisture.',
                'severity': 'warning'
            })
        
        # Rain alerts
        if rain >= self.RAIN_THRESHOLDS['critical']:
            alerts.append({
                'type': 'rain',
                'title': '🌧️ Heavy Rain Warning',
                'message': f'{rain}mm rainfall expected. High risk of disease spread.',
                'recommendation': 'Apply fungicide BEFORE rain. Ensure drainage. Check for standing water.',
                'severity': 'critical'
            })
        elif rain >= self.RAIN_THRESHOLDS['high']:
            alerts.append({
                'type': 'rain',
                'title': '☔ Moderate Rain Alert',
                'message': f'{rain}mm rainfall expected. Disease risk increases.',
                'recommendation': 'Apply preventive treatment before rain. Monitor after rain.',
                'severity': 'high'
            })
        elif rain > 0:
            alerts.append({
                'type': 'rain',
                'title': '🌦️ Light Rain Expected',
                'message': 'Rain expected in next 24 hours.',
                'recommendation': 'Consider applying preventive fungicide before rain.',
                'severity': 'info'
            })
        
        # Wind alerts
        if wind >= self.WIND_THRESHOLDS['critical']:
            alerts.append({
                'type': 'wind',
                'title': '💨 Severe Wind Warning',
                'message': f'Wind speed at {wind} km/h. Risk of physical damage and spore spread.',
                'recommendation': 'Do NOT spray today. Provide wind breaks. Support tall plants.',
                'severity': 'critical'
            })
        elif wind >= self.WIND_THRESHOLDS['high']:
            alerts.append({
                'type': 'wind',
                'title': '🌬️ High Wind Alert',
                'message': f'Wind speed at {wind} km/h. May spread fungal spores.',
                'recommendation': 'Avoid spraying. Monitor for spore spread.',
                'severity': 'high'
            })
        
        return alerts
    
    def _calculate_heat_index(self, temperature: float, humidity: int) -> float:
        """
        Calculate heat index (apparent temperature)
        
        Args:
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            
        Returns:
            Heat index in Celsius
        """
        # Convert to Fahrenheit for calculation
        temp_f = temperature * 9/5 + 32
        
        # Heat index formula (simplified)
        if temp_f < 80:
            return temperature
        
        hi = (
            -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity -
            0.22475541 * temp_f * humidity - 0.00683783 * temp_f * temp_f -
            0.05481717 * humidity * humidity + 0.00122874 * temp_f * temp_f * humidity +
            0.00085282 * temp_f * humidity * humidity - 0.00000199 * temp_f * temp_f * humidity * humidity
        )
        
        # Convert back to Celsius
        hi_celsius = (hi - 32) * 5/9
        return round(max(temperature, hi_celsius), 1)
    
    def _calculate_dew_point(self, temperature: float, humidity: int) -> float:
        """
        Calculate dew point temperature
        
        Args:
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            
        Returns:
            Dew point in Celsius
        """
        # Magnus formula
        a = 17.27
        b = 237.7
        
        alpha = ((a * temperature) / (b + temperature)) + (humidity / 100)
        dew_point = (b * alpha) / (a - alpha)
        
        return round(dew_point, 1)
    
    def _get_mock_weather(self, city: str) -> Dict:
        """
        Generate mock weather data when API is unavailable
        
        Args:
            city: City name
            
        Returns:
            Mock weather data
        """
        # City-based temperature ranges
        city_temps = {
            'Mumbai': (25, 32, 65, 85),
            'Delhi': (15, 35, 40, 75),
            'Bangalore': (18, 28, 60, 85),
            'Chennai': (24, 33, 65, 85),
            'Kolkata': (22, 32, 65, 85),
            'Pune': (18, 30, 55, 80),
            'Hyderabad': (20, 32, 55, 80)
        }
        
        defaults = city_temps.get(city, (20, 30, 55, 80))
        temp_min, temp_max, hum_min, hum_max = defaults
        
        temperature = round(random.uniform(temp_min, temp_max), 1)
        humidity = random.randint(hum_min, hum_max)
        wind_speed = round(random.uniform(5, 20), 1)
        rainfall = round(random.uniform(0, 8), 1)
        
        conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain']
        condition = random.choice(conditions)
        icons = {'Sunny': '01d', 'Partly Cloudy': '02d', 'Cloudy': '03d', 'Light Rain': '10d'}
        
        weather_data = {
            'success': True,
            'city': city,
            'country': 'IN',
            'temperature': temperature,
            'feels_like': round(temperature + random.uniform(-2, 2), 1),
            'temp_min': round(temperature - random.uniform(2, 5), 1),
            'temp_max': round(temperature + random.uniform(2, 5), 1),
            'humidity': humidity,
            'pressure': 1013,
            'wind_speed': wind_speed,
            'wind_direction': random.randint(0, 360),
            'wind_gust': round(wind_speed + random.uniform(0, 5), 1),
            'rainfall': rainfall,
            'clouds': random.randint(10, 90),
            'condition': condition,
            'condition_main': condition.split()[0],
            'weather_icon': icons.get(condition, '01d'),
            'weather_id': 800,
            'sunrise': '06:30 AM',
            'sunset': '06:30 PM',
            'is_mock': True,
            'timestamp': datetime.now().isoformat()
        }
        
        weather_data['disease_risk'] = self._calculate_disease_risk(weather_data)
        weather_data['spray_advisory'] = self._get_spray_advisory(weather_data)
        weather_data['alerts'] = self._get_weather_alerts(weather_data)
        weather_data['disease_risks'] = self._calculate_disease_specific_risks(weather_data)
        weather_data['heat_index'] = self._calculate_heat_index(temperature, humidity)
        weather_data['dew_point'] = self._calculate_dew_point(temperature, humidity)
        
        return weather_data
    
    def _get_mock_forecast(self, city: str, days: int) -> List[Dict]:
        """
        Generate mock forecast data
        
        Args:
            city: City name
            days: Number of days
            
        Returns:
            List of forecast data
        """
        forecast = []
        conditions = ['☀️ Sunny', '⛅ Partly Cloudy', '☁️ Cloudy', '🌧️ Light Rain']
        icons = {'☀️ Sunny': '01d', '⛅ Partly Cloudy': '02d', '☁️ Cloudy': '03d', '🌧️ Light Rain': '10d'}
        
        # Base temperature by city
        city_base_temp = {
            'Mumbai': 28, 'Delhi': 25, 'Bangalore': 24, 'Chennai': 29,
            'Kolkata': 28, 'Pune': 26, 'Hyderabad': 27
        }
        base_temp = city_base_temp.get(city, 26)
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            temp_variation = random.uniform(-5, 5)
            condition = random.choice(conditions)
            
            risk_levels = ['Low', 'Medium', 'High']
            risk = random.choice(risk_levels)
            
            forecast.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%a'),
                'full_day': date.strftime('%A'),
                'temperature': round(base_temp + temp_variation, 1),
                'temp_min': round(base_temp + temp_variation - random.uniform(2, 5), 1),
                'temp_max': round(base_temp + temp_variation + random.uniform(2, 5), 1),
                'humidity': random.randint(55, 85),
                'condition': condition,
                'weather_icon': icons.get(condition, '01d'),
                'rainfall': round(random.uniform(0, 10), 1),
                'wind_speed': round(random.uniform(5, 20), 1),
                'disease_risk': risk,
                'risk_color': '#EF4444' if risk == 'High' else '#F59E0B' if risk == 'Medium' else '#10B981',
                'risk_score': 80 if risk == 'High' else 50 if risk == 'Medium' else 20
            })
        
        return forecast
    
    def get_air_quality(self, lat: float, lon: float) -> Dict:
        """
        Get air quality data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Air quality data
        """
        if not self.is_configured():
            return self._get_mock_air_quality()
        
        try:
            url = f"{self.base_url}/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                aqi = data.get('list', [{}])[0].get('main', {}).get('aqi', 2)
                
                aqi_levels = {
                    1: {'level': 'Good', 'color': '#10B981', 'message': 'Air quality is good. No restrictions.'},
                    2: {'level': 'Fair', 'color': '#34D399', 'message': 'Air quality is acceptable.'},
                    3: {'level': 'Moderate', 'color': '#FBBF24', 'message': 'Sensitive groups should reduce outdoor activity.'},
                    4: {'level': 'Poor', 'color': '#F87171', 'message': 'Reduce outdoor activity.'},
                    5: {'level': 'Very Poor', 'color': '#EF4444', 'message': 'Avoid outdoor activity.'}
                }
                
                components = data.get('list', [{}])[0].get('components', {})
                
                return {
                    'success': True,
                    'aqi': aqi,
                    'level': aqi_levels[aqi]['level'],
                    'color': aqi_levels[aqi]['color'],
                    'message': aqi_levels[aqi]['message'],
                    'components': {
                        'pm2_5': components.get('pm2_5', 0),
                        'pm10': components.get('pm10', 0),
                        'o3': components.get('o3', 0),
                        'no2': components.get('no2', 0),
                        'so2': components.get('so2', 0),
                        'co': components.get('co', 0)
                    }
                }
            else:
                return self._get_mock_air_quality()
                
        except Exception as e:
            logger.error(f"Air quality API error: {str(e)}")
            return self._get_mock_air_quality()
    
    def _get_mock_air_quality(self) -> Dict:
        """
        Generate mock air quality data
        
        Returns:
            Mock air quality data
        """
        aqi = random.randint(1, 5)
        
        aqi_levels = {
            1: {'level': 'Good', 'color': '#10B981', 'message': 'Air quality is good.'},
            2: {'level': 'Fair', 'color': '#34D399', 'message': 'Air quality is acceptable.'},
            3: {'level': 'Moderate', 'color': '#FBBF24', 'message': 'Moderate air quality.'},
            4: {'level': 'Poor', 'color': '#F87171', 'message': 'Poor air quality.'},
            5: {'level': 'Very Poor', 'color': '#EF4444', 'message': 'Very poor air quality.'}
        }
        
        return {
            'success': True,
            'aqi': aqi,
            'level': aqi_levels[aqi]['level'],
            'color': aqi_levels[aqi]['color'],
            'message': aqi_levels[aqi]['message'],
            'components': {
                'pm2_5': round(random.uniform(10, 150), 1),
                'pm10': round(random.uniform(20, 200), 1),
                'o3': round(random.uniform(20, 100), 1),
                'no2': round(random.uniform(10, 80), 1),
                'so2': round(random.uniform(5, 50), 1),
                'co': round(random.uniform(100, 1000), 1)
            },
            'is_mock': True
        }
    
    def get_supported_cities(self) -> List[str]:
        """Get list of supported cities"""
        return self.supported_cities
    
    def clear_cache(self):
        """Clear weather data cache"""
        self._cache.clear()
        logger.info("Weather cache cleared")


# Singleton instance
weather_service = WeatherService()