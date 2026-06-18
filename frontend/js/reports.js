/**
 * FarmIntel AI - Reports JavaScript
 * Complete Backend Integration with PDF/CSV Export
 */

// Initialize AOS
AOS.init({ duration: 800, once: true, offset: 50 });

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const reportTypeSelect = document.getElementById('reportType');
const dateRangeSelect = document.getElementById('dateRange');
const formatBtns = document.querySelectorAll('.format-btn');
const generateBtn = document.getElementById('generateReportBtn');
const totalScansSpan = document.getElementById('totalScansStat');
const diseasesFoundSpan = document.getElementById('diseasesFoundStat');
const avgConfidenceSpan = document.getElementById('avgConfidenceStat');
const healthScoreSpan = document.getElementById('healthScoreStat');
const reportTableBody = document.getElementById('reportTableBody');

let scanHistory = [];
let filteredHistory = [];
let currentFormat = 'pdf';
let distributionChart = null;
let trendChart = null;

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

// Show toast
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Fetch history from backend API
async function fetchHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.history) {
                scanHistory = data.history.map(record => ({
                    id: record.id,
                    disease: record.disease || 'Unknown Disease',
                    date: record.timestamp || record.date || new Date().toISOString(),
                    confidence: record.confidence || 0,
                    severity: record.severity || 'Low',
                    chemical_treatment: record.chemical_treatment || 'Copper hydroxide - 2g/L water. Apply every 7-10 days.',
                    organic_treatment: record.organic_treatment || 'Neem oil 5ml/L + garlic extract. Spray twice weekly.',
                    cultural_practices: record.cultural_practices || 'Remove infected leaves, avoid overhead watering.',
                    prevention_tips: record.prevention_tips || 'Use resistant varieties, crop rotation, proper spacing.'
                }));
                localStorage.setItem('scanHistory', JSON.stringify(scanHistory));
                applyFilters();
                return;
            }
        }
        // Fallback to localStorage
        loadFromLocalStorage();
    } catch (error) {
        console.error('Error fetching history:', error);
        loadFromLocalStorage();
    }
}

// Load from localStorage fallback
function loadFromLocalStorage() {
    const stored = localStorage.getItem('scanHistory');
    if (stored && JSON.parse(stored).length > 0) {
        scanHistory = JSON.parse(stored);
    } else {
        scanHistory = getSampleHistory();
        localStorage.setItem('scanHistory', JSON.stringify(scanHistory));
    }
    applyFilters();
}

// Sample history data (fallback)
function getSampleHistory() {
    const diseases = [
        "Tomato Late Blight", "Tomato Early Blight", "Potato Late Blight",
        "Apple Scab", "Corn Common Rust", "Rice Blast", "Wheat Rust",
        "Tomato Healthy", "Potato Healthy"
    ];
    const severities = ["Severe", "Moderate", "Mild", "Low"];
    const treatments = [
        "Copper hydroxide - 2g/L water. Apply every 7-10 days.",
        "Chlorothalonil - 2ml/L water. Apply at first sign.",
        "Mancozeb - 2g/L water. Apply preventatively."
    ];
    
    const history = [];
    const today = new Date();
    for (let i = 1; i <= 25; i++) {
        const date = new Date();
        date.setDate(today.getDate() - Math.floor(Math.random() * 60));
        history.push({
            id: i,
            disease: diseases[Math.floor(Math.random() * diseases.length)],
            date: date.toLocaleString(),
            confidence: Math.floor(Math.random() * (98 - 65 + 1) + 65),
            severity: severities[Math.floor(Math.random() * severities.length)],
            chemical_treatment: treatments[Math.floor(Math.random() * treatments.length)],
            organic_treatment: "Neem oil 5ml/L + garlic extract. Spray twice weekly.",
            cultural_practices: "Remove infected leaves, avoid overhead watering.",
            prevention_tips: "Use resistant varieties, crop rotation, proper spacing."
        });
    }
    return history.sort((a, b) => new Date(b.date) - new Date(a.date));
}

// Filter by date range
function filterByDateRange(data, range) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    return data.filter(item => {
        const itemDate = new Date(item.date);
        const daysDiff = Math.floor((today - itemDate) / (1000 * 60 * 60 * 24));
        
        switch(range) {
            case 'today': return daysDiff === 0;
            case 'week': return daysDiff <= 7;
            case 'month': return daysDiff <= 30;
            case 'year': return daysDiff <= 365;
            default: return true;
        }
    });
}

// Apply filters and update everything
function applyFilters() {
    const dateRange = dateRangeSelect.value;
    filteredHistory = filterByDateRange(scanHistory, dateRange);
    updateStatistics();
    updateTable();
    renderCharts();
}

// Update statistics
function updateStatistics() {
    const total = filteredHistory.length;
    const diseased = filteredHistory.filter(s => !s.disease.includes('Healthy')).length;
    const avgConf = total > 0 ? Math.round(filteredHistory.reduce((sum, s) => sum + s.confidence, 0) / total) : 0;
    const healthScore = total > 0 ? Math.round((filteredHistory.filter(s => s.disease.includes('Healthy')).length / total) * 100) : 100;
    
    totalScansSpan.innerText = total;
    diseasesFoundSpan.innerText = diseased;
    avgConfidenceSpan.innerText = avgConf;
    healthScoreSpan.innerText = healthScore;
}

// Update table
function updateTable() {
    if (filteredHistory.length === 0) {
        reportTableBody.innerHTML = '<tr class="empty-row"><td colspan="5">No data available for selected period</td></tr>';
        return;
    }
    
    reportTableBody.innerHTML = filteredHistory.slice(0, 15).map(scan => `
        <tr>
            <td>${formatDate(scan.date)}</td>
            <td><div class="disease-cell"><i class="fas fa-leaf"></i><span>${scan.disease}</span></div></td>
            <td><div class="confidence-badge ${getConfidenceClass(scan.confidence)}">${scan.confidence}%</div></td>
            <td><span class="severity-badge ${scan.severity.toLowerCase()}">${scan.severity}</span></td>
            <td class="treatment-cell" title="${scan.chemical_treatment}">${scan.chemical_treatment.substring(0, 40)}...</td>
        </tr>
    `).join('');
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
        return dateStr;
    }
}

function getConfidenceClass(confidence) {
    if (confidence >= 85) return 'high';
    if (confidence >= 70) return 'medium';
    return 'low';
}

// Render charts
function renderCharts() {
    // Disease Distribution Chart
    const diseaseCount = {};
    filteredHistory.forEach(scan => {
        diseaseCount[scan.disease] = (diseaseCount[scan.disease] || 0) + 1;
    });
    const topDiseases = Object.entries(diseaseCount).sort((a, b) => b[1] - a[1]).slice(0, 6);
    
    const ctx1 = document.getElementById('diseaseDistributionChart').getContext('2d');
    if (distributionChart) distributionChart.destroy();
    
    distributionChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: topDiseases.map(d => d[0].length > 20 ? d[0].substring(0, 20) + '...' : d[0]),
            datasets: [{
                label: 'Number of Detections',
                data: topDiseases.map(d => d[1]),
                backgroundColor: ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: 'rgba(0,0,0,0.8)', titleColor: '#fff', bodyColor: '#94A3B8' }
            },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } },
                x: { ticks: { color: '#94A3B8', maxRotation: 45, minRotation: 45 } }
            }
        }
    });
    
    // Detection Trend Chart (last 7 days)
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        last7Days.push(date.toLocaleDateString());
    }
    
    const trendData = last7Days.map(day => {
        return filteredHistory.filter(s => new Date(s.date).toLocaleDateString() === day).length;
    });
    
    const ctx2 = document.getElementById('detectionTrendChart').getContext('2d');
    if (trendChart) trendChart.destroy();
    
    trendChart = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: last7Days.map(d => d.substring(0, 5)),
            datasets: [{
                label: 'Scans per Day',
                data: trendData,
                borderColor: '#4F46E5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#4F46E5',
                pointBorderColor: '#fff',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: { backgroundColor: 'rgba(0,0,0,0.8)', titleColor: '#fff', bodyColor: '#94A3B8' }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } },
                x: { grid: { display: false }, ticks: { color: '#94A3B8' } }
            }
        }
    });
}

// Generate Report via Backend API
async function generateReport() {
    if (filteredHistory.length === 0) {
        showToast('No data available for the selected period', 'error');
        return;
    }
    
    const reportType = reportTypeSelect.value;
    const dateRange = dateRangeSelect.value;
    
    showToast(`Generating ${currentFormat.toUpperCase()} report...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/report/${currentFormat}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                report_type: reportType,
                date_range: dateRange,
                history: filteredHistory
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `farmintel_report_${reportType}_${new Date().toISOString().split('T')[0]}.${currentFormat}`;
            a.click();
            URL.revokeObjectURL(url);
            showToast(`${currentFormat.toUpperCase()} report generated successfully!`, 'success');
            return;
        }
        throw new Error('Report generation failed');
    } catch (error) {
        console.error('Report generation error:', error);
        // Fallback to local generation
        if (currentFormat === 'pdf') {
            generatePDFLocal();
        } else {
            generateCSVLocal();
        }
    }
}

// Generate PDF locally (fallback)
function generatePDFLocal() {
    const reportType = reportTypeSelect.value;
    const dateRange = dateRangeSelect.value;
    const startDate = filteredHistory.length > 0 ? new Date(filteredHistory[filteredHistory.length - 1].date).toLocaleDateString() : 'N/A';
    const endDate = filteredHistory.length > 0 ? new Date(filteredHistory[0].date).toLocaleDateString() : 'N/A';
    const totalScans = filteredHistory.length;
    const diseasedScans = filteredHistory.filter(s => !s.disease.includes('Healthy')).length;
    const avgConfidence = totalScans > 0 ? Math.round(filteredHistory.reduce((sum, s) => sum + s.confidence, 0) / totalScans) : 0;
    
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        showToast('Please allow popups to generate PDF', 'error');
        return;
    }
    
    let reportTitle = 'FarmIntel AI - ';
    if (reportType === 'summary') reportTitle += 'Summary Report';
    else if (reportType === 'detailed') reportTitle += 'Detailed Analysis Report';
    else reportTitle += 'Weather Impact Report';
    
    let dateRangeText = '';
    if (dateRange === 'today') dateRangeText = 'Today';
    else if (dateRange === 'week') dateRangeText = 'Last 7 Days';
    else if (dateRange === 'month') dateRangeText = 'Last 30 Days';
    else if (dateRange === 'year') dateRangeText = 'Last Year';
    else dateRangeText = 'All Time';
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>FarmIntel AI Report</title>
            <style>
                body {
                    font-family: 'Inter', Arial, sans-serif;
                    padding: 40px;
                    background: white;
                    color: #1F2937;
                }
                .header {
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #4F46E5;
                    margin-bottom: 30px;
                }
                .header h1 {
                    color: #4F46E5;
                    margin-bottom: 5px;
                }
                .header p {
                    color: #6B7280;
                    font-size: 12px;
                }
                .summary {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .summary-card {
                    background: #F3F4F6;
                    padding: 15px;
                    text-align: center;
                    border-radius: 10px;
                }
                .summary-value {
                    font-size: 28px;
                    font-weight: bold;
                    color: #4F46E5;
                }
                .summary-label {
                    font-size: 12px;
                    color: #6B7280;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #E5E7EB;
                }
                th {
                    background: #F3F4F6;
                    font-weight: 600;
                }
                .footer {
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #E5E7EB;
                    font-size: 10px;
                    color: #6B7280;
                }
                h2 {
                    color: #374151;
                    font-size: 18px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌾 FarmIntel AI</h1>
                <h2>${reportTitle}</h2>
                <p>Period: ${dateRangeText} (${startDate} - ${endDate}) | Generated: ${new Date().toLocaleString()}</p>
            </div>
            
            <div class="summary">
                <div class="summary-card">
                    <div class="summary-value">${totalScans}</div>
                    <div class="summary-label">Total Scans</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${diseasedScans}</div>
                    <div class="summary-label">Diseased Crops</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${avgConfidence}%</div>
                    <div class="summary-label">Avg Confidence</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${totalScans - diseasedScans}</div>
                    <div class="summary-label">Healthy Crops</div>
                </div>
            </div>
            
            <h2>Detection Records</h2>
            <table>
                <thead>
                    <tr><th>Date</th><th>Disease</th><th>Confidence</th><th>Severity</th><th>Treatment</th></tr>
                </thead>
                <tbody>
                    ${filteredHistory.slice(0, 50).map(s => `
                        <tr>
                            <td>${formatDate(s.date)}</td>
                            <td>${s.disease}</td>
                            <td>${s.confidence}%</td>
                            <td><span style="background:${s.severity === 'Severe' ? '#FEE2E2' : s.severity === 'Moderate' ? '#FEF3C7' : '#D1FAE5'};padding:4px 8px;border-radius:20px;font-size:11px;">${s.severity}</span></td>
                            <td>${s.chemical_treatment.substring(0, 50)}...</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            <div class="footer">
                <p>FarmIntel AI - Empowering Farmers with AI Technology</p>
                <p>This report is automatically generated. For medical advice, consult a local agronomist.</p>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
    showToast('PDF preview opened. Use print to save as PDF.', 'success');
}

// Generate CSV locally (fallback)
function generateCSVLocal() {
    if (filteredHistory.length === 0) {
        showToast('No data to export', 'warning');
        return;
    }
    
    const headers = ['Date', 'Disease', 'Confidence (%)', 'Severity', 'Chemical Treatment', 'Organic Treatment', 'Cultural Practices', 'Prevention Tips'];
    const rows = filteredHistory.map(item => [
        formatDate(item.date),
        item.disease,
        item.confidence,
        item.severity,
        item.chemical_treatment,
        item.organic_treatment,
        item.cultural_practices,
        item.prevention_tips
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `farmintel_report_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('CSV report generated successfully!', 'success');
}

// Event Listeners
reportTypeSelect.addEventListener('change', applyFilters);
dateRangeSelect.addEventListener('change', applyFilters);

formatBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        formatBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFormat = btn.dataset.format;
        showToast(`${currentFormat.toUpperCase()} format selected`, 'info');
    });
});

if (generateBtn) generateBtn.addEventListener('click', generateReport);

// Mobile sidebar
const mobileToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
        if (sidebar) sidebar.classList.toggle('mobile-open');
        if (overlay) overlay.classList.toggle('active');
    });
}
if (overlay) {
    overlay.addEventListener('click', () => {
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (overlay) overlay.classList.remove('active');
    });
}

// Logout
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '../index.html';
    });
}

// Set user name
const userNameElement = document.getElementById('userName');
if (userNameElement) {
    const userStr = localStorage.getItem('farmintel_user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            userNameElement.innerHTML = user.name || 'Farmer';
        } catch (e) {
            userNameElement.innerHTML = localStorage.getItem('userName') || 'John';
        }
    } else {
        userNameElement.innerHTML = localStorage.getItem('userName') || 'John';
    }
}

// Theme toggle
let isDark = false;
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        themeToggle.innerHTML = isDark ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
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
            return true;
        }
        return false;
    } catch (error) {
        console.warn('⚠️ Backend not reachable');
        return false;
    }
}

// Initialize
createParticles();

// Load data from backend or fallback
checkBackendHealth().then(isHealthy => {
    if (isHealthy) {
        fetchHistory();
    } else {
        loadFromLocalStorage();
        showToast('Backend offline. Using local data.', 'warning');
    }
});

// Auto-refresh every 30 seconds
setInterval(() => {
    if (document.visibilityState === 'visible') {
        checkBackendHealth().then(isHealthy => {
            if (isHealthy) fetchHistory();
        });
    }
}, 30000);