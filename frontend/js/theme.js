/**
 * FarmIntel AI - Theme Management
 * Handles dark/light mode, theme persistence, and system preference detection
 */

// Theme Configuration
const THEME_CONFIG = {
    STORAGE_KEY: 'farmintel_theme',
    AUTO_KEY: 'farmintel_theme_auto',
    TRANSITION_DURATION: 300,
    DARK_CLASS: 'dark-mode',
    LIGHT_CLASS: 'light-mode'
};

// Theme Manager Class
class ThemeManager {
    constructor() {
        this.currentTheme = 'light';
        this.isAutoMode = false;
        this.systemPreference = this.getSystemPreference();
        this.observers = [];
        this.init();
    }

    /**
     * Initialize theme manager
     */
    init() {
        this.loadTheme();
        this.setupSystemPreferenceListener();
        this.setupThemeToggleButton();
        this.applyThemeTransitions();
    }

    /**
     * Get system color scheme preference
     * @returns {string} 'dark' or 'light'
     */
    getSystemPreference() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    /**
     * Load saved theme from localStorage
     */
    loadTheme() {
        const savedTheme = localStorage.getItem(THEME_CONFIG.STORAGE_KEY);
        const autoMode = localStorage.getItem(THEME_CONFIG.AUTO_KEY) === 'true';
        
        this.isAutoMode = autoMode;
        
        if (autoMode) {
            this.currentTheme = this.systemPreference;
            this.applyTheme(this.currentTheme);
        } else if (savedTheme && (savedTheme === 'dark' || savedTheme === 'light')) {
            this.currentTheme = savedTheme;
            this.applyTheme(this.currentTheme);
        } else {
            this.currentTheme = this.systemPreference;
            this.applyTheme(this.currentTheme);
        }
        
        this.notifyObservers();
    }

    /**
     * Apply theme to document
     * @param {string} theme - 'dark' or 'light'
     */
    applyTheme(theme) {
        const isDark = theme === 'dark';
        
        if (isDark) {
            document.body.classList.add(THEME_CONFIG.DARK_CLASS);
        } else {
            document.body.classList.remove(THEME_CONFIG.DARK_CLASS);
        }
        
        this.currentTheme = theme;
        
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', isDark ? '#0F0F1A' : '#FFFFFF');
        }
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    /**
     * Set theme with transition effect
     * @param {string} theme - 'dark' or 'light'
     * @param {boolean} save - Whether to save to localStorage
     */
    setTheme(theme, save = true) {
        if (theme !== 'dark' && theme !== 'light') return;
        
        // Add transition class for smooth color changes
        document.body.classList.add('theme-transitioning');
        
        setTimeout(() => {
            this.applyTheme(theme);
            
            setTimeout(() => {
                document.body.classList.remove('theme-transitioning');
            }, THEME_CONFIG.TRANSITION_DURATION);
        }, 10);
        
        if (save) {
            localStorage.setItem(THEME_CONFIG.STORAGE_KEY, theme);
            localStorage.setItem(THEME_CONFIG.AUTO_KEY, 'false');
            this.isAutoMode = false;
        }
        
        this.notifyObservers();
    }

    /**
     * Toggle between dark and light mode
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme, true);
        return newTheme;
    }

    /**
     * Enable auto mode (follow system preference)
     */
    enableAutoMode() {
        this.isAutoMode = true;
        localStorage.setItem(THEME_CONFIG.AUTO_KEY, 'true');
        this.currentTheme = this.systemPreference;
        this.applyTheme(this.currentTheme);
        this.notifyObservers();
    }

    /**
     * Disable auto mode
     */
    disableAutoMode() {
        this.isAutoMode = false;
        localStorage.setItem(THEME_CONFIG.AUTO_KEY, 'false');
    }

    /**
     * Set theme to match system preference
     */
    syncWithSystem() {
        if (this.isAutoMode) {
            const newTheme = this.getSystemPreference();
            if (newTheme !== this.currentTheme) {
                this.currentTheme = newTheme;
                this.applyTheme(this.currentTheme);
                this.notifyObservers();
            }
        }
    }

    /**
     * Setup system preference listener
     */
    setupSystemPreferenceListener() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Modern browsers
        if (mediaQuery.addEventListener) {
            mediaQuery.addEventListener('change', (e) => {
                this.systemPreference = e.matches ? 'dark' : 'light';
                if (this.isAutoMode) {
                    this.currentTheme = this.systemPreference;
                    this.applyTheme(this.currentTheme);
                    this.notifyObservers();
                }
            });
        } 
        // Fallback for older browsers
        else if (mediaQuery.addListener) {
            mediaQuery.addListener((e) => {
                this.systemPreference = e.matches ? 'dark' : 'light';
                if (this.isAutoMode) {
                    this.currentTheme = this.systemPreference;
                    this.applyTheme(this.currentTheme);
                    this.notifyObservers();
                }
            });
        }
    }

    /**
     * Setup theme toggle button
     */
    setupThemeToggleButton() {
        const toggleBtn = document.getElementById('themeToggle');
        if (!toggleBtn) return;
        
        // Update button icon based on theme
        const updateButtonIcon = () => {
            if (this.currentTheme === 'dark') {
                toggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            } else {
                toggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            }
        };
        
        // Initial icon set
        updateButtonIcon();
        
        // Listen to theme changes
        window.addEventListener('themeChanged', updateButtonIcon);
        
        // Toggle on click
        toggleBtn.addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    /**
     * Apply smooth transitions for theme changes
     */
    applyThemeTransitions() {
        // Add CSS for smooth transitions if not already present
        if (!document.querySelector('#theme-transition-styles')) {
            const style = document.createElement('style');
            style.id = 'theme-transition-styles';
            style.textContent = `
                .theme-transitioning,
                .theme-transitioning * {
                    transition: background-color 0.3s ease,
                                border-color 0.3s ease,
                                color 0.3s ease,
                                box-shadow 0.3s ease !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Get current theme
     * @returns {string} 'dark' or 'light'
     */
    getTheme() {
        return this.currentTheme;
    }

    /**
     * Check if auto mode is enabled
     * @returns {boolean}
     */
    isAutoModeEnabled() {
        return this.isAutoMode;
    }

    /**
     * Check if dark mode is active
     * @returns {boolean}
     */
    isDarkMode() {
        return this.currentTheme === 'dark';
    }

    /**
     * Add observer for theme changes
     * @param {Function} callback - Callback function
     */
    addObserver(callback) {
        if (typeof callback === 'function') {
            this.observers.push(callback);
        }
    }

    /**
     * Remove observer
     * @param {Function} callback - Callback function to remove
     */
    removeObserver(callback) {
        this.observers = this.observers.filter(obs => obs !== callback);
    }

    /**
     * Notify all observers of theme change
     */
    notifyObservers() {
        this.observers.forEach(callback => {
            callback(this.currentTheme, this.isAutoMode);
        });
    }

    /**
     * Get CSS variables for current theme
     * @returns {Object} Theme variables
     */
    getThemeVariables() {
        if (this.currentTheme === 'dark') {
            return {
                primary: '#818CF8',
                primaryDark: '#6366F1',
                primaryLight: '#A5B4FC',
                background: '#0F0F1A',
                surface: '#1E293B',
                text: '#F1F5F9',
                textSecondary: '#CBD5E1',
                textMuted: '#94A3B8',
                border: 'rgba(255, 255, 255, 0.1)'
            };
        } else {
            return {
                primary: '#4F46E5',
                primaryDark: '#4338CA',
                primaryLight: '#818CF8',
                background: '#FFFFFF',
                surface: '#F9FAFB',
                text: '#111827',
                textSecondary: '#374151',
                textMuted: '#6B7280',
                border: '#E5E7EB'
            };
        }
    }
}

// Create and export theme manager instance
const themeManager = new ThemeManager();

// Helper function to get current theme
function getCurrentTheme() {
    return themeManager.getTheme();
}

// Helper function to check if dark mode is active
function isDarkMode() {
    return themeManager.isDarkMode();
}

// Helper function to toggle theme
function toggleTheme() {
    return themeManager.toggleTheme();
}

// Helper function to set theme
function setTheme(theme) {
    themeManager.setTheme(theme, true);
}

// Helper function to enable auto mode
function enableAutoMode() {
    themeManager.enableAutoMode();
}

// CSS variables for theme-aware components
function updateCSSVariables() {
    const vars = themeManager.getThemeVariables();
    const root = document.documentElement;
    
    Object.entries(vars).forEach(([key, value]) => {
        root.style.setProperty(`--${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, value);
    });
}

// Listen to theme changes for CSS variables
themeManager.addObserver(() => {
    updateCSSVariables();
});

// Initialize CSS variables
updateCSSVariables();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        themeManager,
        getCurrentTheme,
        isDarkMode,
        toggleTheme,
        setTheme,
        enableAutoMode
    };
}

// Make available globally
window.themeManager = themeManager;
window.getCurrentTheme = getCurrentTheme;
window.isDarkMode = isDarkMode;
window.toggleTheme = toggleTheme;
window.setTheme = setTheme;
window.enableAutoMode = enableAutoMode;

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    // Ensure theme is applied before page becomes visible
    requestAnimationFrame(() => {
        themeManager.applyTheme(themeManager.currentTheme);
    });
});

// Handle page visibility change to sync theme
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        themeManager.syncWithSystem();
    }
});