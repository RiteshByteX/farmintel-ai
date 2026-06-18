/**
 * FarmIntel AI - Dashboard JavaScript
 * Complete Backend Integration - Professional Layout
 */

// Initialize AOS
AOS.init({
    duration: 800,
    once: true,
    offset: 50
});

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Global variables
let dashboardChart = null;
let refreshInterval = null;

// Set current date
function setCurrentDate() {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        dateElement.innerText = new Date().toLocaleDateString('en-US', options);
    }
}

// Load user data
function loadUserData() {
    const userStr = localStorage.getItem('farmintel_user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            const userNameElement = document.getElementById('userName');
            const welcomeMessage = document.getElementById('welcomeMessage');
            
            if (userNameElement) userNameElement.textContent = user.name || 'Farmer';
            if (welcomeMessage) welcomeMessage.innerHTML = `Welcome back, ${user.name || 'Farmer'}! 👋`;
        } catch (e) {
            console.error('Error loading user data:', e);
        }
    }
}

// Fetch statistics from backend
async function fetchStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/history/statistics`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                return data.statistics;
            }
        }
        return null;
    } catch (error) {
        console.error('Error fetching statistics:', error);
        return null;
    }
}

// Fetch recent scans
async function fetchRecentScans(limit = 5) {
    try {
        const response = await fetch(`${API_BASE_URL}/history?limit=${limit}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                return data.history || [];
            }
        }
        return [];
    } catch (error) {
        console.error('Error fetching recent scans:', error);
        return [];
    }
}

// Fetch weather data
async function fetchWeatherData(city = 'Mumbai') {
    try {
        const response = await fetch(`${API_BASE_URL}/weather?city=${encodeURIComponent(city)}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                return data;
            }
        }
        return null;
    } catch (error) {
        console.error('Error fetching weather:', error);
        return null;
    }
}

// Update dashboard statistics
async function updateDashboardStats() {
    const stats = await fetchStatistics();
    
    if (stats) {
        animateNumber('totalScans', stats.total_scans || 0);
        animateNumber('diseasedCrops', stats.diseased_count || 0);
        
        const healthyCount = (stats.total_scans || 0) - (stats.diseased_count || 0);
        animateNumber('healthScore', healthyCount);
        
        // Update trends
        const scanTrend = document.getElementById('scanTrend');
        if (scanTrend && stats.total_scans > 0) {
            scanTrend.innerHTML = `<i class="fas fa-chart-line"></i><span>${stats.total_scans} total</span>`;
        }
        
        const diseaseTrend = document.getElementById('diseaseTrend');
        if (diseaseTrend && stats.disease_rate > 0) {
            diseaseTrend.innerHTML = `<i class="fas fa-arrow-down"></i><span>${stats.disease_rate}%</span>`;
        }
        
        const healthTrend = document.getElementById('healthTrend');
        if (healthTrend && stats.healthy_count > 0 && stats.total_scans > 0) {
            const healthyPercent = Math.round((stats.healthy_count / stats.total_scans) * 100);
            healthTrend.innerHTML = `<i class="fas fa-arrow-up"></i><span>${healthyPercent}% healthy</span>`;
        }
    } else {
        // Fallback to localStorage
        const history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
        animateNumber('totalScans', history.length);
        const diseased = history.filter(s => s.disease && !s.disease.includes('Healthy')).length;
        animateNumber('diseasedCrops', diseased);
        animateNumber('healthScore', history.length - diseased);
    }
}

// Update weather alert
async function updateWeatherAlert() {
    const weatherData = await fetchWeatherData();
    const alertDiv = document.getElementById('weatherAlert');
    const riskElement = document.getElementById('weatherRisk');
    const alertTitle = document.getElementById('alertTitle');
    const alertMessage = document.getElementById('alertMessage');
    
    if (!alertDiv) return;
    
    if (weatherData && weatherData.current) {
        const temp = weatherData.current.temperature;
        const humidity = weatherData.current.humidity;
        const risk = weatherData.disease_risk?.risk_level || 'Low';
        
        // Update risk display
        if (riskElement) {
            riskElement.innerHTML = risk;
            if (risk === 'Critical' || risk === 'High') {
                riskElement.style.color = '#F87171';
            } else if (risk === 'Medium') {
                riskElement.style.color = '#FBBF24';
            } else {
                riskElement.style.color = '#34D399';
            }
        }
        
        // Update alert banner
        if (risk === 'Critical' || risk === 'High') {
            alertDiv.className = 'weather-alert high-risk';
            alertDiv.querySelector('.alert-icon').innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
            if (alertTitle) alertTitle.innerHTML = `⚠️ ${risk} Risk Alert`;
            if (alertMessage) alertMessage.innerHTML = `Temperature: ${temp}°C | Humidity: ${humidity}%. ${risk === 'Critical' ? 'Immediate action required!' : 'High risk of fungal diseases. Apply preventive measures.'}`;
        } else if (risk === 'Medium') {
            alertDiv.className = 'weather-alert medium-risk';
            alertDiv.querySelector('.alert-icon').innerHTML = '<i class="fas fa-cloud-rain"></i>';
            if (alertTitle) alertTitle.innerHTML = '📋 Medium Risk Alert';
            if (alertMessage) alertMessage.innerHTML = `Temperature: ${temp}°C | Humidity: ${humidity}%. Monitor crops regularly for disease symptoms.`;
        } else {
            alertDiv.className = 'weather-alert low-risk';
            alertDiv.querySelector('.alert-icon').innerHTML = '<i class="fas fa-check-circle"></i>';
            if (alertTitle) alertTitle.innerHTML = '✅ Low Risk';
            if (alertMessage) alertMessage.innerHTML = `Temperature: ${temp}°C | Humidity: ${humidity}%. Conditions are favorable for crop growth.`;
        }
    } else {
        if (alertTitle) alertTitle.innerHTML = '⚠️ Weather Alert';
        if (alertMessage) alertMessage.innerHTML = 'Unable to fetch weather data. Please check your connection.';
        if (riskElement) riskElement.innerHTML = '--';
    }
}

// Update recent scans table
async function updateRecentScans() {
    const tbody = document.getElementById('recentScansTable');
    if (!tbody) return;
    
    try {
        const scans = await fetchRecentScans(5);
        
        if (!scans || scans.length === 0) {
            tbody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="5">
                        <div class="empty-state">
                            <i class="fas fa-camera"></i>
                            <h4>No Scans Yet</h4>
                            <p>Click "Start Scanning" to detect your first disease</p>
                            <button class="btn-primary" onclick="location.href='detect.html'">
                                Start Scanning <i class="fas fa-arrow-right"></i>
                            </button>
                        </div>
                    <\/td>
                <\/tr>
            `;
            return;
        }
        
        tbody.innerHTML = scans.map(scan => `
            <tr data-id="${scan.id}">
                <td>
                    <div class="disease-cell">
                        <i class="fas ${scan.is_healthy ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i>
                        <span>${scan.disease || 'Unknown Disease'}</span>
                    </div>
                <\/td>
                <td>${formatDate(scan.timestamp || scan.date)}<\/td>
                <td>
                    <div class="confidence-badge ${getConfidenceClass(scan.confidence)}">
                        ${scan.confidence || 0}%
                    </div>
                <\/td>
                <td>
                    <span class="severity-badge ${(scan.severity || 'Low').toLowerCase()}">
                        ${scan.severity || 'Low'}
                    </span>
                <\/td>
                <td>
                    <button class="view-detail-btn" onclick="viewScanDetail(${scan.id})" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                <\/td>
            <\/tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading recent scans:', error);
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="5">
                    <div class="empty-state">
                        <i class="fas fa-exclamation-circle"></i>
                        <h4>Error Loading Data</h4>
                        <p>Please check if the backend server is running</p>
                        <button class="btn-primary" onclick="location.reload()">
                            Retry <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                <\/td>
            <\/tr>
        `;
    }
}

// Update disease distribution chart
async function updateDiseaseChart() {
    const ctx = document.getElementById('diseaseChart');
    if (!ctx) return;
    
    try {
        const stats = await fetchStatistics();
        const diseaseBreakdown = stats?.disease_breakdown || {};
        
        const diseases = Object.keys(diseaseBreakdown).slice(0, 5);
        const counts = diseases.map(d => diseaseBreakdown[d]);
        
        if (dashboardChart) dashboardChart.destroy();
        
        const colors = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
        
        dashboardChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: diseases.length ? diseases : ['No Data'],
                datasets: [{
                    data: diseases.length ? counts : [1],
                    backgroundColor: diseases.length ? colors : ['#64748B'],
                    borderWidth: 0,
                    borderRadius: 10,
                    spacing: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94A3B8',
                            font: { size: 11, family: 'Inter' },
                            padding: 10
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 15, 26, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#94A3B8',
                        padding: 10,
                        cornerRadius: 8
                    }
                },
                cutout: '65%',
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000
                }
            }
        });
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

// View scan detail
window.viewScanDetail = async function(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/history/${id}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.record) {
                showDetailModal(data.record);
                return;
            }
        }
        showToast('Error loading scan details', 'error');
    } catch (error) {
        console.error('Error fetching scan detail:', error);
        showToast('Error loading scan details', 'error');
    }
};

// Show detail modal
function showDetailModal(scan) {
    const modal = document.getElementById('detailModal');
    if (!modal) {
        createDetailModal(scan);
        return;
    }
    
    const modalBody = document.getElementById('detailModalBody');
    if (!modalBody) return;
    
    const date = formatDate(scan.timestamp || scan.date, 'full');
    
    modalBody.innerHTML = `
        <div class="detail-section">
            <h3>${scan.disease || 'Unknown Disease'}</h3>
            <div class="detail-row">
                <span class="detail-label">Date:</span>
                <span class="detail-value">${date}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Confidence:</span>
                <span class="detail-value">${scan.confidence || 0}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Severity:</span>
                <span class="detail-value severity-badge ${(scan.severity || 'Low').toLowerCase()}">${scan.severity || 'Low'}</span>
            </div>
            <div class="detail-section-title">Chemical Treatment</div>
            <div class="detail-text">${scan.chemical_treatment || 'Copper hydroxide - 2g/L water. Apply every 7-10 days.'}</div>
            <div class="detail-section-title">Organic Treatment</div>
            <div class="detail-text">${scan.organic_treatment || 'Neem oil 5ml/L + garlic extract. Spray twice weekly.'}</div>
            <div class="detail-section-title">Cultural Practices</div>
            <div class="detail-text">${scan.cultural_practices || 'Remove infected leaves, avoid overhead watering.'}</div>
            <div class="detail-section-title">Prevention Tips</div>
            <div class="detail-text">${scan.prevention_tips || 'Use resistant varieties, crop rotation, proper spacing.'}</div>
        </div>
    `;
    
    modal.style.display = 'flex';
    
    // Close modal handlers
    const closeModal = () => modal.style.display = 'none';
    modal.querySelectorAll('.modal-close, #closeDetailModal').forEach(btn => {
        btn.onclick = closeModal;
    });
    window.onclick = (e) => { if (e.target === modal) closeModal(); };
}

// Create detail modal if not exists
function createDetailModal(scan) {
    const modalHTML = `
        <div id="detailModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2><i class="fas fa-file-medical"></i> Scan Details</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body" id="detailModalBody"></div>
                <div class="modal-footer">
                    <button class="btn-primary" id="downloadDetailPdf">Download Report</button>
                    <button class="btn-outline" id="closeDetailModal">Close</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    showDetailModal(scan);
}

// Helper functions
function animateNumber(elementId, endValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startValue = 0;
    const duration = 1000;
    const increment = (endValue - startValue) / (duration / 16);
    let current = startValue;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= endValue) {
            element.textContent = endValue;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

function getConfidenceClass(confidence) {
    if (confidence >= 85) return 'high';
    if (confidence >= 70) return 'medium';
    return 'low';
}

function formatDate(dateStr, format = 'short') {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        if (format === 'short') {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } else {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        }
    } catch {
        return dateStr;
    }
}

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

// Setup event listeners
function setupEventListeners() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            themeToggle.innerHTML = isDark ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        });
    }
    
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            sidebar?.classList.toggle('mobile-open');
            overlay?.classList.toggle('active');
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar?.classList.remove('mobile-open');
            overlay.classList.remove('active');
        });
    }
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.clear();
            window.location.href = '../index.html';
        });
    }
    
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }
}

// Auto refresh
function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(async () => {
        await updateDashboardStats();
        await updateRecentScans();
        await updateDiseaseChart();
        await updateWeatherAlert();
    }, 30000);
}

// Initialize dashboard
async function initDashboard() {
    setCurrentDate();
    loadUserData();
    setupEventListeners();
    
    await updateDashboardStats();
    await updateRecentScans();
    await updateDiseaseChart();
    await updateWeatherAlert();
    startAutoRefresh();
}

// Start dashboard
document.addEventListener('DOMContentLoaded', initDashboard);

// Cleanup
window.addEventListener('beforeunload', () => {
    if (refreshInterval) clearInterval(refreshInterval);
});