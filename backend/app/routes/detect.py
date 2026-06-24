"""
Disease Detection Routes - Image upload and disease detection endpoints
Handles file uploads, image processing, and AI model prediction
"""

import os
import uuid
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime

from app.controllers.disease_controller import DiseaseController
from app.controllers.treatment_controller import TreatmentController
from app.models.schemas import DetectionRequest, ValidationError
from app.services.ml_service import ml_service
from app.utils.image_processor import ImageProcessor

detect_bp = Blueprint('detect', __name__)


def allowed_file(filename):
    """
    Check if file extension is allowed
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file type is allowed
    """
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def convert_numpy_types(obj):
    """
    Convert numpy types to Python native types for JSON serialization
    
    Args:
        obj: Any object that might contain numpy types
        
    Returns:
        Python native types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj


@detect_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    Upload an image file for disease detection
    POST /api/upload
    Content-Type: multipart/form-data
    Body: image (file)
    
    Returns:
        JSON with file information
    """
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided',
                'message': 'Please select an image file to upload'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select an image file'
            }), 400
        
        # Check file type
        if not allowed_file(file.filename):
            allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg'})
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'message': f'Allowed file types: {", ".join(allowed)}'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            return jsonify({
                'success': False,
                'error': 'File too large',
                'message': f'Maximum file size: {max_size // (1024 * 1024)}MB'
            }), 413
        
        # Save file
        result = DiseaseController.save_uploaded_image(file)
        
        if result['success']:
            return jsonify({
                'success': True,
                'filename': result['filename'],
                'filepath': result['filepath'],
                'original_name': result.get('original_name'),
                'size': result.get('size'),
                'message': 'Image uploaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Upload failed')
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred during upload'
        }), 500


@detect_bp.route('/detect', methods=['POST'])
def detect_disease():
    """
    Detect disease from uploaded image
    POST /api/detect
    Supports both:
    - Content-Type: multipart/form-data with "image" file field
    - Content-Type: application/json with {"image_path": "..."} or {"base64_image": "..."}
    
    Returns:
        JSON with disease detection results
    """
    try:
        # === DEBUG: Log request details ===
        current_app.logger.info(f"📥 Request Method: {request.method}")
        current_app.logger.info(f"📥 Request Content-Type: {request.content_type}")
        current_app.logger.info(f"📥 Request files: {request.files}")
        current_app.logger.info(f"📥 Request is_json: {request.is_json}")
        
        # === HANDLE FILE UPLOAD (multipart/form-data) - CHECK THIS FIRST ===
        # Check if request has files first (most specific)
        if request.files and 'image' in request.files:
            current_app.logger.info('📤 Detecting from file upload')
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected',
                    'message': 'Please select an image file'
                }), 400
            
            # Check file type
            if not allowed_file(file.filename):
                allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg'})
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type',
                    'message': f'Allowed file types: {", ".join(allowed)}'
                }), 400
            
            # Save the file temporarily
            save_result = DiseaseController.save_uploaded_image(file)
            
            if not save_result['success']:
                return jsonify({
                    'success': False,
                    'error': save_result.get('error', 'Upload failed')
                }), 500
            
            current_app.logger.info(f"📁 Image saved: {save_result['filepath']}")
            
            # Perform detection on the saved file
            result = DiseaseController.detect_disease(save_result['filepath'])
            
            # Clean up temp file
            try:
                if os.path.exists(save_result['filepath']):
                    os.remove(save_result['filepath'])
                    current_app.logger.info(f"🧹 Temp file cleaned: {save_result['filepath']}")
            except Exception as e:
                current_app.logger.warning(f"⚠️ Could not clean temp file: {e}")
            
            if result['success']:
                # Get treatment recommendations
                treatment = TreatmentController.get_treatment(
                    result['disease'], 
                    result['confidence']
                )
                
                # Get additional disease info
                disease_info = DiseaseController.get_disease_info(result['disease'])
                
                # === FIX: Convert numpy types to Python native types ===
                result = convert_numpy_types(result)
                treatment = convert_numpy_types(treatment)
                disease_info = convert_numpy_types(disease_info)
                
                response_data = {
                    'success': True,
                    'disease': result.get('disease', 'Unknown'),
                    'confidence': float(result.get('confidence', 0)),
                    'class_index': result.get('class_index'),
                    'class_name': result.get('class_name', ''),
                    'severity': result.get('severity', 'Unknown'),
                    'severity_color': result.get('severity_color', ''),
                    'confidence_level': result.get('confidence_level', ''),
                    'is_healthy': bool(result.get('is_healthy', False)),
                    'crop': result.get('crop', ''),
                    'symptoms': disease_info.get('symptoms', []),
                    'causes': disease_info.get('causes', []),
                    'season': disease_info.get('season', ''),
                    'treatment': {
                        'chemical_name': treatment.get('chemical_name', ''),
                        'chemical_dosage': treatment.get('chemical_dosage', ''),
                        'chemical_frequency': treatment.get('chemical_frequency', ''),
                        'chemical_method': treatment.get('chemical_method', ''),
                        'chemical_precautions': treatment.get('chemical_precautions', ''),
                        'organic_name': treatment.get('organic_name', ''),
                        'organic_dosage': treatment.get('organic_dosage', ''),
                        'organic_frequency': treatment.get('organic_frequency', ''),
                        'organic_method': treatment.get('organic_method', ''),
                        'organic_precautions': treatment.get('organic_precautions', ''),
                        'cultural_practices': treatment.get('cultural_practices', []),
                        'prevention_tips': treatment.get('prevention_tips', []),
                        'urgency': treatment.get('urgency', '')
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                current_app.logger.info(f"✅ Detection successful: {response_data['disease']} ({response_data['confidence']}%)")
                return jsonify(response_data)
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Detection failed'),
                    'message': 'Could not detect disease from the provided image'
                }), 500
        
        # === HANDLE JSON (application/json) ===
        elif request.is_json:
            current_app.logger.info('📤 Detecting from JSON')
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided',
                    'message': 'Please provide image_path or base64_image'
                }), 400
            
            # Validate request
            detection_request = DetectionRequest.from_dict(data)
            detection_request.validate()
            
            # Perform detection
            if detection_request.image_path:
                result = DiseaseController.detect_disease(detection_request.image_path)
            elif detection_request.base64_image:
                result = DiseaseController.detect_from_base64(detection_request.base64_image)
            else:
                return jsonify({
                    'success': False,
                    'error': 'No image provided',
                    'message': 'Please provide image_path or base64_image'
                }), 400
            
            if result['success']:
                # Get treatment recommendations
                treatment = TreatmentController.get_treatment(
                    result['disease'], 
                    result['confidence']
                )
                
                # Get additional disease info
                disease_info = DiseaseController.get_disease_info(result['disease'])
                
                # === FIX: Convert numpy types to Python native types ===
                result = convert_numpy_types(result)
                treatment = convert_numpy_types(treatment)
                disease_info = convert_numpy_types(disease_info)
                
                return jsonify({
                    'success': True,
                    'disease': result.get('disease', 'Unknown'),
                    'confidence': float(result.get('confidence', 0)),
                    'class_index': result.get('class_index'),
                    'class_name': result.get('class_name', ''),
                    'severity': result.get('severity', 'Unknown'),
                    'severity_color': result.get('severity_color', ''),
                    'confidence_level': result.get('confidence_level', ''),
                    'is_healthy': bool(result.get('is_healthy', False)),
                    'crop': result.get('crop', ''),
                    'symptoms': disease_info.get('symptoms', []),
                    'causes': disease_info.get('causes', []),
                    'season': disease_info.get('season', ''),
                    'treatment': {
                        'chemical_name': treatment.get('chemical_name', ''),
                        'chemical_dosage': treatment.get('chemical_dosage', ''),
                        'chemical_frequency': treatment.get('chemical_frequency', ''),
                        'chemical_method': treatment.get('chemical_method', ''),
                        'chemical_precautions': treatment.get('chemical_precautions', ''),
                        'organic_name': treatment.get('organic_name', ''),
                        'organic_dosage': treatment.get('organic_dosage', ''),
                        'organic_frequency': treatment.get('organic_frequency', ''),
                        'organic_method': treatment.get('organic_method', ''),
                        'organic_precautions': treatment.get('organic_precautions', ''),
                        'cultural_practices': treatment.get('cultural_practices', []),
                        'prevention_tips': treatment.get('prevention_tips', []),
                        'urgency': treatment.get('urgency', '')
                    },
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Detection failed'),
                    'message': 'Could not detect disease from the provided image'
                }), 500
        
        # === Unsupported content type ===
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported content type',
                'message': f'Use multipart/form-data with "image" field or application/json. Got: {request.content_type}'
            }), 415
            
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': e.message,
            'field': e.field
        }), 400
    except Exception as e:
        current_app.logger.error(f"Detection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred during disease detection'
        }), 500


@detect_bp.route('/detect/base64', methods=['POST'])
def detect_from_base64():
    """
    Detect disease from base64 encoded image
    POST /api/detect/base64
    Content-Type: application/json
    Body: {"image": "base64_encoded_string"}
    
    Returns:
        JSON with disease detection results
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'No image data provided',
                'message': 'Please provide base64 encoded image'
            }), 400
        
        base64_image = data['image']
        
        # Perform detection
        result = DiseaseController.detect_from_base64(base64_image)
        
        if result['success']:
            # Get treatment recommendations
            treatment = TreatmentController.get_treatment(
                result['disease'], 
                result['confidence']
            )
            
            # === FIX: Convert numpy types to Python native types ===
            result = convert_numpy_types(result)
            treatment = convert_numpy_types(treatment)
            
            return jsonify({
                'success': True,
                'disease': result.get('disease', 'Unknown'),
                'confidence': float(result.get('confidence', 0)),
                'severity': result.get('severity', 'Unknown'),
                'treatment': {
                    'chemical_name': treatment.get('chemical_name', ''),
                    'chemical_dosage': treatment.get('chemical_dosage', ''),
                    'organic_name': treatment.get('organic_name', ''),
                    'organic_dosage': treatment.get('organic_dosage', ''),
                    'cultural_practices': treatment.get('cultural_practices', []),
                    'prevention_tips': treatment.get('prevention_tips', [])
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Detection failed'),
                'message': 'Could not detect disease from the provided image'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Base64 detection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred during disease detection'
        }), 500


@detect_bp.route('/detect/batch', methods=['POST'])
def batch_detect():
    """
    Detect diseases from multiple images
    POST /api/detect/batch
    Content-Type: multipart/form-data
    Body: images (multiple files)
    
    Returns:
        JSON with batch detection results
    """
    try:
        # Check if files are present
        if 'images' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No images provided',
                'message': 'Please select at least one image file'
            }), 400
        
        files = request.files.getlist('images')
        
        if len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'No images provided',
                'message': 'Please select at least one image file'
            }), 400
        
        results = []
        success_count = 0
        error_count = 0
        
        for file in files:
            try:
                # Check file type
                if not allowed_file(file.filename):
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': 'Invalid file type'
                    })
                    error_count += 1
                    continue
                
                # Save file
                save_result = DiseaseController.save_uploaded_image(file)
                
                if not save_result['success']:
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': save_result.get('error', 'Upload failed')
                    })
                    error_count += 1
                    continue
                
                # Detect disease
                detection_result = DiseaseController.detect_disease(save_result['filepath'])
                
                # === FIX: Convert numpy types ===
                detection_result = convert_numpy_types(detection_result)
                
                if detection_result['success']:
                    results.append({
                        'filename': file.filename,
                        'success': True,
                        'disease': detection_result.get('disease', 'Unknown'),
                        'confidence': float(detection_result.get('confidence', 0)),
                        'severity': detection_result.get('severity', 'Unknown')
                    })
                    success_count += 1
                else:
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': detection_result.get('error', 'Detection failed')
                    })
                    error_count += 1
                    
                # Clean up temp file
                try:
                    os.remove(save_result['filepath'])
                except:
                    pass
                    
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
                error_count += 1
        
        return jsonify({
            'success': True,
            'total': len(files),
            'success_count': success_count,
            'error_count': error_count,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Batch detection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred during batch detection'
        }), 500


@detect_bp.route('/detect/health', methods=['GET'])
def detect_health():
    """
    Check detection service health
    GET /api/detect/health
    
    Returns:
        JSON with service status
    """
    from app.services.ml_service import ml_service
    
    return jsonify({
        'success': True,
        'service': 'disease_detection',
        'ml_service_loaded': ml_service is not None and ml_service.is_model_loaded() if ml_service else False,
        'model_path': current_app.config.get('MODEL_PATH'),
        'supported_formats': list(current_app.config.get('ALLOWED_EXTENSIONS', {})),
        'max_file_size': current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024),
        'timestamp': datetime.now().isoformat()
    })