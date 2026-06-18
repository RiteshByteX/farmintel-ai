"""
Weather Alerts Utility
Generates weather-based disease alerts and risk notifications for farmers
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta


class WeatherAlertGenerator:
    """
    Utility class for generating weather-based disease alerts
    Provides alerts for high-risk conditions, spray advisories, and disease predictions
    """
    
    # Alert severity levels
    ALERT_SEVERITY = {
        'critical': {'level': 'Critical', 'color': '#7F1D1D', 'bg_color': '#FEE2E2', 'priority': 1},
        'high': {'level': 'High', 'color': '#EF4444', 'bg_color': '#FEE2E2', 'priority': 2},
        'warning': {'level': 'Warning', 'color': '#F59E0B', 'bg_color': '#FEF3C7', 'priority': 3},
        'info': {'level': 'Info', 'color': '#3B82F6', 'bg_color': '#DBEAFE', 'priority': 4},
        'success': {'level': 'Success', 'color': '#10B981', 'bg_color': '#D1FAE5', 'priority': 5}
    }
    
    # Disease-specific weather thresholds
    DISEASE_WEATHER_THRESHOLDS = {
        'Late Blight': {
            'temp_min': 15,
            'temp_max': 22,
            'temp_optimal': 18,
            'humidity_min': 85,
            'humidity_optimal': 90,
            'rain_required': True,
            'wind_sensitivity': 'medium',
            'incubation_days': 5,
            'severity_multiplier': 1.5
        },
        'Early Blight': {
            'temp_min': 20,
            'temp_max': 30,
            'temp_optimal': 25,
            'humidity_min': 70,
            'humidity_optimal': 80,
            'rain_required': False,
            'wind_sensitivity': 'low',
            'incubation_days': 3,
            'severity_multiplier': 1.2
        },
        'Powdery Mildew': {
            'temp_min': 18,
            'temp_max': 28,
            'temp_optimal': 22,
            'humidity_min': 40,
            'humidity_max': 60,
            'humidity_optimal': 50,
            'rain_required': False,
            'wind_sensitivity': 'high',
            'incubation_days': 7,
            'severity_multiplier': 1.3
        },
        'Downy Mildew': {
            'temp_min': 15,
            'temp_max': 25,
            'temp_optimal': 20,
            'humidity_min': 85,
            'humidity_optimal': 90,
            'rain_required': True,
            'wind_sensitivity': 'medium',
            'incubation_days': 4,
            'severity_multiplier': 1.4
        },
        'Rust': {
            'temp_min': 15,
            'temp_max': 25,
            'temp_optimal': 20,
            'humidity_min': 80,
            'humidity_optimal': 85,
            'rain_required': False,
            'wind_sensitivity': 'high',
            'incubation_days': 10,
            'severity_multiplier': 1.2
        },
        'Leaf Spot': {
            'temp_min': 18,
            'temp_max': 28,
            'temp_optimal': 23,
            'humidity_min': 75,
            'humidity_optimal': 85,
            'rain_required': True,
            'wind_sensitivity': 'low',
            'incubation_days': 6,
            'severity_multiplier': 1.1
        },
        'Bacterial Spot': {
            'temp_min': 20,
            'temp_max': 30,
            'temp_optimal': 25,
            'humidity_min': 80,
            'humidity_optimal': 85,
            'rain_required': True,
            'wind_sensitivity': 'low',
            'incubation_days': 3,
            'severity_multiplier': 1.3
        },
        'Scab': {
            'temp_min': 10,
            'temp_max': 20,
            'temp_optimal': 15,
            'humidity_min': 75,
            'humidity_optimal': 85,
            'rain_required': True,
            'wind_sensitivity': 'low',
            'incubation_days': 9,
            'severity_multiplier': 1.2
        },
        'Cercospora': {
            'temp_min': 22,
            'temp_max': 30,
            'temp_optimal': 26,
            'humidity_min': 80,
            'humidity_optimal': 85,
            'rain_required': True,
            'wind_sensitivity': 'low',
            'incubation_days': 7,
            'severity_multiplier': 1.1
        }
    }
    
    @classmethod
    def generate_alerts(cls, weather_data: Dict) -> List[Dict]:
        """
        Generate weather alerts based on current conditions
        
        Args:
            weather_data: Dictionary with current weather data
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Extract weather parameters
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        wind = weather_data.get('wind_speed', 10)
        rain = weather_data.get('rainfall', 0)
        
        # Temperature alerts
        alerts.extend(cls._get_temperature_alerts(temp))
        
        # Humidity alerts
        alerts.extend(cls._get_humidity_alerts(humidity))
        
        # Wind alerts
        alerts.extend(cls._get_wind_alerts(wind))
        
        # Rain alerts
        alerts.extend(cls._get_rain_alerts(rain))
        
        # Disease risk alerts
        alerts.extend(cls._get_disease_risk_alerts(temp, humidity, rain))
        
        # Spray advisory
        spray_alert = cls._get_spray_advisory(temp, humidity, wind, rain)
        if spray_alert:
            alerts.append(spray_alert)
        
        return alerts
    
    @classmethod
    def _get_temperature_alerts(cls, temp: float) -> List[Dict]:
        """Generate temperature-based alerts"""
        alerts = []
        
        if temp >= 38:
            alerts.append({
                'type': 'temperature',
                'severity': 'critical',
                'title': '🚨 Extreme Heat Warning',
                'message': f'Temperature has reached {temp}°C. Extreme heat stress on crops.',
                'recommendation': 'Provide shade, increase irrigation, avoid midday spraying.',
                'affected_crops': ['Tomato', 'Potato', 'Bell Pepper', 'All Vegetables']
            })
        elif temp >= 35:
            alerts.append({
                'type': 'temperature',
                'severity': 'high',
                'title': '🌡️ High Temperature Alert',
                'message': f'Temperature at {temp}°C. Heat stress may affect crop growth.',
                'recommendation': 'Water early morning or evening. Provide temporary shade if possible.',
                'affected_crops': ['Tomato', 'Bell Pepper', 'Strawberry']
            })
        elif temp <= 5:
            alerts.append({
                'type': 'temperature',
                'severity': 'critical',
                'title': '❄️ Frost Warning',
                'message': f'Temperature dropped to {temp}°C. Frost risk for sensitive crops.',
                'recommendation': 'Cover plants, move potted plants indoors, irrigate before frost.',
                'affected_crops': ['Potato', 'Tomato', 'Bell Pepper', 'Strawberry']
            })
        elif temp <= 10:
            alerts.append({
                'type': 'temperature',
                'severity': 'warning',
                'title': '🥶 Cold Stress Alert',
                'message': f'Temperature at {temp}°C. Cold stress may slow growth.',
                'recommendation': 'Use row covers, delay planting, avoid excess moisture.',
                'affected_crops': ['Tomato', 'Bell Pepper', 'Eggplant']
            })
        
        return alerts
    
    @classmethod
    def _get_humidity_alerts(cls, humidity: int) -> List[Dict]:
        """Generate humidity-based alerts"""
        alerts = []
        
        if humidity >= 90:
            alerts.append({
                'type': 'humidity',
                'severity': 'critical',
                'title': '💧 Critical High Humidity',
                'message': f'Humidity at {humidity}%. Perfect conditions for fungal disease outbreak!',
                'recommendation': 'Apply preventive fungicide IMMEDIATELY. Improve air circulation.',
                'high_risk_diseases': ['Late Blight', 'Downy Mildew', 'Leaf Spot']
            })
        elif humidity >= 80:
            alerts.append({
                'type': 'humidity',
                'severity': 'high',
                'title': '⚠️ High Humidity Alert',
                'message': f'Humidity at {humidity}%. High risk for fungal diseases.',
                'recommendation': 'Apply preventive fungicide. Avoid overhead irrigation.',
                'high_risk_diseases': ['Late Blight', 'Early Blight', 'Powdery Mildew']
            })
        elif humidity >= 70:
            alerts.append({
                'type': 'humidity',
                'severity': 'warning',
                'title': '📋 Moderate Humidity Warning',
                'message': f'Humidity at {humidity}%. Monitor for disease symptoms.',
                'recommendation': 'Increase monitoring frequency. Ensure good air circulation.',
                'high_risk_diseases': ['Early Blight', 'Leaf Spot']
            })
        elif humidity <= 30:
            alerts.append({
                'type': 'humidity',
                'severity': 'warning',
                'title': '🌵 Low Humidity Alert',
                'message': f'Humidity at {humidity}%. Dry conditions may stress plants.',
                'recommendation': 'Increase irrigation frequency. Mulch to retain moisture.',
                'affected_crops': ['All crops']
            })
        
        return alerts
    
    @classmethod
    def _get_wind_alerts(cls, wind: float) -> List[Dict]:
        """Generate wind-based alerts"""
        alerts = []
        
        if wind >= 30:
            alerts.append({
                'type': 'wind',
                'severity': 'critical',
                'title': '💨 Severe Wind Warning',
                'message': f'Wind speed at {wind} km/h. Risk of physical damage and spore spread.',
                'recommendation': 'Do NOT spray today. Provide wind breaks. Support tall plants.',
                'affected_crops': ['Corn', 'Tomato', 'All tall crops']
            })
        elif wind >= 20:
            alerts.append({
                'type': 'wind',
                'severity': 'high',
                'title': '🌬️ High Wind Alert',
                'message': f'Wind speed at {wind} km/h. May spread fungal spores.',
                'recommendation': 'Avoid spraying. Monitor for spore spread.',
                'affected_crops': ['All crops']
            })
        elif wind >= 15:
            alerts.append({
                'type': 'wind',
                'severity': 'warning',
                'title': '💨 Moderate Wind Advisory',
                'message': f'Wind speed at {wind} km/h. Use caution when spraying.',
                'recommendation': 'Use drift-reducing nozzles. Spray early morning or evening.',
                'affected_crops': ['All crops']
            })
        
        return alerts
    
    @classmethod
    def _get_rain_alerts(cls, rain: float) -> List[Dict]:
        """Generate rain-based alerts"""
        alerts = []
        
        if rain >= 20:
            alerts.append({
                'type': 'rain',
                'severity': 'critical',
                'title': '🌧️ Heavy Rain Warning',
                'message': f'{rain}mm rainfall expected. High risk of disease spread.',
                'recommendation': 'Apply fungicide BEFORE rain. Ensure drainage. Check for standing water.',
                'high_risk_diseases': ['Late Blight', 'Downy Mildew', 'Bacterial Spot']
            })
        elif rain >= 10:
            alerts.append({
                'type': 'rain',
                'severity': 'high',
                'title': '☔ Moderate Rain Alert',
                'message': f'{rain}mm rainfall expected. Disease risk increases.',
                'recommendation': 'Apply preventive treatment before rain. Monitor after rain.',
                'high_risk_diseases': ['Late Blight', 'Early Blight', 'Leaf Spot']
            })
        elif rain > 0:
            alerts.append({
                'type': 'rain',
                'severity': 'warning',
                'title': '🌦️ Light Rain Expected',
                'message': 'Rain expected in next 24 hours.',
                'recommendation': 'Consider applying preventive fungicide before rain.',
                'high_risk_diseases': ['Fungal diseases']
            })
        
        return alerts
    
    @classmethod
    def _get_disease_risk_alerts(cls, temp: float, humidity: int, rain: float) -> List[Dict]:
        """Generate disease-specific risk alerts"""
        alerts = []
        
        for disease, thresholds in cls.DISEASE_WEATHER_THRESHOLDS.items():
            risk_level = cls._calculate_disease_risk(temp, humidity, rain, thresholds)
            
            if risk_level in ['critical', 'high']:
                alerts.append({
                    'type': 'disease_risk',
                    'severity': risk_level,
                    'title': f'🚨 {disease} Risk Alert',
                    'message': cls._get_disease_risk_message(disease, risk_level, temp, humidity),
                    'recommendation': cls._get_disease_recommendation(disease, risk_level),
                    'disease': disease,
                    'risk_level': risk_level,
                    'incubation_days': thresholds.get('incubation_days', 5)
                })
        
        return alerts
    
    @classmethod
    def _calculate_disease_risk(cls, temp: float, humidity: int, rain: float, thresholds: Dict) -> str:
        """Calculate risk level for a specific disease"""
        temp_min = thresholds.get('temp_min', 0)
        temp_max = thresholds.get('temp_max', 100)
        temp_optimal = thresholds.get('temp_optimal', 22)
        humidity_min = thresholds.get('humidity_min', 0)
        humidity_optimal = thresholds.get('humidity_optimal', 80)
        humidity_max = thresholds.get('humidity_max', 100)
        rain_required = thresholds.get('rain_required', False)
        
        # Check if conditions are favorable
        temp_favorable = temp_min <= temp <= temp_max
        temp_perfect = abs(temp - temp_optimal) <= 2
        
        humidity_favorable = humidity_min <= humidity <= humidity_max
        humidity_perfect = abs(humidity - humidity_optimal) <= 5
        
        rain_favorable = not rain_required or rain > 0
        
        if temp_perfect and humidity_perfect and rain_favorable:
            return 'critical'
        elif temp_favorable and humidity_favorable and rain_favorable:
            return 'high'
        elif temp_favorable or humidity_favorable:
            return 'warning'
        else:
            return 'low'
    
    @classmethod
    def _get_disease_risk_message(cls, disease: str, risk_level: str, temp: float, humidity: int) -> str:
        """Get risk message for disease"""
        if risk_level == 'critical':
            return f"⚠️ CRITICAL: Perfect conditions for {disease} outbreak! (Temp: {temp}°C, Humidity: {humidity}%)"
        elif risk_level == 'high':
            return f"⚠️ HIGH RISK: Conditions favorable for {disease} development. Take preventive action."
        else:
            return f"Conditions are not ideal for {disease} currently. Continue monitoring."
    
    @classmethod
    def _get_disease_recommendation(cls, disease: str, risk_level: str) -> str:
        """Get recommendation for disease prevention"""
        recommendations = {
            'Late Blight': 'Apply copper-based fungicide immediately. Remove infected leaves. Ensure good air circulation.',
            'Early Blight': 'Apply chlorothalonil or mancozeb. Mulch to prevent soil splash. Water at base.',
            'Powdery Mildew': 'Apply sulfur or neem oil. Improve air circulation. Avoid overhead watering.',
            'Downy Mildew': 'Apply copper fungicide. Remove infected leaves. Improve drainage.',
            'Rust': 'Apply fungicide. Remove infected leaves. Space plants properly.',
            'Leaf Spot': 'Apply fungicide. Remove infected leaves. Avoid overhead watering.',
            'Bacterial Spot': 'Apply copper bactericide. Avoid overhead irrigation. Remove infected plants.'
        }
        
        if risk_level == 'critical':
            return f"🚨 IMMEDIATE ACTION: {recommendations.get(disease, 'Apply appropriate fungicide. Monitor closely.')}"
        else:
            return f"⚠️ PREVENTIVE: {recommendations.get(disease, 'Apply preventive fungicide. Increase monitoring.')}"
    
    @classmethod
    def _get_spray_advisory(cls, temp: float, humidity: int, wind: float, rain: float) -> Optional[Dict]:
        """Get spray advisory based on conditions"""
        if wind > 20:
            return {
                'type': 'spray',
                'severity': 'high',
                'title': '🚫 Do Not Spray Today',
                'message': f'Wind speed {wind} km/h is too high for spraying.',
                'recommendation': 'Wait for wind speed to drop below 15 km/h.',
                'best_time': 'Check forecast for calmer conditions'
            }
        elif rain > 0:
            return {
                'type': 'spray',
                'severity': 'warning',
                'title': '⏰ Spray Before Rain',
                'message': 'Rain expected. Apply fungicide BEFORE rain for best protection.',
                'recommendation': 'Apply today if rain is forecast. Allow 2-4 hours to dry before rain.',
                'best_time': 'Apply immediately in the morning'
            }
        elif temp > 32:
            return {
                'type': 'spray',
                'severity': 'warning',
                'title': '🌡️ Spray During Cooler Hours',
                'message': f'Temperature {temp}°C is high for spraying.',
                'recommendation': 'Spray early morning (6-9 AM) or late evening (5-7 PM).',
                'best_time': 'Early morning or late evening'
            }
        elif humidity < 40 or humidity > 85:
            return {
                'type': 'spray',
                'severity': 'info',
                'title': '⚠️ Suboptimal Spraying Conditions',
                'message': f'Humidity {humidity}% is not ideal for spraying.',
                'recommendation': 'Consider adding a wetting agent. Spray early morning.',
                'best_time': 'Early morning when humidity is higher'
            }
        else:
            return {
                'type': 'spray',
                'severity': 'success',
                'title': '✅ Perfect Spraying Conditions',
                'message': 'Current conditions are ideal for spraying.',
                'recommendation': 'Apply treatment as scheduled.',
                'best_time': 'Now - conditions are optimal'
            }
    
    @classmethod
    def get_forecast_alerts(cls, forecast: List[Dict]) -> List[Dict]:
        """
        Generate alerts from forecast data
        
        Args:
            forecast: List of daily forecast dictionaries
            
        Returns:
            List of forecast-based alerts
        """
        alerts = []
        
        for day in forecast[:5]:  # Check next 5 days
            temp = day.get('temperature', 25)
            humidity = day.get('humidity', 65)
            rain = day.get('rainfall', 0)
            date = day.get('date', 'Unknown')
            
            # Rain in forecast
            if rain >= 10:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'high',
                    'title': f'☔ Heavy Rain Forecast - {date}',
                    'message': f'{rain}mm rainfall expected. High disease risk.',
                    'recommendation': 'Apply preventive fungicide BEFORE rain.',
                    'date': date
                })
            elif rain > 0:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'warning',
                    'title': f'🌧️ Rain Forecast - {date}',
                    'message': f'Rain expected. Prepare for disease prevention.',
                    'recommendation': 'Apply preventive treatment before rain.',
                    'date': date
                })
            
            # Temperature extremes
            if temp >= 38:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'critical',
                    'title': f'🔥 Extreme Heat - {date}',
                    'message': f'Temperature forecast: {temp}°C.',
                    'recommendation': 'Prepare shade structures. Increase irrigation.',
                    'date': date
                })
            elif temp <= 5:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'critical',
                    'title': f'❄️ Frost Risk - {date}',
                    'message': f'Temperature forecast: {temp}°C.',
                    'recommendation': 'Prepare frost protection (covers, water).',
                    'date': date
                })
        
        return alerts
    
    @classmethod
    def get_seasonal_alerts(cls, crop: str, month: int = None) -> List[Dict]:
        """
        Generate seasonal alerts for specific crops
        
        Args:
            crop: Crop name
            month: Month number (1-12, default current month)
            
        Returns:
            List of seasonal alerts
        """
        if month is None:
            month = datetime.now().month
        
        alerts = []
        
        seasonal_risks = {
            'Tomato': {
                'rainy': ['Late Blight', 'Early Blight', 'Bacterial Spot'],
                'dry': ['Powdery Mildew', 'Spider Mites'],
                'winter': ['Early Blight', 'Leaf Mold']
            },
            'Potato': {
                'rainy': ['Late Blight', 'Early Blight'],
                'dry': ['Aphids', 'Leafhoppers'],
                'winter': ['Late Blight', 'Scab']
            },
            'Grape': {
                'rainy': ['Downy Mildew', 'Black Rot'],
                'dry': ['Powdery Mildew'],
                'monsoon': ['Anthracnose']
            },
            'Apple': {
                'spring': ['Apple Scab', 'Cedar Rust'],
                'summer': ['Apple Scab', 'Codling Moth'],
                'monsoon': ['Apple Scab']
            }
        }
        
        if crop in seasonal_risks:
            crop_risks = seasonal_risks[crop]
            
            # Determine season based on month
            if 6 <= month <= 9:  # Monsoon/Rainy
                season = 'rainy'
            elif 10 <= month <= 2:  # Winter
                season = 'winter'
            else:  # Summer/Dry
                season = 'dry'
            
            if season in crop_risks:
                diseases = crop_risks[season]
                alerts.append({
                    'type': 'seasonal',
                    'severity': 'warning',
                    'title': f'🌿 Seasonal Alert - {crop}',
                    'message': f'High risk period for: {", ".join(diseases)}',
                    'recommendation': f'Increase monitoring frequency. Apply preventive treatments.',
                    'crop': crop,
                    'season': season,
                    'high_risk_diseases': diseases
                })
        
        return alerts
    
    @classmethod
    def get_alert_summary(cls, weather_data: Dict) -> Dict:
        """
        Get summary of all alerts
        
        Args:
            weather_data: Current weather data
            
        Returns:
            Summary dictionary with counts and highest priority alert
        """
        alerts = cls.generate_alerts(weather_data)
        
        if not alerts:
            return {
                'has_alerts': False,
                'total_alerts': 0,
                'critical_count': 0,
                'high_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'highest_priority': None,
                'alerts': []
            }
        
        # Count by severity
        critical_count = len([a for a in alerts if a.get('severity') == 'critical'])
        high_count = len([a for a in alerts if a.get('severity') == 'high'])
        warning_count = len([a for a in alerts if a.get('severity') == 'warning'])
        info_count = len([a for a in alerts if a.get('severity') == 'info'])
        
        # Find highest priority alert
        highest_priority = None
        for alert in alerts:
            severity = alert.get('severity', 'info')
            if severity == 'critical':
                highest_priority = alert
                break
            elif severity == 'high' and not highest_priority:
                highest_priority = alert
            elif severity == 'warning' and not highest_priority:
                highest_priority = alert
        
        return {
            'has_alerts': True,
            'total_alerts': len(alerts),
            'critical_count': critical_count,
            'high_count': high_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'highest_priority': highest_priority,
            'alerts': alerts
        }