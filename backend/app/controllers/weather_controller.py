"""
Weather Controller
Handles weather data fetching, API integration, and disease risk calculation
"""

import requests
import json
from datetime import datetime, timedelta
from flask import current_app
from app.config.weather_config import WeatherConfig


class WeatherController:
    """
    Controller for weather operations
    Fetches real-time weather data and calculates disease risk
    """
    
    # Cache for weather data to reduce API calls
    _weather_cache = {}
    _cache_duration = 1800  # 30 minutes cache
    
    @classmethod
    def get_weather(cls, city=None, lat=None, lon=None):
        """
        Get current weather data for a location
        
        Args:
            city: City name (e.g., 'Mumbai', 'Delhi')
            lat: Latitude (if city not provided)
            lon: Longitude (if city not provided)
            
        Returns:
            dict: Weather data with disease risk analysis
        """
        # Determine location identifier for caching
        location_key = city or f"{lat},{lon}" or WeatherConfig.DEFAULT_CITY
        
        # Check cache
        cache_key = f"weather_{location_key}"
        if cache_key in cls._weather_cache:
            cached_data, cache_time = cls._weather_cache[cache_key]
            if (datetime.now() - cache_time).seconds < cls._cache_duration:
                current_app.logger.info(f"Returning cached weather for {location_key}")
                return cached_data
        
        try:
            # Try to fetch from API
            if WeatherConfig.is_api_configured():
                weather_data = cls._fetch_from_api(city, lat, lon)
            else:
                current_app.logger.warning("Weather API not configured, using mock data")
                weather_data = cls._get_mock_weather(city or WeatherConfig.DEFAULT_CITY)
            
            # Cache the result
            cls._weather_cache[cache_key] = (weather_data, datetime.now())
            
            return weather_data
            
        except Exception as e:
            current_app.logger.error(f"Weather API error: {str(e)}")
            return cls._get_mock_weather(city or WeatherConfig.DEFAULT_CITY)
    
    @classmethod
    def _fetch_from_api(cls, city=None, lat=None, lon=None):
        """
        Fetch weather data from OpenWeatherMap API
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            
        Returns:
            dict: Parsed weather data
        """
        # Build request parameters
        params = WeatherConfig.get_request_params(city=city, lat=lat, lon=lon)
        
        # Make API request for current weather
        response = requests.get(
            WeatherConfig.get_api_url('weather'),
            params=params,
            timeout=WeatherConfig.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Parse current weather
        weather_data = cls._parse_current_weather(data, city)
        
        # Fetch forecast if enabled
        if WeatherConfig.FETCH_FORECAST:
            forecast = cls._fetch_forecast(city, lat, lon)
            weather_data['forecast'] = forecast
        
        return weather_data
    
    @classmethod
    def _parse_current_weather(cls, data, city=None):
        """
        Parse OpenWeatherMap API response
        
        Args:
            data: API response JSON
            city: City name override
            
        Returns:
            dict: Formatted weather data
        """
        # Extract basic weather data
        temp = data.get('main', {}).get('temp', 25)
        feels_like = data.get('main', {}).get('feels_like', temp)
        humidity = data.get('main', {}).get('humidity', 65)
        pressure = data.get('main', {}).get('pressure', 1013)
        
        # Wind data (convert from m/s to km/h)
        wind_speed = data.get('wind', {}).get('speed', 2.5) * 3.6
        wind_deg = data.get('wind', {}).get('deg', 0)
        
        # Rain data
        rainfall = 0
        if 'rain' in data:
            rainfall = data['rain'].get('1h', 0) or data['rain'].get('3h', 0) / 3 or 0
        
        # Cloud cover
        clouds = data.get('clouds', {}).get('all', 0)
        
        # Weather condition
        weather_condition = data.get('weather', [{}])[0].get('description', 'Unknown')
        weather_icon = data.get('weather', [{}])[0].get('icon', '01d')
        weather_main = data.get('weather', [{}])[0].get('main', 'Clear')
        
        # Sunrise/Sunset
        sunrise = datetime.fromtimestamp(data.get('sys', {}).get('sunrise', 0))
        sunset = datetime.fromtimestamp(data.get('sys', {}).get('sunset', 0))
        
        # Calculate disease risk
        risk = WeatherConfig.calculate_disease_risk(temp, humidity, wind_speed, rainfall)
        
        # Get spray advisory
        spray_advisory = WeatherConfig.get_spray_advisory(temp, humidity, wind_speed, rainfall)
        
        # Get alerts
        alerts = WeatherConfig.get_alert_messages({
            'temperature': temp,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'rainfall': rainfall
        })
        
        # Get disease-specific risks
        disease_risks = cls._calculate_disease_risks(temp, humidity)
        
        return {
            'success': True,
            'city': city or data.get('name', WeatherConfig.DEFAULT_CITY),
            'country': data.get('sys', {}).get('country', 'IN'),
            'temperature': round(temp, 1),
            'feels_like': round(feels_like, 1),
            'humidity': humidity,
            'pressure': pressure,
            'wind_speed': round(wind_speed, 1),
            'wind_direction': wind_deg,
            'rainfall': round(rainfall, 1),
            'clouds': clouds,
            'condition': weather_condition,
            'condition_main': weather_main,
            'weather_icon': weather_icon,
            'sunrise': sunrise.strftime('%I:%M %p'),
            'sunset': sunset.strftime('%I:%M %p'),
            'disease_risk': risk['risk'],
            'risk_score': risk['score'],
            'risk_color': risk['color'],
            'risk_message': risk['message'],
            'alerts': alerts,
            'spray_advisory': spray_advisory,
            'disease_risks': disease_risks,
            'timestamp': datetime.now().isoformat()
        }
    
    @classmethod
    def _fetch_forecast(cls, city=None, lat=None, lon=None):
        """
        Fetch 7-day weather forecast
        
        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            
        Returns:
            list: Forecast data for 7 days
        """
        try:
            params = WeatherConfig.get_request_params(city=city, lat=lat, lon=lon)
            params['cnt'] = WeatherConfig.FORECAST_DAYS * 8  # 8 readings per day
            
            response = requests.get(
                WeatherConfig.get_api_url('forecast'),
                params=params,
                timeout=WeatherConfig.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                raise Exception("Forecast API failed")
            
            data = response.json()
            return cls._parse_forecast_data(data)
            
        except Exception as e:
            current_app.logger.error(f"Forecast API error: {str(e)}")
            return cls._get_mock_forecast(city or WeatherConfig.DEFAULT_CITY)
    
    @classmethod
    def _parse_forecast_data(cls, data):
        """
        Parse forecast API response
        
        Args:
            data: API response JSON
            
        Returns:
            list: Daily forecast data
        """
        forecast_by_day = {}
        
        for item in data.get('list', []):
            dt = datetime.fromtimestamp(item.get('dt', 0))
            day_key = dt.strftime('%Y-%m-%d')
            
            if day_key not in forecast_by_day:
                forecast_by_day[day_key] = {
                    'date': day_key,
                    'day_name': dt.strftime('%A'),
                    'temps': [],
                    'humidities': [],
                    'conditions': [],
                    'rain': 0
                }
            
            forecast_by_day[day_key]['temps'].append(item.get('main', {}).get('temp', 25))
            forecast_by_day[day_key]['humidities'].append(item.get('main', {}).get('humidity', 65))
            forecast_by_day[day_key]['conditions'].append(
                item.get('weather', [{}])[0].get('description', 'Unknown')
            )
            
            if 'rain' in item:
                forecast_by_day[day_key]['rain'] += item['rain'].get('3h', 0)
        
        # Process daily averages
        forecast = []
        for day_key, day_data in list(forecast_by_day.items())[:WeatherConfig.FORECAST_DAYS]:
            avg_temp = sum(day_data['temps']) / len(day_data['temps'])
            avg_humidity = sum(day_data['humidities']) / len(day_data['humidities'])
            
            # Get most common condition
            condition = max(set(day_data['conditions']), key=day_data['conditions'].count)
            
            # Calculate disease risk for the day
            risk = WeatherConfig.calculate_disease_risk(avg_temp, avg_humidity, 10, day_data['rain'])
            
            forecast.append({
                'date': day_data['date'],
                'day': day_data['day_name'][:3],
                'full_day': day_data['day_name'],
                'temperature': round(avg_temp, 1),
                'humidity': round(avg_humidity, 1),
                'condition': condition,
                'rainfall': round(day_data['rain'], 1),
                'disease_risk': risk['risk'],
                'risk_color': risk['color']
            })
        
        return forecast
    
    @classmethod
    def _calculate_disease_risks(cls, temperature, humidity):
        """
        Calculate risk levels for specific diseases
        
        Args:
            temperature: Current temperature in Celsius
            humidity: Current humidity percentage
            
        Returns:
            list: Disease-specific risk assessments
        """
        disease_risks = []
        
        for disease_key, factors in WeatherConfig.DISEASE_RISK_FACTORS.items():
            # Calculate risk score for this disease
            temp_ok = factors['temp_min'] <= temperature <= factors['temp_max']
            humidity_ok = humidity >= factors['humidity_min']
            
            if factors.get('humidity_max'):
                humidity_ok = humidity_ok and humidity <= factors['humidity_max']
            
            if temp_ok and humidity_ok:
                risk_level = 'High'
                risk_score = 80
                message = f"High risk of {factors['name']}. Conditions are favorable."
            elif temp_ok or humidity_ok:
                risk_level = 'Medium'
                risk_score = 50
                message = f"Medium risk of {factors['name']}. Monitor closely."
            else:
                risk_level = 'Low'
                risk_score = 20
                message = f"Low risk of {factors['name']}. Continue normal practices."
            
            disease_risks.append({
                'disease': factors['name'],
                'risk': risk_level,
                'score': risk_score,
                'message': message
            })
        
        # Sort by risk level (highest first)
        risk_order = {'High': 3, 'Medium': 2, 'Low': 1}
        disease_risks.sort(key=lambda x: risk_order.get(x['risk'], 0), reverse=True)
        
        return disease_risks[:5]  # Return top 5 risks
    
    @classmethod
    def get_weather_by_pincode(cls, pincode):
        """
        Get weather data by Indian pincode
        
        Args:
            pincode: Indian postal code
            
        Returns:
            dict: Weather data
        """
        # Map pincode to city (simplified mapping)
        pincode_city_map = {
            '400001': 'Mumbai',
            '110001': 'Delhi',
            '560001': 'Bangalore',
            '600001': 'Chennai',
            '700001': 'Kolkata',
            '411001': 'Pune',
            '380001': 'Ahmedabad',
            '500001': 'Hyderabad',
            '302001': 'Jaipur',
            '226001': 'Lucknow'
        }
        
        city = pincode_city_map.get(str(pincode), WeatherConfig.DEFAULT_CITY)
        return cls.get_weather(city=city)
    
    @classmethod
    def _get_mock_weather(cls, city):
        """
        Generate mock weather data when API is unavailable
        
        Args:
            city: City name
            
        Returns:
            dict: Mock weather data
        """
        import random
        
        # Generate realistic mock data based on city
        city_temps = {
            'Mumbai': (25, 32),
            'Delhi': (15, 35),
            'Bangalore': (18, 28),
            'Chennai': (24, 33),
            'Kolkata': (22, 32),
            'Pune': (18, 30),
            'Hyderabad': (20, 32)
        }
        
        temp_range = city_temps.get(city, (20, 30))
        temperature = round(random.uniform(temp_range[0], temp_range[1]), 1)
        humidity = random.randint(55, 90)
        wind_speed = round(random.uniform(5, 20), 1)
        rainfall = round(random.uniform(0, 8), 1)
        
        conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain']
        condition = random.choice(conditions)
        
        # Calculate disease risk
        risk = WeatherConfig.calculate_disease_risk(temperature, humidity, wind_speed, rainfall)
        
        # Get spray advisory
        spray_advisory = WeatherConfig.get_spray_advisory(temperature, humidity, wind_speed, rainfall)
        
        # Get alerts
        alerts = WeatherConfig.get_alert_messages({
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'rainfall': rainfall
        })
        
        # Get disease-specific risks
        disease_risks = cls._calculate_disease_risks(temperature, humidity)
        
        return {
            'success': True,
            'city': city,
            'country': 'IN',
            'temperature': temperature,
            'feels_like': round(temperature + random.uniform(-2, 2), 1),
            'humidity': humidity,
            'pressure': 1013,
            'wind_speed': wind_speed,
            'wind_direction': random.randint(0, 360),
            'rainfall': rainfall,
            'clouds': random.randint(10, 90),
            'condition': condition,
            'condition_main': condition.split()[0],
            'weather_icon': '04d' if 'Cloud' in condition else '01d',
            'sunrise': '06:30 AM',
            'sunset': '06:30 PM',
            'disease_risk': risk['risk'],
            'risk_score': risk['score'],
            'risk_color': risk['color'],
            'risk_message': risk['message'],
            'alerts': alerts,
            'spray_advisory': spray_advisory,
            'disease_risks': disease_risks,
            'forecast': cls._get_mock_forecast(city),
            'timestamp': datetime.now().isoformat(),
            'is_mock': True
        }
    
    @classmethod
    def _get_mock_forecast(cls, city):
        """
        Generate mock forecast data
        
        Args:
            city: City name
            
        Returns:
            list: Mock forecast data
        """
        import random
        
        forecast = []
        conditions = ['☀️ Sunny', '⛅ Partly Cloudy', '☁️ Cloudy', '🌧️ Light Rain']
        risk_levels = ['Low', 'Medium', 'High']
        
        for i in range(7):
            date = datetime.now() + timedelta(days=i)
            forecast.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%a'),
                'full_day': date.strftime('%A'),
                'temperature': round(28 + random.uniform(-5, 5), 1),
                'humidity': random.randint(55, 85),
                'condition': random.choice(conditions),
                'rainfall': round(random.uniform(0, 10), 1),
                'disease_risk': random.choice(risk_levels),
                'risk_color': '#EF4444' if random.choice(risk_levels) == 'High' else '#F59E0B' if random.choice(risk_levels) == 'Medium' else '#10B981'
            })
        
        return forecast
    
    @classmethod
    def get_air_quality(cls, lat, lon):
        """
        Get air quality data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            dict: Air quality data
        """
        try:
            if not WeatherConfig.is_api_configured():
                return cls._get_mock_air_quality()
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': WeatherConfig.API_KEY
            }
            
            response = requests.get(
                f"{WeatherConfig.API_BASE_URL}/air_pollution",
                params=params,
                timeout=WeatherConfig.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return cls._parse_air_quality(data)
            else:
                return cls._get_mock_air_quality()
                
        except Exception as e:
            current_app.logger.error(f"Air quality API error: {str(e)}")
            return cls._get_mock_air_quality()
    
    @classmethod
    def _parse_air_quality(cls, data):
        """Parse air quality API response"""
        aqi = data.get('list', [{}])[0].get('main', {}).get('aqi', 2)
        
        aqi_levels = {
            1: {'level': 'Good', 'color': '#10B981', 'message': 'Air quality is good. No restrictions.'},
            2: {'level': 'Fair', 'color': '#34D399', 'message': 'Air quality is acceptable.'},
            3: {'level': 'Moderate', 'color': '#FBBF24', 'message': 'Sensitive groups should reduce outdoor activity.'},
            4: {'level': 'Poor', 'color': '#F87171', 'message': 'Reduce outdoor activity.'},
            5: {'level': 'Very Poor', 'color': '#EF4444', 'message': 'Avoid outdoor activity.'}
        }
        
        return {
            'success': True,
            'aqi': aqi,
            'level': aqi_levels[aqi]['level'],
            'color': aqi_levels[aqi]['color'],
            'message': aqi_levels[aqi]['message'],
            'components': data.get('list', [{}])[0].get('components', {})
        }
    
    @classmethod
    def _get_mock_air_quality(cls):
        """Generate mock air quality data"""
        import random
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
            'is_mock': True
        }
    
    @classmethod
    def clear_cache(cls):
        """Clear weather data cache"""
        cls._weather_cache.clear()
        current_app.logger.info("Weather cache cleared")
    
    @classmethod
    def get_weather_summary(cls, city=None):
        """
        Get a simplified weather summary for dashboard
        
        Args:
            city: City name
            
        Returns:
            dict: Simplified weather summary
        """
        weather = cls.get_weather(city=city)
        
        return {
            'city': weather.get('city'),
            'temperature': weather.get('temperature'),
            'humidity': weather.get('humidity'),
            'condition': weather.get('condition'),
            'disease_risk': weather.get('disease_risk'),
            'risk_color': weather.get('risk_color'),
            'alert_count': len(weather.get('alerts', [])),
            'spray_advisory': weather.get('spray_advisory', {}).get('status', 'unknown')
        }