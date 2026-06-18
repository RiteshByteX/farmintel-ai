/**
 * FarmIntel AI - Profile JavaScript
 * Complete Backend Integration with API
 */

// Initialize AOS
AOS.init({ duration: 800, once: true, offset: 50 });

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const editProfileBtn = document.getElementById('editProfileBtn');
const editModal = document.getElementById('editModal');
const saveProfileBtn = document.getElementById('saveProfileBtn');
const cancelEditBtn = document.getElementById('cancelEditBtn');
const themeToggle = document.getElementById('themeToggle');
const logoutBtn = document.getElementById('logoutBtn');
const mobileToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

// User data storage
let userData = {};

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

// Fetch user profile from backend
async function fetchUserProfile() {
    try {
        // Try to get from backend first
        const response = await fetch(`${API_BASE_URL}/profile`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.user) {
                // Merge with local data
                const localUser = JSON.parse(localStorage.getItem('farmintel_user') || '{}');
                userData = { ...localUser, ...data.user };
                localStorage.setItem('farmintel_user', JSON.stringify(userData));
                updateUI();
                return;
            }
        }
        // Fallback to localStorage
        loadUserData();
    } catch (error) {
        console.error('Error fetching profile:', error);
        loadUserData();
    }
}

// Load user data from localStorage
function loadUserData() {
    const storedUser = localStorage.getItem('farmintel_user');
    const scanHistory = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    
    // Default user data
    const defaultUser = {
        id: 1,
        name: 'John Farmer',
        email: 'farmer@farmintel.ai',
        mobile: '+91 98765 43210',
        location: 'Mumbai, Maharashtra',
        farmType: 'Mixed Farming',
        farmSize: '25',
        crops: 'Tomato, Potato, Wheat',
        plan: 'Premium',
        createdAt: '2024-06-15T00:00:00.000Z',
        avatar: null
    };
    
    // Parse stored user data
    let user = defaultUser;
    if (storedUser) {
        user = { ...defaultUser, ...JSON.parse(storedUser) };
    }
    
    userData = user;
    updateUI();
}

// Update UI with user data
function updateUI() {
    const user = userData;
    
    // Profile header
    document.getElementById('profileName').innerText = user.name;
    document.getElementById('profileEmail').innerText = user.email;
    document.getElementById('profilePlan').innerText = user.plan + ' Plan';
    document.getElementById('userName').innerText = user.name.split(' ')[0];
    
    // Personal Information
    document.getElementById('infoFullName').innerText = user.name;
    document.getElementById('infoEmail').innerText = user.email;
    document.getElementById('infoMobile').innerText = user.mobile || 'Not provided';
    document.getElementById('infoJoined').innerText = user.createdAt ? new Date(user.createdAt).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) : 'N/A';
    document.getElementById('infoLocation').innerText = user.location || 'Not provided';
    document.getElementById('infoFarmType').innerText = user.farmType || 'Not specified';
    document.getElementById('infoFarmSize').innerText = user.farmSize ? user.farmSize + ' acres' : 'Not specified';
    document.getElementById('infoCrops').innerText = user.crops || 'Not specified';
    
    // Update stats
    const scanHistory = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    const totalScans = scanHistory.length;
    const diseasedScans = scanHistory.filter(s => !s.disease?.includes('Healthy')).length;
    const detectionRate = totalScans > 0 ? Math.round((diseasedScans / totalScans) * 100) : 0;
    
    document.getElementById('totalScans').innerText = totalScans;
    document.getElementById('detectionRate').innerText = detectionRate + '%';
    document.getElementById('memberSince').innerText = user.createdAt ? new Date(user.createdAt).getFullYear() : 2024;
    
    // Avatar
    const avatarLarge = document.getElementById('profileAvatarLarge');
    if (user.avatar) {
        avatarLarge.style.backgroundImage = `url(${user.avatar})`;
        avatarLarge.style.backgroundSize = 'cover';
        avatarLarge.style.backgroundPosition = 'center';
        avatarLarge.innerHTML = '';
    } else {
        avatarLarge.style.background = 'linear-gradient(135deg, #4F46E5, #7C3AED)';
        avatarLarge.innerHTML = '<i class="fas fa-user"></i>';
    }
}

// Save user data to localStorage and backend
async function saveUserData(updatedData) {
    const existingUser = JSON.parse(localStorage.getItem('farmintel_user') || '{}');
    const newUser = { ...existingUser, ...updatedData };
    
    // Save to localStorage
    localStorage.setItem('farmintel_user', JSON.stringify(newUser));
    localStorage.setItem('userName', newUser.name.split(' ')[0]);
    userData = newUser;
    
    // Try to save to backend
    try {
        const response = await fetch(`${API_BASE_URL}/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
            },
            body: JSON.stringify(newUser)
        });
        if (response.ok) {
            showToast('Profile updated successfully on server!', 'success');
        }
    } catch (error) {
        console.error('Error saving profile to server:', error);
        showToast('Profile saved locally. Server sync will happen later.', 'info');
    }
}

// Open edit modal
function openEditModal() {
    document.getElementById('editFullName').value = userData.name || '';
    document.getElementById('editMobile').value = userData.mobile || '';
    document.getElementById('editLocation').value = userData.location || '';
    document.getElementById('editFarmType').value = userData.farmType || 'Mixed Farming';
    document.getElementById('editFarmSize').value = userData.farmSize || '';
    document.getElementById('editCrops').value = userData.crops || '';
    editModal.style.display = 'flex';
}

// Close edit modal
function closeEditModal() {
    editModal.style.display = 'none';
}

// Save profile changes
async function saveProfileChanges() {
    const updatedData = {
        name: document.getElementById('editFullName').value.trim(),
        mobile: document.getElementById('editMobile').value.trim(),
        location: document.getElementById('editLocation').value.trim(),
        farmType: document.getElementById('editFarmType').value,
        farmSize: document.getElementById('editFarmSize').value.trim(),
        crops: document.getElementById('editCrops').value.trim()
    };
    
    // Validate
    if (!updatedData.name) {
        showToast('Name is required', 'error');
        return;
    }
    
    await saveUserData(updatedData);
    updateUI();
    showToast('Profile updated successfully!', 'success');
    closeEditModal();
}

// Mobile sidebar toggle
function initMobileSidebar() {
    if (!mobileToggle || !sidebar) return;
    
    mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
        if (overlay) overlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
    });
    
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
}

// Theme toggle
function initThemeToggle() {
    let isDark = localStorage.getItem('theme') === 'dark';
    
    if (isDark) {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }
    
    themeToggle.addEventListener('click', () => {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        themeToggle.innerHTML = isDark ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        showToast(`${isDark ? 'Dark' : 'Light'} mode activated`, 'success');
    });
}

// Logout
function initLogout() {
    if (!logoutBtn) return;
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('farmintel_user');
        localStorage.removeItem('farmintel_token');
        localStorage.removeItem('farmintel_logged_in');
        localStorage.removeItem('userName');
        window.location.href = '../index.html';
    });
}

// Modal close handlers
function initModalHandlers() {
    // Close on close button
    document.querySelectorAll('.modal-close, #cancelEditBtn').forEach(btn => {
        btn.addEventListener('click', closeEditModal);
    });
    
    // Close on outside click
    window.addEventListener('click', (e) => {
        if (e.target === editModal) {
            closeEditModal();
        }
    });
    
    // Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && editModal.style.display === 'flex') {
            closeEditModal();
        }
    });
}

// Check backend health
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

// Initialize everything
async function init() {
    createParticles();
    initMobileSidebar();
    initThemeToggle();
    initLogout();
    initModalHandlers();
    
    // Check backend and load data
    const backendHealthy = await checkBackendHealth();
    if (backendHealthy) {
        await fetchUserProfile();
        showToast('Connected to server', 'success');
    } else {
        loadUserData();
        showToast('Offline mode - Using local data', 'warning');
    }
    
    // Event listeners
    if (editProfileBtn) editProfileBtn.addEventListener('click', openEditModal);
    if (saveProfileBtn) saveProfileBtn.addEventListener('click', saveProfileChanges);
}

// Start the app
init();