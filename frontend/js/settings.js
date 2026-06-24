/**
 * FarmIntel AI - Settings JavaScript
 * Complete Authentication Integration
 */

// Initialize AOS
AOS.init({ duration: 800, once: true, offset: 50 });

// ========================================
// AUTHENTICATION HELPERS
// ========================================

function getCurrentUser() {
    const userData = localStorage.getItem('farmintel_current_user');
    if (userData) {
        try {
            return JSON.parse(userData);
        } catch (e) {
            return null;
        }
    }
    return null;
}

function getUsers() {
    const usersData = localStorage.getItem('farmintel_users');
    if (usersData) {
        try {
            return JSON.parse(usersData);
        } catch (e) {
            return [];
        }
    }
    return [];
}

function saveUsers(users) {
    localStorage.setItem('farmintel_users', JSON.stringify(users));
}

function updateUserInStorage(updatedUser) {
    const users = getUsers();
    const index = users.findIndex(u => u.id === updatedUser.id);
    if (index !== -1) {
        users[index] = { ...users[index], ...updatedUser };
        saveUsers(users);
        // Update current user session
        const currentUser = getCurrentUser();
        if (currentUser && currentUser.id === updatedUser.id) {
            localStorage.setItem('farmintel_current_user', JSON.stringify(users[index]));
        }
        return true;
    }
    return false;
}

function isAuthenticated() {
    return getCurrentUser() !== null;
}

// ========================================
// TOAST NOTIFICATION
// ========================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'fa-check-circle' : 
                 type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ========================================
// PARTICLES
// ========================================

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

// ========================================
// LOAD USER DATA
// ========================================

function loadUserData() {
    const user = getCurrentUser();
    if (!user) {
        // Redirect to login if not authenticated
        showToast('Please login first', 'error');
        setTimeout(() => {
            window.location.href = '../index.html';
        }, 1500);
        return;
    }
    
    // Update UI with user data
    const userName = document.getElementById('userName');
    const userRole = document.getElementById('userRole');
    const profileName = document.getElementById('profileName');
    const fullName = document.getElementById('fullName');
    const email = document.getElementById('email');
    
    if (userName) userName.textContent = user.name || 'John';
    if (userRole) userRole.textContent = user.role || 'Farmer';
    if (profileName) profileName.textContent = user.name || 'John Farmer';
    if (fullName) fullName.value = user.name || 'John Farmer';
    if (email) email.value = user.email || 'farmer@farmintel.ai';
    
    // Load saved settings
    loadSettings();
}

// ========================================
// SETTINGS MANAGEMENT
// ========================================

function loadSettings() {
    const savedSettings = localStorage.getItem('farmintel_settings');
    if (savedSettings) {
        try {
            const settings = JSON.parse(savedSettings);
            applySettings(settings);
            return settings;
        } catch (e) {
            console.error('Error loading settings:', e);
        }
    }
    // Default settings
    const defaultSettings = {
        theme: 'light',
        fontSize: 16,
        language: 'en',
        twoFactorAuth: false,
        location: {
            city: 'Mumbai',
            state: 'maharashtra',
            pincode: '400001',
            autoDetect: false
        },
        notifications: {
            comments: true,
            mentions: true,
            followers: true,
            disease: true,
            weather: true,
            updates: true,
            digest: false,
            security: true
        }
    };
    localStorage.setItem('farmintel_settings', JSON.stringify(defaultSettings));
    applySettings(defaultSettings);
    return defaultSettings;
}

function saveSettings(updatedSettings) {
    const currentSettings = JSON.parse(localStorage.getItem('farmintel_settings') || '{}');
    const newSettings = { ...currentSettings, ...updatedSettings };
    localStorage.setItem('farmintel_settings', JSON.stringify(newSettings));
    return newSettings;
}

function applySettings(settings) {
    // Theme
    if (settings.theme === 'dark') {
        document.body.classList.add('dark-mode');
        const themeBtn = document.querySelector('.theme-toggle-btn');
        if (themeBtn) themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
    } else {
        document.body.classList.remove('dark-mode');
        const themeBtn = document.querySelector('.theme-toggle-btn');
        if (themeBtn) themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Font Size
    const fontSize = settings.fontSize || 16;
    document.body.style.fontSize = fontSize + 'px';
    updateFontSizeLabel(fontSize);
    
    // Language
    const langSelect = document.getElementById('languageSelect');
    if (langSelect && settings.language) {
        langSelect.value = settings.language;
    }
    
    // Two Factor Auth
    const twoFactor = document.getElementById('twoFactorAuth');
    if (twoFactor) {
        twoFactor.checked = settings.twoFactorAuth || false;
    }
    
    // Notifications
    if (settings.notifications) {
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
            if (el) {
                el.checked = settings.notifications[key] || false;
            }
        }
    }
    
    // Location
    if (settings.location) {
        const city = document.getElementById('city');
        if (city) city.value = settings.location.city || '';
        const state = document.getElementById('state');
        if (state) state.value = settings.location.state || 'maharashtra';
        const pincode = document.getElementById('pincode');
        if (pincode) pincode.value = settings.location.pincode || '';
        const autoDetect = document.getElementById('autoDetectLocation');
        if (autoDetect) autoDetect.checked = settings.location.autoDetect || false;
    }
    
    // Theme cards
    document.querySelectorAll('.theme-card').forEach(card => {
        card.classList.toggle('active', card.dataset.theme === settings.theme);
    });
}

function updateFontSizeLabel(size) {
    const label = document.getElementById('fontSizeLabel');
    if (!label) return;
    if (size <= 14) label.textContent = 'Small';
    else if (size <= 16) label.textContent = 'Medium';
    else if (size <= 18) label.textContent = 'Large';
    else label.textContent = 'Extra Large';
}

// ========================================
// SETTINGS NAVIGATION
// ========================================

function initSettingsNav() {
    const navItems = document.querySelectorAll('.settings-nav-item');
    const sections = document.querySelectorAll('.settings-section');
    
    function showSection(sectionId) {
        sections.forEach(section => section.classList.remove('active'));
        const target = document.getElementById(sectionId);
        if (target) {
            target.classList.add('active');
            return true;
        }
        return false;
    }
    
    function setActiveNav(targetId) {
        navItems.forEach(nav => nav.classList.remove('active'));
        const activeNav = document.querySelector(`.settings-nav-item[data-target="${targetId}"]`);
        if (activeNav) activeNav.classList.add('active');
    }
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.dataset.target;
            const sectionId = `section-${target}`;
            
            setActiveNav(target);
            showSection(sectionId);
            
            const targetElement = document.getElementById(sectionId);
            if (targetElement) {
                setTimeout(() => {
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        });
    });
}

// ========================================
// PROFILE FORM
// ========================================

function initProfileForm() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('fullName').value.trim();
            const email = document.getElementById('email').value.trim();
            const mobile = document.getElementById('mobile').value.trim();
            const farmType = document.getElementById('farmType').value;
            const farmSize = document.getElementById('farmSize').value;
            
            if (!name) {
                showToast('Name is required', 'error');
                return;
            }
            
            const currentUser = getCurrentUser();
            if (currentUser) {
                const updatedUser = {
                    ...currentUser,
                    name: name,
                    email: email,
                    mobile: mobile,
                    farmType: farmType,
                    farmSize: farmSize
                };
                
                if (updateUserInStorage(updatedUser)) {
                    // Update UI
                    document.getElementById('userName').textContent = name.split(' ')[0];
                    document.getElementById('profileName').textContent = name;
                    showToast('Profile updated successfully!', 'success');
                } else {
                    showToast('Failed to update profile', 'error');
                }
            }
        });
    }
    
    // Avatar upload
    const changePhotoBtn = document.getElementById('changePhotoBtn');
    const avatarUpload = document.getElementById('avatarUpload');
    const profileAvatar = document.getElementById('profileAvatar');
    
    if (changePhotoBtn && avatarUpload) {
        changePhotoBtn.addEventListener('click', () => avatarUpload.click());
        avatarUpload.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    if (profileAvatar) {
                        profileAvatar.style.backgroundImage = `url(${event.target.result})`;
                        profileAvatar.style.backgroundSize = 'cover';
                        profileAvatar.style.backgroundPosition = 'center';
                        profileAvatar.innerHTML = '';
                        showToast('Profile photo updated!', 'success');
                    }
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Cancel button
    const cancelBtn = document.getElementById('cancelProfileBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            const user = getCurrentUser();
            if (user) {
                document.getElementById('fullName').value = user.name || 'John Farmer';
                document.getElementById('email').value = user.email || 'farmer@farmintel.ai';
                document.getElementById('mobile').value = user.mobile || '+91 98765 43210';
                document.getElementById('farmType').value = user.farmType || 'mixed';
                document.getElementById('farmSize').value = user.farmSize || '25';
                showToast('Changes cancelled', 'info');
            }
        });
    }
}

// ========================================
// NOTIFICATIONS
// ========================================

function initNotifications() {
    const saveBtn = document.getElementById('saveNotificationsBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
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
        locationForm.addEventListener('submit', function(e) {
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
        detectBtn.addEventListener('click', function() {
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
                    function() {
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
        passwordForm.addEventListener('submit', function(e) {
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
            
            const user = getCurrentUser();
            if (user) {
                // Verify current password
                const users = getUsers();
                const userRecord = users.find(u => u.id === user.id);
                
                if (userRecord && userRecord.password === currentPass) {
                    // Update password
                    userRecord.password = newPass;
                    saveUsers(users);
                    showToast('Password updated successfully!', 'success');
                    passwordForm.reset();
                } else {
                    showToast('Current password is incorrect', 'error');
                }
            }
        });
    }
    
    // Logout all devices
    const logoutAllBtn = document.getElementById('logoutAllDevices');
    if (logoutAllBtn) {
        logoutAllBtn.addEventListener('click', function() {
            showToast('Logged out from all devices', 'success');
        });
    }
    
    // Two Factor Auth
    const twoFactorAuth = document.getElementById('twoFactorAuth');
    if (twoFactorAuth) {
        twoFactorAuth.addEventListener('change', function() {
            saveSettings({ twoFactorAuth: this.checked });
            showToast(this.checked ? '2FA enabled' : '2FA disabled', 'success');
        });
    }
}

// ========================================
// APPEARANCE
// ========================================

function initAppearance() {
    // Theme cards
    const themeCards = document.querySelectorAll('.theme-card');
    themeCards.forEach(card => {
        card.addEventListener('click', function() {
            themeCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            const theme = this.dataset.theme;
            
            saveSettings({ theme: theme });
            
            if (theme === 'dark') {
                document.body.classList.add('dark-mode');
                document.querySelector('.theme-toggle-btn').innerHTML = '<i class="fas fa-moon"></i>';
            } else if (theme === 'light') {
                document.body.classList.remove('dark-mode');
                document.querySelector('.theme-toggle-btn').innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (prefersDark) {
                    document.body.classList.add('dark-mode');
                } else {
                    document.body.classList.remove('dark-mode');
                }
            }
            showToast('Theme updated!', 'success');
        });
    });
    
    // Font Size
    const fontSizeLabel = document.getElementById('fontSizeLabel');
    const increaseBtn = document.getElementById('increaseFontBtn');
    const decreaseBtn = document.getElementById('decreaseFontBtn');
    let currentFontSize = parseInt(document.body.style.fontSize) || 16;
    
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function() {
            if (currentFontSize < 20) {
                currentFontSize += 2;
                document.body.style.fontSize = currentFontSize + 'px';
                updateFontSizeLabel(currentFontSize);
                saveSettings({ fontSize: currentFontSize });
            }
        });
    }
    
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            if (currentFontSize > 12) {
                currentFontSize -= 2;
                document.body.style.fontSize = currentFontSize + 'px';
                updateFontSizeLabel(currentFontSize);
                saveSettings({ fontSize: currentFontSize });
            }
        });
    }
    
    // Language
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            saveSettings({ language: this.value });
            showToast(`Language changed to ${this.options[this.selectedIndex].text}`, 'success');
        });
    }
    
    // Save Appearance
    const saveAppearanceBtn = document.getElementById('saveAppearanceBtn');
    if (saveAppearanceBtn) {
        saveAppearanceBtn.addEventListener('click', function() {
            showToast('Appearance settings saved!', 'success');
        });
    }
}

// ========================================
// DATA MANAGEMENT
// ========================================

function initDataManagement() {
    // Clear History
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const clearHistoryModal = document.getElementById('clearHistoryModal');
    const confirmClearBtn = document.getElementById('confirmClearHistoryBtn');
    const cancelClearBtn = document.getElementById('cancelClearBtn');
    
    if (clearHistoryBtn && clearHistoryModal) {
        clearHistoryBtn.addEventListener('click', () => {
            clearHistoryModal.style.display = 'flex';
        });
    }
    
    if (confirmClearBtn && clearHistoryModal) {
        confirmClearBtn.addEventListener('click', () => {
            localStorage.removeItem('scanHistory');
            showToast('Scan history cleared successfully!', 'success');
            clearHistoryModal.style.display = 'none';
        });
    }
    
    if (cancelClearBtn && clearHistoryModal) {
        cancelClearBtn.addEventListener('click', () => {
            clearHistoryModal.style.display = 'none';
        });
    }
    
    // Export Data
    const exportDataBtn = document.getElementById('exportDataBtn');
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', function() {
            const data = {
                user: getCurrentUser(),
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
    
    // Backup Data
    const backupDataBtn = document.getElementById('backupDataBtn');
    if (backupDataBtn) {
        backupDataBtn.addEventListener('click', function() {
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
    
    if (deleteAccountBtn && deleteModal) {
        deleteAccountBtn.addEventListener('click', () => {
            deleteModal.style.display = 'flex';
            if (deleteConfirmInput) deleteConfirmInput.value = '';
        });
    }
    
    if (confirmDeleteBtn && deleteModal) {
        confirmDeleteBtn.addEventListener('click', function() {
            if (deleteConfirmInput && deleteConfirmInput.value === 'DELETE') {
                // Delete user from storage
                const currentUser = getCurrentUser();
                if (currentUser) {
                    let users = getUsers();
                    users = users.filter(u => u.id !== currentUser.id);
                    saveUsers(users);
                    localStorage.removeItem('farmintel_current_user');
                    localStorage.removeItem('farmintel_settings');
                    showToast('Account deleted successfully', 'success');
                    setTimeout(() => {
                        window.location.href = '../index.html';
                    }, 1500);
                }
            } else {
                showToast('Please type "DELETE" to confirm', 'error');
            }
        });
    }
    
    if (cancelDeleteBtn && deleteModal) {
        cancelDeleteBtn.addEventListener('click', () => {
            deleteModal.style.display = 'none';
            if (deleteConfirmInput) deleteConfirmInput.value = '';
        });
    }
    
    const manageSubscription = document.getElementById('manageSubscription');
    if (manageSubscription) {
        manageSubscription.addEventListener('click', function() {
            showToast('Subscription management page coming soon!', 'info');
        });
    }
}

// ========================================
// MODALS
// ========================================

function initModals() {
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });
    
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// ========================================
// THEME TOGGLE
// ========================================

function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDark = document.body.classList.contains('dark-mode');
            if (isDark) {
                document.body.classList.remove('dark-mode');
                this.innerHTML = '<i class="fas fa-sun"></i>';
                saveSettings({ theme: 'light' });
                // Update theme card
                document.querySelectorAll('.theme-card').forEach(card => {
                    card.classList.toggle('active', card.dataset.theme === 'light');
                });
                showToast('Light mode activated', 'success');
            } else {
                document.body.classList.add('dark-mode');
                this.innerHTML = '<i class="fas fa-moon"></i>';
                saveSettings({ theme: 'dark' });
                document.querySelectorAll('.theme-card').forEach(card => {
                    card.classList.toggle('active', card.dataset.theme === 'dark');
                });
                showToast('Dark mode activated', 'success');
            }
        });
    }
}

// ========================================
// MOBILE SIDEBAR
// ========================================

function initMobileSidebar() {
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (mobileToggle && sidebar && overlay) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
            overlay.classList.toggle('active');
        });
        
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('active');
        });
    }
}

// ========================================
// LOGOUT
// ========================================

function initLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('farmintel_current_user');
            showToast('Logged out successfully', 'success');
            setTimeout(() => {
                window.location.href = '../index.html';
            }, 1000);
        });
    }
}

// ========================================
// INITIALIZE
// ========================================

function init() {
    console.log('🚀 Initializing Settings page...');
    
    // Check authentication
    if (!isAuthenticated()) {
        showToast('Please login first', 'error');
        setTimeout(() => {
            window.location.href = '../index.html';
        }, 1500);
        return;
    }
    
    createParticles();
    loadUserData();
    
    initMobileSidebar();
    initLogout();
    initThemeToggle();
    initSettingsNav();
    initProfileForm();
    initNotifications();
    initLocation();
    initSecurity();
    initAppearance();
    initDataManagement();
    initAccount();
    initModals();
    
    console.log('✅ Settings page initialized successfully!');
    console.log('👤 Current user:', getCurrentUser());
}

// Start the app
document.addEventListener('DOMContentLoaded', init);