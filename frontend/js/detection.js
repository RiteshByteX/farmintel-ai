/**
 * FarmIntel AI - Disease Detection JavaScript
 * Integrated with Trained Model Backend
 */

// API Configuration - Update this to match your backend
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// DOM Elements
const takePhotoBtn = document.getElementById('takePhotoBtn');
const uploadFileBtn = document.getElementById('uploadFileBtn');
const fileInput = document.getElementById('fileInput');
const cameraInput = document.getElementById('cameraInput');
const previewArea = document.getElementById('previewArea');
const imagePreview = document.getElementById('imagePreview');
const removeImageBtn = document.getElementById('removeImageBtn');
const detectBtn = document.getElementById('detectBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsContent = document.getElementById('resultsContent');

let currentImageFile = null;
let currentImageDataUrl = null;
let currentDetection = null;
let detectionStartTime = null;

// ============================================
// PARTICLE SYSTEM
// ============================================
function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    
    const colors = ['rgba(79, 70, 229, 0.4)', 'rgba(124, 58, 237, 0.3)', 'rgba(16, 185, 129, 0.3)'];
    
    for (let i = 0; i < 50; i++) {
        const p = document.createElement('div');
        p.classList.add('particle');
        const size = Math.random() * 5 + 2;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        p.style.bottom = '-10px';
        p.style.animationDelay = Math.random() * 15 + 's';
        p.style.animationDuration = 8 + Math.random() * 12 + 's';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        container.appendChild(p);
    }
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================
// IMAGE HANDLING
// ============================================
function handleImageFile(file) {
    if (!file) {
        showToast('No file selected', 'error');
        return;
    }
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showToast('Please select a valid image file (JPEG, PNG, etc.)', 'error');
        return;
    }
    
    // Validate file size (max 20MB)
    if (file.size > 20 * 1024 * 1024) {
        showToast('Image size should be less than 20MB', 'error');
        return;
    }
    
    currentImageFile = file;
    const reader = new FileReader();
    
    reader.onload = (e) => {
        currentImageDataUrl = e.target.result;
        imagePreview.src = currentImageDataUrl;
        previewArea.style.display = 'block';
        detectBtn.disabled = false;
        resultsSection.style.display = 'none';
        showToast('Image loaded successfully! Click "Detect Disease"', 'success');
    };
    
    reader.onerror = () => {
        showToast('Error loading image. Please try again.', 'error');
    };
    
    reader.readAsDataURL(file);
}

// ============================================
// CAMERA FUNCTIONALITY - FIXED FOR DESKTOP & MOBILE
// ============================================

// Helper function to capture photo using getUserMedia (works on desktop)
async function captureWithGetUserMedia() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                facingMode: 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        
        // Create video element for preview
        const video = document.createElement('video');
        video.srcObject = stream;
        video.style.position = 'fixed';
        video.style.top = '0';
        video.style.left = '0';
        video.style.width = '100%';
        video.style.height = '100%';
        video.style.objectFit = 'cover';
        video.style.zIndex = '9999';
        document.body.appendChild(video);
        await video.play();
        
        // Create capture button
        const captureBtn = document.createElement('button');
        captureBtn.innerHTML = '📸 Capture';
        captureBtn.style.position = 'fixed';
        captureBtn.style.bottom = '100px';
        captureBtn.style.left = '50%';
        captureBtn.style.transform = 'translateX(-50%)';
        captureBtn.style.zIndex = '10000';
        captureBtn.style.padding = '16px 40px';
        captureBtn.style.borderRadius = '50px';
        captureBtn.style.background = 'linear-gradient(135deg, #4F46E5, #7C3AED)';
        captureBtn.style.border = 'none';
        captureBtn.style.color = 'white';
        captureBtn.style.fontSize = '18px';
        captureBtn.style.fontWeight = '600';
        captureBtn.style.cursor = 'pointer';
        captureBtn.style.boxShadow = '0 4px 20px rgba(79,70,229,0.4)';
        captureBtn.style.transition = 'all 0.3s ease';
        document.body.appendChild(captureBtn);
        
        // Create close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '✕ Close';
        closeBtn.style.position = 'fixed';
        closeBtn.style.top = '20px';
        closeBtn.style.right = '20px';
        closeBtn.style.zIndex = '10000';
        closeBtn.style.padding = '12px 24px';
        closeBtn.style.borderRadius = '50px';
        closeBtn.style.background = 'rgba(0,0,0,0.7)';
        closeBtn.style.border = '1px solid rgba(255,255,255,0.2)';
        closeBtn.style.color = 'white';
        closeBtn.style.fontSize = '16px';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.transition = 'all 0.3s ease';
        document.body.appendChild(closeBtn);
        
        // Hover effects
        captureBtn.onmouseover = () => captureBtn.style.transform = 'translateX(-50%) scale(1.05)';
        captureBtn.onmouseout = () => captureBtn.style.transform = 'translateX(-50%) scale(1)';
        closeBtn.onmouseover = () => closeBtn.style.background = 'rgba(239,68,68,0.8)';
        closeBtn.onmouseout = () => closeBtn.style.background = 'rgba(0,0,0,0.7)';
        
        // Capture photo on click
        return new Promise((resolve) => {
            captureBtn.addEventListener('click', () => {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth || 1280;
                canvas.height = video.videoHeight || 720;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                // Stop stream and remove UI
                stream.getTracks().forEach(track => track.stop());
                video.remove();
                captureBtn.remove();
                closeBtn.remove();
                
                // Convert to file
                canvas.toBlob((blob) => {
                    if (blob) {
                        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                        resolve(file);
                    } else {
                        resolve(null);
                    }
                }, 'image/jpeg', 0.9);
            });
            
            // Close camera on close button click
            closeBtn.addEventListener('click', () => {
                stream.getTracks().forEach(track => track.stop());
                video.remove();
                captureBtn.remove();
                closeBtn.remove();
                resolve(null);
            });
        });
        
    } catch (error) {
        console.warn('Camera error:', error);
        return null;
    }
}

if (takePhotoBtn) {
    takePhotoBtn.addEventListener('click', async () => {
        // Check if camera is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showToast('Camera not supported on this device. Please upload a file instead.', 'warning');
            if (fileInput) {
                fileInput.value = '';
                fileInput.click();
            }
            return;
        }
        
        // Check if device is mobile
        const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
        
        if (isMobile) {
            // On mobile, use native camera input with capture attribute
            if (cameraInput) {
                cameraInput.setAttribute('capture', 'environment');
                cameraInput.value = '';
                cameraInput.click();
                showToast('📸 Opening camera...', 'info');
            }
        } else {
            // On desktop, use getUserMedia API
            showToast('📸 Opening camera...', 'info');
            const file = await captureWithGetUserMedia();
            
            if (file) {
                console.log('📸 Camera captured:', file.name, file.type, (file.size / 1024).toFixed(1) + 'KB');
                handleImageFile(file);
                showToast('✅ Photo captured successfully!', 'success');
            } else {
                showToast('📸 Camera closed or failed to capture', 'info');
            }
        }
    });
}

// Handle mobile camera capture
if (cameraInput) {
    cameraInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            console.log('📸 Camera captured (mobile):', file.name, file.type, (file.size / 1024).toFixed(1) + 'KB');
            handleImageFile(file);
            showToast('✅ Photo captured successfully!', 'success');
        } else {
            showToast('No photo captured. Please try again.', 'error');
        }
    });
}

// ============================================
// FILE UPLOAD FUNCTIONALITY
// ============================================
if (uploadFileBtn) {
    uploadFileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (fileInput) {
            fileInput.value = '';
            fileInput.click();
        }
    });
}

if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            console.log('📁 File selected:', file.name, file.type, (file.size / 1024).toFixed(1) + 'KB');
            handleImageFile(file);
        }
    });
}

// ============================================
// REMOVE IMAGE
// ============================================
if (removeImageBtn) {
    removeImageBtn.addEventListener('click', () => {
        previewArea.style.display = 'none';
        imagePreview.src = '';
        currentImageFile = null;
        currentImageDataUrl = null;
        detectBtn.disabled = true;
        resultsSection.style.display = 'none';
        if (fileInput) fileInput.value = '';
        if (cameraInput) cameraInput.value = '';
        showToast('Image removed', 'info');
    });
}

// ============================================
// SAVE TO HISTORY FUNCTION
// ============================================
async function saveToHistory(detectionData) {
    try {
        // Format data for history
        const historyRecord = {
            id: detectionData.id || Date.now(),
            disease: detectionData.disease,
            confidence: detectionData.confidence,
            severity: detectionData.severity,
            chemical_treatment: detectionData.chemical_treatment || 'N/A',
            organic_treatment: detectionData.organic_treatment || 'N/A',
            cultural_practices: detectionData.cultural_practices || 'N/A',
            prevention_tips: detectionData.prevention_tips || 'N/A',
            timestamp: new Date().toISOString(),
            date: detectionData.date || new Date().toLocaleString(),
            response_time: detectionData.response_time || 'N/A',
            model_used: detectionData.model_used || 'Trained Model'
        };
        
        // Save to localStorage
        let history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
        history.unshift(historyRecord);
        // Keep only last 100 items
        if (history.length > 100) history = history.slice(0, 100);
        localStorage.setItem('scanHistory', JSON.stringify(history));
        
        // Try to save to backend API
        try {
            const response = await fetch('http://127.0.0.1:5000/api/history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(historyRecord)
            });
            
            if (response.ok) {
                console.log('✅ History saved to backend');
            } else {
                console.warn('⚠️ History saved only locally (backend error)');
            }
        } catch (apiError) {
            console.warn('⚠️ History saved only locally (backend not reachable)');
        }
        
        console.log('✅ History saved successfully');
        return true;
    } catch (error) {
        console.error('❌ Error saving history:', error);
        return false;
    }
    // In saveToHistory function, add this at the end:
console.log('✅ History saved. Total records:', history.length);
}

// ============================================
// DETECT DISEASE - Backend Integration with Trained Model
// ============================================
if (detectBtn) {
    detectBtn.addEventListener('click', async () => {
        if (!currentImageFile && !currentImageDataUrl) {
            showToast('Please upload or capture an image first', 'error');
            return;
        }
        
        detectionStartTime = Date.now();
        
        resultsSection.style.display = 'block';
        loadingSpinner.style.display = 'flex';
        resultsContent.style.display = 'none';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        try {
            // Prepare form data for backend
            const formData = new FormData();
            
            if (currentImageFile) {
                // Use the actual file
                formData.append('image', currentImageFile);
            } else if (currentImageDataUrl) {
                // Convert data URL to blob
                const blob = dataURLToBlob(currentImageDataUrl);
                formData.append('image', blob, 'leaf_image.jpg');
            }
            
            showToast('Sending image to AI model for analysis...', 'info');
            
            // === CALL YOUR TRAINED MODEL BACKEND ===
            const response = await fetch(`${API_BASE_URL}/detect`, {
                method: 'POST',
                body: formData,
                // Don't set Content-Type - browser will set it with boundary
            });
            
            // Check if response is OK
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || errorData.message || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Backend response:', data);
            
            if (!data.success && !data.prediction) {
                throw new Error(data.error || 'Detection failed');
            }
            
            // Process backend response
            const prediction = data.prediction || data.result || data;
            
            // Extract disease name and confidence
            let diseaseName = prediction.disease || prediction.class || prediction.label || 'Unknown Disease';
            let confidence = prediction.confidence || prediction.score || prediction.probability || 85;
            
            // Handle different response formats
            if (prediction.predictions && Array.isArray(prediction.predictions)) {
                const topPrediction = prediction.predictions[0];
                diseaseName = topPrediction.class || topPrediction.label || topPrediction.disease || diseaseName;
                confidence = topPrediction.confidence || topPrediction.score || topPrediction.probability || confidence;
            }
            
            // Ensure confidence is a number
            confidence = typeof confidence === 'number' ? confidence : parseFloat(confidence) || 85;
            confidence = Math.round(Math.min(100, Math.max(0, confidence)));
            
            // Get treatment recommendations based on disease
            const treatment = getTreatment(diseaseName, confidence);
            const responseTime = ((Date.now() - detectionStartTime) / 1000).toFixed(1);
            
            currentDetection = {
                id: Date.now(),
                disease: diseaseName,
                confidence: confidence,
                severity: treatment.severity,
                chemical_treatment: treatment.chemical_treatment,
                organic_treatment: treatment.organic_treatment,
                cultural_practices: treatment.cultural_practices,
                prevention_tips: treatment.prevention_tips,
                date: new Date().toLocaleString(),
                response_time: responseTime,
                backend_response: data,
                model_used: prediction.model || 'Trained Model'
            };
            
            // ============================================
            // AUTO-SAVE TO HISTORY
            // ============================================
            await saveToHistory(currentDetection);
            
            displayResults(currentDetection, responseTime);
            loadingSpinner.style.display = 'none';
            resultsContent.style.display = 'block';
            showToast(`✅ Disease detected: ${diseaseName} (${confidence}% confidence)`, 'success');
            
        } catch (error) {
            console.error('❌ Detection error:', error);
            loadingSpinner.style.display = 'none';
            
            // Show error message
            showToast(`❌ Error: ${error.message || 'Failed to detect disease'}`, 'error');
            
            // Display error in results
            resultsContent.style.display = 'block';
            document.getElementById('diseaseName').innerHTML = `<i class="fas fa-exclamation-triangle" style="color:#EF4444;"></i><span style="color:#EF4444;">Detection Failed</span>`;
            document.getElementById('confidenceValue').innerText = '0%';
            document.getElementById('confidenceBar').style.width = '0%';
            document.getElementById('severityText').innerText = 'Error';
            document.getElementById('chemicalTreatment').innerText = 'Please try again or check your connection';
            document.getElementById('organicTreatment').innerText = 'Make sure the backend server is running';
            document.getElementById('culturalPractices').innerText = `Error: ${error.message}`;
            document.getElementById('preventionTips').innerText = 'Try uploading a different image';
            document.getElementById('affectedArea').innerHTML = '--';
            document.getElementById('healthStatus').innerHTML = 'Error';
            document.getElementById('responseTime').innerHTML = '--';
            
            // Re-enable detect button after error
            detectBtn.disabled = false;
        }
    });
}

// ============================================
// UTILITY: Data URL to Blob
// ============================================
function dataURLToBlob(dataURL) {
    const arr = dataURL.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], { type: mime });
}

// ============================================
// TREATMENT DATABASE
// ============================================
function getTreatment(diseaseName, confidence) {
    const diseaseKey = diseaseName.toLowerCase().trim();
    
    // Comprehensive treatment database
    const treatments = {
        // Tomato Diseases
        "tomato late blight": {
            chemical: "Copper hydroxide (2g/L water) - Apply every 7-10 days",
            organic: "Neem oil 5ml/L + garlic extract - Spray twice weekly",
            cultural: "Remove infected leaves, avoid overhead watering",
            prevention: "Use resistant varieties, crop rotation",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "tomato early blight": {
            chemical: "Chlorothalonil (2ml/L water) - Apply at first sign",
            organic: "Baking soda solution (1 tbsp/L) + vegetable oil",
            cultural: "Mulch to prevent soil splash, water at base",
            prevention: "Use disease-free seeds, crop rotation",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "tomato septoria leaf spot": {
            chemical: "Copper-based fungicide",
            organic: "Neem oil + baking soda spray",
            cultural: "Remove infected leaves, improve air circulation",
            prevention: "Rotate crops, use disease-free seeds",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "tomato bacterial spot": {
            chemical: "Copper hydroxide + mancozeb",
            organic: "Copper soap spray",
            cultural: "Avoid overhead watering, remove infected plants",
            prevention: "Use disease-free seeds, crop rotation",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "tomato mosaic virus": {
            chemical: "No chemical treatment available",
            organic: "Remove infected plants immediately",
            cultural: "Control aphids, use virus-free seeds",
            prevention: "Resistant varieties, weed control",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "tomato healthy": {
            chemical: "No treatment needed",
            organic: "Compost tea monthly",
            cultural: "Maintain good practices",
            prevention: "Regular monitoring",
            severity: "Low"
        },
        
        // Potato Diseases
        "potato late blight": {
            chemical: "Mancozeb (2g/L water) - Apply preventatively",
            organic: "Copper spray (Bordeaux mixture)",
            cultural: "Hill soil around stems, destroy infected plants",
            prevention: "Use certified seed potatoes",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "potato early blight": {
            chemical: "Chlorothalonil - Apply at first sign",
            organic: "Baking soda solution",
            cultural: "Proper spacing, avoid overhead irrigation",
            prevention: "Crop rotation, disease-free seeds",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "potato black scurf": {
            chemical: "Seed treatment with fungicides",
            organic: "Use disease-free seed tubers",
            cultural: "Crop rotation, proper harvesting",
            prevention: "Certified seed potatoes",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "potato scab": {
            chemical: "Soil acidification with sulfur",
            organic: "Maintain soil pH below 5.2",
            cultural: "Irrigation during tuber formation",
            prevention: "Resistant varieties, crop rotation",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        },
        "potato healthy": {
            chemical: "No treatment needed",
            organic: "Seaweed extract spray",
            cultural: "Proper watering and hilling",
            prevention: "Regular monitoring",
            severity: "Low"
        },
        
        // Apple Diseases
        "apple scab": {
            chemical: "Sulfur-based fungicide",
            organic: "Compost tea + neem oil",
            cultural: "Rake and destroy fallen leaves",
            prevention: "Plant resistant varieties",
            severity: "Moderate"
        },
        "apple powdery mildew": {
            chemical: "Sulfur or potassium bicarbonate",
            organic: "Neem oil or milk spray",
            cultural: "Prune affected branches, improve air circulation",
            prevention: "Resistant varieties, proper spacing",
            severity: "Moderate"
        },
        "apple cedar rust": {
            chemical: "Myclobutanil fungicide",
            organic: "Sulfur dust",
            cultural: "Remove cedar trees nearby",
            prevention: "Resistant varieties",
            severity: "Moderate"
        },
        "apple healthy": {
            chemical: "No treatment needed",
            organic: "Beneficial insects",
            cultural: "Regular pruning",
            prevention: "Annual dormant oil spray",
            severity: "Low"
        },
        
        // Corn Diseases
        "corn common rust": {
            chemical: "Azoxystrobin fungicide",
            organic: "Sulfur dust",
            cultural: "Early planting",
            prevention: "Plant resistant hybrids",
            severity: "Moderate"
        },
        "corn northern leaf blight": {
            chemical: "Azoxystrobin or pyraclostrobin",
            organic: "Copper spray",
            cultural: "Crop rotation, destroy crop residues",
            prevention: "Resistant hybrids",
            severity: "Moderate"
        },
        "corn gray leaf spot": {
            chemical: "Propiconazole fungicide",
            organic: "Sulfur spray",
            cultural: "Tillage to bury crop residue",
            prevention: "Resistant hybrids, crop rotation",
            severity: "Moderate"
        },
        "corn healthy": {
            chemical: "No treatment needed",
            organic: "Compost application",
            cultural: "Proper spacing",
            prevention: "Crop rotation",
            severity: "Low"
        },
        
        // Wheat Diseases
        "wheat rust": {
            chemical: "Triazole fungicide",
            organic: "Sulfur dust",
            cultural: "Destroy volunteer wheat",
            prevention: "Resistant varieties",
            severity: "Moderate"
        },
        "wheat powdery mildew": {
            chemical: "Propiconazole or tebuconazole",
            organic: "Sulfur or neem oil",
            cultural: "Avoid dense planting",
            prevention: "Resistant varieties",
            severity: "Moderate"
        },
        "wheat fusarium head blight": {
            chemical: "Prothioconazole + tebuconazole",
            organic: "No effective organic treatment",
            cultural: "Crop rotation, tillage",
            prevention: "Resistant varieties, timely planting",
            severity: "Severe"
        },
        "wheat healthy": {
            chemical: "No treatment needed",
            organic: "Compost tea",
            cultural: "Proper fertilization",
            prevention: "Regular monitoring",
            severity: "Low"
        }
    };
    
    // Find matching treatment
    let treatment = null;
    for (const [key, value] of Object.entries(treatments)) {
        if (diseaseKey.includes(key) || key.includes(diseaseKey)) {
            treatment = value;
            break;
        }
    }
    
    // If no match found, use default
    if (!treatment) {
        treatment = {
            chemical: "Consult local agricultural extension for specific treatment",
            organic: "Apply neem oil or compost tea",
            cultural: "Remove affected plant parts",
            prevention: "Maintain proper plant spacing and watering",
            severity: confidence >= 85 ? "Severe" : confidence >= 70 ? "Moderate" : "Mild"
        };
    }
    
    return {
        chemical_treatment: treatment.chemical,
        organic_treatment: treatment.organic,
        cultural_practices: treatment.cultural,
        prevention_tips: treatment.prevention,
        severity: treatment.severity
    };
}

// ============================================
// DISPLAY RESULTS
// ============================================
function displayResults(data, responseTime) {
    // Disease Name
    document.getElementById('diseaseName').innerHTML = `<i class="fas fa-leaf"></i><span>${data.disease}</span>`;
    
    // Confidence Score
    document.getElementById('confidenceValue').innerText = `${data.confidence}%`;
    const confidenceBar = document.getElementById('confidenceBar');
    confidenceBar.style.width = `${data.confidence}%`;
    
    // Color based on confidence
    if (data.confidence >= 85) {
        confidenceBar.style.background = 'linear-gradient(90deg, #10B981, #34D399)';
    } else if (data.confidence >= 70) {
        confidenceBar.style.background = 'linear-gradient(90deg, #F59E0B, #FBBF24)';
    } else {
        confidenceBar.style.background = 'linear-gradient(90deg, #EF4444, #F87171)';
    }
    
    // Severity Tag
    const severityTag = document.getElementById('severityTag');
    document.getElementById('severityText').innerText = data.severity;
    severityTag.className = 'severity-tag';
    if (data.severity === 'Severe') {
        severityTag.classList.add('severe');
    } else if (data.severity === 'Moderate') {
        severityTag.classList.add('moderate');
    } else {
        severityTag.classList.add('mild');
    }
    
    // Treatment Recommendations
    document.getElementById('chemicalTreatment').innerText = data.chemical_treatment;
    document.getElementById('organicTreatment').innerText = data.organic_treatment;
    document.getElementById('culturalPractices').innerText = data.cultural_practices;
    document.getElementById('preventionTips').innerText = data.prevention_tips;
    
    // Statistics
    let affectedArea = data.confidence >= 85 ? '50-75%' : data.confidence >= 70 ? '25-50%' : data.confidence >= 50 ? '10-25%' : '<10%';
    let healthStatus = data.confidence >= 85 ? 'Advanced Disease' : data.confidence >= 70 ? 'Early Stage Disease' : data.confidence >= 50 ? 'Early Stage Disease' : 'Healthy / Very Mild';
    
    document.getElementById('affectedArea').innerHTML = affectedArea;
    document.getElementById('healthStatus').innerHTML = healthStatus;
    document.getElementById('responseTime').innerHTML = `${responseTime}s`;
}

// ============================================
// SAMPLE IMAGES (Auto-detect - Demo Only)
// ============================================
document.querySelectorAll('.sample-item').forEach(item => {
    item.addEventListener('click', async () => {
        const diseaseName = item.getAttribute('data-disease');
        const confidence = parseInt(item.getAttribute('data-confidence'));
        
        // Create a visual preview
        const placeholder = item.querySelector('.sample-placeholder');
        const canvas = document.createElement('canvas');
        canvas.width = 400;
        canvas.height = 300;
        const ctx = canvas.getContext('2d');
        
        // Draw sample image
        const gradient = ctx.createLinearGradient(0, 0, 400, 300);
        const colors = {
            'tomato': ['#1E293B', '#7F1D1D'],
            'potato': ['#1E293B', '#78350F'],
            'healthy': ['#1E293B', '#064E3B']
        };
        
        let colorKey = 'healthy';
        if (placeholder.classList.contains('tomato')) colorKey = 'tomato';
        else if (placeholder.classList.contains('potato')) colorKey = 'potato';
        
        gradient.addColorStop(0, colors[colorKey][0]);
        gradient.addColorStop(1, colors[colorKey][1]);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 400, 300);
        
        // Draw leaf
        ctx.fillStyle = '#10B981';
        ctx.beginPath();
        ctx.ellipse(200, 130, 80, 120, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw spots for diseased samples
        if (diseaseName.includes('Blight') || diseaseName.includes('Scab') || diseaseName.includes('Rust')) {
            ctx.fillStyle = '#8B4513';
            for (let i = 0; i < 8; i++) {
                ctx.beginPath();
                ctx.arc(140 + Math.random() * 120, 70 + Math.random() * 120, 10 + Math.random() * 20, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.fillStyle = '#D97706';
            for (let i = 0; i < 5; i++) {
                ctx.beginPath();
                ctx.arc(150 + Math.random() * 100, 80 + Math.random() * 100, 5 + Math.random() * 10, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        // Draw text
        ctx.fillStyle = 'white';
        ctx.font = 'bold 24px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(diseaseName, 200, 250);
        ctx.font = '18px Inter, sans-serif';
        ctx.fillStyle = '#A5B4FC';
        ctx.fillText(`Confidence: ${confidence}%`, 200, 285);
        
        // Set preview
        currentImageDataUrl = canvas.toDataURL('image/jpeg');
        imagePreview.src = currentImageDataUrl;
        previewArea.style.display = 'block';
        detectBtn.disabled = false;
        resultsSection.style.display = 'none';
        showToast(`Sample: ${diseaseName} loaded!`, 'success');
        
        // Auto-detect for samples
        setTimeout(() => {
            detectionStartTime = Date.now();
            resultsSection.style.display = 'block';
            loadingSpinner.style.display = 'flex';
            resultsContent.style.display = 'none';
            
            setTimeout(() => {
                const treatment = getTreatment(diseaseName, confidence);
                const responseTime = ((Date.now() - detectionStartTime) / 1000).toFixed(1);
                
                currentDetection = {
                    id: Date.now(),
                    disease: diseaseName,
                    confidence: confidence,
                    severity: treatment.severity,
                    chemical_treatment: treatment.chemical_treatment,
                    organic_treatment: treatment.organic_treatment,
                    cultural_practices: treatment.cultural_practices,
                    prevention_tips: treatment.prevention_tips,
                    date: new Date().toLocaleString(),
                    response_time: responseTime,
                    is_sample: true
                };
                
                // Auto-save sample detection to history
                saveToHistory(currentDetection);
                
                displayResults(currentDetection, responseTime);
                loadingSpinner.style.display = 'none';
                resultsContent.style.display = 'block';
                showToast('Sample disease detected!', 'success');
            }, 1500);
        }, 500);
    });
});

// ============================================
// SAVE TO HISTORY (Button)
// ============================================
document.getElementById('saveToHistoryBtn')?.addEventListener('click', async () => {
    if (!currentDetection) {
        showToast('No detection results to save', 'error');
        return;
    }
    
    // Check if already saved
    if (currentDetection.savedAt) {
        showToast('Already saved to history!', 'info');
        return;
    }
    
    try {
        const historyRecord = {
            id: currentDetection.id || Date.now(),
            disease: currentDetection.disease,
            confidence: currentDetection.confidence,
            severity: currentDetection.severity,
            chemical_treatment: currentDetection.chemical_treatment || 'N/A',
            organic_treatment: currentDetection.organic_treatment || 'N/A',
            cultural_practices: currentDetection.cultural_practices || 'N/A',
            prevention_tips: currentDetection.prevention_tips || 'N/A',
            timestamp: new Date().toISOString(),
            date: currentDetection.date || new Date().toLocaleString(),
            response_time: currentDetection.response_time || 'N/A',
            model_used: currentDetection.model_used || 'Trained Model'
        };
        
        // Save to localStorage
        let history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
        history.unshift(historyRecord);
        if (history.length > 100) history = history.slice(0, 100);
        localStorage.setItem('scanHistory', JSON.stringify(history));
        
        // Try to save to backend
        try {
            await fetch('http://127.0.0.1:5000/api/history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(historyRecord)
            });
        } catch (apiError) {
            // Backend not available, but we already saved locally
            console.log('History saved locally only');
        }
        
        // Mark as saved
        currentDetection.savedAt = new Date().toISOString();
        
        showToast('✅ Saved to history successfully!', 'success');
    } catch (error) {
        console.error('Error saving to history:', error);
        showToast('❌ Failed to save to history', 'error');
    }
});

// ============================================
// DOWNLOAD PDF
// ============================================
document.getElementById('downloadPdfBtn')?.addEventListener('click', () => {
    if (!currentDetection) {
        showToast('No detection results to download', 'error');
        return;
    }
    
    showToast('Generating PDF...', 'info');
    
    const win = window.open('', '_blank');
    if (!win) {
        showToast('Please allow popups to download PDF', 'error');
        return;
    }
    
    win.document.write(`
        <html>
        <head>
            <title>FarmIntel AI - Disease Report</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Inter', Arial, sans-serif; padding: 40px; max-width: 900px; margin: 0 auto; background: #f8fafc; }
                .header { background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
                .header h1 { font-size: 28px; margin-bottom: 5px; }
                .header p { opacity: 0.8; }
                .section { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
                .section h2 { color: #4F46E5; font-size: 18px; margin-bottom: 10px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }
                .section h3 { color: #1E293B; font-size: 14px; margin: 8px 0 4px 0; }
                .section p { color: #475569; font-size: 14px; line-height: 1.5; }
                .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
                .stat { text-align: center; background: #F1F5F9; padding: 15px; border-radius: 8px; }
                .stat .value { font-size: 20px; font-weight: bold; color: #1E293B; }
                .stat .label { font-size: 12px; color: #64748B; }
                .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; }
                .badge.severe { background: #FEE2E2; color: #DC2626; }
                .badge.moderate { background: #FEF3C7; color: #D97706; }
                .badge.mild { background: #D1FAE5; color: #059669; }
                .footer { text-align: center; color: #94A3B8; font-size: 12px; margin-top: 30px; border-top: 1px solid #E2E8F0; padding-top: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌾 FarmIntel AI - Disease Report</h1>
                <p>Generated: ${new Date().toLocaleString()}</p>
            </div>
            
            <div class="section">
                <h2>🔬 Detection Results</h2>
                <p style="font-size: 20px; font-weight: bold; margin: 10px 0;">${currentDetection.disease}</p>
                <p>Confidence: <strong>${currentDetection.confidence}%</strong></p>
                <p>Severity: <span class="badge ${currentDetection.severity.toLowerCase()}">${currentDetection.severity}</span></p>
                <p>Response Time: ${currentDetection.response_time}s</p>
                ${currentDetection.model_used ? `<p>Model: ${currentDetection.model_used}</p>` : ''}
            </div>
            
            <div class="section">
                <h2>💊 Treatment Recommendations</h2>
                <h3>Chemical Treatment</h3>
                <p>${currentDetection.chemical_treatment}</p>
                <h3>Organic Treatment</h3>
                <p>${currentDetection.organic_treatment}</p>
                <h3>Cultural Practices</h3>
                <p>${currentDetection.cultural_practices}</p>
                <h3>Prevention Tips</h3>
                <p>${currentDetection.prevention_tips}</p>
            </div>
            
            <div class="section">
                <h2>📊 Statistics</h2>
                <div class="grid">
                    <div class="stat">
                        <div class="value">${document.getElementById('affectedArea').innerText}</div>
                        <div class="label">Affected Area</div>
                    </div>
                    <div class="stat">
                        <div class="value">${document.getElementById('healthStatus').innerText}</div>
                        <div class="label">Health Status</div>
                    </div>
                    <div class="stat">
                        <div class="value">${currentDetection.response_time}s</div>
                        <div class="label">Response Time</div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>FarmIntel AI - Smart Agriculture Solution</p>
                <p>Report ID: ${currentDetection.id}</p>
            </div>
        </body>
        </html>
    `);
    win.document.close();
    setTimeout(() => win.print(), 500);
});

// ============================================
// SHARE RESULTS
// ============================================
document.getElementById('shareResultsBtn')?.addEventListener('click', () => {
    if (!currentDetection) {
        showToast('No detection results to share', 'error');
        return;
    }
    
    const text = `🌾 FarmIntel AI Report\n\n` +
        `Disease: ${currentDetection.disease}\n` +
        `Confidence: ${currentDetection.confidence}%\n` +
        `Severity: ${currentDetection.severity}\n\n` +
        `💊 Chemical: ${currentDetection.chemical_treatment}\n\n` +
        `🌿 Organic: ${currentDetection.organic_treatment}\n\n` +
        `🛡️ Prevention: ${currentDetection.prevention_tips}\n\n` +
        `📅 ${new Date().toLocaleString()}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'FarmIntel AI - Disease Report',
            text: text
        }).catch(() => {});
    } else {
        navigator.clipboard.writeText(text)
            .then(() => showToast('📋 Results copied to clipboard!', 'success'))
            .catch(() => showToast('Could not copy to clipboard', 'error'));
    }
});

// ============================================
// MOBILE SIDEBAR
// ============================================
const mobileToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
        overlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
    });
}

if (overlay) {
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    });
}

// ============================================
// LOGOUT
// ============================================
document.getElementById('logoutBtn')?.addEventListener('click', () => {
    localStorage.removeItem('farmintel_user');
    localStorage.removeItem('farmintel_token');
    localStorage.removeItem('farmintel_logged_in');
    localStorage.removeItem('userName');
    window.location.href = '../index.html';
});

// ============================================
// USER NAME
// ============================================
const userStr = localStorage.getItem('farmintel_user');
if (userStr) {
    try {
        const user = JSON.parse(userStr);
        const userNameElement = document.getElementById('userName');
        if (userNameElement) userNameElement.textContent = user.name || 'Farmer';
    } catch (e) {}
} else {
    const savedName = localStorage.getItem('userName');
    const userNameElement = document.getElementById('userName');
    if (userNameElement) userNameElement.textContent = savedName || 'John Farmer';
}

// ============================================
// THEME TOGGLE
// ============================================
let isDark = false;
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        themeToggle.innerHTML = isDark ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
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

// ============================================
// CHECK BACKEND HEALTH
// ============================================
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend is healthy:', data);
            showToast('✅ Connected to AI model service', 'success');
        } else {
            console.warn('⚠️ Backend response error:', response.status);
            showToast('⚠️ Backend service issue. Please check your connection.', 'warning');
        }
    } catch (error) {
        console.warn('⚠️ Backend not reachable:', error.message);
        showToast('⚠️ Cannot connect to AI service. Make sure backend is running.', 'warning');
    }
}

// ============================================
// INITIALIZE
// ============================================
createParticles();
checkBackendHealth();

// Initialize AOS
if (typeof AOS !== 'undefined') {
    AOS.init({
        duration: 800,
        once: true,
        offset: 50
    });
}

console.log('🌾 FarmIntel AI - Detection Module Loaded');
console.log('📸 Camera support:', !!navigator.mediaDevices?.getUserMedia);
console.log('🔗 Backend API:', API_BASE_URL);