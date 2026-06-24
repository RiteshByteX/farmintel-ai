/**
 * FarmIntel AI - API Integration
 * Complete API service for backend communication
 */

// API Configuration
const API_CONFIG = {
    BASE_URL: '/api',  // Relative URL - works when served from Flask
    TIMEOUT: 30000,
    headers: {
        'Accept': 'application/json'
    }
};

// API Service Class
class FarmIntelAPI {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async fetchWithTimeout(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                signal: controller.signal,
                headers: {
                    ...API_CONFIG.headers,
                    ...options.headers
                }
            });
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || errorData.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout. Please check your connection.');
            }
            throw error;
        }
    }

    /**
     * Upload image to server
     * @param {File} imageFile - The image file to upload
     * @returns {Promise} Upload response with filepath
     */
    async uploadImage(imageFile) {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        try {
            const response = await fetch(`${this.baseURL}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Upload failed');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    /**
     * Detect disease from image file (File Upload - multipart/form-data)
     * This is the primary method for the frontend
     * @param {File} imageFile - The image file to detect disease from
     * @returns {Promise} Detection results
     */
    async detectDiseaseFromFile(imageFile) {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        try {
            console.log('📤 Sending file for detection:', imageFile.name);
            
            const response = await fetch(`${this.baseURL}/detect`, {
                method: 'POST',
                body: formData
                // Don't set Content-Type - browser sets it with boundary
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.error || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ Detection result:', result);
            return result;
            
        } catch (error) {
            console.error('❌ Detection error:', error);
            throw error;
        }
    }

    /**
     * Detect disease from image path (JSON - for server-side processing)
     * @param {string} imagePath - Path of uploaded image
     * @returns {Promise} Detection results
     */
    async detectDisease(imagePath) {
        return this.fetchWithTimeout('/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_path: imagePath })
        });
    }

    /**
     * Detect disease from base64 image (JSON - for base64 uploads)
     * @param {string} base64Image - Base64 encoded image
     * @returns {Promise} Detection results
     */
    async detectDiseaseFromBase64(base64Image) {
        return this.fetchWithTimeout('/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ base64_image: base64Image })
        });
    }

    /**
     * Get treatment recommendations for disease
     * @param {string} diseaseName - Name of detected disease
     * @param {number} confidence - Confidence score
     * @returns {Promise} Treatment recommendations
     */
    async getTreatment(diseaseName, confidence = 0) {
        return this.fetchWithTimeout('/treatment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                disease: diseaseName,
                confidence: confidence 
            })
        });
    }

    /**
     * Get weather data for location
     * @param {string} city - City name or pincode
     * @returns {Promise} Weather data
     */
    async getWeather(city = 'Mumbai') {
        return this.fetchWithTimeout(`/weather?city=${encodeURIComponent(city)}`, {
            method: 'GET'
        });
    }

    /**
     * Get weather by coordinates
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @returns {Promise} Weather data
     */
    async getWeatherByCoords(lat, lon) {
        return this.fetchWithTimeout(`/weather?lat=${lat}&lon=${lon}`, {
            method: 'GET'
        });
    }

    /**
     * Get all scan history
     * @returns {Promise} History data
     */
    async getHistory() {
        return this.fetchWithTimeout('/history', {
            method: 'GET'
        });
    }

    /**
     * Save detection to history
     * @param {Object} detectionData - Detection record to save
     * @returns {Promise} Save response
     */
    async saveToHistory(detectionData) {
        return this.fetchWithTimeout('/history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(detectionData)
        });
    }

    /**
     * Delete history record
     * @param {number} id - Record ID to delete
     * @returns {Promise} Delete response
     */
    async deleteHistoryRecord(id) {
        return this.fetchWithTimeout(`/history/${id}`, {
            method: 'DELETE'
        });
    }

    /**
     * Search history by keyword
     * @param {string} query - Search query
     * @returns {Promise} Filtered history
     */
    async searchHistory(query) {
        return this.fetchWithTimeout(`/history/search?q=${encodeURIComponent(query)}`, {
            method: 'GET'
        });
    }

    /**
     * Generate PDF report
     * @param {Object} data - Report data
     * @returns {Promise} PDF blob
     */
    async generatePDF(data) {
        const response = await fetch(`${this.baseURL}/report/pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        
        return await response.blob();
    }

    /**
     * Generate CSV report
     * @param {Object} data - Report data
     * @returns {Promise} CSV blob
     */
    async generateCSV(data) {
        const response = await fetch(`${this.baseURL}/report/csv`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('CSV generation failed');
        }
        
        return await response.blob();
    }

    /**
     * Get disease library
     * @returns {Promise} Disease library data
     */
    async getDiseaseLibrary() {
        return this.fetchWithTimeout('/disease-library', {
            method: 'GET'
        });
    }

    /**
     * Get disease details by name
     * @param {string} diseaseName - Name of disease
     * @returns {Promise} Disease details
     */
    async getDiseaseDetails(diseaseName) {
        return this.fetchWithTimeout(`/disease-library/${encodeURIComponent(diseaseName)}`, {
            method: 'GET'
        });
    }

    /**
     * Check server health
     * @returns {Promise} Health status
     */
    async healthCheck() {
        try {
            const response = await fetch('/health');
            return response.ok;
        } catch {
            return false;
        }
    }

    /**
     * Get API status with details
     * @returns {Promise} Status object
     */
    async getAPIStatus() {
        try {
            const health = await this.healthCheck();
            return {
                status: health ? 'online' : 'offline',
                timestamp: new Date().toISOString(),
                version: '1.0.0'
            };
        } catch {
            return {
                status: 'offline',
                timestamp: new Date().toISOString(),
                error: 'Cannot connect to server'
            };
        }
    }
}

// Create and export API instance
const farmintelAPI = new FarmIntelAPI();

// Helper function for demo mode
const DEMO_MODE = {
    enabled: false,
    
    detectDiseaseFromFile: async (imageFile) => {
        await new Promise(resolve => setTimeout(resolve, 1500));
        const diseases = [
            "Tomato Late Blight", "Tomato Early Blight", "Potato Late Blight",
            "Apple Scab", "Corn Common Rust", "Rice Blast", "Wheat Rust",
            "Tomato Healthy", "Potato Healthy"
        ];
        const disease = diseases[Math.floor(Math.random() * diseases.length)];
        const confidence = Math.floor(Math.random() * (98 - 75 + 1) + 75);
        const severity = confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild";
        
        return {
            success: true,
            disease: disease,
            confidence: confidence,
            severity: severity,
            severity_color: severity === "Severe" ? "#EF4444" : severity === "Moderate" ? "#F59E0B" : "#10B981",
            confidence_level: confidence >= 85 ? "High" : confidence >= 70 ? "Medium" : "Low",
            is_healthy: disease.includes('Healthy'),
            crop: disease.split(' ')[0],
            treatment: {
                chemical_name: "Copper hydroxide (2g/L water)",
                chemical_dosage: "Apply every 7-10 days",
                organic_name: "Neem oil 5ml/L",
                organic_dosage: "Spray twice weekly",
                cultural_practices: ["Remove infected leaves", "Avoid overhead watering"],
                prevention_tips: ["Use resistant varieties", "Crop rotation"],
                urgency: severity === "Severe" ? "Immediate action needed" : "Monitor regularly"
            },
            timestamp: new Date().toISOString()
        };
    },
    
    detectDisease: async (imagePath) => {
        await new Promise(resolve => setTimeout(resolve, 1500));
        return {
            success: true,
            disease: "Tomato Late Blight",
            confidence: 92,
            severity: "Moderate"
        };
    },
    
    detectDiseaseFromBase64: async (base64Image) => {
        await new Promise(resolve => setTimeout(resolve, 1500));
        return {
            success: true,
            disease: "Tomato Early Blight",
            confidence: 87,
            severity: "Mild"
        };
    },
    
    getTreatment: async (diseaseName, confidence) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        let severity = 'Moderate';
        if (confidence >= 85) severity = 'Severe';
        else if (confidence >= 70) severity = 'Moderate';
        else if (confidence >= 50) severity = 'Mild';
        else severity = 'Low';
        
        return {
            success: true,
            disease: diseaseName,
            confidence: confidence,
            severity: severity,
            urgency: severity === 'Severe' ? 'Immediate action needed' : 
                     severity === 'Moderate' ? 'Action within 3 days' : 
                     'Monitor and treat if spreads',
            chemical_treatment: "Copper hydroxide (2g/L water) - Apply every 7-10 days",
            organic_treatment: "Neem oil 5ml/L + garlic extract - Spray twice weekly",
            cultural_practices: "Remove infected leaves, avoid overhead watering",
            prevention_tips: "Use resistant varieties, crop rotation, proper spacing"
        };
    },
    
    getWeather: async (city) => {
        await new Promise(resolve => setTimeout(resolve, 800));
        return {
            success: true,
            city: city,
            temperature: Math.floor(Math.random() * (35 - 20 + 1) + 20),
            humidity: Math.floor(Math.random() * (95 - 40 + 1) + 40),
            wind_speed: Math.floor(Math.random() * 25),
            rainfall: Math.random() * 10,
            condition: ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain'][Math.floor(Math.random() * 4)],
            disease_risk: Math.random() > 0.7 ? 'High' : Math.random() > 0.4 ? 'Medium' : 'Low',
            risk_message: "Weather conditions are favorable for disease development"
        };
    },
    
    getHistory: async () => {
        await new Promise(resolve => setTimeout(resolve, 500));
        return { success: true, history: JSON.parse(localStorage.getItem('scanHistory') || '[]') };
    }
};

// Wrapper function to use demo mode if needed
async function apiCall(apiFunction, ...args) {
    try {
        const isOnline = await farmintelAPI.healthCheck();
        if (!isOnline && DEMO_MODE.enabled) {
            console.warn('Backend unavailable, using demo mode');
            const demoFunction = DEMO_MODE[apiFunction.name];
            if (demoFunction) {
                return await demoFunction(...args);
            }
        }
        return await apiFunction.apply(farmintelAPI, args);
    } catch (error) {
        console.error(`API Error in ${apiFunction.name}:`, error);
        if (DEMO_MODE.enabled && DEMO_MODE[apiFunction.name]) {
            console.warn('Falling back to demo mode');
            return await DEMO_MODE[apiFunction.name](...args);
        }
        throw error;
    }
}

// Export individual functions
const uploadImage = (file) => apiCall(farmintelAPI.uploadImage, file);
const detectDiseaseFromFile = (file) => apiCall(farmintelAPI.detectDiseaseFromFile, file);
const detectDisease = (imagePath) => apiCall(farmintelAPI.detectDisease, imagePath);
const detectDiseaseFromBase64 = (base64) => apiCall(farmintelAPI.detectDiseaseFromBase64, base64);
const getTreatment = (diseaseName, confidence) => apiCall(farmintelAPI.getTreatment, diseaseName, confidence);
const getWeather = (city) => apiCall(farmintelAPI.getWeather, city);
const getHistory = () => apiCall(farmintelAPI.getHistory);
const saveToHistory = (data) => apiCall(farmintelAPI.saveToHistory, data);
const deleteHistoryRecord = (id) => apiCall(farmintelAPI.deleteHistoryRecord, id);
const searchHistory = (query) => apiCall(farmintelAPI.searchHistory, query);
const generatePDF = (data) => apiCall(farmintelAPI.generatePDF, data);
const generateCSV = (data) => apiCall(farmintelAPI.generateCSV, data);
const getDiseaseLibrary = () => apiCall(farmintelAPI.getDiseaseLibrary);
const getAPIStatus = () => farmintelAPI.getAPIStatus();

// Export everything
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        farmintelAPI,
        uploadImage,
        detectDiseaseFromFile,
        detectDisease,
        detectDiseaseFromBase64,
        getTreatment,
        getWeather,
        getHistory,
        saveToHistory,
        deleteHistoryRecord,
        searchHistory,
        generatePDF,
        generateCSV,
        getDiseaseLibrary,
        getAPIStatus,
        DEMO_MODE
    };
}