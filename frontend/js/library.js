/**
 * FarmIntel AI - Disease Library JavaScript
 * Complete Backend Integration with 29 PlantVillage Diseases
 */

// Initialize AOS
AOS.init({ duration: 800, once: true, offset: 50 });

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const resetAllBtn = document.getElementById('resetAllBtn');
const diseaseGrid = document.getElementById('diseaseGrid');
const resultsCountSpan = document.getElementById('resultsCount');
const noResultsDiv = document.getElementById('noResults');

// Global variables
let currentCropFilter = 'all';
let currentSearchTerm = '';
let diseaseDatabase = [];

// ========================================
// 29 DISEASE CLASSES (PlantVillage Dataset)
// ========================================

const DISEASE_CLASSES = [
    // Apple (4)
    { id: 'apple_scab', name: 'Apple Scab', crop: 'Apple', severity: 'Moderate' },
    { id: 'apple_black_rot', name: 'Apple Black Rot', crop: 'Apple', severity: 'Severe' },
    { id: 'apple_cedar_rust', name: 'Apple Cedar Rust', crop: 'Apple', severity: 'Moderate' },
    { id: 'apple_healthy', name: 'Apple Healthy', crop: 'Apple', severity: 'Low' },
    
    // Bell Pepper (2)
    { id: 'bell_pepper_bacterial_spot', name: 'Bell Pepper Bacterial Spot', crop: 'Bell Pepper', severity: 'Moderate' },
    { id: 'bell_pepper_healthy', name: 'Bell Pepper Healthy', crop: 'Bell Pepper', severity: 'Low' },
    
    // Cherry (2)
    { id: 'cherry_healthy', name: 'Cherry Healthy', crop: 'Cherry', severity: 'Low' },
    { id: 'cherry_powdery_mildew', name: 'Cherry Powdery Mildew', crop: 'Cherry', severity: 'Moderate' },
    
    // Corn (4)
    { id: 'corn_cercospora_leaf_spot', name: 'Corn Cercospora Leaf Spot', crop: 'Corn', severity: 'Moderate' },
    { id: 'corn_common_rust', name: 'Corn Common Rust', crop: 'Corn', severity: 'Moderate' },
    { id: 'corn_healthy', name: 'Corn Healthy', crop: 'Corn', severity: 'Low' },
    { id: 'corn_northern_leaf_blight', name: 'Corn Northern Leaf Blight', crop: 'Corn', severity: 'Severe' },
    
    // Grape (4)
    { id: 'grape_black_rot', name: 'Grape Black Rot', crop: 'Grape', severity: 'Severe' },
    { id: 'grape_esca', name: 'Grape Esca', crop: 'Grape', severity: 'Severe' },
    { id: 'grape_healthy', name: 'Grape Healthy', crop: 'Grape', severity: 'Low' },
    { id: 'grape_leaf_blight', name: 'Grape Leaf Blight', crop: 'Grape', severity: 'Moderate' },
    
    // Peach (2)
    { id: 'peach_bacterial_spot', name: 'Peach Bacterial Spot', crop: 'Peach', severity: 'Moderate' },
    { id: 'peach_healthy', name: 'Peach Healthy', crop: 'Peach', severity: 'Low' },
    
    // Potato (3)
    { id: 'potato_early_blight', name: 'Potato Early Blight', crop: 'Potato', severity: 'Moderate' },
    { id: 'potato_healthy', name: 'Potato Healthy', crop: 'Potato', severity: 'Low' },
    { id: 'potato_late_blight', name: 'Potato Late Blight', crop: 'Potato', severity: 'Severe' },
    
    // Strawberry (2)
    { id: 'strawberry_healthy', name: 'Strawberry Healthy', crop: 'Strawberry', severity: 'Low' },
    { id: 'strawberry_leaf_scorch', name: 'Strawberry Leaf Scorch', crop: 'Strawberry', severity: 'Moderate' },
    
    // Tomato (6)
    { id: 'tomato_bacterial_spot', name: 'Tomato Bacterial Spot', crop: 'Tomato', severity: 'Moderate' },
    { id: 'tomato_early_blight', name: 'Tomato Early Blight', crop: 'Tomato', severity: 'Moderate' },
    { id: 'tomato_healthy', name: 'Tomato Healthy', crop: 'Tomato', severity: 'Low' },
    { id: 'tomato_late_blight', name: 'Tomato Late Blight', crop: 'Tomato', severity: 'Severe' },
    { id: 'tomato_septoria_leaf_spot', name: 'Tomato Septoria Leaf Spot', crop: 'Tomato', severity: 'Moderate' },
    { id: 'tomato_yellow_leaf_curl_virus', name: 'Tomato Yellow Leaf Curl Virus', crop: 'Tomato', severity: 'Severe' }
];

// ========================================
// DISEASE DETAILS DATABASE
// ========================================

const DISEASE_DETAILS = {
    // Apple Diseases
    'Apple Scab': {
        symptoms: 'Olive-green to black spots on leaves and fruit. Leaves may curl and drop prematurely.',
        causes: 'Fungal pathogen Venturia inaequalis. Overwinters in fallen leaves.',
        treatment: 'Apply sulfur or captan fungicides. Rake and destroy fallen leaves.',
        organic: 'Sulfur spray. Neem oil application. Compost tea.',
        prevention: 'Plant resistant varieties. Prune for air circulation. Clean up fallen leaves.',
        season: 'Spring, wet conditions'
    },
    'Apple Black Rot': {
        symptoms: 'Purple spots on leaves turning brown. Fruit shows black, rotting lesions with concentric rings.',
        causes: 'Botryosphaeria obtusa fungus. Enters through wounds.',
        treatment: 'Prune dead wood. Apply captan or thiophanate-methyl fungicides.',
        organic: 'Copper spray. Remove infected fruit and branches.',
        prevention: 'Remove mummified fruit. Prune infected branches. Maintain tree health.',
        season: 'Warm, wet weather'
    },
    'Apple Cedar Rust': {
        symptoms: 'Bright yellow-orange spots on leaves. Small cup-like structures form on spots.',
        causes: 'Gymnosporangium juniperi-virginianae. Requires both apple and cedar trees.',
        treatment: 'Apply myclobutanil or mancozeb. Remove nearby cedar galls.',
        organic: 'Sulfur spray. Prune out galls on cedar trees.',
        prevention: 'Plant resistant varieties. Remove cedar trees within 2 miles.',
        season: 'Spring, rainy weather'
    },
    'Apple Healthy': {
        symptoms: 'Healthy green leaves, proper fruit development, strong branches.',
        causes: 'Good orchard management practices.',
        treatment: 'Regular pruning, fertilization, and pest monitoring.',
        organic: 'Compost application. Beneficial insect habitat. Dormant oil spray.',
        prevention: 'Regular maintenance and monitoring. Integrated pest management.',
        season: 'All growing season'
    },

    // Bell Pepper Diseases
    'Bell Pepper Bacterial Spot': {
        symptoms: 'Small, water-soaked spots on leaves that turn brown with yellow halos.',
        causes: 'Xanthomonas campestris bacteria. Spreads by splashing water.',
        treatment: 'Apply copper-based bactericides. Remove infected plants.',
        organic: 'Bacillus subtilis spray. Compost tea.',
        prevention: 'Use disease-free seeds. Avoid overhead irrigation. Crop rotation.',
        season: 'Warm, wet weather'
    },
    'Bell Pepper Healthy': {
        symptoms: 'Healthy green foliage, strong stems, good fruit production.',
        causes: 'Proper cultivation practices.',
        treatment: 'Regular watering, fertilization, and pest monitoring.',
        organic: 'Compost tea. Seaweed extract.',
        prevention: 'Regular monitoring. Proper spacing. Crop rotation.',
        season: 'All growing season'
    },

    // Cherry Diseases
    'Cherry Healthy': {
        symptoms: 'Healthy green leaves, good fruit development, strong branches.',
        causes: 'Good orchard management.',
        treatment: 'Regular pruning, fertilization, and pest monitoring.',
        organic: 'Compost application. Neem oil preventive spray.',
        prevention: 'Regular maintenance. Proper orchard sanitation.',
        season: 'All growing season'
    },
    'Cherry Powdery Mildew': {
        symptoms: 'White powdery growth on leaves and young shoots.',
        causes: 'Podosphaera clandestina fungus.',
        treatment: 'Apply sulfur or myclobutanil fungicides.',
        organic: 'Milk spray (1:9 with water). Sulfur dust.',
        prevention: 'Prune for air circulation. Plant resistant varieties.',
        season: 'Spring to early summer'
    },

    // Corn Diseases
    'Corn Cercospora Leaf Spot': {
        symptoms: 'Small rectangular brown spots with yellow halos.',
        causes: 'Cercospora zeae-maydis fungus.',
        treatment: 'Apply azoxystrobin or pyraclostrobin.',
        organic: 'Copper spray. Neem oil application.',
        prevention: 'Crop rotation. Plant resistant hybrids. Residue management.',
        season: 'Warm, humid weather'
    },
    'Corn Common Rust': {
        symptoms: 'Small, cinnamon-brown pustules scattered on leaves. Pustules turn black as plant matures.',
        causes: 'Puccinia sorghi fungus. Spreads by wind.',
        treatment: 'Apply azoxystrobin or pyraclostrobin fungicides.',
        organic: 'Sulfur dust. Neem oil spray.',
        prevention: 'Plant resistant hybrids. Early planting.',
        season: 'Cool, moist conditions'
    },
    'Corn Healthy': {
        symptoms: 'Dark green leaves, strong stalks, fully filled ears.',
        causes: 'Good agricultural practices.',
        treatment: 'Proper fertilization, irrigation, and weed management.',
        organic: 'Compost application. Cover cropping.',
        prevention: 'Crop rotation. Soil health management.',
        season: 'All growing season'
    },
    'Corn Northern Leaf Blight': {
        symptoms: 'Long, cigar-shaped gray-green to tan lesions on leaves.',
        causes: 'Exserohilum turcicum fungus. Favored by humid conditions.',
        treatment: 'Apply strobilurin or triazole fungicides.',
        organic: 'Copper spray. Compost tea.',
        prevention: 'Use resistant hybrids. Crop rotation. Residue management.',
        season: 'Warm, humid weather'
    },

    // Grape Diseases
    'Grape Black Rot': {
        symptoms: 'Brown to black circular spots on leaves. Fruit shrivels into hard black mummies.',
        causes: 'Guignardia bidwellii fungus. Overwinters in mummified fruit.',
        treatment: 'Apply myclobutanil or mancozeb at bloom and fruit set.',
        organic: 'Sulfur spray. Remove mummified fruit.',
        prevention: 'Prune for air circulation. Clean up fallen fruit. Plant resistant varieties.',
        season: 'Warm, wet weather'
    },
    'Grape Esca': {
        symptoms: 'Brown spots with dark borders on leaves. White rot in wood.',
        causes: 'Phaeomoniella chlamydospora fungus.',
        treatment: 'Remove infected wood. Protect pruning wounds.',
        organic: 'Bordeaux mixture. Trichoderma application.',
        prevention: 'Use disease-free planting material. Protect wounds after pruning.',
        season: 'Spring to fall'
    },
    'Grape Healthy': {
        symptoms: 'Healthy green foliage, proper fruit clusters, good vine growth.',
        causes: 'Good vineyard management.',
        treatment: 'Regular pruning. Proper fertilization. Canopy management.',
        organic: 'Compost application. Cover crops. Seaweed extract.',
        prevention: 'Integrated pest management. Regular monitoring.',
        season: 'All growing season'
    },
    'Grape Leaf Blight': {
        symptoms: 'Brown spots on leaves that enlarge and coalesce.',
        causes: 'Pseudocercospora vitis fungus.',
        treatment: 'Apply copper-based fungicides.',
        organic: 'Copper spray. Neem oil application.',
        prevention: 'Improve air circulation. Remove infected leaves.',
        season: 'Warm, humid weather'
    },

    // Peach Diseases
    'Peach Bacterial Spot': {
        symptoms: 'Small, angular water-soaked spots on leaves that turn purple-brown.',
        causes: 'Xanthomonas arboricola bacteria.',
        treatment: 'Apply copper-based bactericides. Remove infected branches.',
        organic: 'Copper spray. Bacillus subtilis application.',
        prevention: 'Plant resistant varieties. Avoid overhead irrigation.',
        season: 'Warm, wet weather'
    },
    'Peach Healthy': {
        symptoms: 'Healthy green leaves, good fruit development, strong branches.',
        causes: 'Good orchard management.',
        treatment: 'Regular pruning, fertilization, and pest monitoring.',
        organic: 'Compost application. Neem oil preventive spray.',
        prevention: 'Regular maintenance. Proper orchard sanitation.',
        season: 'All growing season'
    },

    // Potato Diseases
    'Potato Early Blight': {
        symptoms: 'Small dark spots with concentric rings on lower leaves. Leaves turn yellow and die.',
        causes: 'Alternaria solani fungus. Common in warm, humid conditions.',
        treatment: 'Chlorothalonil or mancozeb fungicides. Rotate with non-host crops.',
        organic: 'Baking soda solution. Compost tea. Copper spray.',
        prevention: 'Use disease-free seed potatoes. Maintain proper spacing. Avoid overhead irrigation.',
        season: 'Warm, humid weather'
    },
    'Potato Healthy': {
        symptoms: 'Healthy green foliage, vigorous growth, good tuber development.',
        causes: 'Proper cultivation practices.',
        treatment: 'Consistent moisture, proper fertilization, hilling.',
        organic: 'Compost application. Seaweed extract for nutrition.',
        prevention: 'Crop rotation. Use certified seed potatoes.',
        season: 'All growing season'
    },
    'Potato Late Blight': {
        symptoms: 'Dark brown to black lesions on leaves. White mold on leaf undersides. Tubers show dark, shrunken areas.',
        causes: 'Phytophthora infestans - same pathogen as tomato late blight.',
        treatment: 'Apply mancozeb or chlorothalonil. Destroy infected plants immediately.',
        organic: 'Copper spray (Bordeaux mixture). Bacillus subtilis application.',
        prevention: 'Use certified disease-free seed potatoes. Hill soil around stems. Avoid overhead irrigation.',
        season: 'Cool, wet weather'
    },

    // Strawberry Diseases
    'Strawberry Healthy': {
        symptoms: 'Healthy green leaves, good fruit development, strong runners.',
        causes: 'Good cultivation practices.',
        treatment: 'Regular watering, fertilization, and pest monitoring.',
        organic: 'Compost tea. Seaweed extract. Mulching.',
        prevention: 'Regular monitoring. Proper spacing. Remove old leaves.',
        season: 'All growing season'
    },
    'Strawberry Leaf Scorch': {
        symptoms: 'Purple to brown spots on leaves that enlarge and coalesce.',
        causes: 'Diplocarpon earliana fungus.',
        treatment: 'Apply captan or myclobutanil fungicides.',
        organic: 'Compost tea. Neem oil spray.',
        prevention: 'Use disease-free plants. Crop rotation. Remove infected leaves.',
        season: 'Warm, wet weather'
    },

    // Tomato Diseases
    'Tomato Bacterial Spot': {
        symptoms: 'Small dark spots with yellow halos on leaves. Spots may coalesce and cause defoliation.',
        causes: 'Xanthomonas campestris bacteria. Spreads by splashing water.',
        treatment: 'Apply copper-based bactericides. Remove infected plants.',
        organic: 'Bacillus subtilis. Copper spray. Compost tea.',
        prevention: 'Use disease-free seeds. Avoid overhead irrigation. Crop rotation.',
        season: 'Warm, wet weather'
    },
    'Tomato Early Blight': {
        symptoms: 'Dark spots with concentric rings (target-like appearance) on lower leaves. Yellowing around spots.',
        causes: 'Alternaria solani fungus. Survives in soil and plant debris.',
        treatment: 'Apply chlorothalonil or mancozeb fungicides every 7-10 days.',
        organic: 'Baking soda solution (1 tbsp/L) with vegetable oil. Copper spray.',
        prevention: 'Mulch to prevent soil splash. Water at base. Stake plants for air circulation.',
        season: 'Warm, humid weather'
    },
    'Tomato Healthy': {
        symptoms: 'Vibrant green leaves, strong stem growth, healthy fruit development.',
        causes: 'Proper care and maintenance.',
        treatment: 'Continue regular care: water consistently, fertilize monthly, prune suckers.',
        organic: 'Compost tea application monthly. Neem oil for preventive care.',
        prevention: 'Maintain good cultural practices. Regular monitoring.',
        season: 'All growing season'
    },
    'Tomato Late Blight': {
        symptoms: 'Dark, water-soaked spots on leaves that turn brown and crispy. White fuzzy growth on undersides during humid conditions.',
        causes: 'Fungal pathogen Phytophthora infestans. Spreads rapidly in cool, wet weather.',
        treatment: 'Apply copper-based fungicides (copper hydroxide 2g/L). Remove and destroy infected plants.',
        organic: 'Neem oil 5ml/L + garlic extract spray. Bacillus subtilis as biological control.',
        prevention: 'Use resistant varieties. Avoid overhead irrigation. Provide good air circulation. Rotate crops every 3 years.',
        season: 'Cool, wet weather (spring and fall)'
    },
    'Tomato Septoria Leaf Spot': {
        symptoms: 'Small circular spots with gray centers and dark borders on lower leaves.',
        causes: 'Septoria lycopersici fungus. Survives on plant debris.',
        treatment: 'Apply chlorothalonil or mancozeb fungicides.',
        organic: 'Baking soda solution. Copper spray. Compost tea.',
        prevention: 'Remove lower leaves. Mulch to prevent soil splash. Crop rotation.',
        season: 'Warm, humid weather'
    },
    'Tomato Yellow Leaf Curl Virus': {
        symptoms: 'Yellowing and curling of leaves. Stunted growth. Reduced fruit production.',
        causes: 'Begomovirus transmitted by whiteflies.',
        treatment: 'No cure - Control whitefly vectors. Remove infected plants.',
        organic: 'Neem oil for whitefly control. Yellow sticky traps. Reflective mulch.',
        prevention: 'Use resistant varieties. Insect netting. Control whiteflies. Remove weed hosts.',
        season: 'Warm weather (whitefly activity)'
    }
};

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

// Build full disease database
function buildDiseaseDatabase() {
    return DISEASE_CLASSES.map(disease => {
        const details = DISEASE_DETAILS[disease.name] || DISEASE_DETAILS['Tomato Late Blight'];
        return {
            ...disease,
            symptoms: details.symptoms || 'Information not available',
            causes: details.causes || 'Information not available',
            treatment: details.treatment || 'Consult local agronomist',
            organicTreatment: details.organic || 'Neem oil 5ml/L. Spray weekly.',
            prevention: details.prevention || 'Practice good crop management. Regular monitoring.',
            season: details.season || 'Varies by region'
        };
    });
}

// Fetch diseases from backend API
async function fetchDiseases() {
    try {
        // First check if backend is available
        const healthResponse = await fetch(`${API_BASE_URL}/health`);
        if (!healthResponse.ok) {
            throw new Error('Backend not available');
        }

        // Try to get treatment list from backend
        const response = await fetch(`${API_BASE_URL}/treatment/list`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.diseases) {
                // Map backend disease names to our database
                const backendDiseases = data.diseases;
                const enhancedDiseases = backendDiseases.map(name => {
                    // Find matching disease in our classes
                    const matched = DISEASE_CLASSES.find(d => 
                        d.name.toLowerCase() === name.toLowerCase() ||
                        name.toLowerCase().includes(d.name.toLowerCase()) ||
                        d.name.toLowerCase().includes(name.toLowerCase())
                    );
                    
                    if (matched) {
                        const details = DISEASE_DETAILS[matched.name] || DISEASE_DETAILS['Tomato Late Blight'];
                        return {
                            ...matched,
                            symptoms: details.symptoms || 'Information not available',
                            causes: details.causes || 'Information not available',
                            treatment: details.treatment || 'Consult local agronomist',
                            organicTreatment: details.organic || 'Neem oil 5ml/L. Spray weekly.',
                            prevention: details.prevention || 'Practice good crop management.',
                            season: details.season || 'Varies by region'
                        };
                    }
                    return null;
                }).filter(d => d !== null);
                
                if (enhancedDiseases.length > 0) {
                    diseaseDatabase = enhancedDiseases;
                    localStorage.setItem('diseaseDatabase', JSON.stringify(diseaseDatabase));
                    renderDiseases();
                    return;
                }
            }
        }
        // Fallback to local database
        loadFromLocalStorage();
    } catch (error) {
        console.error('Error fetching diseases:', error);
        loadFromLocalStorage();
    }
}

// Load from localStorage fallback
function loadFromLocalStorage() {
    const stored = localStorage.getItem('diseaseDatabase');
    if (stored && JSON.parse(stored).length > 0) {
        diseaseDatabase = JSON.parse(stored);
    } else {
        diseaseDatabase = buildDiseaseDatabase();
        localStorage.setItem('diseaseDatabase', JSON.stringify(diseaseDatabase));
    }
    renderDiseases();
}

// ========================================
// FIXED: Get crop icon using EMOJIS
// ========================================
function getCropIcon(crop) {
    const icons = {
        'Apple': '🍎',
        'Tomato': '🍅',
        'Potato': '🥔',
        'Corn': '🌽',
        'Grape': '🍇',
        'Peach': '🍑',
        'Strawberry': '🍓',
        'Cherry': '🍒',
        'Bell Pepper': '🫑'
    };
    return icons[crop] || '🌿';
}

// Get crop color
function getCropColor(crop) {
    const colors = {
        'Apple': 'apple',
        'Tomato': 'tomato',
        'Potato': 'potato',
        'Corn': 'corn',
        'Grape': 'grape',
        'Peach': 'peach',
        'Strawberry': 'strawberry',
        'Cherry': 'cherry',
        'Bell Pepper': 'bellpepper'
    };
    return colors[crop] || 'default';
}

// Get severity class
function getSeverityClass(severity) {
    if (severity === 'Severe') return 'high';
    if (severity === 'Moderate') return 'moderate';
    return 'low';
}

// Filter diseases
function getFilteredDiseases() {
    let filtered = [...diseaseDatabase];
    
    if (currentCropFilter !== 'all') {
        filtered = filtered.filter(d => d.crop === currentCropFilter);
    }
    
    if (currentSearchTerm) {
        const term = currentSearchTerm.toLowerCase();
        filtered = filtered.filter(d => 
            d.name.toLowerCase().includes(term) ||
            d.crop.toLowerCase().includes(term) ||
            (d.symptoms && d.symptoms.toLowerCase().includes(term)) ||
            (d.treatment && d.treatment.toLowerCase().includes(term))
        );
    }
    
    return filtered;
}

// ========================================
// FIXED: Render diseases with EMOJI icons
// ========================================
function renderDiseases() {
    const filtered = getFilteredDiseases();
    resultsCountSpan.innerText = filtered.length;
    
    if (filtered.length === 0) {
        diseaseGrid.style.display = 'none';
        noResultsDiv.style.display = 'block';
        return;
    }
    
    diseaseGrid.style.display = 'grid';
    noResultsDiv.style.display = 'none';
    
    diseaseGrid.innerHTML = filtered.map(disease => `
        <div class="disease-card" data-id="${disease.id}">
            <div class="card-header">
                <div class="crop-icon ${getCropColor(disease.crop)}">
                    <span style="font-size: 1.5rem; line-height: 1;">${getCropIcon(disease.crop)}</span>
                </div>
                <div class="severity-badge ${getSeverityClass(disease.severity)}">
                    ${disease.severity} Risk
                </div>
            </div>
            <div class="card-body">
                <h3>${disease.name}</h3>
                <p class="symptoms-preview">${disease.symptoms ? disease.symptoms.substring(0, 80) + '...' : 'Information not available'}</p>
                <div class="disease-crop">
                    <i class="fas fa-tractor"></i>
                    <span>${disease.crop}</span>
                </div>
            </div>
            <div class="card-footer">
                <button class="read-more-btn" onclick="showDiseaseDetail('${disease.id}')">
                    READ MORE <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// ========================================
// FIXED: Show disease detail with EMOJI icons
// ========================================
window.showDiseaseDetail = function(diseaseId) {
    const disease = diseaseDatabase.find(d => d.id === diseaseId);
    if (!disease) return;
    
    document.getElementById('modalDiseaseName').innerText = disease.name;
    
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="disease-detail">
            <div class="detail-header">
                <div class="crop-tag ${getCropColor(disease.crop)}">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">${getCropIcon(disease.crop)}</span>
                    <span>${disease.crop}</span>
                </div>
                <div class="severity-badge ${getSeverityClass(disease.severity)}">${disease.severity} Risk</div>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-stethoscope"></i> Symptoms</h4>
                <p>${disease.symptoms || 'Information not available'}</p>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-microscope"></i> Causes</h4>
                <p>${disease.causes || 'Information not available'}</p>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-flask"></i> Chemical Treatment</h4>
                <p>${disease.treatment || 'Consult local agronomist'}</p>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-leaf"></i> Organic Treatment</h4>
                <p>${disease.organicTreatment || 'Neem oil 5ml/L. Spray weekly.'}</p>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-shield-alt"></i> Prevention</h4>
                <p>${disease.prevention || 'Practice good crop management. Regular monitoring.'}</p>
            </div>
            
            <div class="detail-section">
                <h4><i class="fas fa-calendar-alt"></i> Active Season</h4>
                <p>${disease.season || 'Varies by region'}</p>
            </div>
        </div>
    `;
    
    selectedDiseaseId = diseaseId;
    const modal = document.getElementById('diseaseModal');
    if (modal) modal.style.display = 'flex';
};

// Setup filter chips
function setupFilters() {
    const chips = document.querySelectorAll('.chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentCropFilter = chip.dataset.crop;
            renderDiseases();
        });
    });
}

// Setup event listeners
function setupEventListeners() {
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearchTerm = e.target.value;
            renderDiseases();
        });
    }
    
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentSearchTerm = '';
            renderDiseases();
            showToast('Search cleared', 'info');
        });
    }
    
    if (resetAllBtn) {
        resetAllBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentSearchTerm = '';
            currentCropFilter = 'all';
            document.querySelectorAll('.chip').forEach(chip => {
                chip.classList.remove('active');
                if (chip.dataset.crop === 'all') chip.classList.add('active');
            });
            renderDiseases();
            showToast('All filters reset', 'success');
        });
    }
    
    // Modal close
    const modal = document.getElementById('diseaseModal');
    const modalClose = document.querySelectorAll('.modal-close, #closeModalBtn');
    modalClose.forEach(btn => {
        if (btn) btn.addEventListener('click', () => {
            if (modal) modal.style.display = 'none';
        });
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            if (modal) modal.style.display = 'none';
        }
    });
    
    // Detect from library button
    const detectBtn = document.getElementById('detectFromLibraryBtn');
    if (detectBtn) {
        detectBtn.addEventListener('click', () => {
            const diseaseName = document.getElementById('modalDiseaseName').innerText;
            localStorage.setItem('selectedDisease', diseaseName);
            window.location.href = 'detect.html';
        });
    }
}

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
setupFilters();
setupEventListeners();

// Load diseases from backend or fallback
checkBackendHealth().then(isHealthy => {
    if (isHealthy) {
        fetchDiseases();
    } else {
        loadFromLocalStorage();
        showToast('Backend offline. Using local disease library.', 'warning');
    }
});

// Auto-refresh every 5 minutes
setInterval(() => {
    if (document.visibilityState === 'visible') {
        checkBackendHealth().then(isHealthy => {
            if (isHealthy) fetchDiseases();
        });
    }
}, 300000);