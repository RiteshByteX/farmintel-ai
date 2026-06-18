/**
 * FarmIntel AI - Main JavaScript
 * Core initialization, global utilities, and app bootstrap
 */

// ========================================
// 1. APP CONFIGURATION
// ========================================

const APP_CONFIG = {
    name: 'FarmIntel AI',
    version: '1.0.0',
    environment: 'production', // 'development', 'production'
    debug: false,
    apiUrl: 'http://localhost:5000/api',
    features: {
        camera: true,
        offlineMode: false,
        notifications: true,
        weatherAlerts: true
    }
};

// ========================================
// 2. GLOBAL UTILITIES
// ========================================

// Format date
function formatDate(date, format = 'short') {
    const d = new Date(date);
    if (format === 'short') {
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } else if (format === 'long') {
        return d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    } else if (format === 'time') {
        return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return d.toLocaleDateString();
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Format percentage
function formatPercentage(value, decimals = 0) {
    return `${value.toFixed(decimals)}%`;
}

// Truncate text
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Debounce function
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Deep clone object
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Check if value is empty
function isEmpty(value) {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string') return value.trim() === '';
    if (Array.isArray(value)) return value.length === 0;
    if (typeof value === 'object') return Object.keys(value).length === 0;
    return false;
}

// Local storage wrapper
const storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Storage set error:', e);
            return false;
        }
    },
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Storage get error:', e);
            return defaultValue;
        }
    },
    remove(key) {
        localStorage.removeItem(key);
    },
    clear() {
        localStorage.clear();
    },
    has(key) {
        return localStorage.getItem(key) !== null;
    }
};

// Cookie utilities
const cookies = {
    set(name, value, days = 7) {
        const expires = new Date();
        expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
    },
    get(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    },
    delete(name) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }
};

// URL utilities
const urlUtils = {
    getParams() {
        const params = {};
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        for (const [key, value] of urlParams) {
            params[key] = value;
        }
        return params;
    },
    getParam(key) {
        return new URLSearchParams(window.location.search).get(key);
    },
    setParam(key, value) {
        const url = new URL(window.location.href);
        url.searchParams.set(key, value);
        window.history.pushState({}, '', url);
    },
    removeParam(key) {
        const url = new URL(window.location.href);
        url.searchParams.delete(key);
        window.history.pushState({}, '', url);
    }
};

// Device detection
const device = {
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },
    isTablet() {
        return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
    },
    isDesktop() {
        return !this.isMobile() && !this.isTablet();
    },
    getOS() {
        const userAgent = navigator.userAgent;
        if (/Windows/i.test(userAgent)) return 'Windows';
        if (/Mac/i.test(userAgent)) return 'macOS';
        if (/Linux/i.test(userAgent)) return 'Linux';
        if (/Android/i.test(userAgent)) return 'Android';
        if (/iPhone|iPad|iPod/i.test(userAgent)) return 'iOS';
        return 'Unknown';
    },
    getBrowser() {
        const userAgent = navigator.userAgent;
        if (/Chrome/i.test(userAgent) && !/Edge/i.test(userAgent)) return 'Chrome';
        if (/Safari/i.test(userAgent) && !/Chrome/i.test(userAgent)) return 'Safari';
        if (/Firefox/i.test(userAgent)) return 'Firefox';
        if (/Edge/i.test(userAgent)) return 'Edge';
        return 'Unknown';
    }
};

// ========================================
// 3. DOM UTILITIES
// ========================================

// DOM ready helper
function domReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// Element visibility check
function isElementInViewport(el, partially = false) {
    const rect = el.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    const windowWidth = window.innerWidth || document.documentElement.clientWidth;
    
    if (partially) {
        return rect.bottom > 0 && rect.top < windowHeight && rect.right > 0 && rect.left < windowWidth;
    }
    return rect.top >= 0 && rect.left >= 0 && rect.bottom <= windowHeight && rect.right <= windowWidth;
}

// Scroll to element
function scrollToElement(el, offset = 0, behavior = 'smooth') {
    const element = typeof el === 'string' ? document.querySelector(el) : el;
    if (!element) return;
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({ top: elementPosition - offset, behavior });
}

// Get element dimensions
function getElementDimensions(el) {
    const rect = el.getBoundingClientRect();
    return {
        width: rect.width,
        height: rect.height,
        top: rect.top,
        left: rect.left,
        bottom: rect.bottom,
        right: rect.right
    };
}

// ========================================
// 4. LOADING STATES
// ========================================

// Show global loader
function showLoader(message = 'Loading...') {
    let loader = document.getElementById('globalLoader');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'globalLoader';
        loader.className = 'global-loader';
        loader.innerHTML = `
            <div class="loader-overlay">
                <div class="loader-container">
                    <div class="loader-spinner"></div>
                    <p class="loader-message">${message}</p>
                </div>
            </div>
        `;
        document.body.appendChild(loader);
        
        // Add styles if not present
        if (!document.querySelector('#loader-styles')) {
            const style = document.createElement('style');
            style.id = 'loader-styles';
            style.textContent = `
                .global-loader {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 9999;
                }
                .loader-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.7);
                    backdrop-filter: blur(5px);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .loader-container {
                    text-align: center;
                    background: var(--card-bg, #1E293B);
                    padding: 2rem;
                    border-radius: 1rem;
                    min-width: 200px;
                }
                .loader-spinner {
                    width: 40px;
                    height: 40px;
                    border: 3px solid rgba(79, 70, 229, 0.2);
                    border-top-color: #4F46E5;
                    border-radius: 50%;
                    margin: 0 auto 1rem;
                    animation: spin 0.8s linear infinite;
                }
                .loader-message {
                    color: var(--text-primary, white);
                    font-size: 0.875rem;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    } else {
        const msgEl = loader.querySelector('.loader-message');
        if (msgEl) msgEl.textContent = message;
        loader.style.display = 'block';
    }
}

// Hide global loader
function hideLoader() {
    const loader = document.getElementById('globalLoader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// ========================================
// 5. NOTIFICATION SYSTEM
// ========================================

// Show notification
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ========================================
// 6. MOBILE MENU
// ========================================

// Initialize mobile sidebar
function initMobileSidebar() {
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!mobileToggle || !sidebar) return;
    
    function openSidebar() {
        sidebar.classList.add('mobile-open');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeSidebar() {
        sidebar.classList.remove('mobile-open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    mobileToggle.addEventListener('click', openSidebar);
    
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
            closeSidebar();
        }
    });
}

// ========================================
// 7. PAGE TRANSITIONS
// ========================================

// Page transition manager
const pageTransitions = {
    init() {
        document.querySelectorAll('a').forEach(link => {
            if (link.hostname === window.location.hostname && !link.target) {
                link.addEventListener('click', (e) => {
                    if (link.getAttribute('href') && !link.getAttribute('href').startsWith('#') && !link.getAttribute('href').startsWith('javascript:')) {
                        e.preventDefault();
                        this.navigateTo(link.getAttribute('href'));
                    }
                });
            }
        });
    },
    navigateTo(url) {
        document.body.classList.add('page-exit');
        setTimeout(() => {
            window.location.href = url;
        }, 300);
    }
};

// ========================================
// 8. ANALYTICS (Basic)
// ========================================

const analytics = {
    trackPageView(page) {
        if (APP_CONFIG.debug) {
            console.log(`[Analytics] Page view: ${page}`);
        }
    },
    trackEvent(category, action, label = null) {
        if (APP_CONFIG.debug) {
            console.log(`[Analytics] Event: ${category} - ${action}${label ? ` - ${label}` : ''}`);
        }
    }
};

// ========================================
// 9. ERROR HANDLING
// ========================================

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (APP_CONFIG.debug) {
        showNotification('An unexpected error occurred', 'error');
    }
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);
    if (APP_CONFIG.debug) {
        showNotification('Something went wrong', 'error');
    }
});

// ========================================
// 10. APP INITIALIZATION
// ========================================

// Initialize all page-specific components
function initPageComponents() {
    // Initialize AOS if available
    if (typeof AOS !== 'undefined' && AOS.init) {
        AOS.init({
            duration: 800,
            once: true,
            offset: 50
        });
    }
    
    // Initialize mobile sidebar
    initMobileSidebar();
    
    // Initialize smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Add active class to current nav item
    const currentPath = window.location.pathname.split('/').pop();
    document.querySelectorAll('.nav-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && href === currentPath) {
            item.classList.add('active');
        }
    });
}

// Set user name from storage
function setUserName() {
    const userName = storage.get('userName', 'John');
    const nameElements = document.querySelectorAll('#userName, .user-name');
    nameElements.forEach(el => {
        el.textContent = userName;
    });
}

// Initialize auth state
function initAuthState() {
    const isLoggedIn = storage.get('isLoggedIn', false);
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (isLoggedIn) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (signupBtn) signupBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'flex';
    } else {
        if (loginBtn) loginBtn.style.display = 'flex';
        if (signupBtn) signupBtn.style.display = 'flex';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

// Main initialization
function initApp() {
    // Set debug mode
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        APP_CONFIG.debug = true;
        APP_CONFIG.environment = 'development';
    }
    
    // Initialize components
    initPageComponents();
    setUserName();
    initAuthState();
    
    // Track page view
    analytics.trackPageView(window.location.pathname);
    
    // Log initialization
    if (APP_CONFIG.debug) {
        console.log(`${APP_CONFIG.name} v${APP_CONFIG.version} initialized`);
        console.log(`Environment: ${APP_CONFIG.environment}`);
        console.log(`Device: ${device.getOS()} - ${device.getBrowser()}`);
        console.log(`Mobile: ${device.isMobile()}`);
    }
}

// Export for global use
window.app = {
    config: APP_CONFIG,
    utils: {
        formatDate,
        formatNumber,
        formatPercentage,
        truncateText,
        debounce,
        throttle,
        deepClone,
        generateId,
        isEmpty,
        storage,
        cookies,
        urlUtils,
        device
    },
    dom: {
        domReady,
        isElementInViewport,
        scrollToElement,
        getElementDimensions
    },
    ui: {
        showLoader,
        hideLoader,
        showNotification
    },
    analytics,
    initApp
};

// Initialize on DOM ready
domReady(() => {
    initApp();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.app;
}