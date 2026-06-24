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
    
    # Regional crop information for Chandigarh and surrounding areas
    REGIONAL_CROPS = {
        'Chandigarh': {
            'kharif': ['Rice', 'Maize', 'Cotton', 'Sugarcane'],
            'rabi': ['Wheat', 'Barley', 'Mustard', 'Gram'],
            'summer': ['Vegetables', 'Fruits', 'Sunflower']
        },
        'Punjab': {
            'kharif': ['Rice', 'Maize', 'Cotton'],
            'rabi': ['Wheat', 'Barley', 'Mustard'],
            'summer': ['Potato', 'Tomato', 'Cauliflower']
        },
        'Haryana': {
            'kharif': ['Rice', 'Maize', 'Sugarcane'],
            'rabi': ['Wheat', 'Barley', 'Mustard'],
            'summer': ['Vegetables', 'Fruits']
        }
    }
    
    @classmethod
    def generate_alerts(cls, weather_data: Dict, location: str = 'Chandigarh') -> List[Dict]:
        """
        Generate weather alerts based on current conditions
        
        Args:
            weather_data: Dictionary with current weather data
            location: Location name (default: Chandigarh)
            
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
        alerts.extend(cls._get_humidity_alerts(humidity, location))
        
        # Wind alerts
        alerts.extend(cls._get_wind_alerts(wind))
        
        # Rain alerts
        alerts.extend(cls._get_rain_alerts(rain, location))
        
        # Disease risk alerts
        alerts.extend(cls._get_disease_risk_alerts(temp, humidity, rain, location))
        
        # Spray advisory
        spray_alert = cls._get_spray_advisory(temp, humidity, wind, rain)
        if spray_alert:
            alerts.append(spray_alert)
        
        # Location-specific alerts
        alerts.extend(cls._get_location_specific_alerts(location, temp, humidity, rain))
        
        return alerts
    
    @classmethod
    def _get_temperature_alerts(cls, temp: float) -> List[Dict]:
        """Generate temperature-based alerts"""
        alerts = []
        
        # Chandigarh-specific temperature thresholds
        if temp >= 40:  # Higher threshold for Chandigarh's hot summers
            alerts.append({
                'type': 'temperature',
                'severity': 'critical',
                'title': '🚨 Extreme Heat Warning - Chandigarh Region',
                'message': f'Temperature has reached {temp}°C. Extreme heat stress on crops in Chandigarh region.',
                'recommendation': 'Provide shade, increase irrigation, avoid midday spraying. Protect young plants.',
                'affected_crops': ['Tomato', 'Potato', 'Bell Pepper', 'Vegetables']
            })
        elif temp >= 37:
            alerts.append({
                'type': 'temperature',
                'severity': 'high',
                'title': '🌡️ High Temperature Alert',
                'message': f'Temperature at {temp}°C. Heat stress may affect crop growth in the region.',
                'recommendation': 'Water early morning or evening. Provide temporary shade if possible.',
                'affected_crops': ['Tomato', 'Bell Pepper', 'Strawberry', 'Vegetables']
            })
        elif temp >= 35:
            alerts.append({
                'type': 'temperature',
                'severity': 'warning',
                'title': '🌡️ Warm Temperature Advisory',
                'message': f'Temperature at {temp}°C. Monitor crops for heat stress.',
                'recommendation': 'Increase irrigation frequency. Mulch to conserve soil moisture.',
                'affected_crops': ['All crops']
            })
        elif temp <= 2:  # Chandigarh winter temperatures can drop low
            alerts.append({
                'type': 'temperature',
                'severity': 'critical',
                'title': '❄️ Frost Warning - Chandigarh Region',
                'message': f'Temperature dropped to {temp}°C. Frost risk for sensitive crops.',
                'recommendation': 'Cover plants, use row covers, irrigate before frost. Protect young plants.',
                'affected_crops': ['Potato', 'Tomato', 'Bell Pepper', 'Strawberry']
            })
        elif temp <= 5:
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
    def _get_humidity_alerts(cls, humidity: int, location: str = 'Chandigarh') -> List[Dict]:
        """Generate humidity-based alerts"""
        alerts = []
        
        # Chandigarh typically has lower humidity than coastal areas
        if humidity >= 85:
            alerts.append({
                'type': 'humidity',
                'severity': 'critical',
                'title': '💧 Critical High Humidity - Unusual for Chandigarh',
                'message': f'Humidity at {humidity}%. Unusually high for this region. Perfect conditions for fungal disease outbreak!',
                'recommendation': 'Apply preventive fungicide IMMEDIATELY. Improve air circulation.',
                'high_risk_diseases': ['Late Blight', 'Downy Mildew', 'Leaf Spot']
            })
        elif humidity >= 75:
            alerts.append({
                'type': 'humidity',
                'severity': 'high',
                'title': '⚠️ High Humidity Alert',
                'message': f'Humidity at {humidity}%. Elevated risk for fungal diseases.',
                'recommendation': 'Apply preventive fungicide. Avoid overhead irrigation.',
                'high_risk_diseases': ['Late Blight', 'Early Blight', 'Powdery Mildew']
            })
        elif humidity >= 65:
            alerts.append({
                'type': 'humidity',
                'severity': 'warning',
                'title': '📋 Moderate Humidity Warning',
                'message': f'Humidity at {humidity}%. Monitor for disease symptoms.',
                'recommendation': 'Increase monitoring frequency. Ensure good air circulation.',
                'high_risk_diseases': ['Early Blight', 'Leaf Spot']
            })
        elif humidity <= 25:
            alerts.append({
                'type': 'humidity',
                'severity': 'warning',
                'title': '🌵 Low Humidity Alert - Chandigarh Region',
                'message': f'Humidity at {humidity}%. Very dry conditions may stress plants.',
                'recommendation': 'Increase irrigation frequency. Mulch to retain moisture. Use drip irrigation.',
                'affected_crops': ['All crops']
            })
        
        return alerts
    
    @classmethod
    def _get_wind_alerts(cls, wind: float) -> List[Dict]:
        """Generate wind-based alerts"""
        alerts = []
        
        if wind >= 35:  # Higher threshold for Chandigarh's occasional strong winds
            alerts.append({
                'type': 'wind',
                'severity': 'critical',
                'title': '💨 Severe Wind Warning',
                'message': f'Wind speed at {wind} km/h. Risk of physical damage and spore spread.',
                'recommendation': 'Do NOT spray today. Provide wind breaks. Support tall plants.',
                'affected_crops': ['Corn', 'Tomato', 'All tall crops']
            })
        elif wind >= 25:
            alerts.append({
                'type': 'wind',
                'severity': 'high',
                'title': '🌬️ High Wind Alert',
                'message': f'Wind speed at {wind} km/h. May spread fungal spores.',
                'recommendation': 'Avoid spraying. Monitor for spore spread.',
                'affected_crops': ['All crops']
            })
        elif wind >= 18:
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
    def _get_rain_alerts(cls, rain: float, location: str = 'Chandigarh') -> List[Dict]:
        """Generate rain-based alerts"""
        alerts = []
        
        # Chandigarh receives moderate rainfall compared to coastal areas
        if rain >= 30:
            alerts.append({
                'type': 'rain',
                'severity': 'critical',
                'title': '🌧️ Heavy Rain Warning - Chandigarh Region',
                'message': f'{rain}mm rainfall expected. High risk of waterlogging and disease spread.',
                'recommendation': 'Apply fungicide BEFORE rain. Ensure drainage. Check for standing water.',
                'high_risk_diseases': ['Late Blight', 'Downy Mildew', 'Bacterial Spot']
            })
        elif rain >= 15:
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
                'message': f'{rain}mm rain expected. Prepare for disease prevention.',
                'recommendation': 'Consider applying preventive fungicide before rain.',
                'high_risk_diseases': ['Fungal diseases']
            })
        
        return alerts
    
    @classmethod
    def _get_disease_risk_alerts(cls, temp: float, humidity: int, rain: float, location: str = 'Chandigarh') -> List[Dict]:
        """Generate disease-specific risk alerts"""
        alerts = []
        
        for disease, thresholds in cls.DISEASE_WEATHER_THRESHOLDS.items():
            risk_level = cls._calculate_disease_risk(temp, humidity, rain, thresholds)
            
            if risk_level in ['critical', 'high']:
                alerts.append({
                    'type': 'disease_risk',
                    'severity': risk_level,
                    'title': f'🚨 {disease} Risk Alert - {location} Region',
                    'message': cls._get_disease_risk_message(disease, risk_level, temp, humidity, location),
                    'recommendation': cls._get_disease_recommendation(disease, risk_level, location),
                    'disease': disease,
                    'risk_level': risk_level,
                    'incubation_days': thresholds.get('incubation_days', 5),
                    'location': location
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
    def _get_disease_risk_message(cls, disease: str, risk_level: str, temp: float, humidity: int, location: str = 'Chandigarh') -> str:
        """Get risk message for disease"""
        if risk_level == 'critical':
            return f"⚠️ CRITICAL: Perfect conditions for {disease} outbreak in {location}! (Temp: {temp}°C, Humidity: {humidity}%)"
        elif risk_level == 'high':
            return f"⚠️ HIGH RISK: Conditions favorable for {disease} development in {location}. Take preventive action."
        else:
            return f"Conditions are not ideal for {disease} currently. Continue monitoring."
    
    @classmethod
    def _get_disease_recommendation(cls, disease: str, risk_level: str, location: str = 'Chandigarh') -> str:
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
            return f"🚨 IMMEDIATE ACTION: {recommendations.get(disease, 'Apply appropriate fungicide. Monitor closely.')} Consider consulting local agriculture office in {location}."
        else:
            return f"⚠️ PREVENTIVE: {recommendations.get(disease, 'Apply preventive fungicide. Increase monitoring.')}"
    
    @classmethod
    def _get_spray_advisory(cls, temp: float, humidity: int, wind: float, rain: float) -> Optional[Dict]:
        """Get spray advisory based on conditions"""
        if wind > 25:
            return {
                'type': 'spray',
                'severity': 'high',
                'title': '🚫 Do Not Spray Today',
                'message': f'Wind speed {wind} km/h is too high for effective spraying.',
                'recommendation': 'Wait for wind speed to drop below 18 km/h.',
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
        elif temp > 35:
            return {
                'type': 'spray',
                'severity': 'warning',
                'title': '🌡️ Spray During Cooler Hours',
                'message': f'Temperature {temp}°C is high for effective spraying.',
                'recommendation': 'Spray early morning (6-9 AM) or late evening (5-7 PM).',
                'best_time': 'Early morning or late evening'
            }
        elif humidity < 35 or humidity > 85:
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
    def _get_location_specific_alerts(cls, location: str, temp: float, humidity: int, rain: float) -> List[Dict]:
        """Get location-specific alerts for Chandigarh and surrounding regions"""
        alerts = []
        
        if location in cls.REGIONAL_CROPS:
            crops = cls.REGIONAL_CROPS[location]
            
            # Determine current season
            month = datetime.now().month
            if 6 <= month <= 10:
                season = 'kharif'
                season_name = 'Kharif (Monsoon)'
            elif 11 <= month <= 3:
                season = 'rabi'
                season_name = 'Rabi (Winter)'
            else:
                season = 'summer'
                season_name = 'Summer'
            
            if season in crops:
                active_crops = crops[season]
                
                # Temperature alert for specific crops
                if temp >= 38 and 'Wheat' in active_crops:
                    alerts.append({
                        'type': 'location_specific',
                        'severity': 'critical',
                        'title': f'🌾 Wheat Heat Stress Alert - {location}',
                        'message': f'High temperature ({temp}°C) during wheat grain filling stage. Significant yield loss possible.',
                        'recommendation': 'Increase irrigation. Apply stress-reducing practices. Protect grain development.',
                        'crops': active_crops,
                        'season': season_name
                    })
                
                # Humidity alert for specific crops
                if humidity >= 80 and ('Rice' in active_crops or 'Maize' in active_crops):
                    alerts.append({
                        'type': 'location_specific',
                        'severity': 'high',
                        'title': f'🌾 Crop Disease Alert - {location}',
                        'message': f'High humidity ({humidity}%) in {location} favors disease development in {", ".join(active_crops[:3])}.',
                        'recommendation': 'Apply preventive fungicide. Monitor crops daily. Improve field drainage.',
                        'crops': active_crops,
                        'season': season_name
                    })
                
                # Rain alert for specific crops
                if rain >= 15 and ('Cotton' in active_crops or 'Sugarcane' in active_crops):
                    alerts.append({
                        'type': 'location_specific',
                        'severity': 'critical',
                        'title': f'🌧️ Waterlogging Risk - {location}',
                        'message': f'Heavy rain ({rain}mm) may cause waterlogging in {location} fields.',
                        'recommendation': 'Ensure proper drainage. Monitor for root rot diseases. Avoid mechanical operations.',
                        'crops': active_crops,
                        'season': season_name
                    })
        
        return alerts
    
    @classmethod
    def get_forecast_alerts(cls, forecast: List[Dict], location: str = 'Chandigarh') -> List[Dict]:
        """
        Generate alerts from forecast data
        
        Args:
            forecast: List of daily forecast dictionaries
            location: Location name (default: Chandigarh)
            
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
            if rain >= 20:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'critical',
                    'title': f'☔ Heavy Rain Forecast - {date} - {location}',
                    'message': f'{rain}mm rainfall expected in {location}. High disease and waterlogging risk.',
                    'recommendation': 'Apply preventive fungicide BEFORE rain. Ensure field drainage. Protect young plants.',
                    'date': date,
                    'location': location
                })
            elif rain >= 10:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'high',
                    'title': f'☔ Moderate Rain Forecast - {date} - {location}',
                    'message': f'Rain expected in {location}. Prepare for disease prevention.',
                    'recommendation': 'Apply preventive treatment before rain. Monitor after rain.',
                    'date': date,
                    'location': location
                })
            elif rain > 0:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'warning',
                    'title': f'🌧️ Light Rain Forecast - {date}',
                    'message': f'Light rain expected in {location} area.',
                    'recommendation': 'Consider applying preventive fungicide before rain.',
                    'date': date,
                    'location': location
                })
            
            # Temperature extremes for Chandigarh region
            if temp >= 40:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'critical',
                    'title': f'🔥 Extreme Heat Forecast - {date} - Chandigarh Region',
                    'message': f'Temperature forecast: {temp}°C. Extreme heat expected.',
                    'recommendation': 'Prepare shade structures. Increase irrigation. Protect crops from heat stress.',
                    'date': date,
                    'location': location
                })
            elif temp >= 37:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'high',
                    'title': f'🌡️ High Temperature Forecast - {date}',
                    'message': f'Temperature forecast: {temp}°C. Heat stress risk.',
                    'recommendation': 'Ensure adequate irrigation. Protect sensitive crops.',
                    'date': date,
                    'location': location
                })
            elif temp <= 2:
                alerts.append({
                    'type': 'forecast',
                    'severity': 'critical',
                    'title': f'❄️ Frost Risk - {date} - Chandigarh Region',
                    'message': f'Temperature forecast: {temp}°C. Frost risk for sensitive crops.',
                    'recommendation': 'Prepare frost protection (covers, water). Protect crops.',
                    'date': date,
                    'location': location
                })
        
        return alerts
    
    @classmethod
    def get_seasonal_alerts(cls, crop: str, location: str = 'Chandigarh', month: int = None) -> List[Dict]:
        """
        Generate seasonal alerts for specific crops in Chandigarh region
        
        Args:
            crop: Crop name
            location: Location name (default: Chandigarh)
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
            'Wheat': {
                'winter': ['Rust', 'Leaf Blight', 'Powdery Mildew'],
                'summer': ['Termites', 'Aphids']
            },
            'Rice': {
                'rainy': ['Blast', 'Leaf Spot', 'Stem Borer'],
                'winter': ['Bacterial Leaf Blight']
            },
            'Maize': {
                'rainy': ['Leaf Blight', 'Rust', 'Stem Borer'],
                'winter': ['Smut', 'Aphids']
            },
            'Cotton': {
                'rainy': ['Bacterial Blight', 'Aphids', 'Bollworm'],
                'winter': ['Mites', 'Whitefly']
            },
            'Sugarcane': {
                'rainy': ['Red Rot', 'Smut', 'Top Borer'],
                'winter': ['Sett Rot']
            }
        }
        
        if crop in seasonal_risks:
            crop_risks = seasonal_risks[crop]
            
            # Determine season based on month
            if 6 <= month <= 9:  # Monsoon/Rainy
                season = 'rainy'
                season_name = 'Monsoon'
            elif 10 <= month <= 2:  # Winter
                season = 'winter'
                season_name = 'Winter'
            else:  # Summer/Dry
                season = 'dry'
                season_name = 'Summer'
            
            if season in crop_risks:
                diseases = crop_risks[season]
                alerts.append({
                    'type': 'seasonal',
                    'severity': 'warning',
                    'title': f'🌿 Seasonal Alert - {crop} in {location}',
                    'message': f'High risk period for {crop} in {location}: {", ".join(diseases)}',
                    'recommendation': f'Increase monitoring frequency. Apply preventive treatments. Consult local agricultural office in {location} if symptoms appear.',
                    'crop': crop,
                    'season': season_name,
                    'high_risk_diseases': diseases,
                    'location': location
                })
        
        return alerts
    
    @classmethod
    def get_alert_summary(cls, weather_data: Dict, location: str = 'Chandigarh') -> Dict:
        """
        Get summary of all alerts for a location
        
        Args:
            weather_data: Current weather data
            location: Location name (default: Chandigarh)
            
        Returns:
            Summary dictionary with counts and highest priority alert
        """
        alerts = cls.generate_alerts(weather_data, location)
        
        if not alerts:
            return {
                'has_alerts': False,
                'total_alerts': 0,
                'critical_count': 0,
                'high_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'highest_priority': None,
                'alerts': [],
                'location': location
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
            'alerts': alerts,
            'location': location,
            'crop_season': cls._get_current_season()
        }
    
    @classmethod
    def _get_current_season(cls) -> str:
        """Get current agricultural season"""
        month = datetime.now().month
        if 6 <= month <= 10:
            return 'Kharif (Monsoon)'
        elif 11 <= month <= 3:
            return 'Rabi (Winter)'
        else:
            return 'Summer'