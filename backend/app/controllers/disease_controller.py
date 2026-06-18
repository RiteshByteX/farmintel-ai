"""
Disease Detection Controller
Handles image processing, disease detection, and analysis logic
Supports 29 disease classes from PlantVillage dataset
"""

import os
import uuid
import base64
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

from app.services.ml_service import ml_service
from app.utils.image_processor import ImageProcessor
from app.utils.severity import SeverityCalculator


class DiseaseController:
    """
    Controller for disease detection operations
    Handles image upload, preprocessing, and disease prediction
    """
    
    # 29 Disease Classes Mapping (from your dataset)
    DISEASE_CLASSES = {
        # Apple (4)
        'Apple Scab': {'crop': 'Apple', 'severity': 'Moderate'},
        'Apple Black Rot': {'crop': 'Apple', 'severity': 'Severe'},
        'Apple Cedar Rust': {'crop': 'Apple', 'severity': 'Moderate'},
        'Apple Healthy': {'crop': 'Apple', 'severity': 'Low'},
        
        # Bell Pepper (2)
        'Bell Pepper Bacterial Spot': {'crop': 'Bell Pepper', 'severity': 'Moderate'},
        'Bell Pepper Healthy': {'crop': 'Bell Pepper', 'severity': 'Low'},
        
        # Cherry (2)
        'Cherry Healthy': {'crop': 'Cherry', 'severity': 'Low'},
        'Cherry Powdery Mildew': {'crop': 'Cherry', 'severity': 'Moderate'},
        
        # Corn (4)
        'Corn Cercospora Leaf Spot': {'crop': 'Corn', 'severity': 'Moderate'},
        'Corn Common Rust': {'crop': 'Corn', 'severity': 'Moderate'},
        'Corn Healthy': {'crop': 'Corn', 'severity': 'Low'},
        'Corn Northern Leaf Blight': {'crop': 'Corn', 'severity': 'Severe'},
        
        # Grape (4)
        'Grape Black Rot': {'crop': 'Grape', 'severity': 'Severe'},
        'Grape Esca': {'crop': 'Grape', 'severity': 'Severe'},
        'Grape Healthy': {'crop': 'Grape', 'severity': 'Low'},
        'Grape Leaf Blight': {'crop': 'Grape', 'severity': 'Moderate'},
        
        # Peach (2)
        'Peach Bacterial Spot': {'crop': 'Peach', 'severity': 'Moderate'},
        'Peach Healthy': {'crop': 'Peach', 'severity': 'Low'},
        
        # Potato (3)
        'Potato Early Blight': {'crop': 'Potato', 'severity': 'Moderate'},
        'Potato Healthy': {'crop': 'Potato', 'severity': 'Low'},
        'Potato Late Blight': {'crop': 'Potato', 'severity': 'Severe'},
        
        # Strawberry (2)
        'Strawberry Healthy': {'crop': 'Strawberry', 'severity': 'Low'},
        'Strawberry Leaf Scorch': {'crop': 'Strawberry', 'severity': 'Moderate'},
        
        # Tomato (6)
        'Tomato Bacterial Spot': {'crop': 'Tomato', 'severity': 'Moderate'},
        'Tomato Early Blight': {'crop': 'Tomato', 'severity': 'Moderate'},
        'Tomato Healthy': {'crop': 'Tomato', 'severity': 'Low'},
        'Tomato Late Blight': {'crop': 'Tomato', 'severity': 'Severe'},
        'Tomato Septoria Leaf Spot': {'crop': 'Tomato', 'severity': 'Moderate'},
        'Tomato Yellow Leaf Curl Virus': {'crop': 'Tomato', 'severity': 'Severe'}
    }
    
    @staticmethod
    def save_uploaded_image(file):
        """
        Save uploaded image to temporary storage
        
        Args:
            file: Uploaded file object from request
            
        Returns:
            dict: File information with success status
        """
        try:
            # Validate file
            if not file or file.filename == '':
                return {
                    'success': False,
                    'error': 'No file selected'
                }
            
            # Check file extension
            allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg'})
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_ext not in allowed_extensions:
                return {
                    'success': False,
                    'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }
            
            # Generate secure filename
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}.{file_ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure upload directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save file
            file.save(filepath)
            
            current_app.logger.info(f"Image saved: {filename}")
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'original_name': original_filename,
                'size': os.path.getsize(filepath)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error saving image: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to save image: {str(e)}'
            }
    
    @staticmethod
    def save_base64_image(base64_string, filename=None):
        """
        Save base64 encoded image to temporary storage
        
        Args:
            base64_string: Base64 encoded image string
            filename: Optional filename
            
        Returns:
            dict: File information with success status
        """
        try:
            # Extract base64 data
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Generate filename if not provided
            if not filename:
                filename = f"{uuid.uuid4().hex}.jpg"
            else:
                filename = secure_filename(filename)
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure upload directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath
            }
            
        except Exception as e:
            current_app.logger.error(f"Error saving base64 image: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to save image: {str(e)}'
            }
    
    @staticmethod
    def detect_disease(image_path):
        """
        Detect disease from image using ML model
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Detection results with disease name, confidence, etc.
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': 'Image file not found'
                }
            
            # Preprocess image for model
            processed_image = ImageProcessor.preprocess_for_model(image_path)
            
            if processed_image is None:
                return {
                    'success': False,
                    'error': 'Failed to preprocess image'
                }
            
            # Run prediction using ML service
            prediction = ml_service.predict(processed_image)
            
            if not prediction.get('success', False):
                return {
                    'success': False,
                    'error': prediction.get('error', 'Prediction failed')
                }
            
            # Get disease information
            disease_name = prediction.get('disease_name', 'Unknown')
            confidence = prediction.get('confidence', 0)
            class_index = prediction.get('class_index', 0)
            class_name = prediction.get('class_name', '')
            
            # Calculate severity
            severity = SeverityCalculator.calculate(confidence)
            
            # Get crop info
            crop_info = DiseaseController.DISEASE_CLASSES.get(disease_name, {})
            
            # Determine if healthy
            is_healthy = 'Healthy' in disease_name
            
            return {
                'success': True,
                'disease': disease_name,
                'disease_class': class_name,
                'confidence': round(confidence, 2),
                'class_index': class_index,
                'severity': severity['level'],
                'severity_color': severity['color'],
                'severity_action': severity['action'],
                'crop': crop_info.get('crop', 'Unknown'),
                'is_healthy': is_healthy,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error detecting disease: {str(e)}")
            return {
                'success': False,
                'error': f'Detection failed: {str(e)}'
            }
    
    @staticmethod
    def detect_from_base64(base64_string):
        """
        Detect disease from base64 encoded image
        
        Args:
            base64_string: Base64 encoded image string
            
        Returns:
            dict: Detection results
        """
        # Save base64 image
        save_result = DiseaseController.save_base64_image(base64_string)
        
        if not save_result['success']:
            return save_result
        
        # Detect disease
        detection_result = DiseaseController.detect_disease(save_result['filepath'])
        
        # Clean up temporary file
        try:
            os.remove(save_result['filepath'])
        except:
            pass
        
        return detection_result
    
    @staticmethod
    def get_disease_info(disease_name):
        """
        Get detailed information about a specific disease
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            dict: Disease information
        """
        disease_info = {
            # Apple Diseases
            'Apple Scab': {
                'symptoms': 'Olive-green to black spots on leaves and fruit. Leaves may curl and drop prematurely.',
                'causes': 'Fungal pathogen Venturia inaequalis. Overwinters in fallen leaves.',
                'season': 'Spring, wet conditions',
                'treatment': 'Apply sulfur or captan fungicides. Rake and destroy fallen leaves.',
                'prevention': 'Plant resistant varieties. Prune for air circulation.'
            },
            'Apple Black Rot': {
                'symptoms': 'Purple spots on leaves turning brown. Fruit shows black, rotting lesions with concentric rings.',
                'causes': 'Botryosphaeria obtusa fungus. Enters through wounds.',
                'season': 'Warm, wet weather',
                'treatment': 'Prune dead wood. Apply captan or thiophanate-methyl fungicides.',
                'prevention': 'Remove mummified fruit. Prune infected branches.'
            },
            'Apple Cedar Rust': {
                'symptoms': 'Bright yellow-orange spots on leaves. Small cup-like structures form on spots.',
                'causes': 'Gymnosporangium juniperi-virginianae. Requires both apple and cedar trees.',
                'season': 'Spring, rainy weather',
                'treatment': 'Apply myclobutanil or mancozeb. Remove nearby cedar galls.',
                'prevention': 'Plant resistant varieties. Remove cedar trees within 2 miles.'
            },
            
            # Potato Diseases
            'Potato Early Blight': {
                'symptoms': 'Small dark spots with concentric rings on lower leaves. Leaves turn yellow and die.',
                'causes': 'Alternaria solani fungus. Common in warm, humid conditions.',
                'season': 'Warm, humid weather',
                'treatment': 'Chlorothalonil or mancozeb fungicides. Rotate with non-host crops.',
                'prevention': 'Use disease-free seed potatoes. Maintain proper plant spacing.'
            },
            'Potato Late Blight': {
                'symptoms': 'Dark brown to black lesions on leaves. White mold on leaf undersides. Tubers show dark, shrunken areas.',
                'causes': 'Phytophthora infestans - same pathogen as tomato late blight.',
                'season': 'Cool, wet weather',
                'treatment': 'Apply mancozeb or chlorothalonil. Destroy infected plants immediately.',
                'prevention': 'Use certified disease-free seed potatoes. Hill soil around stems.'
            },
            
            # Tomato Diseases
            'Tomato Early Blight': {
                'symptoms': 'Dark spots with concentric rings (target-like appearance) on lower leaves. Yellowing around spots.',
                'causes': 'Alternaria solani fungus. Survives in soil and plant debris.',
                'season': 'Warm, humid weather',
                'treatment': 'Apply chlorothalonil or mancozeb fungicides every 7-10 days.',
                'prevention': 'Mulch to prevent soil splash. Water at base of plant.'
            },
            'Tomato Late Blight': {
                'symptoms': 'Dark, water-soaked spots on leaves that turn brown and crispy. White fuzzy growth on undersides.',
                'causes': 'Phytophthora infestans fungus. Spreads rapidly in cool, wet weather.',
                'season': 'Cool, wet weather',
                'treatment': 'Apply copper-based fungicides. Remove and destroy infected plants.',
                'prevention': 'Use resistant varieties. Avoid overhead irrigation.'
            },
            'Tomato Bacterial Spot': {
                'symptoms': 'Small dark spots with yellow halos on leaves. Spots may coalesce and cause defoliation.',
                'causes': 'Xanthomonas campestris bacteria. Spreads by splashing water.',
                'season': 'Warm, wet weather',
                'treatment': 'Apply copper-based bactericides. Remove infected plants.',
                'prevention': 'Use disease-free seeds. Avoid overhead irrigation.'
            },
            'Tomato Septoria Leaf Spot': {
                'symptoms': 'Small circular spots with gray centers and dark borders on lower leaves.',
                'causes': 'Septoria lycopersici fungus. Survives on plant debris.',
                'season': 'Warm, humid weather',
                'treatment': 'Apply chlorothalonil or mancozeb fungicides.',
                'prevention': 'Remove lower leaves. Mulch to prevent soil splash.'
            },
            'Tomato Yellow Leaf Curl Virus': {
                'symptoms': 'Yellowing and curling of leaves. Stunted growth. Reduced fruit production.',
                'causes': 'Begomovirus transmitted by whiteflies.',
                'season': 'Warm weather (whitefly activity)',
                'treatment': 'No cure - Control whitefly vectors. Remove infected plants.',
                'prevention': 'Use resistant varieties. Insect netting. Control whiteflies.'
            },
            
            # Corn Diseases
            'Corn Common Rust': {
                'symptoms': 'Small, cinnamon-brown pustules scattered on leaves. Pustules turn black as plant matures.',
                'causes': 'Puccinia sorghi fungus. Spreads by wind.',
                'season': 'Cool, moist conditions',
                'treatment': 'Apply azoxystrobin or pyraclostrobin fungicides.',
                'prevention': 'Plant resistant hybrids. Early planting.'
            },
            'Corn Northern Leaf Blight': {
                'symptoms': 'Long, cigar-shaped gray-green to tan lesions on leaves.',
                'causes': 'Exserohilum turcicum fungus. Favored by humid conditions.',
                'season': 'Warm, humid weather',
                'treatment': 'Apply strobilurin or triazole fungicides.',
                'prevention': 'Use resistant hybrids. Crop rotation.'
            },
            'Corn Cercospora Leaf Spot': {
                'symptoms': 'Small rectangular brown spots with yellow halos.',
                'causes': 'Cercospora zeae-maydis fungus.',
                'season': 'Warm, humid weather',
                'treatment': 'Apply azoxystrobin or pyraclostrobin.',
                'prevention': 'Crop rotation. Plant resistant hybrids.'
            },
            
            # Grape Diseases
            'Grape Black Rot': {
                'symptoms': 'Brown to black circular spots on leaves. Fruit shrivels into hard black mummies.',
                'causes': 'Guignardia bidwellii fungus.',
                'season': 'Warm, wet weather',
                'treatment': 'Apply myclobutanil or mancozeb at bloom.',
                'prevention': 'Remove mummified fruit. Prune for air circulation.'
            },
            'Grape Esca': {
                'symptoms': 'Brown spots with dark borders on leaves. White rot in wood.',
                'causes': 'Phaeomoniella chlamydospora fungus.',
                'season': 'Spring to fall',
                'treatment': 'Remove infected wood. Protect pruning wounds.',
                'prevention': 'Use disease-free planting material.'
            },
            'Grape Leaf Blight': {
                'symptoms': 'Brown spots on leaves that enlarge and coalesce.',
                'causes': 'Pseudocercospora vitis fungus.',
                'season': 'Warm, humid weather',
                'treatment': 'Apply copper-based fungicides.',
                'prevention': 'Improve air circulation. Remove infected leaves.'
            },
            
            # Bell Pepper Diseases
            'Bell Pepper Bacterial Spot': {
                'symptoms': 'Small, water-soaked spots on leaves that turn brown with yellow halos.',
                'causes': 'Xanthomonas campestris bacteria.',
                'season': 'Warm, wet weather',
                'treatment': 'Apply copper-based bactericides.',
                'prevention': 'Use disease-free seeds. Avoid overhead irrigation.'
            },
            
            # Cherry Diseases
            'Cherry Powdery Mildew': {
                'symptoms': 'White powdery growth on leaves and young shoots.',
                'causes': 'Podosphaera clandestina fungus.',
                'season': 'Spring to early summer',
                'treatment': 'Apply sulfur or myclobutanil fungicides.',
                'prevention': 'Prune for air circulation. Plant resistant varieties.'
            },
            
            # Peach Diseases
            'Peach Bacterial Spot': {
                'symptoms': 'Small, angular water-soaked spots on leaves that turn purple-brown.',
                'causes': 'Xanthomonas arboricola bacteria.',
                'season': 'Warm, wet weather',
                'treatment': 'Apply copper-based bactericides.',
                'prevention': 'Plant resistant varieties. Avoid overhead irrigation.'
            },
            
            # Strawberry Diseases
            'Strawberry Leaf Scorch': {
                'symptoms': 'Purple to brown spots on leaves that enlarge and coalesce.',
                'causes': 'Diplocarpon earliana fungus.',
                'season': 'Warm, wet weather',
                'treatment': 'Apply captan or myclobutanil fungicides.',
                'prevention': 'Use disease-free plants. Crop rotation.'
            }
        }
        
        return disease_info.get(disease_name, {
            'symptoms': 'Information not available for this disease',
            'causes': 'Information not available',
            'season': 'Information not available',
            'treatment': 'Consult local agronomist',
            'prevention': 'Practice good crop management'
        })
    
    @staticmethod
    def get_all_diseases():
        """
        Get list of all available diseases
        
        Returns:
            list: All disease names
        """
        return list(DiseaseController.DISEASE_CLASSES.keys())
    
    @staticmethod
    def get_diseases_by_crop(crop_name):
        """
        Get diseases for a specific crop
        
        Args:
            crop_name: Name of the crop
            
        Returns:
            list: Disease names for the crop
        """
        diseases = []
        for disease, info in DiseaseController.DISEASE_CLASSES.items():
            if info.get('crop') == crop_name:
                diseases.append(disease)
        return diseases
    
    @staticmethod
    def batch_detect(image_paths):
        """
        Detect diseases for multiple images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            dict: Batch detection results
        """
        results = []
        for path in image_paths:
            result = DiseaseController.detect_disease(path)
            results.append(result)
        
        success_count = len([r for r in results if r.get('success')])
        
        return {
            'success': True,
            'total': len(results),
            'success_count': success_count,
            'error_count': len(results) - success_count,
            'results': results
        }
    
    @staticmethod
    def cleanup_temp_files(image_path):
        """
        Clean up temporary image file
        
        Args:
            image_path: Path to image file to delete
            
        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error cleaning up file: {str(e)}")
            return False