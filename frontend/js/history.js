/**
 * FarmIntel AI - Scan History JavaScript
 * Complete Backend Integration
 */

// Initialize AOS
AOS.init({ duration: 800, once: true, offset: 50 });

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const severityFilter = document.getElementById('severityFilter');
const dateFilter = document.getElementById('dateFilter');
const clearFiltersBtn = document.getElementById('clearFiltersBtn');
const historyTableBody = document.getElementById('historyTableBody');
const selectAllCheckbox = document.getElementById('selectAllCheckbox');
const deleteAllBtn = document.getElementById('deleteAllBtn');
const exportCsvBtn = document.getElementById('exportCsvBtn');
const exportPdfBtn = document.getElementById('exportPdfBtn');
const totalScansSpan = document.getElementById('totalScans');
const diseasesDetectedSpan = document.getElementById('diseasesDetected');
const avgConfidenceSpan = document.getElementById('avgConfidence');
const lastScanSpan = document.getElementById('lastScan');

let scanHistory = [];
let filteredHistory = [];
let currentPage = 1;
let itemsPerPage = 10;
let currentDeleteId = null;

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
                // Convert backend format to frontend format
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
        // If API fails, try localStorage
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

// Load history
function loadHistory() {
    fetchHistory();
}

// Sample history data (fallback)
function getSampleHistory() {
    const diseases = [
        "Tomato Late Blight", "Tomato Early Blight", "Potato Late Blight",
        "Apple Scab", "Corn Common Rust", "Rice Blast", "Wheat Rust",
        "Tomato Healthy", "Potato Healthy"
    ];
    const severities = ["Severe", "Moderate", "Mild", "Low"];
    
    const history = [];
    for (let i = 1; i <= 15; i++) {
        const date = new Date();
        date.setDate(date.getDate() - Math.floor(Math.random() * 60));
        history.push({
            id: i,
            disease: diseases[Math.floor(Math.random() * diseases.length)],
            date: date.toLocaleString(),
            confidence: Math.floor(Math.random() * (98 - 65 + 1) + 65),
            severity: severities[Math.floor(Math.random() * severities.length)],
            chemical_treatment: "Copper hydroxide - 2g/L water. Apply every 7-10 days.",
            organic_treatment: "Neem oil 5ml/L + garlic extract. Spray twice weekly.",
            cultural_practices: "Remove infected leaves, avoid overhead watering.",
            prevention_tips: "Use resistant varieties, crop rotation, proper spacing."
        });
    }
    return history.sort((a, b) => new Date(b.date) - new Date(a.date));
}

// Apply filters
function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase();
    const severityValue = severityFilter.value;
    const dateValue = dateFilter.value;
    
    filteredHistory = scanHistory.filter(record => {
        if (searchTerm && !record.disease.toLowerCase().includes(searchTerm)) return false;
        if (severityValue !== 'all' && record.severity !== severityValue) return false;
        
        if (dateValue !== 'all') {
            const recordDate = new Date(record.date);
            const now = new Date();
            const daysDiff = Math.floor((now - recordDate) / (1000 * 60 * 60 * 24));
            if (dateValue === 'today' && daysDiff > 0) return false;
            if (dateValue === 'week' && daysDiff > 7) return false;
            if (dateValue === 'month' && daysDiff > 30) return false;
            if (dateValue === 'year' && daysDiff > 365) return false;
        }
        return true;
    });
    
    updateStats();
    currentPage = 1;
    renderTable();
}

// Update statistics
function updateStats() {
    totalScansSpan.innerText = filteredHistory.length;
    const diseasedCount = filteredHistory.filter(r => !r.disease.includes('Healthy')).length;
    diseasesDetectedSpan.innerText = diseasedCount;
    const avgConf = filteredHistory.length > 0 ? Math.round(filteredHistory.reduce((sum, r) => sum + r.confidence, 0) / filteredHistory.length) : 0;
    avgConfidenceSpan.innerText = avgConf;
    if (filteredHistory.length > 0) {
        const lastDate = new Date(filteredHistory[0].date);
        lastScanSpan.innerText = lastDate.toLocaleDateString();
    } else {
        lastScanSpan.innerText = '-';
    }
}

function getConfidenceClass(confidence) {
    if (confidence >= 85) return 'high';
    if (confidence >= 70) return 'medium';
    return 'low';
}

// Render table
function renderTable() {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageRecords = filteredHistory.slice(start, end);
    const paginationContainer = document.getElementById('paginationContainer');
    
    if (pageRecords.length === 0) {
        historyTableBody.innerHTML = `<tr class="empty-row"><td colspan="7"><div class="empty-state"><i class="fas fa-history"></i><h4>No matching records found</h4><p>Try adjusting your search or filters</p></div></td></tr>`;
        if (paginationContainer) paginationContainer.style.display = 'none';
        return;
    }
    
    if (paginationContainer) paginationContainer.style.display = 'flex';
    
    historyTableBody.innerHTML = pageRecords.map(record => `
        <tr data-id="${record.id}">
            <td><input type="checkbox" class="record-checkbox" data-id="${record.id}"></td>
            <td><div class="disease-cell"><i class="fas fa-leaf"></i><span>${record.disease}</span></div></td>
            <td>${formatDate(record.date)}</td>
            <td><div class="confidence-badge ${getConfidenceClass(record.confidence)}">${record.confidence}%</div></td>
            <td><span class="severity-badge ${record.severity.toLowerCase()}">${record.severity}</span></td>
            <td class="treatment-preview" title="${record.chemical_treatment}">${record.chemical_treatment.substring(0, 40)}...</td>
            <td><div class="action-buttons"><button class="view-btn" onclick="viewDetails(${record.id})"><i class="fas fa-eye"></i></button><button class="delete-btn" onclick="confirmDelete(${record.id})"><i class="fas fa-trash"></i></button></div></td>
        </tr>
    `).join('');
    
    updatePagination();
    
    document.querySelectorAll('.record-checkbox').forEach(cb => {
        cb.addEventListener('change', updateSelectAllState);
    });
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        return date.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
        return dateStr;
    }
}

function updatePagination() {
    const totalPages = Math.ceil(filteredHistory.length / itemsPerPage);
    const pageNumbers = document.getElementById('pageNumbers');
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    
    if (prevBtn) prevBtn.disabled = currentPage === 1;
    if (nextBtn) nextBtn.disabled = currentPage === totalPages;
    
    if (!pageNumbers) return;
    
    let pagesHtml = '';
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage + 1 < maxVisible) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    if (startPage > 1) {
        pagesHtml += `<button class="page-num" data-page="1">1</button>`;
        if (startPage > 2) pagesHtml += `<span class="page-dots">...</span>`;
    }
    
    for (let i = startPage; i <= endPage; i++) {
        pagesHtml += `<button class="page-num ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) pagesHtml += `<span class="page-dots">...</span>`;
        pagesHtml += `<button class="page-num" data-page="${totalPages}">${totalPages}</button>`;
    }
    
    pageNumbers.innerHTML = pagesHtml;
    
    document.querySelectorAll('.page-num').forEach(btn => {
        btn.addEventListener('click', () => {
            currentPage = parseInt(btn.dataset.page);
            renderTable();
        });
    });
}

function updateSelectAllState() {
    const checkboxes = document.querySelectorAll('.record-checkbox');
    const checked = document.querySelectorAll('.record-checkbox:checked');
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = checkboxes.length > 0 && checkboxes.length === checked.length;
        selectAllCheckbox.indeterminate = checked.length > 0 && checked.length < checkboxes.length;
    }
}

// View details from backend
window.viewDetails = async function(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/history/${id}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.record) {
                showDetailModal(data.record);
                return;
            }
        }
        // Fallback: find in local history
        const record = scanHistory.find(r => r.id === id);
        if (record) {
            showDetailModal(record);
        } else {
            showToast('Record not found', 'error');
        }
    } catch (error) {
        console.error('Error fetching detail:', error);
        const record = scanHistory.find(r => r.id === id);
        if (record) {
            showDetailModal(record);
        }
    }
};

// Show detail modal
function showDetailModal(record) {
    const modalBody = document.getElementById('modalBody');
    if (!modalBody) return;
    
    modalBody.innerHTML = `
        <div class="detail-section">
            <h3>${record.disease}</h3>
            <div class="detail-row"><span class="detail-label">Scan Date:</span><span class="detail-value">${formatDate(record.date)}</span></div>
            <div class="detail-row"><span class="detail-label">Confidence:</span><span class="detail-value">${record.confidence}%</span></div>
            <div class="detail-row"><span class="detail-label">Severity:</span><span class="detail-value severity-badge ${record.severity.toLowerCase()}">${record.severity}</span></div>
            <div class="detail-section-title"><i class="fas fa-flask"></i> Chemical Treatment</div>
            <div class="detail-text">${record.chemical_treatment}</div>
            <div class="detail-section-title"><i class="fas fa-leaf"></i> Organic Treatment</div>
            <div class="detail-text">${record.organic_treatment}</div>
            <div class="detail-section-title"><i class="fas fa-tractor"></i> Cultural Practices</div>
            <div class="detail-text">${record.cultural_practices}</div>
            <div class="detail-section-title"><i class="fas fa-shield-alt"></i> Prevention Tips</div>
            <div class="detail-text">${record.prevention_tips}</div>
        </div>
    `;
    
    const modal = document.getElementById('detailModal');
    if (modal) modal.style.display = 'flex';
    currentDeleteId = record.id;
}

// Confirm delete
window.confirmDelete = function(id) {
    currentDeleteId = id;
    const modal = document.getElementById('deleteModal');
    if (modal) modal.style.display = 'flex';
};

// Delete record from backend
async function deleteRecord() {
    if (!currentDeleteId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/history/${currentDeleteId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Remove from local history
            scanHistory = scanHistory.filter(r => r.id !== currentDeleteId);
            localStorage.setItem('scanHistory', JSON.stringify(scanHistory));
            applyFilters();
            showToast('Record deleted successfully', 'success');
        } else {
            // Fallback: remove from local only
            scanHistory = scanHistory.filter(r => r.id !== currentDeleteId);
            localStorage.setItem('scanHistory', JSON.stringify(scanHistory));
            applyFilters();
            showToast('Record deleted (offline mode)', 'success');
        }
    } catch (error) {
        // Fallback: remove from local only
        scanHistory = scanHistory.filter(r => r.id !== currentDeleteId);
        localStorage.setItem('scanHistory', JSON.stringify(scanHistory));
        applyFilters();
        showToast('Record deleted', 'success');
    }
    
    const modal = document.getElementById('deleteModal');
    if (modal) modal.style.display = 'none';
    currentDeleteId = null;
}

// Delete selected records
async function deleteSelected() {
    const selectedIds = Array.from(document.querySelectorAll('.record-checkbox:checked')).map(cb => parseInt(cb.dataset.id));
    if (selectedIds.length === 0) {
        showToast('No records selected', 'warning');
        return;
    }
    
    if (!confirm(`Delete ${selectedIds.length} record(s)? This cannot be undone.`)) return;
    
    try {
        // Try batch delete API
        const response = await fetch(`${API_BASE_URL}/history/batch/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ record_ids: selectedIds })
        });
        
        if (response.ok) {
            scanHistory = scanHistory.filter(r => !selectedIds.includes(r.id));
            localStorage.setItem('scanHistory', JSON.stringify(scanHistory));
            applyFilters();
            showToast(`${selectedIds.length} record(s) deleted`, 'success');
        } else {
            throw new Error('Batch delete failed');
        }
    } catch (error) {
        // Fallback: delete one by one
        selectedIds.forEach(id => {
            scanHistory = scanHistory.filter(r => r.id !== id);
        });
        localStorage.setItem('scanHistory', JSON.stringify(scanHistory));
        applyFilters();
        showToast(`${selectedIds.length} record(s) deleted`, 'success');
    }
}

// Export CSV from backend
async function exportToCSV() {
    if (filteredHistory.length === 0) {
        showToast('No data to export', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/report/csv`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                report_type: 'history',
                history: filteredHistory 
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `farmintel_history_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('CSV exported successfully', 'success');
            return;
        }
        throw new Error('CSV export failed');
    } catch (error) {
        // Fallback: local CSV generation
        const headers = ['Disease', 'Scan Date', 'Confidence (%)', 'Severity', 'Chemical Treatment', 'Organic Treatment', 'Cultural Practices', 'Prevention Tips'];
        const rows = filteredHistory.map(r => [r.disease, r.date, r.confidence, r.severity, r.chemical_treatment, r.organic_treatment, r.cultural_practices, r.prevention_tips]);
        const csvContent = [headers, ...rows].map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `farmintel_history_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('CSV exported (offline mode)', 'success');
    }
}

// Export PDF
async function exportToPDF() {
    if (filteredHistory.length === 0) {
        showToast('No data to export', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/report/pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                report_type: 'history',
                history: filteredHistory 
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `farmintel_report_${new Date().toISOString().split('T')[0]}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('PDF exported successfully', 'success');
            return;
        }
        throw new Error('PDF export failed');
    } catch (error) {
        // Fallback: print window
        const printWindow = window.open('', '_blank');
        if (!printWindow) {
            showToast('Please allow popups to export PDF', 'error');
            return;
        }
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>FarmIntel AI - Scan History</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 40px; }
                    h1 { color: #4F46E5; }
                    .header { text-align: center; margin-bottom: 30px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background: #f0f0f0; font-weight: bold; }
                    .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #666; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>FarmIntel AI - Scan History Report</h1>
                    <p>Generated: ${new Date().toLocaleString()}</p>
                    <p>Total Records: ${filteredHistory.length}</p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Disease</th>
                            <th>Scan Date</th>
                            <th>Confidence</th>
                            <th>Severity</th>
                            <th>Treatment</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filteredHistory.map(r => `
                            <tr>
                                <td>${r.disease}</td>
                                <td>${formatDate(r.date)}</td>
                                <td>${r.confidence}%</td>
                                <td>${r.severity}</td>
                                <td>${r.chemical_treatment.substring(0, 60)}...</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <div class="footer">
                    <p>FarmIntel AI - Empowering Farmers with AI Technology</p>
                </div>
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        showToast('PDF preview opened. Use print to save as PDF.', 'info');
    }
}

// Event Listeners
if (searchInput) searchInput.addEventListener('input', applyFilters);
if (severityFilter) severityFilter.addEventListener('change', applyFilters);
if (dateFilter) dateFilter.addEventListener('change', applyFilters);
if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        if (severityFilter) severityFilter.value = 'all';
        if (dateFilter) dateFilter.value = 'all';
        applyFilters();
        showToast('Filters cleared', 'info');
    });
}
if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', (e) => {
        document.querySelectorAll('.record-checkbox').forEach(cb => cb.checked = e.target.checked);
    });
}
if (deleteAllBtn) deleteAllBtn.addEventListener('click', deleteSelected);
if (exportCsvBtn) exportCsvBtn.addEventListener('click', exportToCSV);
if (exportPdfBtn) exportPdfBtn.addEventListener('click', exportToPDF);

const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
const closeDetailModal = document.getElementById('closeDetailModal');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');

if (confirmDeleteBtn) confirmDeleteBtn.addEventListener('click', deleteRecord);
if (cancelDeleteBtn) cancelDeleteBtn.addEventListener('click', () => {
    const modal = document.getElementById('deleteModal');
    if (modal) modal.style.display = 'none';
});
if (closeDetailModal) closeDetailModal.addEventListener('click', () => {
    const modal = document.getElementById('detailModal');
    if (modal) modal.style.display = 'none';
});

// Modal close on outside click
window.onclick = (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
};

// Mobile sidebar
const mobileToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (mobileToggle) {
    mobileToggle.onclick = () => {
        if (sidebar) sidebar.classList.toggle('mobile-open');
        if (overlay) overlay.classList.toggle('active');
    };
}
if (overlay) {
    overlay.onclick = () => {
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (overlay) overlay.classList.remove('active');
    };
}

// Logout
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.onclick = () => {
        localStorage.clear();
        window.location.href = '../index.html';
    };
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
    themeToggle.onclick = () => {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        themeToggle.innerHTML = isDark ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        showToast(`${isDark ? 'Dark' : 'Light'} mode activated`, 'success');
    };
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
loadHistory();

// Auto-refresh every 30 seconds
setInterval(() => {
    if (document.visibilityState === 'visible') {
        fetchHistory();
    }
}, 30000);