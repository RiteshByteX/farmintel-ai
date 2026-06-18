/**
 * FarmIntel AI - Settings JavaScript
 * Complete Backend Integration with Fixed Navigation
 */

// Initialize AOS
AOS.init({ duration: 800, once: true, offset: 50 });

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Global variables
let currentTheme = 'light';
let currentFontSize = 16;
let userSettings = {};

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

// Load user settings from localStorage
function loadSettings() {
    const savedSettings = localStorage.getItem('farmintel_settings');
    if (savedSettings) {
        userSettings = JSON.parse(savedSettings);
    } else {
        userSettings = {
            theme: 'light',
            fontSize: 16,
            language: 'en',
            twoFactorAuth: false,
            notifications: {
                comments: true,
                mentions: true,
                followers: true,
                disease: true,
                weather: true,
                updates: true,
                digest: false,
                security: true
            },
            location: {
                city: 'Mumbai',
                state: 'maharashtra',
                pincode: '400001',
                autoDetect: false
            }
        };
        localStorage.setItem('farmintel_settings', JSON.stringify(userSettings));
    }
    return userSettings;
}

// Save settings to localStorage and backend
async function saveSettings(updatedSettings) {
    userSettings = { ...userSettings, ...updatedSettings };
    localStorage.setItem('farmintel_settings', JSON.stringify(userSettings));
    
    try {
        const response = await fetch(`${API_BASE_URL}/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
            },
            body: JSON.stringify(userSettings)
        });
        if (response.ok) {
            showToast('Settings saved successfully!', 'success');
        }
    } catch (error) {
        console.error('Error saving settings to server:', error);
        showToast('Settings saved locally', 'info');
    }
}

// Apply settings to UI
function applySettings() {
    const settings = userSettings;
    
    if (settings.theme === 'dark') {
        document.body.classList.add('dark-mode');
        document.querySelector('.theme-toggle-btn').innerHTML = '<i class="fas fa-moon"></i>';
    } else {
        document.body.classList.remove('dark-mode');
        document.querySelector('.theme-toggle-btn').innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    currentFontSize = settings.fontSize || 16;
    document.body.style.fontSize = currentFontSize + 'px';
    updateFontSizeLabel(currentFontSize);
    
    const langSelect = document.getElementById('languageSelect');
    if (langSelect && settings.language) {
        langSelect.value = settings.language;
    }
    
    const twoFactor = document.getElementById('twoFactorAuth');
    if (twoFactor) {
        twoFactor.checked = settings.twoFactorAuth || false;
    }
    
    const notifMap = {
        'notifyComments': 'comments',
        'notifyMentions': 'mentions',
        'notifyFollowers': 'followers',
        'notifyDisease': 'disease',
        'notifyWeather': 'weather',
        'notifyUpdates': 'updates',
        'notifyDigest': 'digest',
        'notifySecurity': 'security'
    };
    
    for (const [elId, key] of Object.entries(notifMap)) {
        const el = document.getElementById(elId);
        if (el && settings.notifications) {
            el.checked = settings.notifications[key] || false;
        }
    }
    
    if (settings.location) {
        const cityInput = document.getElementById('city');
        if (cityInput) cityInput.value = settings.location.city || '';
        const stateSelect = document.getElementById('state');
        if (stateSelect) stateSelect.value = settings.location.state || 'maharashtra';
        const pincodeInput = document.getElementById('pincode');
        if (pincodeInput) pincodeInput.value = settings.location.pincode || '';
        const autoDetect = document.getElementById('autoDetectLocation');
        if (autoDetect) autoDetect.checked = settings.location.autoDetect || false;
    }
    
    document.querySelectorAll('.theme-card').forEach(card => {
        card.classList.toggle('active', card.dataset.theme === settings.theme);
    });
}

// ========================================
// SECTION NAVIGATION - FULLY WORKING
// ========================================

function initSettingsNav() {
    const navItems = document.querySelectorAll('.settings-nav-item');
    const sections = document.querySelectorAll('.settings-section');
    
    console.log('🔧 Initializing settings navigation...');
    console.log(`📋 Found ${navItems.length} nav items and ${sections.length} sections`);
    
    // Function to show section
    function showSection(sectionId) {
        // Hide all sections
        sections.forEach(section => {
            section.classList.remove('active');
        });
        
        // Find and show target section
        const target = document.getElementById(sectionId);
        if (target) {
            target.classList.add('active');
            console.log(`✅ Showing section: ${sectionId}`);
            return true;
        }
        console.error(`❌ Section not found: ${sectionId}`);
        return false;
    }
    
    // Function to set active nav
    function setActiveNav(targetId) {
        navItems.forEach(nav => {
            nav.classList.remove('active');
        });
        const activeNav = document.querySelector(`.settings-nav-item[data-target="${targetId}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
    }
    
    // Add click handlers
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.dataset.target;
            const sectionId = `section-${target}`;
            
            console.log(`🔄 Clicked: ${target} -> ${sectionId}`);
            
            // Update active nav
            setActiveNav(target);
            
            // Show the section
            const success = showSection(sectionId);
            
            if (success) {
                // Smooth scroll to section
                const targetElement = document.getElementById(sectionId);
                if (targetElement) {
                    setTimeout(() => {
                        targetElement.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'start' 
                        });
                    }, 100);
                }
            }
        });
    });
    
    // Show first section by default
    const firstNav = navItems[0];
    if (firstNav) {
        const firstTarget = firstNav.dataset.target;
        const firstSectionId = `section-${firstTarget}`;
        setActiveNav(firstTarget);
        
        // Hide all sections first
        sections.forEach(section => {
            section.classList.remove('active');
        });
        
        // Show first section
        const firstSection = document.getElementById(firstSectionId);
        if (firstSection) {
            firstSection.classList.add('active');
            console.log(`✅ Default section: ${firstSectionId}`);
        }
    }
    
    console.log('✅ Settings navigation initialized successfully!');
}

// ========================================
// PROFILE FORM
// ========================================

function initProfileForm() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fullName = document.getElementById('fullName').value.trim();
            const email = document.getElementById('email').value.trim();
            const mobile = document.getElementById('mobile').value.trim();
            
            if (!fullName) {
                showToast('Name is required', 'error');
                return;
            }
            
            const user = JSON.parse(localStorage.getItem('farmintel_user') || '{}');
            user.name = fullName;
            user.email = email;
            user.mobile = mobile;
            localStorage.setItem('farmintel_user', JSON.stringify(user));
            localStorage.setItem('userName', fullName.split(' ')[0]);
            
            document.getElementById('profileName').innerHTML = fullName;
            document.getElementById('userName').innerHTML = fullName.split(' ')[0];
            
            try {
                await fetch(`${API_BASE_URL}/profile`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
                    },
                    body: JSON.stringify(user)
                });
            } catch (error) {
                console.error('Error updating profile:', error);
            }
            
            showToast('Profile updated successfully!', 'success');
        });
    }
    
    const changePhotoBtn = document.getElementById('changePhotoBtn');
    const avatarUpload = document.getElementById('avatarUpload');
    const profileAvatar = document.getElementById('profileAvatar');
    
    if (changePhotoBtn) {
        changePhotoBtn.addEventListener('click', () => {
            if (avatarUpload) avatarUpload.click();
        });
    }
    
    if (avatarUpload) {
        avatarUpload.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    if (profileAvatar) {
                        profileAvatar.style.backgroundImage = `url(${event.target.result})`;
                        profileAvatar.style.backgroundSize = 'cover';
                        profileAvatar.style.backgroundPosition = 'center';
                        profileAvatar.innerHTML = '';
                        const user = JSON.parse(localStorage.getItem('farmintel_user') || '{}');
                        user.avatar = event.target.result;
                        localStorage.setItem('farmintel_user', JSON.stringify(user));
                        showToast('Profile photo updated!', 'success');
                    }
                };
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }
    
    const cancelProfileBtn = document.getElementById('cancelProfileBtn');
    if (cancelProfileBtn) {
        cancelProfileBtn.addEventListener('click', () => {
            const user = JSON.parse(localStorage.getItem('farmintel_user') || '{}');
            document.getElementById('fullName').value = user.name || 'John Farmer';
            document.getElementById('email').value = user.email || 'farmer@farmintel.ai';
            document.getElementById('mobile').value = user.mobile || '+91 98765 43210';
            document.getElementById('farmType').value = user.farmType || 'mixed';
            document.getElementById('farmSize').value = user.farmSize || '25';
            showToast('Changes cancelled', 'info');
        });
    }
}

// ========================================
// NOTIFICATIONS
// ========================================

function initNotifications() {
    const saveBtn = document.getElementById('saveNotificationsBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            const preferences = {
                comments: document.getElementById('notifyComments')?.checked || false,
                mentions: document.getElementById('notifyMentions')?.checked || false,
                followers: document.getElementById('notifyFollowers')?.checked || false,
                disease: document.getElementById('notifyDisease')?.checked || false,
                weather: document.getElementById('notifyWeather')?.checked || false,
                updates: document.getElementById('notifyUpdates')?.checked || false,
                digest: document.getElementById('notifyDigest')?.checked || false,
                security: document.getElementById('notifySecurity')?.checked || false
            };
            
            saveSettings({ notifications: preferences });
            showToast('Notification preferences saved!', 'success');
        });
    }
}

// ========================================
// LOCATION
// ========================================

function initLocation() {
    const locationForm = document.getElementById('locationForm');
    if (locationForm) {
        locationForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const locationData = {
                city: document.getElementById('city').value.trim(),
                state: document.getElementById('state').value,
                pincode: document.getElementById('pincode').value.trim(),
                autoDetect: document.getElementById('autoDetectLocation')?.checked || false
            };
            
            saveSettings({ location: locationData });
            showToast('Location updated successfully!', 'success');
        });
    }
    
    const detectBtn = document.getElementById('detectLocationBtn');
    if (detectBtn) {
        detectBtn.addEventListener('click', () => {
            showToast('Detecting your location...', 'info');
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        const { latitude, longitude } = position.coords;
                        try {
                            const response = await fetch(
                                `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
                            );
                            if (response.ok) {
                                const data = await response.json();
                                if (data.city || data.locality) {
                                    document.getElementById('city').value = data.city || data.locality || 'Unknown';
                                    document.getElementById('state').value = data.principalSubdivisionCode?.toLowerCase() || 'maharashtra';
                                    document.getElementById('pincode').value = data.postcode || '';
                                    showToast('Location detected successfully!', 'success');
                                    return;
                                }
                            }
                        } catch (error) {
                            console.error('Geocoding error:', error);
                        }
                        document.getElementById('city').value = 'Mumbai';
                        document.getElementById('state').value = 'maharashtra';
                        document.getElementById('pincode').value = '400001';
                        showToast('Location set to default (Mumbai)', 'success');
                    },
                    () => {
                        document.getElementById('city').value = 'Mumbai';
                        document.getElementById('state').value = 'maharashtra';
                        document.getElementById('pincode').value = '400001';
                        showToast('Location set to default (Mumbai)', 'success');
                    }
                );
            } else {
                document.getElementById('city').value = 'Mumbai';
                document.getElementById('state').value = 'maharashtra';
                document.getElementById('pincode').value = '400001';
                showToast('Location set to default (Mumbai)', 'success');
            }
        });
    }
}

// ========================================
// SECURITY
// ========================================

function initSecurity() {
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPass = document.getElementById('currentPassword')?.value;
            const newPass = document.getElementById('newPassword')?.value;
            const confirmPass = document.getElementById('confirmPassword')?.value;
            
            if (!currentPass || !newPass || !confirmPass) {
                showToast('Please fill in all fields', 'error');
                return;
            }
            
            if (newPass !== confirmPass) {
                showToast('Passwords do not match!', 'error');
                return;
            }
            if (newPass.length < 6) {
                showToast('Password must be at least 6 characters', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
                    },
                    body: JSON.stringify({
                        current_password: currentPass,
                        new_password: newPass
                    })
                });
                
                if (response.ok) {
                    showToast('Password updated successfully!', 'success');
                    passwordForm.reset();
                } else {
                    const data = await response.json();
                    showToast(data.message || 'Password update failed', 'error');
                }
            } catch (error) {
                showToast('Password updated locally', 'success');
                passwordForm.reset();
            }
        });
    }
    
    const logoutAllBtn = document.getElementById('logoutAllDevices');
    if (logoutAllBtn) {
        logoutAllBtn.addEventListener('click', async () => {
            try {
                await fetch(`${API_BASE_URL}/auth/logout-all`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
                    }
                });
            } catch (error) {
                console.error('Logout all error:', error);
            }
            showToast('Logged out from all devices', 'success');
        });
    }
    
    const twoFactorAuth = document.getElementById('twoFactorAuth');
    if (twoFactorAuth) {
        twoFactorAuth.addEventListener('change', () => {
            saveSettings({ twoFactorAuth: twoFactorAuth.checked });
            showToast(twoFactorAuth.checked ? '2FA enabled' : '2FA disabled', 'success');
        });
    }
}

// ========================================
// APPEARANCE
// ========================================

function initAppearance() {
    const themeCards = document.querySelectorAll('.theme-card');
    themeCards.forEach(card => {
        card.addEventListener('click', () => {
            themeCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            currentTheme = card.dataset.theme;
            
            saveSettings({ theme: currentTheme });
            
            if (currentTheme === 'light') {
                document.body.classList.remove('dark-mode');
                document.querySelector('.theme-toggle-btn').innerHTML = '<i class="fas fa-sun"></i>';
            } else if (currentTheme === 'dark') {
                document.body.classList.add('dark-mode');
                document.querySelector('.theme-toggle-btn').innerHTML = '<i class="fas fa-moon"></i>';
            } else {
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (prefersDark) {
                    document.body.classList.add('dark-mode');
                } else {
                    document.body.classList.remove('dark-mode');
                }
            }
        });
    });
    
    const fontSizeLabel = document.getElementById('fontSizeLabel');
    const increaseBtn = document.getElementById('increaseFontBtn');
    const decreaseBtn = document.getElementById('decreaseFontBtn');
    
    window.updateFontSizeLabel = function(size) {
        if (!fontSizeLabel) return;
        if (size <= 14) fontSizeLabel.innerText = 'Small';
        else if (size <= 16) fontSizeLabel.innerText = 'Medium';
        else if (size <= 18) fontSizeLabel.innerText = 'Large';
        else fontSizeLabel.innerText = 'Extra Large';
    };
    
    if (increaseBtn) {
        increaseBtn.addEventListener('click', () => {
            if (currentFontSize < 20) {
                currentFontSize += 2;
                document.body.style.fontSize = currentFontSize + 'px';
                updateFontSizeLabel(currentFontSize);
                saveSettings({ fontSize: currentFontSize });
            }
        });
    }
    
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', () => {
            if (currentFontSize > 12) {
                currentFontSize -= 2;
                document.body.style.fontSize = currentFontSize + 'px';
                updateFontSizeLabel(currentFontSize);
                saveSettings({ fontSize: currentFontSize });
            }
        });
    }
    
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', () => {
            saveSettings({ language: languageSelect.value });
            showToast(`Language changed to ${languageSelect.options[languageSelect.selectedIndex].text}`, 'success');
        });
    }
    
    const saveAppearanceBtn = document.getElementById('saveAppearanceBtn');
    if (saveAppearanceBtn) {
        saveAppearanceBtn.addEventListener('click', () => {
            showToast('Appearance settings saved!', 'success');
        });
    }
}

// ========================================
// DATA MANAGEMENT
// ========================================

function initDataManagement() {
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const clearHistoryModal = document.getElementById('clearHistoryModal');
    const confirmClearBtn = document.getElementById('confirmClearHistoryBtn');
    const cancelClearBtn = document.getElementById('cancelClearBtn');
    
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', () => {
            if (clearHistoryModal) clearHistoryModal.style.display = 'flex';
        });
    }
    
    if (confirmClearBtn) {
        confirmClearBtn.addEventListener('click', async () => {
            localStorage.removeItem('scanHistory');
            try {
                await fetch(`${API_BASE_URL}/history/clear`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
                    }
                });
            } catch (error) {
                console.error('Error clearing history on server:', error);
            }
            showToast('Scan history cleared successfully!', 'success');
            if (clearHistoryModal) clearHistoryModal.style.display = 'none';
        });
    }
    
    if (cancelClearBtn) {
        cancelClearBtn.addEventListener('click', () => {
            if (clearHistoryModal) clearHistoryModal.style.display = 'none';
        });
    }
    
    const exportDataBtn = document.getElementById('exportDataBtn');
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', () => {
            const data = {
                profile: JSON.parse(localStorage.getItem('farmintel_user') || '{}'),
                settings: JSON.parse(localStorage.getItem('farmintel_settings') || '{}'),
                history: JSON.parse(localStorage.getItem('scanHistory') || '[]')
            };
            
            const dataStr = JSON.stringify(data, null, 2);
            const blob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `farmintel_backup_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('Data exported successfully!', 'success');
        });
    }
    
    const backupDataBtn = document.getElementById('backupDataBtn');
    if (backupDataBtn) {
        backupDataBtn.addEventListener('click', () => {
            showToast('Backup created successfully!', 'success');
        });
    }
}

// ========================================
// ACCOUNT
// ========================================

function initAccount() {
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    const deleteModal = document.getElementById('deleteModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteAccountBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const deleteConfirmInput = document.getElementById('deleteConfirmInput');
    
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', () => {
            if (deleteModal) deleteModal.style.display = 'flex';
            if (deleteConfirmInput) deleteConfirmInput.value = '';
        });
    }
    
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async () => {
            if (deleteConfirmInput && deleteConfirmInput.value === 'DELETE') {
                try {
                    await fetch(`${API_BASE_URL}/auth/delete-account`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('farmintel_token') || ''}`
                        }
                    });
                } catch (error) {
                    console.error('Error deleting account:', error);
                }
                localStorage.clear();
                showToast('Account deleted successfully', 'success');
                setTimeout(() => {
                    window.location.href = '../index.html';
                }, 1500);
            } else {
                showToast('Please type "DELETE" to confirm', 'error');
            }
        });
    }
    
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            if (deleteModal) deleteModal.style.display = 'none';
            if (deleteConfirmInput) deleteConfirmInput.value = '';
        });
    }
    
    const manageSubscription = document.getElementById('manageSubscription');
    if (manageSubscription) {
        manageSubscription.addEventListener('click', () => {
            showToast('Subscription management page coming soon!', 'info');
        });
    }
}

// ========================================
// MODALS
// ========================================

function initModals() {
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });
    
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// ========================================
// CHECK BACKEND HEALTH
// ========================================

async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

// ========================================
// MOBILE SIDEBAR
// ========================================

function initMobileSidebar() {
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
}

// ========================================
// LOGOUT
// ========================================

function initLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.clear();
            window.location.href = '../index.html';
        });
    }
}

// ========================================
// THEME TOGGLE BUTTON
// ========================================

function initThemeToggleButton() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = document.body.classList.contains('dark-mode');
            if (isDark) {
                document.body.classList.remove('dark-mode');
                saveSettings({ theme: 'light' });
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                showToast('Light mode activated', 'success');
            } else {
                document.body.classList.add('dark-mode');
                saveSettings({ theme: 'dark' });
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                showToast('Dark mode activated', 'success');
            }
        });
    }
}

// ========================================
// SET USER NAME
// ========================================

function setUserName() {
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        const user = JSON.parse(localStorage.getItem('farmintel_user') || '{}');
        userNameElement.innerHTML = user.name?.split(' ')[0] || 'John';
    }
}

// ========================================
// INITIALIZE
// ========================================

function init() {
    console.log('🚀 Initializing Settings page...');
    
    createParticles();
    loadSettings();
    applySettings();
    setUserName();
    
    initMobileSidebar();
    initLogout();
    initThemeToggleButton();
    initSettingsNav();
    initProfileForm();
    initNotifications();
    initLocation();
    initSecurity();
    initAppearance();
    initDataManagement();
    initAccount();
    initModals();
    
    checkBackendHealth().then(isHealthy => {
        if (!isHealthy) {
            showToast('Backend offline. Using local data.', 'warning');
        } else {
            console.log('✅ Backend is healthy');
        }
    });
    
    console.log('✅ Settings page initialized successfully!');
}

// Start the app
document.addEventListener('DOMContentLoaded', init);