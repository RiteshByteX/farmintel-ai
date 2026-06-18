/**
 * FarmIntel AI - FAQ with Premium AI Chatbot
 * Complete Intelligent Chatbot with Proper Formatting
 */

// Initialize AOS
AOS.init({ duration: 800, once: true, offset: 50 });

// DOM Elements
const faqContainer = document.getElementById('faqContainer');
const noResultsDiv = document.getElementById('noResults');
const searchInput = document.getElementById('faqSearch');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const resetSearchBtn = document.getElementById('resetSearchBtn');
const contactSupportBtn = document.getElementById('contactSupportBtn');

// Global variables
let currentCategory = 'all';
let currentSearchTerm = '';
let isChatOpen = true;
let chatTypingTimeout = null;
let messageHistory = [];

// ========================================
// ENHANCED FAQ DATABASE with Rich Answers
// ========================================

const faqData = [
    // Getting Started
    {
        id: 1,
        question: "What is FarmIntel AI and how does it work?",
        answer: "FarmIntel AI is an AI-powered web application that helps farmers detect crop diseases instantly by uploading a photo of a diseased leaf.\n\n🔍 How it works:\n• You upload a photo of a diseased leaf\n• Our AI model analyzes the image\n• Identifies the disease with confidence score\n• Shows severity level (Severe/Moderate/Mild/Low)\n• Provides chemical and organic treatment recommendations\n• Includes weather analysis for disease risk prediction\n\n🌾 The app supports 38 disease classes across 10+ crops including Tomato, Potato, Apple, Corn, Grape, and more!",
        category: "getting-started",
        keywords: ["what is", "overview", "how it works", "explain", "purpose"]
    },
    {
        id: 2,
        question: "How do I get started with FarmIntel AI?",
        answer: "Getting started is simple! Follow these steps:\n\n1️⃣ Create a free account using your email or mobile number\n2️⃣ Log in to your dashboard\n3️⃣ Click on 'Detect Disease' from the sidebar\n4️⃣ Upload a photo or take a picture of the affected leaf\n5️⃣ Click 'Detect Disease' to get instant results\n6️⃣ Save your results to history for future reference\n\n💡 Tip: Use the sample images to test the app without a real leaf!",
        category: "getting-started",
        keywords: ["start", "begin", "setup", "signup", "register", "create account"]
    },
    {
        id: 3,
        question: "Is FarmIntel AI free to use?",
        answer: "Yes! FarmIntel AI offers multiple plans:\n\n🆓 Free Plan:\n• Disease detection with treatment recommendations\n• Weather analysis\n• Up to 50 saved scans\n• Basic support\n\n💎 Premium Plan:\n• Unlimited scans\n• Detailed reports with PDF/CSV export\n• Priority support\n• Multi-language support\n\n🏢 Enterprise Plan:\n• Team access\n• API integration\n• Dedicated support\n• Custom model training\n\nAll plans are designed to be affordable for farmers of all sizes!",
        category: "billing",
        keywords: ["free", "cost", "price", "premium", "subscription", "paid", "money"]
    },
    {
        id: 4,
        question: "What crops does FarmIntel AI support?",
        answer: "FarmIntel AI currently supports 38 disease classes across 10+ crops:\n\n🍅 Tomato - 10 diseases (Late Blight, Early Blight, Bacterial Spot, Septoria Leaf Spot, Yellow Leaf Curl Virus, and more)\n🥔 Potato - 3 diseases (Late Blight, Early Blight, Healthy)\n🍎 Apple - 4 diseases (Scab, Black Rot, Cedar Rust, Healthy)\n🌽 Corn - 4 diseases (Cercospora, Common Rust, Northern Leaf Blight, Healthy)\n🌾 Rice - 3 diseases (Blast, Brown Spot, Healthy)\n🌾 Wheat - 2 diseases (Rust, Healthy)\n🍇 Grape - 4 diseases (Black Rot, Esca, Leaf Blight, Healthy)\n🍑 Peach - 3 diseases (Bacterial Spot, Scab, Healthy)\n🍓 Strawberry - 2 diseases (Leaf Scorch, Healthy)\n🌶️ Bell Pepper - 3 diseases (Bacterial Spot, Healthy)\n\nWe're continuously adding more crops based on user feedback!",
        category: "getting-started",
        keywords: ["crops", "supported", "plants", "vegetables", "fruits", "tomato", "potato", "apple"]
    },
    
    // Disease Detection
    {
        id: 5,
        question: "How accurate is the disease detection?",
        answer: "Our AI model achieves approximately 94% accuracy on validation datasets!\n\n📊 Accuracy Details:\n• Trained on over 50,000 images\n• Validated on diverse crop diseases\n• 94% average accuracy across all diseases\n• Confidence score (0-100%) shows reliability\n\n📸 For Best Results:\n• Use natural daylight (avoid flash)\n• Keep camera steady\n• Focus on the affected area\n• Include both healthy and diseased tissue\n• Avoid shadows or glare\n\n💡 Higher confidence = more reliable result. If confidence is below 70%, try retaking the photo.",
        category: "accuracy",
        keywords: ["accuracy", "reliable", "correct", "trust", "confidence", "percent"]
    },
    {
        id: 6,
        question: "Can I use the app offline?",
        answer: "Currently, FarmIntel AI requires an internet connection for disease detection as it uses cloud-based AI processing.\n\n📶 Why internet is needed:\n• AI model runs on our servers\n• Real-time weather data updates\n• Treatment database access\n\n💡 What you CAN do offline:\n• View saved scan history\n• Access previously detected results\n• Read treatment recommendations\n• Browse disease library\n\n🚀 Future: We're working on an offline-capable mobile app!",
        category: "technical",
        keywords: ["offline", "internet", "connection", "mobile", "network", "wifi"]
    },
    {
        id: 7,
        question: "What should I do if the confidence score is low?",
        answer: "If confidence score is below 70%, try these tips:\n\n📸 Photo Tips:\n1️⃣ Take a clearer photo in natural daylight\n2️⃣ Ensure the affected area is in focus\n3️⃣ Include both healthy and diseased tissue in frame\n4️⃣ Avoid shadows or glare on the leaf\n5️⃣ Try taking from a different angle\n6️⃣ Make sure the leaf is clean (no dirt or water drops)\n\n🔄 Alternative Options:\n• Use the sample images to test the app\n• Try uploading a different photo\n• Use the disease library to compare symptoms\n\n👨‍🌾 If still low, consult a local agronomist for expert advice.",
        category: "detection",
        keywords: ["low confidence", "error", "wrong", "incorrect", "bad", "poor"]
    },
    {
        id: 8,
        question: "How does the severity level work?",
        answer: "Severity is calculated based on the confidence score to help prioritize action:\n\n🔴 Severe (85%+):\n• Immediate action needed\n• Apply treatment today\n• High risk of crop loss\n\n🟠 Moderate (70-84%):\n• Action within 3 days\n• Monitor closely\n• Medium risk\n\n🟡 Mild (50-69%):\n• Monitor and treat if spreads\n• Low immediate risk\n\n🟢 Low (below 50%):\n• Retake clearer photo\n• No immediate action needed\n\n💡 Higher confidence = more severe disease progression.",
        category: "detection",
        keywords: ["severity", "level", "urgent", "priority", "serious", "critical"]
    },
    
    // Privacy & Security
    {
        id: 9,
        question: "Is my data private and secure?",
        answer: "Absolutely! We take privacy and security very seriously:\n\n🔒 Security Measures:\n• All data transmission is encrypted using SSL/TLS\n• Images and scan history are stored securely\n• We never share your data with third parties\n\n📁 Your Data Control:\n• You retain 100% ownership of all images\n• Delete your history anytime\n• Delete your account permanently\n\n🛡️ Best Practices:\n• Use a strong password\n• Log out on shared devices\n• Review your scan history regularly\n\nYour privacy matters to us!",
        category: "privacy",
        keywords: ["privacy", "security", "data", "safe", "encrypted", "protect"]
    },
    {
        id: 10,
        question: "Who owns the photos I upload?",
        answer: "You retain 100% ownership of all images you upload to FarmIntel AI.\n\n📸 Ownership Rights:\n• You own all your photos\n• We only process them for disease detection\n• We don't claim any rights to your images\n• You can delete any image anytime\n\n🔬 How We Use Images:\n• For disease detection only\n• We don't use your images for training without explicit permission\n• Images are deleted after processing (if you choose)\n\n💡 You have full control over your data.",
        category: "privacy",
        keywords: ["ownership", "photos", "images", "rights", "property"]
    },
    
    // Technical
    {
        id: 11,
        question: "What devices and browsers are supported?",
        answer: "FarmIntel AI works on all modern devices and browsers:\n\n🌐 Supported Browsers:\n• Google Chrome (Recommended)\n• Mozilla Firefox\n• Apple Safari\n• Microsoft Edge\n\n📱 Device Support:\n• Desktop computers\n• Laptops\n• Tablets (iPad, Android)\n• Mobile phones (iOS and Android)\n\n📸 Camera Requirements:\n• Works best with Chrome on Android\n• Safari on iOS for iPhones\n• Camera requires HTTPS or localhost\n\n💡 For the best experience, use Chrome on any device!",
        category: "technical",
        keywords: ["browser", "device", "mobile", "desktop", "compatible", "chrome", "safari"]
    },
    {
        id: 12,
        question: "Why is my camera not working?",
        answer: "Camera access issues are usually due to browser permissions. Here's how to fix it:\n\n🔧 Troubleshooting:\n1️⃣ Click the lock icon in your browser address bar\n2️⃣ Allow camera permissions for this site\n3️⃣ Refresh the page\n4️⃣ Ensure you're using HTTPS (or localhost)\n5️⃣ Try Chrome or Safari for better compatibility\n\n📱 Mobile Tips:\n• On Android: Use Chrome\n• On iPhone: Use Safari\n• Close other apps using the camera\n\n💡 If still not working, try uploading a photo from your gallery instead.",
        category: "technical",
        keywords: ["camera", "not working", "permission", "access", "denied"]
    },
    {
        id: 13,
        question: "How do I download reports?",
        answer: "Downloading reports is easy! Follow these steps:\n\n📊 Steps to Generate Report:\n1️⃣ Go to the Reports page from the sidebar\n2️⃣ Select your preferred report type:\n   • Summary Report - Overview of all scans\n   • Detailed Analysis - Complete disease data\n   • Weather Impact - Weather risk analysis\n3️⃣ Choose date range (Today, Week, Month, Year, All Time)\n4️⃣ Select format (PDF or CSV)\n5️⃣ Click 'Generate Report'\n6️⃣ The file will download automatically\n\n📄 What's Included:\n• Disease detection results\n• Treatment recommendations\n• Confidence scores and severity\n• Weather analysis\n• Statistical summaries\n\n💡 Premium users get unlimited report generation!",
        category: "technical",
        keywords: ["download", "report", "pdf", "csv", "export", "print"]
    },
    
    // Treatment
    {
        id: 14,
        question: "Are the treatment recommendations safe?",
        answer: "Our treatment recommendations are based on agricultural research and guidelines. However, always follow these safety practices:\n\n🛡️ Safety Guidelines:\n1️⃣ Read product labels carefully\n2️⃣ Follow recommended dosages exactly\n3️⃣ Wear protective equipment when applying chemicals\n4️⃣ Test on a small area first\n5️⃣ Consult local agronomists for region-specific advice\n\n⚠️ Important Reminders:\n• FarmIntel AI is a guidance tool\n• Not a replacement for professional advice\n• Always follow local regulations\n• Store chemicals safely\n\n🌿 Organic treatments are generally safer for the environment and beneficial insects.",
        category: "detection",
        keywords: ["treatment", "safe", "chemical", "organic", "pesticide", "fungicide"]
    },
    {
        id: 15,
        question: "What's the difference between chemical and organic treatment?",
        answer: "We provide both options so farmers can choose based on their farming philosophy:\n\n🧪 Chemical Treatment:\n• Synthetic fungicides/bactericides\n• Quick, effective control\n• Fast-acting results\n• May have environmental impacts\n• Follow strict dosage guidelines\n\n🌱 Organic Treatment:\n• Natural ingredients (neem oil, copper spray, baking soda)\n• Beneficial microbes (Bacillus subtilis)\n• Eco-friendly\n• May require more frequent application\n• Safer for beneficial insects\n\n💡 Choose based on:\n• Urgency of the situation\n• Your farming philosophy\n• Local regulations\n• Environmental considerations",
        category: "detection",
        keywords: ["chemical", "organic", "difference", "treatment", "natural", "synthetic"]
    },
    
    // Weather
    {
        id: 16,
        question: "How does the weather risk index work?",
        answer: "The Disease Risk Index combines multiple weather factors to predict disease risk:\n\n📊 Risk Factors:\n• Temperature - Extreme temps stress plants\n• Humidity - >80% creates fungal risk\n• Rainfall - Spreads disease spores\n• Wind Speed - Spreads spores\n\n📈 Risk Levels:\n🔴 HIGH (Score 60+):\n• Humidity >80% or extreme temps\n• Immediate preventive action needed\n• Apply fungicide BEFORE rain\n\n🟡 MEDIUM (Score 30-59):\n• Humidity 65-80%\n• Regular monitoring recommended\n• Be prepared to take action\n\n🟢 LOW (Score <30):\n• Optimal conditions\n• Continue normal practices\n\n🌤️ Weather data updates in real-time from OpenWeatherMap.",
        category: "detection",
        keywords: ["weather", "risk", "index", "humidity", "temperature", "rain"]
    },
    
    // History
    {
        id: 17,
        question: "How long is my scan history stored?",
        answer: "Your scan history storage depends on your plan:\n\n📁 Storage Details:\n• Free Plan: Up to 50 scans\n• Premium Plan: Unlimited storage\n• Enterprise Plan: Unlimited + team access\n\n⏰ Retention Policy:\n• History is stored indefinitely\n• You can delete individual scans\n• Clear entire history anytime\n\n💾 Where Data is Stored:\n• Browser local storage (if not logged in)\n• Secure cloud database (if logged in)\n• Fully encrypted\n\n📊 You can also export history as PDF or CSV reports.",
        category: "technical",
        keywords: ["history", "store", "save", "delete", "storage", "records"]
    },
    
    // Account
    {
        id: 18,
        question: "How do I reset my password?",
        answer: "Resetting your password is quick and easy:\n\n🔐 Steps to Reset:\n1️⃣ Click 'Forgot Password?' on the login screen\n2️⃣ Enter your registered email address\n3️⃣ Check your email for a reset link\n4️⃣ Click the link and create a new password\n5️⃣ Log in with your new password\n\n📧 Email Issues:\n• Check your spam/junk folder\n• Wait 5-10 minutes\n• Try resending the request\n• Contact support if not received\n\n🔒 Password Tips:\n• Use at least 8 characters\n• Include numbers and symbols\n• Don't reuse passwords\n• Use a password manager",
        category: "billing",
        keywords: ["password", "reset", "forgot", "login", "account", "change"]
    },
    {
        id: 19,
        question: "Can I delete my account?",
        answer: "Yes, you can delete your account anytime. Here's what happens:\n\n🗑️ Account Deletion:\n• Go to Settings → Account → Delete Account\n• Confirmation required\n• Action cannot be undone\n\n📁 Data Deleted:\n• All scan history\n• Saved images\n• Account information\n• Preferences and settings\n\n💾 Before Deleting:\n• Download any important reports\n• Save any data you need\n• Export your scan history\n\n💡 Consider downgrading to Free plan instead of deleting.",
        category: "privacy",
        keywords: ["delete", "account", "remove", "close", "permanent"]
    },
    
    // Support
    {
        id: 20,
        question: "How do I contact support?",
        answer: "We're here to help! Reach us through any of these channels:\n\n📧 Email Support:\n• support@farmintel.ai\n• Response within 24 hours\n• Include detailed description\n\n💬 Live Chat:\n• Available on this page\n• 9 AM - 6 PM IST\n• Real-time assistance\n\n📝 Contact Form:\n• Available on this page\n• Submit your question\n• We'll respond promptly\n\n🕐 Response Times:\n• Free Plan: 24-48 hours\n• Premium Plan: 12-24 hours\n• Enterprise: Priority support\n\n💡 For quick answers, use the chat feature or search the FAQ!",
        category: "getting-started",
        keywords: ["contact", "support", "help", "email", "phone", "chat"]
    }
];

// ========================================
// AI CHATBOT INTELLIGENCE ENGINE
// ========================================

const chatbotResponses = {
    // Greetings
    greetings: {
        patterns: ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "namaste", "howdy"],
        response: "👋 Hello! I'm FarmIntel AI Assistant. I'm here to help you with:\n\n🌾 Disease detection and diagnosis\n🍅 Crop disease identification\n💊 Treatment recommendations\n📊 Weather risk analysis\n📄 Reports and history\n\nWhat would you like to know today?"
    },
    
    // Welcome
    welcome: {
        patterns: ["who are you", "what can you do", "help", "assist", "capabilities"],
        response: "I'm your AI-powered farming assistant! Here's what I can help with:\n\n1️⃣ Disease Detection - Upload a leaf photo for instant diagnosis\n2️⃣ Treatment Recommendations - Chemical and organic options\n3️⃣ Weather Analysis - Disease risk based on weather\n4️⃣ Disease Library - Learn about different crop diseases\n5️⃣ Reports - Generate PDF/CSV reports\n6️⃣ History - View and manage your scan history\n\n🌾 What would you like to explore first?"
    },
    
    // Detection
    detection: {
        patterns: ["detect", "detection", "scan", "upload", "photo", "picture", "image", "identify", "diagnose"],
        response: "📸 How disease detection works:\n\n1️⃣ Go to the 'Detect Disease' page from the sidebar\n2️⃣ Choose how to capture:\n   • 📷 Take a photo with your camera\n   • 📁 Upload from your gallery\n   • 🖼️ Try sample images\n3️⃣ The AI analyzes the image\n4️⃣ Results include:\n   • 🩺 Disease name\n   • 📊 Confidence score (0-100%)\n   • 🔴 Severity level (Severe/Moderate/Mild/Low)\n   • 💊 Treatment recommendations\n   • 🌿 Organic alternatives\n\n💡 For best results: use natural daylight, keep camera steady, and focus on the affected area!"
    },
    
    // Crops
    crops: {
        patterns: ["crop", "crops", "plant", "plants", "vegetable", "fruit", "tomato", "potato", "apple", "corn", "rice", "wheat", "grape", "peach", "strawberry"],
        response: "🌾 FarmIntel AI supports 38 disease classes across 10+ crops:\n\n🍅 Tomato - 10 diseases\n🥔 Potato - 3 diseases\n🍎 Apple - 4 diseases\n🌽 Corn - 4 diseases\n🌾 Rice - 3 diseases\n🌾 Wheat - 2 diseases\n🍇 Grape - 4 diseases\n🍑 Peach - 3 diseases\n🍓 Strawberry - 2 diseases\n🌶️ Bell Pepper - 3 diseases\n\n🔬 Each crop has multiple disease classes including healthy status.\n\n📈 We're continuously adding more crops based on farmer feedback!"
    },
    
    // Accuracy
    accuracy: {
        patterns: ["accuracy", "accurate", "correct", "reliable", "trust", "confidence"],
        response: "📊 Our AI model is highly accurate!\n\n🎯 Accuracy Stats:\n• 94% average accuracy on validation datasets\n• Trained on over 50,000 images\n• Validated on diverse crop diseases\n\n📸 Confidence Score Explained:\n• 85-100%: Very High - Reliable result\n• 70-84%: High - Good result\n• 50-69%: Medium - Consider retaking\n• Below 50%: Low - Retake photo\n\n💡 Tips for Better Accuracy:\n• Natural daylight photos\n• Steady camera\n• Focus on affected area\n• Clean, clear leaf\n\nHigher confidence = More reliable result!"
    },
    
    // Treatment
    treatment: {
        patterns: ["treatment", "treat", "remedy", "cure", "chemical", "organic", "pesticide", "fungicide"],
        response: "💊 We provide both treatment options:\n\n🧪 Chemical Treatment:\n• Synthetic fungicides/bactericides\n• Quick, effective control\n• Follow dosage guidelines carefully\n• Wear protective equipment\n\n🌿 Organic Treatment:\n• Natural ingredients\n• Neem oil, copper spray, baking soda\n• Beneficial microbes\n• Eco-friendly\n• May need frequent application\n\n📋 Each treatment includes:\n• Name and dosage\n• Application method\n• Frequency of application\n• Safety precautions\n\n💡 Choose based on urgency and farming philosophy!"
    },
    
    // Weather
    weather: {
        patterns: ["weather", "rain", "humidity", "temperature", "risk", "forecast"],
        response: "🌤️ Weather Risk Index:\n\n📊 Factors Analyzed:\n• 🌡️ Temperature - Extreme temps stress plants\n• 💧 Humidity - >80% creates fungal risk\n• ☔ Rainfall - Spreads disease spores\n• 💨 Wind Speed - Spreads spores\n\n🔴 HIGH Risk (Score 60+):\n• Immediate preventive action needed\n• Apply fungicide BEFORE rain\n\n🟡 MEDIUM Risk (Score 30-59):\n• Regular monitoring recommended\n• Be prepared to take action\n\n🟢 LOW Risk (Score <30):\n• Optimal conditions\n• Continue normal practices\n\n🌐 Weather data updates in real-time!"
    },
    
    // Privacy
    privacy: {
        patterns: ["privacy", "private", "secure", "data", "safe", "encrypted", "protect", "share"],
        response: "🔒 Your Privacy Matters to Us!\n\n🛡️ Security Measures:\n• SSL/TLS encryption for all data\n• Secure cloud storage\n• No third-party data sharing\n\n📁 Your Data Control:\n• You own 100% of your images\n• Delete history anytime\n• Delete account permanently\n\n🔐 Best Practices:\n• Use a strong password\n• Log out on shared devices\n• Review history regularly\n\n💡 We never use your images for training without explicit permission!"
    },
    
    // History
    history: {
        patterns: ["history", "save", "saved", "store", "storage", "records", "past", "previous"],
        response: "📁 Your Scan History:\n\n💾 Storage Limits:\n• Free Plan: Up to 50 scans\n• Premium Plan: Unlimited storage\n\n📊 What's Saved:\n• Disease name and confidence\n• Severity level\n• Treatment recommendations\n• Date and time\n\n🔍 Manage Your History:\n• View all scans\n• Search by disease name\n• Filter by severity\n• Delete individual scans\n• Export as PDF/CSV\n\n📥 History is stored securely and accessible anytime!"
    },
    
    // Reports
    reports: {
        patterns: ["report", "reports", "export", "pdf", "csv", "download", "print"],
        response: "📄 Generate Professional Reports:\n\n📊 Report Types:\n• Summary Report - Overview of all scans\n• Detailed Analysis - Complete disease data\n• Weather Impact - Risk analysis\n\n📅 Date Range:\n• Today\n• Last 7 Days\n• Last 30 Days\n• Last Year\n• All Time\n\n📁 Export Formats:\n• PDF - Professional formatted report\n• CSV - Data for analysis in Excel\n\n📋 What's Included:\n• Disease detection results\n• Treatment recommendations\n• Confidence scores and severity\n• Weather analysis\n• Statistical summaries\n\n💡 Premium users get unlimited reports!"
    },
    
    // Billing
    billing: {
        patterns: ["free", "cost", "price", "premium", "paid", "money", "subscription", "plan"],
        response: "💎 FarmIntel AI Plans:\n\n🆓 Free Plan:\n• ✅ Disease detection\n• ✅ Treatment recommendations\n• ✅ Weather analysis\n• ✅ 50 saved scans\n• ✅ Basic support\n\n💎 Premium Plan:\n• ✅ Everything in Free\n• ✅ Unlimited scans\n• ✅ Detailed reports\n• ✅ PDF/CSV export\n• ✅ Priority support\n• ✅ Multi-language\n\n🏢 Enterprise Plan:\n• ✅ Everything in Premium\n• ✅ Team access\n• ✅ API integration\n• ✅ Custom model training\n• ✅ Dedicated support\n\n🌾 All plans designed for farmers of all sizes!"
    },
    
    // Camera
    camera: {
        patterns: ["camera", "photo", "picture", "image", "upload", "blurry", "focus"],
        response: "📸 Tips for Perfect Photos:\n\n✅ DO:\n1️⃣ Use natural daylight (avoid flash)\n2️⃣ Keep camera steady (use both hands)\n3️⃣ Focus on the affected area\n4️⃣ Include both healthy and diseased tissue\n5️⃣ Take clean, clear photos\n6️⃣ Try different angles\n\n❌ DON'T:\n• Use flash (causes glare)\n• Take in low light\n• Include shadows\n• Take blurry photos\n\n🔧 Camera Not Working?\n1️⃣ Check browser permissions\n2️⃣ Allow camera access\n3️⃣ Use Chrome or Safari\n4️⃣ Try uploading from gallery\n\n💡 Good photos = More accurate detection!"
    },
    
    // Healthy
    healthy: {
        patterns: ["healthy", "health", "disease-free", "clean", "good"],
        response: "🌱 Healthy Plant Detection:\n\n✅ What 'Healthy' Means:\n• No signs of disease detected\n• Plant is in good condition\n• Continue regular care\n\n📊 Healthy Confidence:\n• High confidence = Very healthy\n• Medium confidence = Monitor closely\n\n💚 Recommendations for Healthy Plants:\n• Continue regular monitoring\n• Maintain proper watering\n• Balanced fertilization\n• Preventive measures\n\n🔄 Regular scanning helps:\n• Detect diseases early\n• Track plant health\n• Prevent crop loss\n\n🌾 Keep up the good work!"
    },
    
    // Fallback
    fallback: {
        response: "🤔 I'm not sure I fully understand your question. Here are some things I can help with:\n\n🌾 How disease detection works\n🍅 Supported crops and diseases\n📊 Accuracy and confidence scores\n💊 Treatment recommendations\n☁️ Weather risk analysis\n🔒 Privacy and security\n📄 Reports and history\n\n💡 Tip: Try rephrasing your question or use the search bar above to find specific topics.\n\n📚 You can also browse the FAQ categories below for common questions."
    }
};

// ========================================
// CHATBOT FUNCTIONS
// ========================================

function findBestResponse(userMessage) {
    const message = userMessage.toLowerCase().trim();
    
    // Check for empty message
    if (!message) return chatbotResponses.fallback.response;
    
    // Check FAQ database first (exact or partial match)
    for (const faq of faqData) {
        const questionLower = faq.question.toLowerCase();
        if (message.includes(questionLower) || 
            questionLower.includes(message) ||
            faq.keywords.some(k => message.includes(k))) {
            return faq.answer;
        }
    }
    
    // Check greetings
    for (const pattern of chatbotResponses.greetings.patterns) {
        if (message.includes(pattern)) {
            return chatbotResponses.greetings.response;
        }
    }
    
    // Check welcome/intent
    for (const pattern of chatbotResponses.welcome.patterns) {
        if (message.includes(pattern)) {
            return chatbotResponses.welcome.response;
        }
    }
    
    // Check each response category with scoring
    let bestMatch = null;
    let bestScore = 0;
    
    const categories = [
        'detection', 'crops', 'accuracy', 'treatment', 'weather', 
        'privacy', 'history', 'reports', 'billing', 'support', 
        'camera', 'scans', 'healthy'
    ];
    
    for (const category of categories) {
        const data = chatbotResponses[category];
        let score = 0;
        
        for (const pattern of data.patterns) {
            if (message.includes(pattern)) {
                score += 3;
            }
            // Check word-by-word for partial matches
            const patternWords = pattern.split(' ');
            for (const word of patternWords) {
                if (word.length > 2 && message.includes(word)) {
                    score += 0.5;
                }
            }
        }
        
        if (score > bestScore) {
            bestScore = score;
            bestMatch = data;
        }
    }
    
    // Return best match or fallback
    if (bestMatch && bestScore >= 1.5) {
        return bestMatch.response;
    }
    
    return chatbotResponses.fallback.response;
}

function formatMessageWithEmojis(text) {
    // Ensure emojis are properly displayed
    return text;
}

function addChatMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    // Remove typing indicator if present
    const typingIndicator = chatMessages.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    // Message content
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Format message with line breaks and lists
    const formattedMessage = message
        .replace(/\n/g, '<br>')
        .replace(/\• /g, '• ')
        .replace(/1️⃣/g, '1️⃣ ')
        .replace(/2️⃣/g, '2️⃣ ')
        .replace(/3️⃣/g, '3️⃣ ')
        .replace(/4️⃣/g, '4️⃣ ')
        .replace(/5️⃣/g, '5️⃣ ')
        .replace(/6️⃣/g, '6️⃣ ');
    
    const p = document.createElement('p');
    p.innerHTML = formattedMessage;
    content.appendChild(p);
    
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = 'Just now';
    content.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Store message in history
    messageHistory.push({
        text: message,
        isUser: isUser,
        timestamp: new Date().toISOString()
    });
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    // Remove existing typing indicator
    const existing = chatMessages.querySelector('.typing-indicator');
    if (existing) existing.remove();
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot';
    typingDiv.innerHTML = `
        <div class="avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function processChatMessage(userMessage) {
    if (!userMessage || !userMessage.trim()) return;
    
    // Add user message
    addChatMessage(userMessage.trim(), true);
    
    // Clear input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Get response with delay
    clearTimeout(chatTypingTimeout);
    chatTypingTimeout = setTimeout(() => {
        const response = findBestResponse(userMessage);
        addChatMessage(response, false);
        updateSuggestions(userMessage);
    }, 400 + Math.random() * 600);
}

function updateSuggestions(userMessage) {
    const suggestionsContainer = document.getElementById('quickSuggestions');
    if (!suggestionsContainer) return;
    
    const message = userMessage.toLowerCase();
    const allQuestions = faqData.map(f => f.question);
    
    // Find related questions
    const related = allQuestions.filter(q => {
        const qLower = q.toLowerCase();
        const words = message.split(' ').filter(w => w.length > 2);
        return words.some(word => qLower.includes(word)) ||
               words.some(word => qLower.split(' ').some(qw => qw.includes(word)));
    }).slice(0, 5);
    
    if (related.length > 0) {
        suggestionsContainer.innerHTML = related.map(q => `
            <button class="suggestion-chip" data-suggestion="${q}">
                <i class="fas fa-arrow-right"></i> ${q.length > 35 ? q.substring(0, 35) + '...' : q}
            </button>
        `).join('');
    } else {
        // Default suggestions
        const defaultSuggestions = [
            { icon: 'camera', text: 'How do I detect a disease?' },
            { icon: 'seedling', text: 'What crops are supported?' },
            { icon: 'chart-line', text: 'How accurate is the detection?' },
            { icon: 'lock', text: 'Is my data private?' },
            { icon: 'save', text: 'How do I save scans?' },
            { icon: 'pills', text: 'What are the treatment options?' }
        ];
        suggestionsContainer.innerHTML = defaultSuggestions.map(s => `
            <button class="suggestion-chip" data-suggestion="${s.text}">
                <i class="fas fa-${s.icon}"></i> ${s.text}
            </button>
        `).join('');
    }
}

// ========================================
// SETUP FUNCTIONS
// ========================================

function getCategoryName(category) {
    const names = {
        'getting-started': 'Getting Started',
        'detection': 'Disease Detection',
        'accuracy': 'Accuracy & AI',
        'privacy': 'Privacy & Security',
        'billing': 'Plans & Billing',
        'technical': 'Technical'
    };
    return names[category] || category;
}

function setupCategoryTabs() {
    const tabs = document.querySelectorAll('.category-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentCategory = tab.dataset.category;
            renderFAQs();
        });
    });
}

function getFilteredFAQs() {
    let filtered = [...faqData];
    
    if (currentCategory !== 'all') {
        filtered = filtered.filter(faq => faq.category === currentCategory);
    }
    
    if (currentSearchTerm) {
        const term = currentSearchTerm.toLowerCase();
        filtered = filtered.filter(faq => 
            faq.question.toLowerCase().includes(term) ||
            faq.answer.toLowerCase().includes(term) ||
            faq.keywords.some(k => k.toLowerCase().includes(term))
        );
    }
    
    return filtered;
}

function renderFAQs() {
    const filtered = getFilteredFAQs();
    
    if (filtered.length === 0) {
        if (faqContainer) faqContainer.style.display = 'none';
        if (noResultsDiv) noResultsDiv.style.display = 'block';
        return;
    }
    
    if (faqContainer) faqContainer.style.display = 'block';
    if (noResultsDiv) noResultsDiv.style.display = 'none';
    
    faqContainer.innerHTML = filtered.map(faq => `
        <div class="faq-item" data-id="${faq.id}">
            <div class="faq-question" onclick="toggleFaq(${faq.id})">
                <div class="question-content">
                    <i class="fas fa-question-circle"></i>
                    <span>${faq.question}</span>
                </div>
                <i class="fas fa-chevron-down faq-toggle-icon"></i>
            </div>
            <div class="faq-answer" id="faq-answer-${faq.id}">
                <div class="answer-content">
                    <i class="fas fa-reply-all"></i>
                    <p style="white-space: pre-line;">${faq.answer}</p>
                </div>
                <div class="answer-footer">
                    <span class="category-badge">${getCategoryName(faq.category)}</span>
                    <button class="helpful-btn" onclick="markHelpful(${faq.id})">
                        <i class="fas fa-thumbs-up"></i> Was this helpful?
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

window.toggleFaq = function(id) {
    const answerDiv = document.getElementById(`faq-answer-${id}`);
    const faqItem = answerDiv?.closest('.faq-item');
    const icon = faqItem?.querySelector('.faq-toggle-icon');
    
    if (!answerDiv || !icon) return;
    
    if (answerDiv.classList.contains('open')) {
        answerDiv.classList.remove('open');
        icon.classList.remove('rotated');
    } else {
        document.querySelectorAll('.faq-answer').forEach(answer => {
            answer.classList.remove('open');
        });
        document.querySelectorAll('.faq-toggle-icon').forEach(icn => {
            icn.classList.remove('rotated');
        });
        answerDiv.classList.add('open');
        icon.classList.add('rotated');
    }
};

window.markHelpful = function(id) {
    showToast('👍 Thanks for your feedback!', 'success');
};

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ========================================
// EVENT LISTENERS
// ========================================

function setupEventListeners() {
    // Search
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearchTerm = e.target.value;
            renderFAQs();
        });
    }
    
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentSearchTerm = '';
            renderFAQs();
            showToast('Search cleared', 'info');
        });
    }
    
    if (resetSearchBtn) {
        resetSearchBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentSearchTerm = '';
            document.querySelectorAll('.category-tab').forEach(tab => {
                tab.classList.remove('active');
                if (tab.dataset.category === 'all') tab.classList.add('active');
            });
            currentCategory = 'all';
            renderFAQs();
            showToast('All filters reset', 'success');
        });
    }
    
    // Chatbot
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChatBtn');
    
    if (sendBtn) {
        sendBtn.addEventListener('click', () => {
            if (chatInput) processChatMessage(chatInput.value);
        });
    }
    
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                processChatMessage(chatInput.value);
            }
        });
    }
    
    // Suggestion chips
    document.addEventListener('click', (e) => {
        const chip = e.target.closest('.suggestion-chip');
        if (chip) {
            const suggestion = chip.getAttribute('data-suggestion');
            if (suggestion) {
                const chatInput = document.getElementById('chatInput');
                if (chatInput) chatInput.value = suggestion;
                processChatMessage(suggestion);
            }
        }
    });
    
    // Toggle chat
    const toggleBtn = document.getElementById('toggleChatBtn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const body = document.getElementById('chatbotBody');
            const icon = toggleBtn.querySelector('i');
            if (body) {
                body.classList.toggle('collapsed');
                if (icon) {
                    icon.classList.toggle('fa-chevron-down');
                    icon.classList.toggle('fa-chevron-up');
                }
            }
        });
    }
    
    // Contact Modal
    const contactModal = document.getElementById('contactModal');
    if (contactSupportBtn) {
        contactSupportBtn.addEventListener('click', () => {
            if (contactModal) contactModal.style.display = 'flex';
        });
    }
    
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            showToast('📧 Message sent successfully! We\'ll respond within 24 hours.', 'success');
            if (contactModal) contactModal.style.display = 'none';
            contactForm.reset();
        });
    }
    
    // Modal close
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
// PARTICLES & THEME
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

// Initialize
createParticles();
setupCategoryTabs();
setupEventListeners();
renderFAQs();

// Welcome message in chat after load
setTimeout(() => {
    addChatMessage("👋 Welcome to FarmIntel AI Assistant! I'm here to help you with disease detection, crop diagnosis, treatment recommendations, and more. What would you like to know?", false);
}, 1000);