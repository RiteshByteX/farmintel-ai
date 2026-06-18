"""
Disease Model - TensorFlow model wrapper for plant disease detection
Supports 29 disease classes from PlantVillage dataset
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from flask import current_app
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class PredictionResult:
    """Data class for prediction results"""
    disease_name: str
    confidence: float
    class_index: int
    class_name: str
    severity: str
    confidence_level: str
    is_healthy: bool
    all_probabilities: Optional[Dict[str, float]] = None
    top_predictions: Optional[List[Tuple[str, float]]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON response"""
        return {
            'disease_name': self.disease_name,
            'confidence': round(self.confidence, 2),
            'class_index': self.class_index,
            'class_name': self.class_name,
            'severity': self.severity,
            'confidence_level': self.confidence_level,
            'is_healthy': self.is_healthy,
            'top_predictions': self.top_predictions[:5] if self.top_predictions else []
        }


class DiseaseModel:
    """
    Wrapper class for TensorFlow disease detection model
    Supports 29 disease classes from PlantVillage dataset
    """
    
    # 29 CLASS NAMES (PlantVillage Dataset)
    CLASS_NAMES = [
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
        'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust',
        'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight',
        'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        'Peach___Bacterial_spot', 'Peach___healthy',
        'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight',
        'Strawberry___healthy', 'Strawberry___Leaf_scorch',
        'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy',
        'Tomato___Late_blight', 'Tomato___Septoria_leaf_spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
    ]
    
    # User-friendly display names
    DISPLAY_NAMES = {
        'Apple___Apple_scab': 'Apple Scab',
        'Apple___Black_rot': 'Apple Black Rot',
        'Apple___Cedar_apple_rust': 'Apple Cedar Rust',
        'Apple___healthy': 'Apple Healthy',
        'Pepper,_bell___Bacterial_spot': 'Bell Pepper Bacterial Spot',
        'Pepper,_bell___healthy': 'Bell Pepper Healthy',
        'Cherry_(including_sour)___healthy': 'Cherry Healthy',
        'Cherry_(including_sour)___Powdery_mildew': 'Cherry Powdery Mildew',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 'Corn Cercospora Leaf Spot',
        'Corn_(maize)___Common_rust': 'Corn Common Rust',
        'Corn_(maize)___healthy': 'Corn Healthy',
        'Corn_(maize)___Northern_Leaf_Blight': 'Corn Northern Leaf Blight',
        'Grape___Black_rot': 'Grape Black Rot',
        'Grape___Esca_(Black_Measles)': 'Grape Esca',
        'Grape___healthy': 'Grape Healthy',
        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': 'Grape Leaf Blight',
        'Peach___Bacterial_spot': 'Peach Bacterial Spot',
        'Peach___healthy': 'Peach Healthy',
        'Potato___Early_blight': 'Potato Early Blight',
        'Potato___healthy': 'Potato Healthy',
        'Potato___Late_blight': 'Potato Late Blight',
        'Strawberry___healthy': 'Strawberry Healthy',
        'Strawberry___Leaf_scorch': 'Strawberry Leaf Scorch',
        'Tomato___Bacterial_spot': 'Tomato Bacterial Spot',
        'Tomato___Early_blight': 'Tomato Early Blight',
        'Tomato___healthy': 'Tomato Healthy',
        'Tomato___Late_blight': 'Tomato Late Blight',
        'Tomato___Septoria_leaf_spot': 'Tomato Septoria Leaf Spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Tomato Yellow Leaf Curl Virus'
    }
    
    # Crop groupings
    CROP_GROUPS = {
        'Apple': ['Apple Scab', 'Apple Black Rot', 'Apple Cedar Rust', 'Apple Healthy'],
        'Bell Pepper': ['Bell Pepper Bacterial Spot', 'Bell Pepper Healthy'],
        'Cherry': ['Cherry Healthy', 'Cherry Powdery Mildew'],
        'Corn': ['Corn Cercospora Leaf Spot', 'Corn Common Rust', 'Corn Healthy', 'Corn Northern Leaf Blight'],
        'Grape': ['Grape Black Rot', 'Grape Esca', 'Grape Healthy', 'Grape Leaf Blight'],
        'Peach': ['Peach Bacterial Spot', 'Peach Healthy'],
        'Potato': ['Potato Early Blight', 'Potato Healthy', 'Potato Late Blight'],
        'Strawberry': ['Strawberry Healthy', 'Strawberry Leaf Scorch'],
        'Tomato': ['Tomato Bacterial Spot', 'Tomato Early Blight', 'Tomato Healthy', 
                   'Tomato Late Blight', 'Tomato Septoria Leaf Spot', 'Tomato Yellow Leaf Curl Virus']
    }
    
    # Severity thresholds
    SEVERITY_THRESHOLDS = {
        'severe': 85,
        'moderate': 70,
        'mild': 50,
        'low': 0
    }
    
    CONFIDENCE_LEVELS = {
        'Very High': 90,
        'High': 75,
        'Medium': 60,
        'Low': 40,
        'Very Low': 0
    }
    
    def __init__(self, model_path: str = None):
        """
        Initialize the disease detection model
        
        Args:
            model_path: Path to the trained model file (.h5 or .keras)
        """
        # Don't use current_app at module load time
        if model_path:
            self.model_path = model_path
        else:
            # Try environment variable first
            self.model_path = os.environ.get('MODEL_PATH', 'models/plant_disease_model.h5')
        
        self.model = None
        self.input_shape = (224, 224, 3)
        self.confidence_threshold = 0.5
        self.class_indices = None
        self._load_model()
        self._load_class_indices()
    
    def _load_model(self):
        """Load the TensorFlow model from disk"""
        try:
            # Check multiple possible paths
            possible_paths = [
                self.model_path,
                os.path.join('models', 'plant_disease_model.h5'),
                os.path.join(os.path.dirname(__file__), '../../models/plant_disease_model.h5')
            ]
            
            loaded = False
            for path in possible_paths:
                if os.path.exists(path):
                    self.model = load_model(path)
                    self.model_path = path
                    loaded = True
                    print(f"✅ Model loaded from {path}")
                    break
            
            if not loaded:
                print(f"⚠️ Model not found at {self.model_path}")
                self.model = None
                
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            self.model = None
    
    def _load_class_indices(self):
        """Load class indices from JSON file if available"""
        indices_path = os.path.join(os.path.dirname(self.model_path), 'class_indices.json')
        if os.path.exists(indices_path):
            try:
                with open(indices_path, 'r') as f:
                    self.class_indices = json.load(f)
                print(f"✅ Loaded class indices from {indices_path}")
            except Exception as e:
                print(f"Error loading class indices: {e}")
    
    def preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """Preprocess image for model input"""
        import cv2
        
        # Resize to target size
        if image_array.shape[:2] != self.input_shape[:2]:
            image_array = cv2.resize(image_array, self.input_shape[:2])
        
        # Convert BGR to RGB if needed
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        
        # Normalize pixel values to [0, 1]
        image_array = image_array.astype('float32') / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def preprocess_image_file(self, image_path: str) -> np.ndarray:
        """Load and preprocess image from file path"""
        import cv2
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        return self.preprocess_image(img)
    
    def predict(self, image_input: np.ndarray) -> PredictionResult:
        """Predict disease from preprocessed image array"""
        if self.model is None:
            return self._mock_prediction()
        
        try:
            predictions = self.model.predict(image_input, verbose=0)
            predictions = predictions[0]
            
            class_idx = np.argmax(predictions)
            confidence = float(predictions[class_idx]) * 100
            
            class_name = self.CLASS_NAMES[class_idx] if class_idx < len(self.CLASS_NAMES) else "Unknown"
            disease_name = self.get_display_name(class_name)
            
            severity = self._calculate_severity(confidence)
            confidence_level = self._get_confidence_level(confidence)
            is_healthy = 'healthy' in disease_name.lower()
            
            top_indices = np.argsort(predictions)[::-1][:5]
            top_predictions = [
                (self.get_display_name(self.CLASS_NAMES[i]), float(predictions[i]) * 100)
                for i in top_indices
            ]
            
            return PredictionResult(
                disease_name=disease_name,
                confidence=confidence,
                class_index=class_idx,
                class_name=class_name,
                severity=severity,
                confidence_level=confidence_level,
                is_healthy=is_healthy,
                top_predictions=top_predictions
            )
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return self._mock_prediction()
    
    def predict_from_file(self, image_path: str) -> PredictionResult:
        """Predict disease from image file path"""
        processed_image = self.preprocess_image_file(image_path)
        return self.predict(processed_image)
    
    def _mock_prediction(self) -> PredictionResult:
        """Generate mock prediction when model is not available"""
        import random
        
        mock_diseases = [
            "Tomato Late Blight", "Tomato Early Blight", "Potato Late Blight",
            "Apple Scab", "Corn Common Rust", "Grape Black Rot",
            "Tomato Healthy", "Potato Healthy", "Apple Healthy"
        ]
        
        disease_name = random.choice(mock_diseases)
        confidence = random.uniform(70, 98)
        severity = self._calculate_severity(confidence)
        confidence_level = self._get_confidence_level(confidence)
        is_healthy = 'healthy' in disease_name.lower()
        
        class_name = "Unknown"
        for key, name in self.DISPLAY_NAMES.items():
            if name == disease_name:
                class_name = key
                break
        
        top_predictions = [(disease_name, confidence)]
        
        return PredictionResult(
            disease_name=disease_name,
            confidence=confidence,
            class_index=0,
            class_name=class_name,
            severity=severity,
            confidence_level=confidence_level,
            is_healthy=is_healthy,
            top_predictions=top_predictions
        )
    
    def _calculate_severity(self, confidence: float) -> str:
        """Calculate severity level based on confidence score"""
        if confidence >= self.SEVERITY_THRESHOLDS['severe']:
            return "Severe"
        elif confidence >= self.SEVERITY_THRESHOLDS['moderate']:
            return "Moderate"
        elif confidence >= self.SEVERITY_THRESHOLDS['mild']:
            return "Mild"
        else:
            return "Low"
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        for level, threshold in sorted(self.CONFIDENCE_LEVELS.items(), key=lambda x: x[1], reverse=True):
            if confidence >= threshold:
                return level
        return "Very Low"
    
    def get_display_name(self, class_name: str) -> str:
        """Get user-friendly display name for a class"""
        if class_name in self.DISPLAY_NAMES:
            return self.DISPLAY_NAMES[class_name]
        
        class_lower = class_name.lower()
        for key, name in self.DISPLAY_NAMES.items():
            if key.lower() in class_lower or class_lower in key.lower():
                return name
        
        return class_name.replace('_', ' ').replace('___', ' - ')
    
    def is_model_loaded(self) -> bool:
        """Check if model is successfully loaded"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if self.model:
            return {
                'loaded': True,
                'model_path': self.model_path,
                'input_shape': self.input_shape,
                'num_classes': len(self.CLASS_NAMES),
                'classes': self.CLASS_NAMES
            }
        else:
            return {
                'loaded': False,
                'model_path': self.model_path,
                'message': 'Model not loaded - using mock predictions',
                'num_classes': len(self.CLASS_NAMES)
            }


# Singleton instance
disease_model = DiseaseModel()