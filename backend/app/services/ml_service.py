"""
ML Service - Machine Learning Service for Disease Detection
Handles model loading, image preprocessing, and disease prediction
Supports 29 disease classes from PlantVillage dataset
"""

import os
import logging
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import random

# Setup logger
logger = logging.getLogger(__name__)


class MLService:
    """
    Machine Learning Service for plant disease detection
    Loads and manages TensorFlow model, provides prediction interface
    """
    
    # 29 Class Names (PlantVillage Dataset)
    CLASS_NAMES = [
        # Apple (4)
        'Apple___Apple_scab',
        'Apple___Black_rot',
        'Apple___Cedar_apple_rust',
        'Apple___healthy',
        
        # Bell Pepper (2)
        'Pepper,_bell___Bacterial_spot',
        'Pepper,_bell___healthy',
        
        # Cherry (2)
        'Cherry_(including_sour)___healthy',
        'Cherry_(including_sour)___Powdery_mildew',
        
        # Corn/Maize (4)
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust',
        'Corn_(maize)___healthy',
        'Corn_(maize)___Northern_Leaf_Blight',
        
        # Grape (4)
        'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)',
        'Grape___healthy',
        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        
        # Peach (2)
        'Peach___Bacterial_spot',
        'Peach___healthy',
        
        # Potato (3)
        'Potato___Early_blight',
        'Potato___healthy',
        'Potato___Late_blight',
        
        # Strawberry (2)
        'Strawberry___healthy',
        'Strawberry___Leaf_scorch',
        
        # Tomato (6)
        'Tomato___Bacterial_spot',
        'Tomato___Early_blight',
        'Tomato___healthy',
        'Tomato___Late_blight',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
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
    
    # Severity thresholds
    SEVERITY_THRESHOLDS = {
        'severe': 85,
        'moderate': 70,
        'mild': 50,
        'low': 0
    }
    
    # Severity colors and actions
    SEVERITY_INFO = {
        'Severe': {'color': '#EF4444', 'action': 'Immediate action needed - Apply treatment today'},
        'Moderate': {'color': '#F59E0B', 'action': 'Action within 3 days - Monitor closely'},
        'Mild': {'color': '#10B981', 'action': 'Monitor and treat if spreads'},
        'Low': {'color': '#6B7280', 'action': 'Retake clearer photo for accurate detection'}
    }
    
    def __init__(self, model_path: str = None):
        """
        Initialize ML Service
        
        Args:
            model_path: Path to the trained model file
        """
        # Use environment variable or default path
        if model_path is None:
            model_path = os.environ.get('MODEL_PATH', 'models/plant_disease_model.h5')
        
        self.model_path = model_path
        self.model = None
        self.input_shape = (224, 224, 3)
        self.confidence_threshold = 0.5
        self._load_model()
    
    def _load_model(self):
        """Load the TensorFlow model from disk"""
        try:
            # Check multiple possible paths
            possible_paths = [
                self.model_path,
                os.path.join('models', 'plant_disease_model.h5'),
                os.path.join('backend', 'models', 'plant_disease_model.h5'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'plant_disease_model.h5')
            ]
            
            loaded = False
            for path in possible_paths:
                if os.path.exists(path):
                    self.model = load_model(path)
                    self.model_path = path
                    loaded = True
                    print(f"✅ ML Model loaded from {path}")
                    print(f"   Input shape: {self.model.input_shape}")
                    print(f"   Output classes: {self.model.output_shape[-1]}")
                    break
            
            if not loaded:
                print(f"⚠️ Model not found. Searched paths:")
                for path in possible_paths:
                    print(f"   - {os.path.abspath(path)}")
                print(f"   Using mock prediction mode.")
                self.model = None
                
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            self.model = None
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load and preprocess image for model input
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image array or None if error
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize to target size
            img = cv2.resize(img, self.input_shape[:2])
            
            # Normalize pixel values to [0, 1]
            img = img.astype('float32') / 255.0
            
            # Add batch dimension
            img = np.expand_dims(img, axis=0)
            
            return img
            
        except Exception as e:
            print(f"Image preprocessing error: {str(e)}")
            return None
    
    def predict(self, image_input) -> Dict[str, Any]:
        """
        Predict disease from image input (path or array)
        
        Args:
            image_input: Path to image file or preprocessed image array
            
        Returns:
            Dictionary with prediction results
        """
        # Handle different input types
        if isinstance(image_input, str):
            # It's a file path
            processed_image = self.preprocess_image(image_input)
            if processed_image is None:
                return self._get_mock_prediction("Image preprocessing failed")
        elif isinstance(image_input, np.ndarray):
            # It's already preprocessed
            processed_image = image_input
        else:
            return self._get_mock_prediction("Invalid input type")
        
        # Run prediction
        if self.model is None:
            return self._get_mock_prediction()
        
        try:
            # Get prediction
            predictions = self.model.predict(processed_image, verbose=0)
            predictions = predictions[0]  # Remove batch dimension
            
            # Get top prediction
            class_idx = np.argmax(predictions)
            confidence = float(predictions[class_idx]) * 100
            
            # Get class name
            class_name = self.CLASS_NAMES[class_idx] if class_idx < len(self.CLASS_NAMES) else "Unknown"
            disease_name = self.get_display_name(class_name)
            
            # Calculate severity
            severity = self._calculate_severity(confidence)
            severity_info = self.SEVERITY_INFO.get(severity, self.SEVERITY_INFO['Low'])
            
            # Get top 5 predictions
            top_indices = np.argsort(predictions)[::-1][:5]
            top_predictions = [
                {
                    'disease': self.get_display_name(self.CLASS_NAMES[i]),
                    'confidence': float(predictions[i]) * 100,
                    'class_name': self.CLASS_NAMES[i]
                }
                for i in top_indices
            ]
            
            # Get crop name
            crop = self._get_crop_from_disease(disease_name)
            
            return {
                'success': True,
                'disease_name': disease_name,
                'disease': disease_name,  # Alias for compatibility
                'confidence': round(confidence, 2),
                'class_index': class_idx,
                'class_name': class_name,
                'severity': severity,
                'severity_level': severity,
                'severity_color': severity_info['color'],
                'severity_action': severity_info['action'],
                'is_healthy': 'healthy' in disease_name.lower(),
                'crop': crop,
                'top_predictions': top_predictions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return self._get_mock_prediction(str(e))
    
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
    
    def _get_crop_from_disease(self, disease_name: str) -> str:
        """Extract crop name from disease name"""
        crops = ['Apple', 'Bell Pepper', 'Cherry', 'Corn', 'Grape', 'Peach', 'Potato', 'Strawberry', 'Tomato']
        for crop in crops:
            if crop in disease_name:
                return crop
        return 'Unknown'
    
    def _get_mock_prediction(self, error_msg: str = None) -> Dict[str, Any]:
        """
        Generate mock prediction when model is not available
        
        Args:
            error_msg: Optional error message
            
        Returns:
            Mock prediction results
        """
        # Common diseases for mock (from 29 classes)
        mock_diseases = [
            ("Tomato Late Blight", 92),
            ("Tomato Early Blight", 87),
            ("Potato Late Blight", 89),
            ("Apple Scab", 85),
            ("Corn Common Rust", 84),
            ("Grape Black Rot", 86),
            ("Tomato Healthy", 91),
            ("Potato Healthy", 90),
            ("Apple Healthy", 88)
        ]
        
        disease_name, confidence = random.choice(mock_diseases)
        severity = self._calculate_severity(confidence)
        severity_info = self.SEVERITY_INFO.get(severity, self.SEVERITY_INFO['Low'])
        crop = self._get_crop_from_disease(disease_name)
        
        # Find class name
        class_name = "Unknown"
        for key, name in self.DISPLAY_NAMES.items():
            if name == disease_name:
                class_name = key
                break
        
        return {
            'success': True,
            'disease_name': disease_name,
            'disease': disease_name,
            'confidence': round(confidence, 2),
            'class_index': 0,
            'class_name': class_name,
            'severity': severity,
            'severity_level': severity,
            'severity_color': severity_info['color'],
            'severity_action': severity_info['action'],
            'is_healthy': 'healthy' in disease_name.lower(),
            'crop': crop,
            'top_predictions': [],
            'is_mock': True,
            'message': error_msg or "Using mock prediction (model not loaded)",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_display_name(self, class_name: str) -> str:
        """Get user-friendly display name for a class"""
        return self.DISPLAY_NAMES.get(class_name, class_name.replace('_', ' ').replace('___', ' - '))
    
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
                'classes': self.CLASS_NAMES[:5]  # Return first 5 for brevity
            }
        else:
            return {
                'loaded': False,
                'model_path': self.model_path,
                'message': 'Model not loaded - using mock predictions',
                'num_classes': len(self.CLASS_NAMES)
            }
    
    def batch_predict(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Predict diseases for multiple images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of prediction results
        """
        results = []
        for path in image_paths:
            result = self.predict(path)
            result['image_path'] = path
            results.append(result)
        return results
    
    def predict_with_confidence_check(self, image_path: str, min_confidence: float = 50) -> Dict[str, Any]:
        """
        Predict with minimum confidence threshold check
        
        Args:
            image_path: Path to image file
            min_confidence: Minimum acceptable confidence (0-100)
            
        Returns:
            Prediction result with confidence validation
        """
        result = self.predict(image_path)
        
        if result.get('success', False):
            confidence = result.get('confidence', 0)
            if confidence < min_confidence:
                result['warning'] = f"Low confidence ({confidence}%). Please upload a clearer image."
                result['needs_review'] = True
        
        return result


# Singleton instance
ml_service = MLService()