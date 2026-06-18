"""
Treatment Controller
Handles treatment recommendations, remedies, and prevention tips for crop diseases
Supports 29 disease classes from PlantVillage dataset
"""

import json
import os
from datetime import datetime
from flask import current_app


class TreatmentController:
    """
    Controller for treatment operations
    Provides chemical, organic, and cultural treatment recommendations
    """
    
    # Complete Treatment Database for 29 Diseases
    TREATMENTS = {
        # ========================================
        # Apple Diseases (4)
        # ========================================
        "Apple Scab": {
            "chemical": {
                "name": "Sulfur-based fungicide",
                "dosage": "3g per liter of water",
                "frequency": "Apply in spring when leaves emerge",
                "method": "Spray entire tree thoroughly",
                "precautions": "Do not apply in hot weather (>80°F)",
                "products": ["Wettable Sulfur", "Lime Sulfur"]
            },
            "organic": {
                "name": "Compost Tea + Neem Oil",
                "dosage": "5ml neem oil + 1 cup compost tea per liter",
                "frequency": "Apply every 10 days",
                "method": "Spray on leaves and fruit",
                "precautions": "Test on small branch first",
                "alternative": "Baking soda spray"
            },
            "cultural": {
                "practices": [
                    "Rake and destroy fallen leaves in autumn",
                    "Prune for air circulation",
                    "Remove infected fruit",
                    "Clean pruning tools",
                    "Reduce humidity in orchard"
                ],
                "spacing": "15-20 feet between trees",
                "watering": "Water at base, avoid wetting leaves",
                "soil": "Well-draining soil"
            },
            "prevention": [
                "Plant resistant varieties like 'Enterprise' or 'Liberty'",
                "Apply preventive sprays at green tip stage",
                "Maintain tree health with proper nutrition",
                "Remove overwintering sites",
                "Monitor weather for infection periods"
            ],
            "severity": "Moderate",
            "urgency": "Action within 7 days"
        },
        "Apple Black Rot": {
            "chemical": {
                "name": "Captan or thiophanate-methyl",
                "dosage": "2g per liter of water",
                "frequency": "Apply at bloom and fruit set",
                "method": "Spray on foliage and fruit",
                "precautions": "Rotate with different fungicides",
                "products": ["Captan 50WP", "Thiophanate-methyl"]
            },
            "organic": {
                "name": "Copper Spray",
                "dosage": "2g copper sulfate per liter",
                "frequency": "Apply during growing season",
                "method": "Spray on affected areas",
                "precautions": "Use stainless steel equipment",
                "alternative": "Sulfur spray"
            },
            "cultural": {
                "practices": [
                    "Remove mummified fruit from trees",
                    "Prune dead or diseased wood",
                    "Clean up fallen fruit and leaves",
                    "Sanitize pruning tools between cuts"
                ],
                "spacing": "15-20 feet between trees",
                "watering": "Avoid overhead irrigation",
                "soil": "Well-draining soil"
            },
            "prevention": [
                "Maintain tree health with proper fertilization",
                "Remove infected branches promptly",
                "Apply preventive fungicides in early spring",
                "Practice good orchard sanitation"
            ],
            "severity": "Severe",
            "urgency": "Immediate action required"
        },
        "Apple Cedar Rust": {
            "chemical": {
                "name": "Myclobutanil or mancozeb",
                "dosage": "1.5ml per liter of water",
                "frequency": "Apply every 10-14 days",
                "method": "Spray on foliage",
                "precautions": "Do not apply during flowering",
                "products": ["Immunox", "Manzate"]
            },
            "organic": {
                "name": "Sulfur Spray",
                "dosage": "3g per liter of water",
                "frequency": "Apply every 10-14 days",
                "method": "Spray on leaves",
                "precautions": "Avoid in hot weather",
                "alternative": "Neem oil"
            },
            "cultural": {
                "practices": [
                    "Remove nearby cedar trees if possible",
                    "Prune out galls on cedar trees",
                    "Increase air circulation",
                    "Plant resistant varieties"
                ],
                "spacing": "20-25 feet from cedar trees",
                "watering": "Water at base",
                "soil": "Well-draining soil"
            },
            "prevention": [
                "Plant resistant apple varieties",
                "Remove cedar trees within 2 miles",
                "Apply preventive fungicides in spring",
                "Monitor weather for infection periods"
            ],
            "severity": "Moderate",
            "urgency": "Action within 10 days"
        },
        "Apple Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "Annual dormant oil spray recommended",
                "method": "N/A",
                "precautions": "Use organic dormant oil",
                "products": ["Dormant Oil"]
            },
            "organic": {
                "name": "Beneficial Insect Habitat",
                "dosage": "Plant flowers nearby",
                "frequency": "Seasonal",
                "method": "Provide habitat for natural predators",
                "precautions": "Avoid broad-spectrum pesticides",
                "alternative": "Companion planting"
            },
            "cultural": {
                "practices": [
                    "Annual winter pruning",
                    "Mulch around base",
                    "Regular watering",
                    "Fertilize in spring",
                    "Thin fruit for quality"
                ],
                "spacing": "Standard spacing",
                "watering": "Deep weekly watering",
                "soil": "Rich organic matter"
            },
            "prevention": [
                "Regular monitoring",
                "Proper pruning",
                "Fertilize based on soil test",
                "Integrated pest management"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Bell Pepper Diseases (2)
        # ========================================
        "Bell Pepper Bacterial Spot": {
            "chemical": {
                "name": "Copper-based bactericide",
                "dosage": "2g per liter of water",
                "frequency": "Apply at first sign of disease",
                "method": "Spray on foliage",
                "precautions": "Do not exceed recommended dose",
                "products": ["Kocide 3000", "Cuprofix"]
            },
            "organic": {
                "name": "Bacillus subtilis",
                "dosage": "5ml per liter of water",
                "frequency": "Apply weekly",
                "method": "Spray on leaves",
                "precautions": "Apply in morning",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Avoid overhead irrigation",
                    "Remove infected leaves",
                    "Practice crop rotation",
                    "Sanitize tools"
                ],
                "spacing": "18-24 inches between plants",
                "watering": "Water at base in morning",
                "soil": "Well-draining soil"
            },
            "prevention": [
                "Use disease-free seeds",
                "Crop rotation (3-4 years)",
                "Avoid working with wet plants",
                "Apply preventive copper sprays"
            ],
            "severity": "Moderate",
            "urgency": "Action within 5 days"
        },
        "Bell Pepper Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "Continue regular preventive care",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Compost Tea",
                "dosage": "1 cup per gallon of water",
                "frequency": "Apply monthly",
                "method": "Foliar spray",
                "precautions": "Use well-aged compost",
                "alternative": "Seaweed extract"
            },
            "cultural": {
                "practices": [
                    "Regular monitoring",
                    "Proper spacing",
                    "Consistent watering",
                    "Mulch to retain moisture"
                ],
                "spacing": "18-24 inches",
                "watering": "Regular, consistent",
                "soil": "Rich in organic matter"
            },
            "prevention": [
                "Regular scouting",
                "Remove weeds",
                "Maintain plant health",
                "Practice crop rotation"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Cherry Diseases (2)
        # ========================================
        "Cherry Powdery Mildew": {
            "chemical": {
                "name": "Sulfur or myclobutanil",
                "dosage": "2g per liter of water",
                "frequency": "Apply every 7-10 days",
                "method": "Spray on foliage",
                "precautions": "Do not apply in hot weather",
                "products": ["Wettable Sulfur", "Immunox"]
            },
            "organic": {
                "name": "Milk Spray",
                "dosage": "1 part milk to 9 parts water",
                "frequency": "Apply weekly",
                "method": "Spray on affected areas",
                "precautions": "Use skim milk",
                "alternative": "Baking soda solution"
            },
            "cultural": {
                "practices": [
                    "Prune for air circulation",
                    "Remove infected leaves",
                    "Avoid overhead watering",
                    "Reduce humidity"
                ],
                "spacing": "15-20 feet between trees",
                "watering": "Water at base",
                "soil": "Well-draining"
            },
            "prevention": [
                "Plant resistant varieties",
                "Apply preventive sulfur in spring",
                "Maintain good air circulation",
                "Remove plant debris"
            ],
            "severity": "Moderate",
            "urgency": "Action within 7 days"
        },
        "Cherry Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "N/A",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Neem Oil",
                "dosage": "5ml per liter of water",
                "frequency": "Apply monthly as preventive",
                "method": "Spray on foliage",
                "precautions": "Test on small area",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Regular pruning",
                    "Proper fertilization",
                    "Mulch around base",
                    "Monitor for pests"
                ],
                "spacing": "Standard spacing",
                "watering": "Deep weekly watering",
                "soil": "Well-draining"
            },
            "prevention": [
                "Regular monitoring",
                "Proper orchard sanitation",
                "Balanced nutrition",
                "Integrated pest management"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Corn Diseases (4)
        # ========================================
        "Corn Cercospora Leaf Spot": {
            "chemical": {
                "name": "Azoxystrobin or pyraclostrobin",
                "dosage": "1ml per liter of water",
                "frequency": "Apply at first sign of disease",
                "method": "Spray on foliage",
                "precautions": "Rotate with different fungicides",
                "products": ["Quadris", "Headline"]
            },
            "organic": {
                "name": "Copper Spray",
                "dosage": "2g per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on leaves",
                "precautions": "Use copper sulfate",
                "alternative": "Neem oil"
            },
            "cultural": {
                "practices": [
                    "Crop rotation",
                    "Residue management",
                    "Plant resistant hybrids",
                    "Proper fertility"
                ],
                "spacing": "8-12 inches between plants",
                "watering": "Avoid overhead irrigation",
                "soil": "Well-draining"
            },
            "prevention": [
                "Plant resistant hybrids",
                "Crop rotation with soybeans",
                "Tillage to bury crop residue",
                "Balanced fertilization"
            ],
            "severity": "Moderate",
            "urgency": "Action within 10 days"
        },
        "Corn Common Rust": {
            "chemical": {
                "name": "Azoxystrobin",
                "dosage": "1ml per liter of water",
                "frequency": "Apply when rust first appears",
                "method": "Spray on foliage",
                "precautions": "Rotate with different fungicides",
                "products": ["Quadris", "Headline"]
            },
            "organic": {
                "name": "Sulfur Dust",
                "dosage": "15-20 lbs per acre",
                "frequency": "Apply during dry conditions",
                "method": "Dust on leaves",
                "precautions": "Avoid during hot weather",
                "alternative": "Neem oil"
            },
            "cultural": {
                "practices": [
                    "Plant early to avoid peak disease",
                    "Remove volunteer corn",
                    "Crop rotation",
                    "Destroy infected residue"
                ],
                "spacing": "8-12 inches",
                "watering": "Avoid overhead irrigation",
                "soil": "Well-draining"
            },
            "prevention": [
                "Plant resistant hybrids",
                "Early planting",
                "Avoid excess nitrogen",
                "Destroy volunteer corn"
            ],
            "severity": "Moderate",
            "urgency": "Action within 7 days"
        },
        "Corn Northern Leaf Blight": {
            "chemical": {
                "name": "Strobilurin or triazole",
                "dosage": "1ml per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on foliage",
                "precautions": "Rotate fungicides",
                "products": ["Stratego", "Quilt"]
            },
            "organic": {
                "name": "Copper Spray",
                "dosage": "2g per liter of water",
                "frequency": "Apply preventatively",
                "method": "Spray on leaves",
                "precautions": "Use copper hydroxide",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Crop rotation",
                    "Tillage to bury residue",
                    "Plant resistant hybrids",
                    "Proper spacing"
                ],
                "spacing": "8-12 inches",
                "watering": "Avoid overhead irrigation",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use resistant hybrids",
                "Crop rotation",
                "Tillage of crop residue",
                "Balanced nitrogen fertilization"
            ],
            "severity": "Severe",
            "urgency": "Immediate action required"
        },
        "Corn Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "N/A",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Compost Application",
                "dosage": "2-3 inches",
                "frequency": "At planting",
                "method": "Side dress",
                "precautions": "Use well-aged compost",
                "alternative": "Cover cropping"
            },
            "cultural": {
                "practices": [
                    "Proper spacing",
                    "Weed management",
                    "Adequate irrigation",
                    "Timely fertilization"
                ],
                "spacing": "Standard spacing",
                "watering": "Consistent moisture",
                "soil": "Well-draining"
            },
            "prevention": [
                "Crop rotation",
                "Resistant varieties",
                "Soil health management",
                "Regular scouting"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Grape Diseases (4)
        # ========================================
        "Grape Black Rot": {
            "chemical": {
                "name": "Myclobutanil or mancozeb",
                "dosage": "1.5ml per liter of water",
                "frequency": "Apply at bloom and fruit set",
                "method": "Spray on clusters and leaves",
                "precautions": "Do not apply during harvest",
                "products": ["Immunox", "Manzate"]
            },
            "organic": {
                "name": "Sulfur Spray",
                "dosage": "3g per liter of water",
                "frequency": "Apply every 10-14 days",
                "method": "Spray on vines",
                "precautions": "Avoid in hot weather",
                "alternative": "Copper spray"
            },
            "cultural": {
                "practices": [
                    "Prune for air circulation",
                    "Remove mummified fruit",
                    "Clean up fallen berries",
                    "Train vines properly"
                ],
                "spacing": "6-8 feet between vines",
                "watering": "Drip irrigation preferred",
                "soil": "Well-draining"
            },
            "prevention": [
                "Plant resistant varieties",
                "Apply preventive fungicides",
                "Good canopy management",
                "Sanitize pruning tools"
            ],
            "severity": "Severe",
            "urgency": "Immediate action required"
        },
        "Grape Esca": {
            "chemical": {
                "name": "Trichoderma-based treatments",
                "dosage": "As directed",
                "frequency": "Apply in spring",
                "method": "Spray on pruning wounds",
                "precautions": "Use fresh product",
                "products": ["Trichoderma", "Vintec"]
            },
            "organic": {
                "name": "Bordeaux Mixture",
                "dosage": "1g copper sulfate + 1g lime per liter",
                "frequency": "Apply in spring",
                "method": "Spray on trunks",
                "precautions": "Use stainless steel equipment",
                "alternative": "Sulfur"
            },
            "cultural": {
                "practices": [
                    "Remove infected wood",
                    "Protect pruning wounds",
                    "Maintain vine health",
                    "Avoid mechanical damage"
                ],
                "spacing": "6-8 feet",
                "watering": "Avoid water stress",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use disease-free planting material",
                "Protect wounds after pruning",
                "Maintain vine vigor",
                "Remove infected vines"
            ],
            "severity": "Severe",
            "urgency": "Immediate action required"
        },
        "Grape Leaf Blight": {
            "chemical": {
                "name": "Mancozeb or copper",
                "dosage": "2g per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on foliage",
                "precautions": "Rotate fungicides",
                "products": ["Manzate", "Kocide"]
            },
            "organic": {
                "name": "Neem Oil",
                "dosage": "5ml per liter of water",
                "frequency": "Apply weekly",
                "method": "Spray on leaves",
                "precautions": "Test on small area",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Remove infected leaves",
                    "Improve air circulation",
                    "Avoid overhead watering",
                    "Train vines properly"
                ],
                "spacing": "6-8 feet",
                "watering": "Drip irrigation",
                "soil": "Well-draining"
            },
            "prevention": [
                "Good canopy management",
                "Proper spacing",
                "Remove leaf litter",
                "Apply preventive sprays"
            ],
            "severity": "Moderate",
            "urgency": "Action within 7 days"
        },
        "Grape Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "N/A",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Compost Tea",
                "dosage": "1 cup per gallon",
                "frequency": "Apply monthly",
                "method": "Foliar spray",
                "precautions": "Use well-aged compost",
                "alternative": "Seaweed extract"
            },
            "cultural": {
                "practices": [
                    "Regular pruning",
                    "Canopy management",
                    "Proper irrigation",
                    "Weed control"
                ],
                "spacing": "Standard spacing",
                "watering": "Consistent moisture",
                "soil": "Well-draining"
            },
            "prevention": [
                "Integrated pest management",
                "Regular monitoring",
                "Balanced nutrition",
                "Sanitation practices"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Peach Diseases (2)
        # ========================================
        "Peach Bacterial Spot": {
            "chemical": {
                "name": "Copper-based bactericide",
                "dosage": "2g per liter of water",
                "frequency": "Apply at petal fall",
                "method": "Spray on foliage and fruit",
                "precautions": "Do not exceed recommended dose",
                "products": ["Kocide", "Cuprofix"]
            },
            "organic": {
                "name": "Bacillus subtilis",
                "dosage": "5ml per liter of water",
                "frequency": "Apply weekly",
                "method": "Spray on leaves",
                "precautions": "Apply in morning",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Avoid overhead irrigation",
                    "Prune for air circulation",
                    "Remove infected fruit",
                    "Sanitize tools"
                ],
                "spacing": "15-20 feet between trees",
                "watering": "Water at base",
                "soil": "Well-draining"
            },
            "prevention": [
                "Plant resistant varieties",
                "Apply preventive copper sprays",
                "Maintain tree health",
                "Remove infected branches"
            ],
            "severity": "Moderate",
            "urgency": "Action within 7 days"
        },
        "Peach Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "N/A",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Neem Oil",
                "dosage": "5ml per liter of water",
                "frequency": "Apply monthly",
                "method": "Spray on foliage",
                "precautions": "Test on small area",
                "alternative": "Dormant oil"
            },
            "cultural": {
                "practices": [
                    "Regular pruning",
                    "Proper fertilization",
                    "Mulch around base",
                    "Monitor for pests"
                ],
                "spacing": "Standard spacing",
                "watering": "Deep weekly watering",
                "soil": "Well-draining"
            },
            "prevention": [
                "Regular monitoring",
                "Proper orchard sanitation",
                "Balanced nutrition",
                "Integrated pest management"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Potato Diseases (3)
        # ========================================
        "Potato Early Blight": {
            "chemical": {
                "name": "Chlorothalonil",
                "dosage": "2ml per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on foliage",
                "precautions": "Follow pre-harvest interval",
                "products": ["Bravo", "Daconil"]
            },
            "organic": {
                "name": "Baking Soda Solution",
                "dosage": "1 tbsp + 1 tsp oil per liter",
                "frequency": "Apply weekly",
                "method": "Spray on leaves",
                "precautions": "Test on small area",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Crop rotation",
                    "Remove plant debris",
                    "Proper spacing",
                    "Avoid overhead irrigation"
                ],
                "spacing": "12-15 inches between plants",
                "watering": "Water at base",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use disease-free seed potatoes",
                "Crop rotation (3-4 years)",
                "Maintain proper fertility",
                "Hill soil around plants"
            ],
            "severity": "Moderate",
            "urgency": "Action within 5 days"
        },
        "Potato Late Blight": {
            "chemical": {
                "name": "Mancozeb",
                "dosage": "2g per liter of water",
                "frequency": "Apply preventatively",
                "method": "Spray on foliage",
                "precautions": "Do not apply within 14 days of harvest",
                "products": ["Dithane", "Manzate"]
            },
            "organic": {
                "name": "Copper Spray (Bordeaux)",
                "dosage": "1g copper sulfate + 1g lime per liter",
                "frequency": "Apply every 10-14 days",
                "method": "Spray on plants",
                "precautions": "Use stainless steel equipment",
                "alternative": "Neem oil"
            },
            "cultural": {
                "practices": [
                    "Hill soil around stems",
                    "Destroy volunteer potatoes",
                    "Remove infected plants",
                    "Harvest promptly"
                ],
                "spacing": "12-15 inches",
                "watering": "Avoid overhead irrigation",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use certified disease-free seed potatoes",
                "Avoid overhead irrigation",
                "Destroy potato volunteers",
                "Store tubers in cool, dry place"
            ],
            "severity": "Severe",
            "urgency": "Immediate action required"
        },
        "Potato Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "N/A",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Seaweed Extract",
                "dosage": "2ml per liter of water",
                "frequency": "Apply monthly",
                "method": "Foliar spray",
                "precautions": "Use in morning",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Regular hilling",
                    "Consistent moisture",
                    "Weed control",
                    "Monitor for pests"
                ],
                "spacing": "Standard spacing",
                "watering": "Regular, consistent",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use certified seed potatoes",
                "Crop rotation",
                "Regular monitoring",
                "Proper storage"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Strawberry Diseases (2)
        # ========================================
        "Strawberry Leaf Scorch": {
            "chemical": {
                "name": "Captan or myclobutanil",
                "dosage": "2g per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on foliage",
                "precautions": "Follow label directions",
                "products": ["Captan", "Immunox"]
            },
            "organic": {
                "name": "Compost Tea + Neem Oil",
                "dosage": "5ml neem oil + 1 cup compost tea per liter",
                "frequency": "Apply weekly",
                "method": "Spray on leaves",
                "precautions": "Test on small area",
                "alternative": "Baking soda"
            },
            "cultural": {
                "practices": [
                    "Remove infected leaves",
                    "Improve air circulation",
                    "Avoid overhead watering",
                    "Mulch around plants"
                ],
                "spacing": "12-18 inches between plants",
                "watering": "Water at base",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use disease-free plants",
                "Crop rotation (3-4 years)",
                "Remove old leaves after harvest",
                "Apply preventive fungicides"
            ],
            "severity": "Moderate",
            "urgency": "Action within 7 days"
        },
        "Strawberry Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "N/A",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Seaweed Extract",
                "dosage": "2ml per liter of water",
                "frequency": "Apply monthly",
                "method": "Foliar spray",
                "precautions": "Use in morning",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Regular watering",
                    "Mulch to retain moisture",
                    "Remove runners",
                    "Monitor for pests"
                ],
                "spacing": "12-18 inches",
                "watering": "Consistent moisture",
                "soil": "Well-draining, rich in organic matter"
            },
            "prevention": [
                "Regular monitoring",
                "Proper spacing",
                "Remove old leaves",
                "Renovate beds after harvest"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        
        # ========================================
        # Tomato Diseases (6)
        # ========================================
        "Tomato Bacterial Spot": {
            "chemical": {
                "name": "Copper-based bactericide",
                "dosage": "2g per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on foliage",
                "precautions": "Do not exceed recommended dose",
                "products": ["Kocide", "Cuprofix"]
            },
            "organic": {
                "name": "Bacillus subtilis",
                "dosage": "5ml per liter of water",
                "frequency": "Apply weekly",
                "method": "Spray on leaves",
                "precautions": "Apply in morning",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Avoid overhead irrigation",
                    "Remove infected leaves",
                    "Practice crop rotation",
                    "Sanitize tools"
                ],
                "spacing": "24-36 inches between plants",
                "watering": "Water at base",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use disease-free seeds",
                "Crop rotation (3-4 years)",
                "Avoid working with wet plants",
                "Apply preventive copper sprays"
            ],
            "severity": "Moderate",
            "urgency": "Action within 5 days"
        },
        "Tomato Early Blight": {
            "chemical": {
                "name": "Chlorothalonil",
                "dosage": "2ml per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on foliage",
                "precautions": "Rotate with different fungicides",
                "products": ["Bravo", "Daconil"]
            },
            "organic": {
                "name": "Baking Soda Solution",
                "dosage": "1 tbsp + 1 tsp oil per liter",
                "frequency": "Apply weekly",
                "method": "Spray on leaves",
                "precautions": "Test on small area",
                "alternative": "Compost tea"
            },
            "cultural": {
                "practices": [
                    "Remove lower leaves",
                    "Mulch to prevent soil splash",
                    "Water at base",
                    "Stake plants"
                ],
                "spacing": "24-36 inches",
                "watering": "Water at base in morning",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use disease-free seeds",
                "Crop rotation",
                "Avoid overhead watering",
                "Remove plant debris"
            ],
            "severity": "Moderate",
            "urgency": "Action within 5 days"
        },
        "Tomato Late Blight": {
            "chemical": {
                "name": "Copper Hydroxide",
                "dosage": "2g per liter of water",
                "frequency": "Apply every 7-10 days",
                "method": "Spray on both sides of leaves",
                "precautions": "Wear protective gear",
                "products": ["Kocide 3000", "Champ DP"]
            },
            "organic": {
                "name": "Neem Oil + Garlic",
                "dosage": "5ml neem oil + 3 garlic cloves per liter",
                "frequency": "Spray twice weekly",
                "method": "Mix well and strain",
                "precautions": "Test on small area first",
                "alternative": "Bordeaux mixture"
            },
            "cultural": {
                "practices": [
                    "Remove infected leaves",
                    "Avoid overhead watering",
                    "Ensure air circulation",
                    "Mulch around plants"
                ],
                "spacing": "24-36 inches",
                "watering": "Water in morning, avoid wetting leaves",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use resistant varieties",
                "Practice crop rotation",
                "Apply preventive copper spray",
                "Avoid planting near potatoes"
            ],
            "severity": "Severe",
            "urgency": "Immediate action required"
        },
        "Tomato Healthy": {
            "chemical": {
                "name": "No treatment needed",
                "dosage": "N/A",
                "frequency": "Continue regular preventive care",
                "method": "N/A",
                "precautions": "N/A",
                "products": []
            },
            "organic": {
                "name": "Compost Tea",
                "dosage": "1 cup per gallon",
                "frequency": "Apply monthly",
                "method": "Foliar spray",
                "precautions": "Use well-aged compost",
                "alternative": "Seaweed extract"
            },
            "cultural": {
                "practices": [
                    "Consistent watering",
                    "Fertilize every 2-3 weeks",
                    "Prune suckers",
                    "Monitor for pests"
                ],
                "spacing": "24-36 inches",
                "watering": "Regular, consistent",
                "soil": "Rich organic matter"
            },
            "prevention": [
                "Regular monitoring",
                "Remove yellowing leaves",
                "Proper spacing",
                "Use disease-free seeds"
            ],
            "severity": "Low",
            "urgency": "No action needed"
        },
        "Tomato Septoria Leaf Spot": {
            "chemical": {
                "name": "Chlorothalonil or mancozeb",
                "dosage": "2ml per liter of water",
                "frequency": "Apply at first sign",
                "method": "Spray on lower leaves first",
                "precautions": "Rotate fungicides",
                "products": ["Bravo", "Dithane"]
            },
            "organic": {
                "name": "Baking Soda Solution",
                "dosage": "1 tbsp + 1 tsp oil per liter",
                "frequency": "Apply weekly",
                "method": "Spray on affected areas",
                "precautions": "Test on small area",
                "alternative": "Neem oil"
            },
            "cultural": {
                "practices": [
                    "Remove lower leaves",
                    "Mulch to prevent soil splash",
                    "Avoid overhead watering",
                    "Stake plants"
                ],
                "spacing": "24-36 inches",
                "watering": "Water at base",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use disease-free seeds",
                "Crop rotation",
                "Remove plant debris",
                "Apply preventive fungicides"
            ],
            "severity": "Moderate",
            "urgency": "Action within 7 days"
        },
        "Tomato Yellow Leaf Curl Virus": {
            "chemical": {
                "name": "No cure - Control whitefly vectors",
                "dosage": "Use insecticidal soap",
                "frequency": "As needed for whitefly control",
                "method": "Spray on undersides of leaves",
                "precautions": "Use in evening",
                "products": ["Insecticidal soap", "Neem oil"]
            },
            "organic": {
                "name": "Neem Oil + Sticky Traps",
                "dosage": "5ml neem oil per liter",
                "frequency": "Apply weekly for whiteflies",
                "method": "Spray + yellow sticky traps",
                "precautions": "Test on small area",
                "alternative": "Reflective mulch"
            },
            "cultural": {
                "practices": [
                    "Remove infected plants immediately",
                    "Control whiteflies",
                    "Use reflective mulches",
                    "Row covers for young plants"
                ],
                "spacing": "24-36 inches",
                "watering": "Regular irrigation",
                "soil": "Well-draining"
            },
            "prevention": [
                "Use resistant varieties",
                "Insect netting",
                "Control whiteflies",
                "Remove weed hosts"
            ],
            "severity": "Severe",
            "urgency": "Immediate action required"
        }
    }
    
    # Default treatment for unknown diseases
    DEFAULT_TREATMENT = {
        "chemical": {
            "name": "Consult Local Agronomist",
            "dosage": "As recommended",
            "frequency": "As prescribed",
            "method": "Professional application recommended",
            "precautions": "Follow local guidelines",
            "products": ["Consult expert"]
        },
        "organic": {
            "name": "Neem Oil Solution",
            "dosage": "5ml neem oil per liter of water",
            "frequency": "Spray weekly as preventive",
            "method": "Mix with mild soap, spray on affected areas",
            "precautions": "Test on small area first",
            "alternative": "Garlic-chili spray"
        },
        "cultural": {
            "practices": [
                "Remove and destroy infected plant parts",
                "Maintain good field hygiene",
                "Avoid working in wet conditions",
                "Improve air circulation",
                "Maintain proper plant nutrition"
            ],
            "spacing": "Follow crop-specific recommendations",
            "watering": "Water at base, avoid leaf wetness",
            "soil": "Maintain soil health with organic matter"
        },
        "prevention": [
            "Practice crop rotation (3-4 years)",
            "Use disease-free seeds",
            "Regular field monitoring",
            "Maintain proper plant spacing",
            "Apply preventive organic sprays"
        ],
        "severity": "Moderate",
        "urgency": "Consult expert"
    }
    
    @classmethod
    def get_treatment(cls, disease_name, confidence=0):
        """
        Get treatment recommendations for a disease
        
        Args:
            disease_name: Name of the detected disease
            confidence: Confidence score of detection (0-100)
            
        Returns:
            dict: Complete treatment recommendations
        """
        # Get treatment for the disease or use default
        treatment = cls.TREATMENTS.get(disease_name, cls.DEFAULT_TREATMENT)
        
        # Calculate severity based on confidence
        severity = cls._calculate_severity(confidence)
        
        # Calculate affected area
        affected_area = cls._calculate_affected_area(confidence)
        
        # Calculate health status
        health_status = cls._calculate_health_status(confidence, disease_name)
        
        return {
            'success': True,
            'disease': disease_name,
            'confidence': confidence,
            'severity': severity['level'],
            'severity_color': severity['color'],
            'urgency': treatment.get('urgency', severity['urgency']),
            
            # Chemical Treatment
            'chemical_name': treatment['chemical']['name'],
            'chemical_dosage': treatment['chemical']['dosage'],
            'chemical_frequency': treatment['chemical']['frequency'],
            'chemical_method': treatment['chemical']['method'],
            'chemical_precautions': treatment['chemical']['precautions'],
            'chemical_products': treatment['chemical'].get('products', []),
            
            # Organic Treatment
            'organic_name': treatment['organic']['name'],
            'organic_dosage': treatment['organic']['dosage'],
            'organic_frequency': treatment['organic']['frequency'],
            'organic_method': treatment['organic']['method'],
            'organic_precautions': treatment['organic']['precautions'],
            'organic_alternative': treatment['organic'].get('alternative', ''),
            
            # Cultural Practices
            'cultural_practices': treatment['cultural']['practices'],
            'cultural_spacing': treatment['cultural'].get('spacing', 'Follow standard spacing'),
            'cultural_watering': treatment['cultural'].get('watering', 'Water at base'),
            'cultural_soil': treatment['cultural'].get('soil', 'Maintain soil health'),
            
            # Prevention Tips
            'prevention_tips': treatment['prevention'],
            
            # Additional Info
            'affected_area': affected_area,
            'health_status': health_status
        }
    
    @classmethod
    def _calculate_severity(cls, confidence):
        """Calculate severity level based on confidence score"""
        if confidence >= 85:
            return {
                'level': 'Severe',
                'color': '#EF4444',
                'urgency': 'Immediate action needed - Apply treatment today'
            }
        elif confidence >= 70:
            return {
                'level': 'Moderate',
                'color': '#F59E0B',
                'urgency': 'Action within 3 days - Monitor closely'
            }
        elif confidence >= 50:
            return {
                'level': 'Mild',
                'color': '#10B981',
                'urgency': 'Monitor and treat if spreads'
            }
        else:
            return {
                'level': 'Low',
                'color': '#6B7280',
                'urgency': 'Retake clearer photo for accurate detection'
            }
    
    @classmethod
    def _calculate_affected_area(cls, confidence):
        """Calculate estimated affected area percentage"""
        if confidence >= 85:
            return '50-75%'
        elif confidence >= 70:
            return '25-50%'
        elif confidence >= 50:
            return '10-25%'
        else:
            return '<10%'
    
    @classmethod
    def _calculate_health_status(cls, confidence, disease_name):
        """Calculate health status based on confidence and disease"""
        if 'Healthy' in disease_name:
            return 'Excellent - No disease detected'
        elif confidence >= 85:
            return 'Critical - Immediate Action Required'
        elif confidence >= 70:
            return 'Early Stage Disease - Treatment Recommended'
        elif confidence >= 50:
            return 'Initial Stage - Monitor Closely'
        else:
            return 'Uncertain - Consider Re-testing'
    
    @classmethod
    def get_all_diseases(cls):
        """Get list of all available diseases in the database"""
        return list(cls.TREATMENTS.keys())
    
    @classmethod
    def search_treatment(cls, query):
        """
        Search for treatment by disease name
        
        Args:
            query: Search query string
            
        Returns:
            list: Matching diseases with basic treatment info
        """
        query_lower = query.lower()
        results = []
        
        for disease, treatment in cls.TREATMENTS.items():
            if query_lower in disease.lower():
                results.append({
                    'disease': disease,
                    'chemical': treatment['chemical']['name'],
                    'chemical_dosage': treatment['chemical']['dosage'],
                    'organic': treatment['organic']['name'],
                    'severity': treatment.get('severity', 'Moderate'),
                    'urgency': treatment.get('urgency', 'Consult expert')
                })
        
        return results
    
    @classmethod
    def get_disease_summary(cls, disease_name):
        """
        Get a brief summary of disease treatment
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            dict: Summary information
        """
        treatment = cls.TREATMENTS.get(disease_name, cls.DEFAULT_TREATMENT)
        
        return {
            'disease': disease_name,
            'chemical_treatment': f"{treatment['chemical']['name']} - {treatment['chemical']['dosage']}",
            'organic_treatment': f"{treatment['organic']['name']} - {treatment['organic']['dosage']}",
            'severity': treatment.get('severity', 'Moderate'),
            'urgency': treatment.get('urgency', 'Consult expert'),
            'key_prevention': treatment['prevention'][0] if treatment['prevention'] else 'Practice good crop management'
        }
    
    @classmethod
    def get_treatment_by_crop(cls, crop_name):
        """
        Get all treatments for a specific crop
        
        Args:
            crop_name: Name of the crop (Apple, Potato, Tomato, etc.)
            
        Returns:
            list: Treatments for diseases affecting the crop
        """
        results = []
        crop_lower = crop_name.lower()
        
        for disease, treatment in cls.TREATMENTS.items():
            if crop_lower in disease.lower():
                results.append({
                    'disease': disease,
                    'chemical': treatment['chemical']['name'],
                    'organic': treatment['organic']['name'],
                    'severity': treatment.get('severity', 'Moderate'),
                    'urgency': treatment.get('urgency', 'Consult expert')
                })
        
        return results
    
    @classmethod
    def get_emergency_treatments(cls):
        """
        Get treatments for high-urgency diseases
        
        Returns:
            list: Diseases requiring immediate action
        """
        emergencies = []
        
        for disease, treatment in cls.TREATMENTS.items():
            urgency = treatment.get('urgency', '')
            severity = treatment.get('severity', '')
            if 'Immediate' in urgency or severity == 'Severe':
                emergencies.append({
                    'disease': disease,
                    'severity': severity,
                    'urgency': urgency,
                    'chemical': treatment['chemical']['name'],
                    'organic': treatment['organic']['name']
                })
        
        return emergencies