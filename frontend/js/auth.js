/**
 * FarmIntel AI - Authentication Service
 * Complete auth functionality with session management
 */

// Auth Configuration
const AUTH_CONFIG = {
    STORAGE_KEYS: {
        USER: 'farmintel_user',
        TOKEN: 'farmintel_token',
        IS_LOGGED_IN: 'farmintel_logged_in',
        SESSION_EXPIRY: 'farmintel_session_expiry',
        REMEMBER_ME: 'farmintel_remember_me'
    },
    SESSION_DURATION: {
        REMEMBER: 30 * 24 * 60 * 60 * 1000, // 30 days
        DEFAULT: 24 * 60 * 60 * 1000 // 24 hours
    }
};

// Demo Users Database (for testing without backend)
const DEMO_USERS = {
    'admin@farmintel.ai': {
        id: 1,
        name: 'Admin User',
        email: 'admin@farmintel.ai',
        password: 'admin123',
        role: 'admin',
        plan: 'premium',
        avatar: null,
        createdAt: '2024-01-01'
    },
    'farmer@farmintel.ai': {
        id: 2,
        name: 'John Farmer',
        email: 'farmer@farmintel.ai',
        password: 'farmer123',
        role: 'user',
        plan: 'premium',
        avatar: null,
        createdAt: '2024-06-01'
    },
    'demo@farmintel.ai': {
        id: 3,
        name: 'Demo User',
        email: 'demo@farmintel.ai',
        password: 'demo123',
        role: 'user',
        plan: 'basic',
        avatar: null,
        createdAt: '2024-06-10'
    }
};

// User Class
class User {
    constructor(data) {
        this.id = data.id;
        this.name = data.name;
        this.email = data.email;
        this.role = data.role || 'user';
        this.plan = data.plan || 'basic';
        this.avatar = data.avatar || null;
        this.createdAt = data.createdAt || new Date().toISOString();
        this.lastLogin = data.lastLogin || null;
        this.preferences = data.preferences || {
            theme: 'light',
            language: 'en',
            fontSize: 16,
            notifications: {
                email: true,
                push: true,
                diseaseAlerts: true,
                weatherAlerts: true
            }
        };
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            email: this.email,
            role: this.role,
            plan: this.plan,
            avatar: this.avatar,
            createdAt: this.createdAt,
            lastLogin: this.lastLogin,
            preferences: this.preferences
        };
    }

    isAdmin() {
        return this.role === 'admin';
    }

    isPremium() {
        return this.plan === 'premium';
    }

    updatePreferences(preferences) {
        this.preferences = { ...this.preferences, ...preferences };
        this.save();
    }
}

// Authentication Service Class
class AuthService {
    constructor() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.sessionTimer = null;
        this.init();
    }

    /**
     * Initialize auth service
     */
    init() {
        this.loadSession();
        this.setupSessionCheck();
        this.setupActivityListeners();
    }

    /**
     * Load session from storage
     */
    loadSession() {
        const isLoggedIn = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.IS_LOGGED_IN);
        const userData = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.USER);
        const sessionExpiry = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.SESSION_EXPIRY);
        
        if (isLoggedIn === 'true' && userData && sessionExpiry) {
            // Check if session is expired
            if (new Date().getTime() < parseInt(sessionExpiry)) {
                this.currentUser = new User(JSON.parse(userData));
                this.isAuthenticated = true;
                this.startSessionTimer();
            } else {
                this.logout();
            }
        }
    }

    /**
     * Setup session expiry check
     */
    setupSessionCheck() {
        setInterval(() => {
            if (this.isAuthenticated) {
                const sessionExpiry = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.SESSION_EXPIRY);
                if (sessionExpiry && new Date().getTime() > parseInt(sessionExpiry)) {
                    this.logout();
                    this.dispatchEvent('sessionExpired');
                }
            }
        }, 60000); // Check every minute
    }

    /**
     * Setup activity listeners to extend session
     */
    setupActivityListeners() {
        const events = ['click', 'keypress', 'mousemove', 'scroll', 'touchstart'];
        events.forEach(event => {
            document.addEventListener(event, () => {
                if (this.isAuthenticated) {
                    this.extendSession();
                }
            });
        });
    }

    /**
     * Start session timer
     */
    startSessionTimer() {
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
        }
        
        this.sessionTimer = setInterval(() => {
            const rememberMe = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.REMEMBER_ME) === 'true';
            const duration = rememberMe ? AUTH_CONFIG.SESSION_DURATION.REMEMBER : AUTH_CONFIG.SESSION_DURATION.DEFAULT;
            const newExpiry = new Date().getTime() + duration;
            localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.SESSION_EXPIRY, newExpiry.toString());
        }, 30 * 60 * 1000); // Refresh expiry every 30 minutes
    }

    /**
     * Extend current session
     */
    extendSession() {
        if (this.isAuthenticated) {
            const rememberMe = localStorage.getItem(AUTH_CONFIG.STORAGE_KEYS.REMEMBER_ME) === 'true';
            const duration = rememberMe ? AUTH_CONFIG.SESSION_DURATION.REMEMBER : AUTH_CONFIG.SESSION_DURATION.DEFAULT;
            const newExpiry = new Date().getTime() + duration;
            localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.SESSION_EXPIRY, newExpiry.toString());
        }
    }

    /**
     * Login user
     * @param {string} email - User email
     * @param {string} password - User password
     * @param {boolean} rememberMe - Remember me flag
     * @returns {Promise} Login result
     */
    async login(email, password, rememberMe = false) {
        try {
            // Validate inputs
            if (!email || !password) {
                throw new Error('Email and password are required');
            }
            
            // Normalize email
            email = email.toLowerCase().trim();
            
            // Demo authentication (replace with real API call)
            const userData = DEMO_USERS[email];
            
            if (!userData || userData.password !== password) {
                throw new Error('Invalid email or password');
            }
            
            // Create user object
            const user = new User({
                ...userData,
                lastLogin: new Date().toISOString()
            });
            
            // Save session
            const duration = rememberMe ? AUTH_CONFIG.SESSION_DURATION.REMEMBER : AUTH_CONFIG.SESSION_DURATION.DEFAULT;
            const expiry = new Date().getTime() + duration;
            
            localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.USER, JSON.stringify(user.toJSON()));
            localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.IS_LOGGED_IN, 'true');
            localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.SESSION_EXPIRY, expiry.toString());
            localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.REMEMBER_ME, rememberMe.toString());
            
            // Set current user
            this.currentUser = user;
            this.isAuthenticated = true;
            this.startSessionTimer();
            
            // Dispatch login event
            this.dispatchEvent('login', user);
            
            return {
                success: true,
                user: user.toJSON(),
                message: 'Login successful'
            };
            
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Signup new user
     * @param {Object} userData - User registration data
     * @returns {Promise} Signup result
     */
    async signup(userData) {
        try {
            const { name, email, password, mobile, district, crop } = userData;
            
            // Validate inputs
            if (!name || !email || !password) {
                throw new Error('Name, email and password are required');
            }
            
            if (password.length < 6) {
                throw new Error('Password must be at least 6 characters');
            }
            
            // Check if user already exists
            if (DEMO_USERS[email.toLowerCase()]) {
                throw new Error('User already exists with this email');
            }
            
            // Create new user (in real app, this would be an API call)
            const newUser = {
                id: Object.keys(DEMO_USERS).length + 1,
                name: name,
                email: email.toLowerCase(),
                password: password,
                role: 'user',
                plan: 'basic',
                avatar: null,
                createdAt: new Date().toISOString(),
                mobile: mobile,
                district: district,
                crop: crop
            };
            
            // In real app, save to backend
            // DEMO_USERS[email.toLowerCase()] = newUser;
            
            // Auto login after signup
            return await this.login(email, password, false);
            
        } catch (error) {
            console.error('Signup error:', error);
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Logout user
     */
    logout() {
        // Clear session
        localStorage.removeItem(AUTH_CONFIG.STORAGE_KEYS.USER);
        localStorage.removeItem(AUTH_CONFIG.STORAGE_KEYS.IS_LOGGED_IN);
        localStorage.removeItem(AUTH_CONFIG.STORAGE_KEYS.SESSION_EXPIRY);
        
        // Don't remove remember me preference
        
        // Clear current user
        this.currentUser = null;
        this.isAuthenticated = false;
        
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
            this.sessionTimer = null;
        }
        
        // Dispatch logout event
        this.dispatchEvent('logout');
    }

    /**
     * Get current user
     * @returns {Object|null} Current user or null
     */
    getCurrentUser() {
        return this.currentUser ? this.currentUser.toJSON() : null;
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isLoggedIn() {
        return this.isAuthenticated;
    }

    /**
     * Update user profile
     * @param {Object} updates - Profile updates
     * @returns {Promise} Update result
     */
    async updateProfile(updates) {
        try {
            if (!this.currentUser) {
                throw new Error('User not authenticated');
            }
            
            // Update user object
            Object.assign(this.currentUser, updates);
            
            // Save to storage
            localStorage.setItem(AUTH_CONFIG.STORAGE_KEYS.USER, JSON.stringify(this.currentUser.toJSON()));
            
            // Dispatch update event
            this.dispatchEvent('profileUpdate', this.currentUser);
            
            return {
                success: true,
                user: this.currentUser.toJSON(),
                message: 'Profile updated successfully'
            };
            
        } catch (error) {
            console.error('Profile update error:', error);
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Change user password
     * @param {string} currentPassword - Current password
     * @param {string} newPassword - New password
     * @returns {Promise} Password change result
     */
    async changePassword(currentPassword, newPassword) {
        try {
            if (!this.currentUser) {
                throw new Error('User not authenticated');
            }
            
            // In real app, verify current password with backend
            // For demo, we'll just simulate success
            
            if (newPassword.length < 6) {
                throw new Error('New password must be at least 6 characters');
            }
            
            // Dispatch password change event
            this.dispatchEvent('passwordChange');
            
            return {
                success: true,
                message: 'Password changed successfully'
            };
            
        } catch (error) {
            console.error('Password change error:', error);
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Update user preferences
     * @param {Object} preferences - User preferences
     * @returns {Promise} Update result
     */
    async updatePreferences(preferences) {
        try {
            if (!this.currentUser) {
                throw new Error('User not authenticated');
            }
            
            this.currentUser.updatePreferences(preferences);
            
            return {
                success: true,
                preferences: this.currentUser.preferences,
                message: 'Preferences updated successfully'
            };
            
        } catch (error) {
            console.error('Preferences update error:', error);
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Reset password (forgot password)
     * @param {string} email - User email
     * @returns {Promise} Reset result
     */
    async resetPassword(email) {
        try {
            if (!email) {
                throw new Error('Email is required');
            }
            
            // In real app, send reset link to email
            // For demo, just simulate success
            
            return {
                success: true,
                message: 'Password reset link sent to your email'
            };
            
        } catch (error) {
            console.error('Password reset error:', error);
            return {
                success: false,
                message: error.message
            };
        }
    }

    /**
     * Dispatch custom event
     * @param {string} eventName - Event name
     * @param {any} detail - Event detail
     */
    dispatchEvent(eventName, detail = null) {
        const event = new CustomEvent(`auth:${eventName}`, { detail });
        window.dispatchEvent(event);
    }

    /**
     * Add event listener
     * @param {string} eventName - Event name
     * @param {Function} callback - Callback function
     */
    on(eventName, callback) {
        window.addEventListener(`auth:${eventName}`, callback);
    }

    /**
     * Remove event listener
     * @param {string} eventName - Event name
     * @param {Function} callback - Callback function
     */
    off(eventName, callback) {
        window.removeEventListener(`auth:${eventName}`, callback);
    }
}

// Create and export auth instance
const auth = new AuthService();

// DOM ready handler for auth UI
document.addEventListener('DOMContentLoaded', () => {
    initAuthUI();
});

/**
 * Initialize authentication UI components
 */
function initAuthUI() {
    // Update UI based on auth state
    updateAuthUI();
    
    // Listen for auth events
    auth.on('login', () => updateAuthUI());
    auth.on('logout', () => updateAuthUI());
    auth.on('profileUpdate', () => updateAuthUI());
}

/**
 * Update UI based on authentication state
 */
function updateAuthUI() {
    const isLoggedIn = auth.isLoggedIn();
    const user = auth.getCurrentUser();
    
    // Update login/logout buttons
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const userAvatar = document.getElementById('userAvatar');
    const userNameSpan = document.getElementById('userName');
    
    if (isLoggedIn && user) {
        // User is logged in
        if (loginBtn) loginBtn.style.display = 'none';
        if (signupBtn) signupBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'flex';
        
        // Update user info
        if (userNameSpan) userNameSpan.textContent = user.name.split(' ')[0];
        if (userAvatar) {
            if (user.avatar) {
                userAvatar.style.backgroundImage = `url(${user.avatar})`;
                userAvatar.style.backgroundSize = 'cover';
                userAvatar.innerHTML = '';
            } else {
                userAvatar.innerHTML = '<i class="fas fa-user"></i>';
            }
        }
    } else {
        // User is logged out
        if (loginBtn) loginBtn.style.display = 'flex';
        if (signupBtn) signupBtn.style.display = 'flex';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

/**
 * Helper function to show auth modal
 * @param {string} type - 'login' or 'signup'
 */
function showAuthModal(type = 'login') {
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    
    if (type === 'login' && loginModal) {
        loginModal.style.display = 'flex';
    } else if (type === 'signup' && signupModal) {
        signupModal.style.display = 'flex';
    }
}

/**
 * Helper function to close auth modal
 */
function closeAuthModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (modal.style.display === 'flex') {
            modal.style.display = 'none';
        }
    });
}

/**
 * Handle login form submission
 * @param {Event} event - Form submit event
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail')?.value;
    const password = document.getElementById('loginPassword')?.value;
    const rememberMe = document.getElementById('rememberMe')?.checked || false;
    
    if (!email || !password) {
        showToast('Please enter email and password', 'error');
        return;
    }
    
    showToast('Logging in...', 'info');
    
    const result = await auth.login(email, password, rememberMe);
    
    if (result.success) {
        showToast(result.message, 'success');
        closeAuthModals();
        
        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = 'pages/dashboard.html';
        }, 1000);
    } else {
        showToast(result.message, 'error');
    }
}

/**
 * Handle signup form submission
 * @param {Event} event - Form submit event
 */
async function handleSignup(event) {
    event.preventDefault();
    
    const name = document.getElementById('signupName')?.value;
    const email = document.getElementById('signupEmail')?.value;
    const password = document.getElementById('signupPassword')?.value;
    const confirmPassword = document.getElementById('signupConfirmPassword')?.value;
    const mobile = document.getElementById('signupPhone')?.value;
    const district = document.getElementById('signupDistrict')?.value;
    const crop = document.getElementById('signupCrop')?.value;
    
    if (!name || !email || !password) {
        showToast('Please fill all required fields', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    showToast('Creating account...', 'info');
    
    const result = await auth.signup({
        name, email, password, mobile, district, crop
    });
    
    if (result.success) {
        showToast(result.message, 'success');
        closeAuthModals();
        
        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = 'pages/dashboard.html';
        }, 1000);
    } else {
        showToast(result.message, 'error');
    }
}

/**
 * Handle logout
 */
function handleLogout() {
    auth.logout();
    showToast('Logged out successfully', 'success');
    
    // Redirect to home page
    setTimeout(() => {
        window.location.href = '../index.html';
    }, 1000);
}

/**
 * Show toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Export functions for global use
window.auth = auth;
window.handleLogin = handleLogin;
window.handleSignup = handleSignup;
window.handleLogout = handleLogout;
window.showAuthModal = showAuthModal;
window.closeAuthModals = closeAuthModals;

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        auth,
        handleLogin,
        handleSignup,
        handleLogout,
        showAuthModal,
        closeAuthModals,
        updateAuthUI
    };
}