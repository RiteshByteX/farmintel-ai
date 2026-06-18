/**
 * FarmIntel AI - Weather Analysis JavaScript
 * Complete weather functionality with location detection
 */

// Initialize AOS
AOS.init({
    duration: 800,
    once: true,
    offset: 50
});

// DOM Elements
const locationInput = document.getElementById('locationInput');
const searchLocationBtn = document.getElementById('searchLocationBtn');
const detectLocationBtn = document.getElementById('detectLocationBtn');
const weatherLocationSpan = document.getElementById('weatherLocation').querySelector('span');
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
    
    setTimeout(() => toast.remove(), 3000);
}

// Get weather data (mock data - replace with actual API call)
async function getWeatherData(location) {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate realistic mock data based on location name
    const locationHash = location.toLowerCase().split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    
    const temperatures = [22, 24, 26, 28, 30, 32, 34];
    const humidities = [55, 65, 75, 85, 90];
    const conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Heavy Rain', 'Thunderstorm'];
    
    const tempIndex = locationHash % temperatures.length;
    const humidityIndex = (locationHash + 7) % humidities.length;
    const conditionIndex = (locationHash + 3) % conditions.length;
    
    const temp = temperatures[tempIndex];
    const hum = humidities[humidityIndex];
    
    return {
        temperature: temp,
        humidity: hum,
        wind_speed: Math.floor(Math.random() * 25) + 5,
        rainfall: Math.random() * 10,
        condition: conditions[conditionIndex],
        min_temp: temp - 4,
        max_temp: temp + 4,
        location_name: location,
        timestamp: new Date().toLocaleString()
    };
}

// Generate forecast data
function generateForecastData() {
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
            risk: risk,
            icon: getWeatherIcon(humidityBase, tempBase)
        });
    }
    return forecast;
}

function getWeatherIcon(humidity, temp) {
    if (humidity > 80) return 'cloud-rain';
    if (humidity > 65) return 'cloud-sun-rain';
    if (temp > 30) return 'sun';
    return 'cloud-sun';
}

// Calculate disease risk
function calculateDiseaseRisk(temp, humidity, wind, rain) {
    let riskScore = 0;
    let risk = 'Low';
    let message = '';
    
    // Temperature factor
    if (temp > 32 || temp < 15) {
        riskScore += 2;
    } else if (temp > 28 || temp < 18) {
        riskScore += 1;
    }
    
    // Humidity factor (most important for fungal diseases)
    if (humidity > 85) {
        riskScore += 3;
    } else if (humidity > 75) {
        riskScore += 2;
    } else if (humidity > 65) {
        riskScore += 1;
    }
    
    // Wind factor
    if (wind > 20) {
        riskScore += 1;
    }
    
    // Rain factor
    if (rain > 5) {
        riskScore += 2;
    } else if (rain > 0) {
        riskScore += 1;
    }
    
    if (riskScore >= 5) {
        risk = 'High';
        message = '⚠️ CRITICAL: Perfect conditions for disease outbreak! Apply preventive fungicide immediately.';
    } else if (riskScore >= 3) {
        risk = 'Medium';
        message = '⚠️ Moderate risk. Monitor crops regularly.';
    } else {
        risk = 'Low';
        message = '✅ Low risk. Conditions are favorable. Continue regular monitoring.';
    }
    
    return { risk, message, score: riskScore };
}

// Get spray advisory
function getSprayAdvisory(temp, humidity, wind) {
    if (wind > 15) {
        return '⚠️ Not recommended today. Wind speed too high. Wait for calmer conditions (<15 km/h).';
    } else if (humidity > 80) {
        return '⚠️ Apply preventive fungicide today! High humidity creates disease risk.';
    } else if (temp > 30) {
        return '🌡️ Spray early morning or late evening to avoid heat stress on plants.';
    } else if (humidity < 60 && temp < 30) {
        return '✅ Perfect conditions for spraying today. Apply as scheduled.';
    } else {
        return '📋 Moderate conditions. Spraying possible but monitor weather changes.';
    }
}

// Get trend analysis
function getTrendAnalysis(forecast) {
    const avgHumidity = forecast.reduce((sum, d) => sum + d.humidity, 0) / 7;
    const highRiskDays = forecast.filter(d => d.risk === 'High').length;
    
    if (avgHumidity > 75) {
        return `Humidity expected to remain high for next ${highRiskDays} days. Monitor crops closely for early signs of disease.`;
    } else if (avgHumidity > 65) {
        return `Moderate humidity levels expected. Regular monitoring recommended.`;
    } else {
        return `Good weather conditions ahead. Continue standard crop management practices.`;
    }
}

// Update UI with weather data
async function updateWeatherData(location) {
    showToast(`Fetching weather data for ${location}...`, 'info');
    
    try {
        const data = await getWeatherData(location);
        const forecast = generateForecastData();
        const risk = calculateDiseaseRisk(data.temperature, data.humidity, data.wind_speed, data.rainfall);
        
        // Update current weather
        currentTemp.innerText = data.temperature;
        weatherCondition.innerText = data.condition;
        weatherLocationSpan.innerText = `${data.location_name.toUpperCase()}`;
        humidity.innerText = data.humidity;
        windSpeed.innerText = data.wind_speed;
        rainfall.innerText = data.rainfall.toFixed(1);
        minTemp.innerText = data.min_temp;
        maxTemp.innerText = data.max_temp;
        
        // Update weather icon
        const weatherIcon = document.getElementById('weatherIcon');
        if (data.condition === 'Sunny') weatherIcon.innerHTML = '<i class="fas fa-sun"></i>';
        else if (data.condition === 'Partly Cloudy') weatherIcon.innerHTML = '<i class="fas fa-cloud-sun"></i>';
        else if (data.condition === 'Cloudy') weatherIcon.innerHTML = '<i class="fas fa-cloud"></i>';
        else if (data.condition === 'Light Rain') weatherIcon.innerHTML = '<i class="fas fa-cloud-rain"></i>';
        else if (data.condition === 'Heavy Rain') weatherIcon.innerHTML = '<i class="fas fa-cloud-showers-heavy"></i>';
        else if (data.condition === 'Thunderstorm') weatherIcon.innerHTML = '<i class="fas fa-bolt"></i>';
        else weatherIcon.innerHTML = '<i class="fas fa-cloud-sun-rain"></i>';
        
        // Update risk index
        riskValue.innerText = risk.risk;
        riskValue.style.color = risk.risk === 'High' ? '#F87171' : risk.risk === 'Medium' ? '#FBBF24' : '#34D399';
        
        const riskPercent = risk.risk === 'High' ? 85 : risk.risk === 'Medium' ? 60 : 30;
        riskFill.style.width = `${riskPercent}%`;
        riskFill.style.background = risk.risk === 'High' ? '#EF4444' : risk.risk === 'Medium' ? '#F59E0B' : '#10B981';
        riskMessage.innerText = risk.message;
        
        // Update risk factors
        const tempPercent = Math.min(100, Math.abs(data.temperature - 25) * 10);
        const humidityPercent = Math.min(100, data.humidity);
        const windPercent = Math.min(100, data.wind_speed * 2);
        const rainPercent = Math.min(100, data.rainfall * 10);
        
        document.getElementById('tempFactor').style.width = `${tempPercent}%`;
        document.getElementById('humidityFactor').style.width = `${humidityPercent}%`;
        document.getElementById('windFactor').style.width = `${windPercent}%`;
        document.getElementById('rainFactor').style.width = `${rainPercent}%`;
        
        // Color factor bars
        document.getElementById('tempFactor').className = `factor-fill ${data.temperature > 32 || data.temperature < 15 ? 'high' : data.temperature > 28 || data.temperature < 18 ? 'medium' : 'low'}`;
        document.getElementById('humidityFactor').className = `factor-fill ${data.humidity > 80 ? 'high' : data.humidity > 65 ? 'medium' : 'low'}`;
        document.getElementById('windFactor').className = `factor-fill ${data.wind_speed > 20 ? 'high' : data.wind_speed > 12 ? 'medium' : 'low'}`;
        document.getElementById('rainFactor').className = `factor-fill ${data.rainfall > 5 ? 'high' : data.rainfall > 0 ? 'medium' : 'low'}`;
        
        // Update factor statuses
        document.getElementById('tempStatus').innerText = data.temperature > 32 ? 'High' : data.temperature < 18 ? 'Low' : 'Normal';
        document.getElementById('tempStatus').className = `factor-status ${data.temperature > 32 || data.temperature < 15 ? 'danger' : 'success'}`;
        document.getElementById('humidityStatus').innerText = data.humidity > 80 ? 'Critical' : data.humidity > 65 ? 'High' : 'Normal';
        document.getElementById('humidityStatus').className = `factor-status ${data.humidity > 80 ? 'danger' : data.humidity > 65 ? 'warning' : 'success'}`;
        document.getElementById('windStatus').innerText = data.wind_speed > 20 ? 'High' : data.wind_speed > 12 ? 'Moderate' : 'Low';
        document.getElementById('rainStatus').innerText = data.rainfall > 5 ? 'Heavy' : data.rainfall > 0 ? 'Light' : 'None';
        
        // Update alerts
        updateAlerts(data, risk);
        
        // Update spray advisory
        sprayAdvisory.innerText = getSprayAdvisory(data.temperature, data.humidity, data.wind_speed);
        
        // Update trend analysis
        trendAnalysis.innerText = getTrendAnalysis(forecast);
        
        // Update forecast grid
        updateForecastGrid(forecast);
        
        // Update chart
        updateWeatherChart(forecast);
        
        showToast(`Weather data updated for ${location}!`, 'success');
        
    } catch (error) {
        console.error('Error fetching weather:', error);
        showToast('Error fetching weather data', 'error');
    }
}

// Update alerts
function updateAlerts(data, risk) {
    alertsContainer.innerHTML = '';
    
    if (data.humidity > 80) {
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
    
    if (data.rainfall > 0) {
        alertsContainer.innerHTML += `
            <div class="alert-card warning">
                <i class="fas fa-cloud-rain"></i>
                <div class="alert-content">
                    <h4>☔ Rain Expected</h4>
                    <p>Rain forecast in next 24 hours. Apply fungicide BEFORE rain for best protection.</p>
                </div>
            </div>
        `;
    }
    
    if (data.wind_speed > 20) {
        alertsContainer.innerHTML += `
            <div class="alert-card warning">
                <i class="fas fa-wind"></i>
                <div class="alert-content">
                    <h4>💨 High Wind Alert</h4>
                    <p>High wind speeds may spread fungal spores. Consider wind barriers if possible.</p>
                </div>
            </div>
        `;
    }
    
    if (risk.risk === 'High') {
        alertsContainer.innerHTML += `
            <div class="alert-card high">
                <i class="fas fa-skull-crosswalk"></i>
                <div class="alert-content">
                    <h4>🚨 Critical Disease Risk</h4>
                    <p>Perfect conditions for disease outbreak! Immediate preventive action recommended.</p>
                </div>
            </div>
        `;
    }
    
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

// Update forecast grid
function updateForecastGrid(forecast) {
    const grid = document.getElementById('forecastGrid');
    grid.innerHTML = forecast.map(day => `
        <div class="forecast-card ${day.risk.toLowerCase()}">
            <div class="forecast-day">${day.day}</div>
            <i class="fas fa-${day.icon}"></i>
            <div class="forecast-temp">${day.temperature}°C</div>
            <div class="forecast-humidity">${day.humidity}%</div>
            <div class="forecast-risk ${day.risk.toLowerCase()}">${day.risk}</div>
        </div>
    `).join('');
}

// Update weather chart
function updateWeatherChart(forecast) {
    const ctx = document.getElementById('weatherTrendChart').getContext('2d');
    
    if (weatherChart) weatherChart.destroy();
    
    weatherChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: forecast.map(d => d.day),
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: forecast.map(d => d.temperature),
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
                    data: forecast.map(d => d.humidity),
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
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } },
                x: { grid: { display: false }, ticks: { color: '#94A3B8' } }
            }
        }
    });
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
            
            // In a real app, you would reverse geocode lat/lng to city name
            // For demo, we'll use a mock city based on coordinates
            const mockCities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'];
            const cityIndex = Math.floor((latitude + longitude) % mockCities.length);
            const city = mockCities[cityIndex];
            
            locationInput.value = city;
            currentLocation = city;
            await updateWeatherData(city);
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

// Search location by city/pincode
async function searchLocation() {
    const location = locationInput.value.trim();
    if (!location) {
        showToast('Please enter a city name or pincode', 'error');
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
updateWeatherData('Mumbai');

// Auto-refresh every 5 minutes
setInterval(() => {
    updateWeatherData(currentLocation);
}, 300000);