/**
 * FarmIntel AI - Weather Analysis JavaScript
 * Complete Backend Integration with OpenWeatherMap API
 */

// Initialize AOS
AOS.init({
    duration: 800,
    once: true,
    offset: 50
});

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const locationInput = document.getElementById('locationInput');
const searchLocationBtn = document.getElementById('searchLocationBtn');
const detectLocationBtn = document.getElementById('detectLocationBtn');
const weatherLocationSpan = document.getElementById('weatherLocation')?.querySelector('span');
const currentTemp = document.getElementById('currentTemp');
const weatherCondition = document.getElementById('weatherCondition');
const humidity = document.getElementById('humidity');
const windSpeed = document.getElementById('windSpeed');
const rainfall = document.getElementById('rainfall');
const minTemp = document.getElementById('minTemp');
const maxTemp = document.getElementById('maxTemp');
const riskValue = document.getElementById('riskValue');
const riskFill = document.getElementById('riskFill');
const riskMessage = document.getElementById('riskMessage');
const alertsContainer = document.getElementById('alertsContainer');
const sprayAdvisory = document.getElementById('sprayAdvisory');
const trendAnalysis = document.getElementById('trendAnalysis');
const weatherIcon = document.getElementById('weatherIcon');

let weatherChart = null;
let currentLocation = 'Mumbai';

// Create particles
function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    
    for (let i = 0; i < 50; i++) {
        const p = document.createElement('div');
        p.classList.add('particle');
        p.style.width = Math.random() * 5 + 2 + 'px';
        p.style.height = p.style.width;
        p.style.left = Math.random() * 100 + '%';
        p.style.bottom = '-10px';
        p.style.animationDelay = Math.random() * 15 + 's';
        p.style.animationDuration = 8 + Math.random() * 12 + 's';
        p.style.background = `rgba(79, 70, 229, ${Math.random() * 0.3 + 0.1})`;
        container.appendChild(p);
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutToast 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Get weather data from backend API
async function getWeatherData(location) {
    try {
        const response = await fetch(`${API_BASE_URL}/weather?city=${encodeURIComponent(location)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to fetch weather');
        }
        
        return data;
    } catch (error) {
        console.error('Weather API error:', error);
        showToast(`Error fetching weather for ${location}`, 'error');
        return null;
    }
}

// Get forecast data from backend
async function getForecastData(location) {
    try {
        const response = await fetch(`${API_BASE_URL}/weather/forecast?city=${encodeURIComponent(location)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            return data.forecast || [];
        }
        return [];
    } catch (error) {
        console.error('Forecast API error:', error);
        return [];
    }
}

// Update UI with weather data
async function updateWeatherData(location) {
    if (!location || location.trim() === '') {
        location = 'Mumbai';
    }
    
    showToast(`Fetching weather data for ${location}...`, 'info');
    
    try {
        // Fetch current weather
        const weatherData = await getWeatherData(location);
        
        if (!weatherData || !weatherData.current) {
            throw new Error('No weather data received');
        }
        
        const current = weatherData.current;
        const locationName = weatherData.location?.city || location;
        
        // Update current weather display
        if (currentTemp) currentTemp.innerText = current.temperature || '--';
        if (weatherCondition) weatherCondition.innerText = current.condition || 'Unknown';
        if (weatherLocationSpan) weatherLocationSpan.innerText = locationName.toUpperCase();
        if (humidity) humidity.innerText = current.humidity || '--';
        if (windSpeed) windSpeed.innerText = current.wind_speed || '--';
        if (rainfall) rainfall.innerText = current.rainfall || '0';
        if (minTemp) minTemp.innerText = current.temp_min || (current.temperature - 4);
        if (maxTemp) maxTemp.innerText = current.temp_max || (current.temperature + 4);
        
        // Update weather icon
        updateWeatherIcon(current.condition_main || current.condition);
        
        // Update risk index
        const risk = weatherData.disease_risk || {};
        const riskLevel = risk.risk_level || 'Low';
        const riskScore = risk.risk_score || 30;
        
        if (riskValue) {
            riskValue.innerText = riskLevel;
            riskValue.style.color = riskLevel === 'High' ? '#F87171' : riskLevel === 'Medium' ? '#FBBF24' : '#34D399';
        }
        
        if (riskFill) {
            const percent = riskLevel === 'High' ? 85 : riskLevel === 'Medium' ? 60 : 30;
            riskFill.style.width = `${percent}%`;
            riskFill.style.background = riskLevel === 'High' ? '#EF4444' : riskLevel === 'Medium' ? '#F59E0B' : '#10B981';
        }
        
        if (riskMessage) {
            riskMessage.innerText = risk.risk_message || getRiskMessage(riskLevel);
        }
        
        // Update risk factors
        updateRiskFactors(current);
        
        // Update alerts
        updateAlerts(weatherData.alerts || [], current);
        
        // Update spray advisory
        if (sprayAdvisory) {
            sprayAdvisory.innerText = getSprayAdvisory(current.temperature, current.humidity, current.wind_speed);
        }
        
        // Fetch and update forecast
        const forecast = await getForecastData(location);
        
        if (forecast && forecast.length > 0) {
            updateForecastGrid(forecast);
            updateWeatherChart(forecast);
            if (trendAnalysis) {
                trendAnalysis.innerText = getTrendAnalysis(forecast);
            }
        } else {
            // Fallback to generated forecast
            const fallbackForecast = generateFallbackForecast();
            updateForecastGrid(fallbackForecast);
            updateWeatherChart(fallbackForecast);
            if (trendAnalysis) {
                trendAnalysis.innerText = getTrendAnalysis(fallbackForecast);
            }
        }
        
        showToast(`Weather updated for ${locationName}!`, 'success');
        
    } catch (error) {
        console.error('Error updating weather:', error);
        showToast('Error fetching weather data. Using fallback data.', 'warning');
        
        // Use fallback data
        useFallbackWeatherData(location);
    }
}

// Update weather icon based on condition
function updateWeatherIcon(condition) {
    if (!weatherIcon) return;
    
    const conditionLower = (condition || '').toLowerCase();
    
    if (conditionLower.includes('sun') || conditionLower.includes('clear')) {
        weatherIcon.innerHTML = '<i class="fas fa-sun"></i>';
    } else if (conditionLower.includes('partly') || conditionLower.includes('cloud')) {
        weatherIcon.innerHTML = '<i class="fas fa-cloud-sun"></i>';
    } else if (conditionLower.includes('rain') || conditionLower.includes('shower')) {
        weatherIcon.innerHTML = '<i class="fas fa-cloud-rain"></i>';
    } else if (conditionLower.includes('thunder') || conditionLower.includes('storm')) {
        weatherIcon.innerHTML = '<i class="fas fa-bolt"></i>';
    } else if (conditionLower.includes('snow')) {
        weatherIcon.innerHTML = '<i class="fas fa-snowflake"></i>';
    } else if (conditionLower.includes('mist') || conditionLower.includes('fog')) {
        weatherIcon.innerHTML = '<i class="fas fa-smog"></i>';
    } else {
        weatherIcon.innerHTML = '<i class="fas fa-cloud-sun-rain"></i>';
    }
}

// Get risk message
function getRiskMessage(riskLevel) {
    if (riskLevel === 'High') {
        return '⚠️ CRITICAL: Perfect conditions for disease outbreak! Apply preventive fungicide immediately.';
    } else if (riskLevel === 'Medium') {
        return '⚠️ Moderate risk. Monitor crops regularly for disease symptoms.';
    } else {
        return '✅ Low risk. Conditions are favorable. Continue regular monitoring.';
    }
}

// Update risk factors display
function updateRiskFactors(weather) {
    const temp = weather.temperature || 25;
    const humidity = weather.humidity || 65;
    const wind = weather.wind_speed || 10;
    const rain = weather.rainfall || 0;
    
    // Temperature factor
    const tempPercent = Math.min(100, Math.abs(temp - 25) * 8);
    const tempFactor = document.getElementById('tempFactor');
    const tempStatus = document.getElementById('tempStatus');
    if (tempFactor) {
        tempFactor.style.width = `${tempPercent}%`;
        tempFactor.className = `factor-fill ${temp > 32 || temp < 15 ? 'high' : temp > 28 || temp < 18 ? 'medium' : 'low'}`;
    }
    if (tempStatus) {
        tempStatus.innerText = temp > 32 ? 'High' : temp < 18 ? 'Low' : 'Normal';
        tempStatus.className = `factor-status ${temp > 32 || temp < 15 ? 'danger' : 'success'}`;
    }
    
    // Humidity factor
    const humidityPercent = Math.min(100, humidity);
    const humidityFactor = document.getElementById('humidityFactor');
    const humidityStatus = document.getElementById('humidityStatus');
    if (humidityFactor) {
        humidityFactor.style.width = `${humidityPercent}%`;
        humidityFactor.className = `factor-fill ${humidity > 80 ? 'high' : humidity > 65 ? 'medium' : 'low'}`;
    }
    if (humidityStatus) {
        humidityStatus.innerText = humidity > 80 ? 'Critical' : humidity > 65 ? 'High' : 'Normal';
        humidityStatus.className = `factor-status ${humidity > 80 ? 'danger' : humidity > 65 ? 'warning' : 'success'}`;
    }
    
    // Wind factor
    const windPercent = Math.min(100, wind * 3);
    const windFactor = document.getElementById('windFactor');
    const windStatus = document.getElementById('windStatus');
    if (windFactor) {
        windFactor.style.width = `${windPercent}%`;
        windFactor.className = `factor-fill ${wind > 20 ? 'high' : wind > 12 ? 'medium' : 'low'}`;
    }
    if (windStatus) {
        windStatus.innerText = wind > 20 ? 'High' : wind > 12 ? 'Moderate' : 'Low';
    }
    
    // Rain factor
    const rainPercent = Math.min(100, rain * 8);
    const rainFactor = document.getElementById('rainFactor');
    const rainStatus = document.getElementById('rainStatus');
    if (rainFactor) {
        rainFactor.style.width = `${rainPercent}%`;
        rainFactor.className = `factor-fill ${rain > 5 ? 'high' : rain > 0 ? 'medium' : 'low'}`;
    }
    if (rainStatus) {
        rainStatus.innerText = rain > 5 ? 'Heavy' : rain > 0 ? 'Light' : 'None';
    }
}

// Update alerts
function updateAlerts(alerts, weather) {
    if (!alertsContainer) return;
    
    alertsContainer.innerHTML = '';
    
    // Add API alerts if any
    if (alerts && alerts.length > 0) {
        alerts.forEach(alert => {
            const severity = alert.severity || 'warning';
            alertsContainer.innerHTML += `
                <div class="alert-card ${severity}">
                    <i class="fas ${severity === 'high' ? 'fa-exclamation-triangle' : severity === 'critical' ? 'fa-skull-crosswalk' : 'fa-info-circle'}"></i>
                    <div class="alert-content">
                        <h4>${alert.title || 'Weather Alert'}</h4>
                        <p>${alert.message || alert}</p>
                    </div>
                </div>
            `;
        });
    }
    
    // Add humidity alert
    if (weather.humidity > 80) {
        alertsContainer.innerHTML += `
            <div class="alert-card high">
                <i class="fas fa-exclamation-triangle"></i>
                <div class="alert-content">
                    <h4>⚠️ High Humidity Alert</h4>
                    <p>Humidity levels above 80% create perfect conditions for fungal diseases. Apply preventive fungicide immediately.</p>
                </div>
            </div>
        `;
    }
    
    // Add rain alert
    if (weather.rainfall > 0) {
        alertsContainer.innerHTML += `
            <div class="alert-card warning">
                <i class="fas fa-cloud-rain"></i>
                <div class="alert-content">
                    <h4>☔ Rain Expected</h4>
                    <p>Rain forecast. Apply fungicide BEFORE rain for best protection.</p>
                </div>
            </div>
        `;
    }
    
    // Add wind alert
    if (weather.wind_speed > 20) {
        alertsContainer.innerHTML += `
            <div class="alert-card warning">
                <i class="fas fa-wind"></i>
                <div class="alert-content">
                    <h4>💨 High Wind Alert</h4>
                    <p>High wind speeds may spread fungal spores. Avoid spraying today.</p>
                </div>
            </div>
        `;
    }
    
    // If no alerts, show good conditions
    if (alertsContainer.innerHTML === '') {
        alertsContainer.innerHTML = `
            <div class="alert-card success">
                <i class="fas fa-check-circle"></i>
                <div class="alert-content">
                    <h4>✅ Good Conditions</h4>
                    <p>Current weather conditions are favorable. Continue regular monitoring.</p>
                </div>
            </div>
        `;
    }
}

// Get spray advisory
function getSprayAdvisory(temp, humidity, wind) {
    if (wind > 15) {
        return '⚠️ Not recommended today. Wind speed too high. Wait for calmer conditions (<15 km/h).';
    } else if (humidity > 80) {
        return '⚠️ Apply preventive fungicide today! High humidity creates disease risk.';
    } else if (temp > 32) {
        return '🌡️ Spray early morning or late evening to avoid heat stress on plants.';
    } else if (humidity < 60 && temp < 30) {
        return '✅ Perfect conditions for spraying today. Apply as scheduled.';
    } else {
        return '📋 Moderate conditions. Spraying possible but monitor weather changes.';
    }
}

// Get trend analysis
function getTrendAnalysis(forecast) {
    if (!forecast || forecast.length === 0) {
        return 'Loading trend analysis...';
    }
    
    const avgHumidity = forecast.reduce((sum, d) => sum + (d.humidity || 0), 0) / forecast.length;
    const highRiskDays = forecast.filter(d => d.disease_risk === 'High' || d.risk === 'High').length;
    
    if (avgHumidity > 75) {
        return `Humidity expected to remain high for next ${highRiskDays} days. Monitor crops closely for early signs of disease.`;
    } else if (avgHumidity > 65) {
        return `Moderate humidity levels expected. Regular monitoring recommended.`;
    } else {
        return `Good weather conditions ahead. Continue standard crop management practices.`;
    }
}

// Update forecast grid
function updateForecastGrid(forecast) {
    const grid = document.getElementById('forecastGrid');
    if (!grid) return;
    
    if (!forecast || forecast.length === 0) {
        grid.innerHTML = '<div class="forecast-card">No forecast data available</div>';
        return;
    }
    
    grid.innerHTML = forecast.map(day => {
        const risk = day.disease_risk || day.risk || 'Low';
        const temp = day.temperature || '--';
        const humidity = day.humidity || '--';
        const icon = getForecastIcon(day.condition);
        
        return `
            <div class="forecast-card ${risk.toLowerCase()}">
                <div class="forecast-day">${day.day || day.date?.slice(5) || '--'}</div>
                <i class="fas fa-${icon}"></i>
                <div class="forecast-temp">${temp}°C</div>
                <div class="forecast-humidity">${humidity}%</div>
                <div class="forecast-risk ${risk.toLowerCase()}">${risk}</div>
            </div>
        `;
    }).join('');
}

// Get forecast icon based on condition
function getForecastIcon(condition) {
    if (!condition) return 'cloud-sun';
    const cond = condition.toLowerCase();
    if (cond.includes('sun') || cond.includes('clear')) return 'sun';
    if (cond.includes('cloud')) return 'cloud';
    if (cond.includes('rain')) return 'cloud-rain';
    if (cond.includes('thunder')) return 'bolt';
    return 'cloud-sun';
}

// Update weather chart
function updateWeatherChart(forecast) {
    const ctx = document.getElementById('weatherTrendChart');
    if (!ctx) return;
    
    if (weatherChart) weatherChart.destroy();
    
    if (!forecast || forecast.length === 0) {
        return;
    }
    
    const labels = forecast.map(d => d.day || d.date?.slice(5) || '');
    const temps = forecast.map(d => d.temperature || 0);
    const humidities = forecast.map(d => d.humidity || 0);
    
    weatherChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temps,
                    borderColor: '#FBBF24',
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#FBBF24',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Humidity (%)',
                    data: humidities,
                    borderColor: '#4F46E5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#4F46E5',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#94A3B8', font: { size: 12 } }
                },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                y: { 
                    beginAtZero: true, 
                    grid: { color: 'rgba(255,255,255,0.05)' }, 
                    ticks: { color: '#94A3B8' } 
                },
                x: { 
                    grid: { display: false }, 
                    ticks: { color: '#94A3B8' } 
                }
            }
        }
    });
}

// Generate fallback forecast when API fails
function generateFallbackForecast() {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const forecast = [];
    
    for (let i = 0; i < 7; i++) {
        const tempBase = 25 + Math.sin(i) * 3;
        const humidityBase = 70 + Math.cos(i * 1.5) * 15;
        
        let risk = 'Medium';
        if (humidityBase > 80) risk = 'High';
        else if (humidityBase < 65) risk = 'Low';
        
        forecast.push({
            day: days[i],
            temperature: Math.round(tempBase),
            humidity: Math.round(humidityBase),
            disease_risk: risk,
            risk: risk,
            condition: humidityBase > 80 ? 'Rainy' : humidityBase > 65 ? 'Cloudy' : 'Sunny'
        });
    }
    return forecast;
}

// Use fallback weather data
function useFallbackWeatherData(location) {
    const temp = 27;
    const humidity = 71;
    const wind = 12;
    const rain = 0;
    
    if (currentTemp) currentTemp.innerText = temp;
    if (weatherCondition) weatherCondition.innerText = 'Partly Cloudy';
    if (weatherLocationSpan) weatherLocationSpan.innerText = location.toUpperCase();
    if (humidity) humidity.innerText = humidity;
    if (windSpeed) windSpeed.innerText = wind;
    if (rainfall) rainfall.innerText = rain;
    if (minTemp) minTemp.innerText = temp - 4;
    if (maxTemp) maxTemp.innerText = temp + 4;
    
    updateWeatherIcon('Partly Cloudy');
    
    if (riskValue) {
        riskValue.innerText = 'Low';
        riskValue.style.color = '#34D399';
    }
    if (riskFill) {
        riskFill.style.width = '30%';
        riskFill.style.background = '#10B981';
    }
    if (riskMessage) {
        riskMessage.innerText = '✅ Low risk. Conditions are favorable.';
    }
    
    updateRiskFactors({ temperature: temp, humidity: humidity, wind_speed: wind, rainfall: rain });
    
    const fallbackAlerts = [];
    updateAlerts(fallbackAlerts, { temperature: temp, humidity: humidity, wind_speed: wind, rainfall: rain });
    
    if (sprayAdvisory) {
        sprayAdvisory.innerText = getSprayAdvisory(temp, humidity, wind);
    }
    
    const fallbackForecast = generateFallbackForecast();
    updateForecastGrid(fallbackForecast);
    updateWeatherChart(fallbackForecast);
    if (trendAnalysis) {
        trendAnalysis.innerText = getTrendAnalysis(fallbackForecast);
    }
}

// Detect user's location
function detectUserLocation() {
    showToast('Detecting your location...', 'info');
    
    if (!navigator.geolocation) {
        showToast('Geolocation is not supported by your browser', 'error');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude } = position.coords;
            showToast(`Location detected! Fetching weather...`, 'success');
            
            try {
                const response = await fetch(`${API_BASE_URL}/weather?lat=${latitude}&lon=${longitude}`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.location?.city) {
                        locationInput.value = data.location.city;
                        currentLocation = data.location.city;
                        await updateWeatherData(currentLocation);
                        return;
                    }
                }
                // Fallback: use a mock city
                const mockCities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'];
                const cityIndex = Math.floor((latitude + longitude) % mockCities.length);
                const city = mockCities[cityIndex];
                locationInput.value = city;
                currentLocation = city;
                await updateWeatherData(city);
            } catch (error) {
                const mockCities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'];
                const cityIndex = Math.floor((latitude + longitude) % mockCities.length);
                const city = mockCities[cityIndex];
                locationInput.value = city;
                currentLocation = city;
                await updateWeatherData(city);
            }
        },
        (error) => {
            let errorMessage = 'Unable to detect location. ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Please allow location access.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'Location request timed out.';
                    break;
                default:
                    errorMessage += 'Please enter city manually.';
            }
            showToast(errorMessage, 'error');
        }
    );
}

// Search location by city
async function searchLocation() {
    const location = locationInput?.value.trim();
    if (!location) {
        showToast('Please enter a city name', 'error');
        return;
    }
    
    currentLocation = location;
    await updateWeatherData(location);
}

// Event Listeners
if (searchLocationBtn) searchLocationBtn.addEventListener('click', searchLocation);
if (detectLocationBtn) detectLocationBtn.addEventListener('click', detectUserLocation);
if (locationInput) locationInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchLocation();
});

// Mobile sidebar
const mobileToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
        overlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
    });
}

if (overlay) {
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    });
}

// Logout
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('farmintel_user');
        localStorage.removeItem('farmintel_token');
        localStorage.removeItem('farmintel_logged_in');
        window.location.href = '../index.html';
    });
}

// Set user name
const userStr = localStorage.getItem('farmintel_user');
if (userStr) {
    try {
        const user = JSON.parse(userStr);
        const userNameElement = document.getElementById('userName');
        if (userNameElement) userNameElement.innerHTML = user.name || 'Farmer';
    } catch (e) {}
} else {
    const userNameElement = document.getElementById('userName');
    if (userNameElement) userNameElement.innerHTML = 'John Farmer';
}

// Theme toggle
let isDark = false;
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        themeToggle.innerHTML = isDark ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        showToast(`${isDark ? 'Dark' : 'Light'} mode activated`, 'success');
    });
}

// Load saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    isDark = true;
    document.body.classList.add('dark-mode');
    if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
}

// Check backend health
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend is healthy');
            showToast('Connected to weather service', 'success');
        } else {
            console.warn('⚠️ Backend response error');
            showToast('Weather service issue. Using fallback data.', 'warning');
        }
    } catch (error) {
        console.warn('⚠️ Backend not reachable');
        showToast('Weather service offline. Using demo data.', 'warning');
    }
}

// Initialize
createParticles();
checkBackendHealth();
updateWeatherData('Mumbai');

// Auto-refresh every 5 minutes
setInterval(() => {
    updateWeatherData(currentLocation);
}, 300000);