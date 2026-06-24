/**
 * FarmIntel AI - Real-Time Weather Analysis
 * Fetches weather data from backend API
 */

// Initialize AOS
AOS.init({
    duration: 800,
    once: true,
    offset: 50
});

// Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api', // Your Flask backend URL
    UPDATE_INTERVAL: 300000 // 5 minutes
};

// DOM Elements
const locationInput = document.getElementById('locationInput');
const searchLocationBtn = document.getElementById('searchLocationBtn');
const detectLocationBtn = document.getElementById('detectLocationBtn');
const refreshWeatherBtn = document.getElementById('refreshWeatherBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const weatherLocationSpan = document.getElementById('weatherLocation').querySelector('span');
const currentTemp = document.getElementById('currentTemp');
const weatherCondition = document.getElementById('weatherCondition');
const humidity = document.getElementById('humidity');
const windSpeed = document.getElementById('windSpeed');
const rainfall = document.getElementById('rainfall');
const minTemp = document.getElementById('minTemp');
const maxTemp = document.getElementById('maxTemp');
const pressure = document.getElementById('pressure');
const riskValue = document.getElementById('riskValue');
const riskFill = document.getElementById('riskFill');
const riskMessage = document.getElementById('riskMessage');
const riskBadge = document.getElementById('riskBadge');
const alertsContainer = document.getElementById('alertsContainer');
const sprayAdvisory = document.getElementById('sprayAdvisory');
const trendAnalysis = document.getElementById('trendAnalysis');
const updateTimeSpan = document.querySelector('#updateTime span');

let weatherChart = null;
let currentLocation = 'Chandigarh';
let updateTimer = null;

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
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };
    toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) toast.remove();
    }, 4000);
}

// Show/hide loading spinner
function setLoading(show) {
    if (loadingSpinner) {
        loadingSpinner.style.display = show ? 'block' : 'none';
    }
}

// Get weather icon class
function getWeatherIconClass(iconCode) {
    const iconMap = {
        '01d': 'fa-sun',
        '01n': 'fa-moon',
        '02d': 'fa-cloud-sun',
        '02n': 'fa-cloud-moon',
        '03d': 'fa-cloud',
        '03n': 'fa-cloud',
        '04d': 'fa-cloud',
        '04n': 'fa-cloud',
        '09d': 'fa-cloud-rain',
        '09n': 'fa-cloud-rain',
        '10d': 'fa-cloud-sun-rain',
        '10n': 'fa-cloud-moon-rain',
        '11d': 'fa-bolt',
        '11n': 'fa-bolt',
        '13d': 'fa-snowflake',
        '13n': 'fa-snowflake',
        '50d': 'fa-smog',
        '50n': 'fa-smog'
    };
    return iconMap[iconCode] || 'fa-cloud-sun-rain';
}

// Fetch weather data from backend API
async function fetchWeatherData(location) {
    try {
        setLoading(true);
        
        // Build query parameters
        const params = new URLSearchParams();
        if (location) {
            params.append('city', location);
        }
        
        const url = `${API_CONFIG.BASE_URL}/weather?${params.toString()}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `API Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Failed to fetch weather data');
        }
        
        return data;
        
    } catch (error) {
        console.error('Weather API Error:', error);
        showToast(`Failed to fetch weather: ${error.message}`, 'error');
        return null;
    } finally {
        setLoading(false);
    }
}

// Fetch forecast from backend API
async function fetchForecast(location) {
    try {
        const params = new URLSearchParams();
        if (location) {
            params.append('city', location);
        }
        params.append('days', '7');
        
        const url = `${API_CONFIG.BASE_URL}/weather/forecast?${params.toString()}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            return null;
        }
        
        const data = await response.json();
        return data.success ? data.forecast : null;
        
    } catch (error) {
        console.warn('Forecast API Error:', error);
        return null;
    }
}

// Update UI with weather data
async function updateWeatherData(location) {
    showToast(`Fetching real-time weather for ${location}...`, 'info');
    
    try {
        const data = await fetchWeatherData(location);
        
        if (!data) {
            return;
        }
        
        // Extract data from API response
        const weather = data.current || {};
        const locationInfo = data.location || {};
        const diseaseRisk = data.disease_risk || {};
        const alerts = data.alerts || [];
        const sprayAdvisoryData = data.spray_advisory || {};
        const forecastData = data.forecast || [];
        
        // Update location input
        const cityName = locationInfo.city || location || 'Unknown';
        locationInput.value = cityName;
        currentLocation = cityName;
        
        // Update current weather
        currentTemp.textContent = weather.temperature || '--';
        weatherCondition.textContent = weather.condition || 'Unknown';
        weatherLocationSpan.textContent = `${cityName.toUpperCase()}${locationInfo.country ? `, ${locationInfo.country}` : ''}`;
        humidity.textContent = weather.humidity || '--';
        windSpeed.textContent = weather.wind_speed || '--';
        rainfall.textContent = weather.rainfall || '0.0';
        minTemp.textContent = weather.min_temp || weather.temperature || '--';
        maxTemp.textContent = weather.max_temp || weather.temperature || '--';
        if (pressure) pressure.textContent = weather.pressure || '--';
        
        // Update update time
        if (updateTimeSpan) {
            updateTimeSpan.textContent = `Last updated: ${new Date().toLocaleString()}`;
        }
        
        // Update weather icon
        const weatherIcon = document.getElementById('weatherIcon');
        const iconClass = getWeatherIconClass(weather.weather_icon || '01d');
        weatherIcon.innerHTML = `<i class="fas ${iconClass}"></i>`;
        
        // Update risk index
        const riskLevel = diseaseRisk.risk_level || 'Low';
        const riskScore = diseaseRisk.risk_score || 0;
        const riskColor = diseaseRisk.risk_color || '#10B981';
        const riskMsg = diseaseRisk.risk_message || 'Loading weather data...';
        
        riskValue.textContent = riskLevel;
        riskValue.style.color = riskColor;
        
        const riskPercent = riskLevel === 'Critical' ? 95 : 
                           riskLevel === 'High' ? 80 : 
                           riskLevel === 'Medium' ? 55 : 25;
        riskFill.style.width = `${riskPercent}%`;
        riskFill.style.background = riskColor;
        riskMessage.textContent = riskMsg;
        
        // Update risk badge
        if (riskBadge) {
            riskBadge.className = `risk-badge ${riskLevel.toLowerCase()}`;
            riskBadge.textContent = riskLevel;
        }
        
        // Update risk factors
        const temp = weather.temperature || 25;
        const hum = weather.humidity || 65;
        const wind = weather.wind_speed || 10;
        const rain = weather.rainfall || 0;
        
        const tempPercent = Math.min(100, Math.max(0, Math.abs(temp - 25) * 6));
        const humidityPercent = Math.min(100, hum);
        const windPercent = Math.min(100, wind * 2);
        const rainPercent = Math.min(100, rain * 8);
        
        document.getElementById('tempFactor').style.width = `${tempPercent}%`;
        document.getElementById('humidityFactor').style.width = `${humidityPercent}%`;
        document.getElementById('windFactor').style.width = `${windPercent}%`;
        document.getElementById('rainFactor').style.width = `${rainPercent}%`;
        
        // Color factor bars
        document.getElementById('tempFactor').className = `factor-fill ${temp > 35 || temp < 0 ? 'high' : temp > 30 || temp < 10 ? 'medium' : 'low'}`;
        document.getElementById('humidityFactor').className = `factor-fill ${hum > 80 ? 'high' : hum > 65 ? 'medium' : 'low'}`;
        document.getElementById('windFactor').className = `factor-fill ${wind > 25 ? 'high' : wind > 15 ? 'medium' : 'low'}`;
        document.getElementById('rainFactor').className = `factor-fill ${rain > 15 ? 'high' : rain > 5 ? 'medium' : 'low'}`;
        
        // Update factor statuses
        const tempStatus = document.getElementById('tempStatus');
        const humidityStatus = document.getElementById('humidityStatus');
        const windStatus = document.getElementById('windStatus');
        const rainStatus = document.getElementById('rainStatus');
        
        if (tempStatus) {
            tempStatus.textContent = temp > 35 ? 'Extreme' : temp > 30 ? 'High' : temp < 0 ? 'Freezing' : temp < 5 ? 'Cold' : 'Normal';
            tempStatus.className = `factor-status ${temp > 35 || temp < 0 ? 'danger' : temp > 30 || temp < 5 ? 'warning' : 'success'}`;
        }
        if (humidityStatus) {
            humidityStatus.textContent = hum > 80 ? 'Critical' : hum > 65 ? 'High' : 'Normal';
            humidityStatus.className = `factor-status ${hum > 80 ? 'danger' : hum > 65 ? 'warning' : 'success'}`;
        }
        if (windStatus) {
            windStatus.textContent = wind > 25 ? 'High' : wind > 15 ? 'Moderate' : 'Low';
            windStatus.className = `factor-status ${wind > 25 ? 'danger' : wind > 15 ? 'warning' : 'success'}`;
        }
        if (rainStatus) {
            rainStatus.textContent = rain > 15 ? 'Heavy' : rain > 5 ? 'Moderate' : rain > 0 ? 'Light' : 'None';
        }
        
        // Update alerts
        updateAlerts(alerts);
        
        // Update spray advisory
        if (sprayAdvisoryData && sprayAdvisoryData.message) {
            sprayAdvisory.textContent = sprayAdvisoryData.message;
        } else {
            sprayAdvisory.textContent = 'No spray advisory available.';
        }
        
        // Update trend analysis
        if (forecastData && forecastData.length > 0) {
            const avgHumidity = forecastData.reduce((sum, d) => sum + (d.humidity || 0), 0) / forecastData.length;
            const highRiskDays = forecastData.filter(d => d.disease_risk === 'High' || d.disease_risk === 'Critical').length;
            const rainyDays = forecastData.filter(d => (d.rainfall || 0) > 5).length;
            
            let analysis = '';
            if (avgHumidity > 75) {
                analysis += `High humidity expected (${Math.round(avgHumidity)}%) over next 7 days. `;
            } else if (avgHumidity > 60) {
                analysis += `Moderate humidity levels expected (${Math.round(avgHumidity)}%). `;
            } else {
                analysis += `Low humidity conditions expected (${Math.round(avgHumidity)}%). `;
            }
            
            if (highRiskDays > 0) {
                analysis += `${highRiskDays} day(s) of high/critical disease risk. `;
            }
            
            if (rainyDays > 0) {
                analysis += `${rainyDays} day(s) with rainfall expected. Apply fungicide before rain.`;
            } else {
                analysis += 'No significant rainfall expected. Continue regular monitoring.';
            }
            
            trendAnalysis.textContent = analysis;
        } else {
            trendAnalysis.textContent = 'No forecast data available for trend analysis.';
        }
        
        // Update forecast grid
        if (forecastData && forecastData.length > 0) {
            updateForecastGrid(forecastData);
        }
        
        // Update chart
        if (forecastData && forecastData.length > 0) {
            updateWeatherChart(forecastData);
        }
        
        showToast(`Weather updated for ${cityName}!`, 'success');
        
    } catch (error) {
        console.error('Error updating weather:', error);
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Update alerts in UI
function updateAlerts(alerts) {
    alertsContainer.innerHTML = '';
    
    if (!alerts || alerts.length === 0) {
        alertsContainer.innerHTML = `
            <div class="alert-card success">
                <i class="fas fa-check-circle"></i>
                <div class="alert-content">
                    <h4>✅ Good Conditions</h4>
                    <p>Current weather conditions are favorable. Continue regular monitoring.</p>
                </div>
            </div>
        `;
        return;
    }
    
    alerts.forEach(alert => {
        const severity = alert.severity || 'info';
        const typeClass = severity === 'critical' ? 'high' : 
                         severity === 'high' ? 'high' : 
                         severity === 'warning' ? 'warning' : 
                         severity === 'success' ? 'success' : 'info';
        
        alertsContainer.innerHTML += `
            <div class="alert-card ${typeClass}">
                <i class="fas ${alert.icon || 'fa-info-circle'}"></i>
                <div class="alert-content">
                    <h4>${alert.title || 'Alert'}</h4>
                    <p>${alert.message || 'Weather alert'}</p>
                </div>
            </div>
        `;
    });
}

// Update forecast grid
function updateForecastGrid(forecast) {
    const grid = document.getElementById('forecastGrid');
    if (!forecast || forecast.length === 0) {
        grid.innerHTML = '<p style="color: #94A3B8; grid-column: 1/-1; text-align: center;">No forecast data available</p>';
        return;
    }
    
    grid.innerHTML = forecast.map(day => {
        const riskClass = (day.disease_risk || 'Low').toLowerCase();
        const iconClass = getWeatherIconClass(day.weather_icon || '01d');
        const temp = day.temperature || '--';
        const hum = day.humidity || '--';
        const risk = day.disease_risk || 'Low';
        
        return `
            <div class="forecast-card ${riskClass}">
                <div class="forecast-day">${day.day || day.date || '--'}</div>
                <i class="fas ${iconClass}"></i>
                <div class="forecast-temp">${temp}°C</div>
                <div class="forecast-humidity">${hum}%</div>
                <div class="forecast-risk ${riskClass}">${risk}</div>
            </div>
        `;
    }).join('');
}

// Update weather chart
function updateWeatherChart(forecast) {
    const ctx = document.getElementById('weatherTrendChart').getContext('2d');
    
    if (weatherChart) weatherChart.destroy();
    
    const labels = forecast.map(d => d.day || d.date || '');
    const temps = forecast.map(d => d.temperature || 0);
    const hums = forecast.map(d => d.humidity || 0);
    
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
                    data: hums,
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

// Detect user's location
async function detectUserLocation() {
    showToast('Detecting your location...', 'info');
    
    try {
        // Try IP-based geolocation first
        const ipResponse = await fetch('https://ipapi.co/json/');
        if (ipResponse.ok) {
            const ipData = await ipResponse.json();
            const city = ipData.city || ipData.region || ipData.country_name;
            
            if (city && city !== 'Unknown') {
                showToast(`Location detected: ${city}!`, 'success');
                locationInput.value = city;
                currentLocation = city;
                await updateWeatherData(city);
                return;
            }
        }
    } catch (error) {
        console.warn('IP geolocation failed:', error);
    }
    
    // Try browser geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;
                showToast(`Location detected! Fetching weather...`, 'success');
                
                try {
                    // Use the API to get weather by coordinates
                    const params = new URLSearchParams();
                    params.append('lat', latitude);
                    params.append('lon', longitude);
                    
                    const url = `${API_CONFIG.BASE_URL}/weather?${params.toString()}`;
                    const response = await fetch(url);
                    
                    if (response.ok) {
                        const data = await response.json();
                        const city = data.location?.city || 'Unknown';
                        locationInput.value = city;
                        currentLocation = city;
                        await updateWeatherData(city);
                    } else {
                        // Use coordinates as fallback
                        const coords = `${latitude.toFixed(4)},${longitude.toFixed(4)}`;
                        locationInput.value = coords;
                        currentLocation = coords;
                        await updateWeatherData(coords);
                    }
                } catch (error) {
                    showToast('Error with location service. Please enter city manually.', 'error');
                }
            },
            (error) => {
                let errorMessage = 'Unable to detect location. ';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage += 'Please allow location access or enter city manually.';
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
                showToast(errorMessage, 'warning');
            }
        );
    } else {
        showToast('Geolocation not supported. Please enter city manually.', 'warning');
    }
}

// Search location by city
async function searchLocation() {
    const location = locationInput.value.trim();
    if (!location) {
        showToast('Please enter a city name', 'error');
        return;
    }
    
    currentLocation = location;
    await updateWeatherData(location);
}

// Refresh weather data
async function refreshWeather() {
    if (refreshWeatherBtn) {
        refreshWeatherBtn.classList.add('spinning');
    }
    await updateWeatherData(currentLocation);
    if (refreshWeatherBtn) {
        setTimeout(() => {
            refreshWeatherBtn.classList.remove('spinning');
        }, 1000);
    }
}

// Event Listeners
if (searchLocationBtn) searchLocationBtn.addEventListener('click', searchLocation);
if (detectLocationBtn) detectLocationBtn.addEventListener('click', detectUserLocation);
if (refreshWeatherBtn) refreshWeatherBtn.addEventListener('click', refreshWeather);
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
    });
}
if (overlay) {
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
    });
}

// Logout
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('userName');
        window.location.href = '../index.html';
    });
}

// Set user name
const userName = localStorage.getItem('userName') || 'John';
const userNameElement = document.getElementById('userName');
if (userNameElement) userNameElement.innerHTML = userName;

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

const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    isDark = true;
    document.body.classList.add('dark-mode');
    if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
}

// Initialize
createParticles();

// Start with default location
updateWeatherData('Chandigarh');

// Auto-refresh every 5 minutes
if (updateTimer) clearInterval(updateTimer);
updateTimer = setInterval(() => {
    if (currentLocation) {
        updateWeatherData(currentLocation);
    }
}, API_CONFIG.UPDATE_INTERVAL);