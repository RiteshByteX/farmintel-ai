"""
Treatment Routes - Treatment recommendations and remedies endpoints
Handles lookup of chemical, organic, and cultural treatment recommendations
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from app.controllers.treatment_controller import TreatmentController
from app.models.schemas import TreatmentRequest, ValidationError

treatment_bp = Blueprint('treatment', __name__)


@treatment_bp.route('/treatment', methods=['POST'])
def get_treatment():
    """
    Get treatment recommendations for a detected disease
    POST /api/treatment
    Content-Type: application/json
    Body: {"disease_name": "Tomato Late Blight", "confidence": 94.2}
    
    Returns:
        JSON with treatment recommendations
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'message': 'Please provide disease_name'
            }), 400
        
        # Validate request
        treatment_request = TreatmentRequest.from_dict(data)
        treatment_request.validate()
        
        # Get treatment recommendations
        result = TreatmentController.get_treatment(
            treatment_request.disease_name,
            treatment_request.confidence
        )
        
        if result.get('success', True):
            return jsonify({
                'success': True,
                'disease': result.get('disease'),
                'confidence': result.get('confidence'),
                'severity': result.get('severity'),
                'severity_color': result.get('severity_color'),
                'urgency': result.get('urgency'),
                
                # Chemical Treatment
                'chemical_name': result.get('chemical_name'),
                'chemical_dosage': result.get('chemical_dosage'),
                'chemical_frequency': result.get('chemical_frequency'),
                'chemical_method': result.get('chemical_method'),
                'chemical_precautions': result.get('chemical_precautions'),
                'chemical_products': result.get('chemical_products', []),
                
                # Organic Treatment
                'organic_name': result.get('organic_name'),
                'organic_dosage': result.get('organic_dosage'),
                'organic_frequency': result.get('organic_frequency'),
                'organic_method': result.get('organic_method'),
                'organic_precautions': result.get('organic_precautions'),
                'organic_alternative': result.get('organic_alternative'),
                
                # Cultural Practices
                'cultural_practices': result.get('cultural_practices', []),
                'cultural_spacing': result.get('cultural_spacing'),
                'cultural_watering': result.get('cultural_watering'),
                'cultural_soil': result.get('cultural_soil'),
                
                # Prevention Tips
                'prevention_tips': result.get('prevention_tips', []),
                
                # Additional Info
                'affected_area': result.get('affected_area'),
                'health_status': result.get('health_status'),
                
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Treatment lookup failed'),
                'message': f'Could not find treatment for {treatment_request.disease_name}'
            }), 404
            
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': e.message,
            'field': e.field
        }), 400
    except Exception as e:
        current_app.logger.error(f"Treatment error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching treatment recommendations'
        }), 500


@treatment_bp.route('/treatment/disease/<string:disease_name>', methods=['GET'])
def get_treatment_by_disease(disease_name):
    """
    Get treatment recommendations by disease name (GET method)
    GET /api/treatment/disease/Tomato%20Late%20Blight
    
    Returns:
        JSON with treatment recommendations
    """
    try:
        # Get treatment recommendations
        result = TreatmentController.get_treatment(disease_name)
        
        if result.get('success', True):
            return jsonify({
                'success': True,
                'disease': result.get('disease'),
                'severity': result.get('severity'),
                'urgency': result.get('urgency'),
                'chemical_treatment': f"{result.get('chemical_name', '')} - {result.get('chemical_dosage', '')}",
                'organic_treatment': f"{result.get('organic_name', '')} - {result.get('organic_dosage', '')}",
                'cultural_practices': result.get('cultural_practices', []),
                'prevention_tips': result.get('prevention_tips', []),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Disease not found',
                'message': f'No treatment found for {disease_name}'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Treatment error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching treatment recommendations'
        }), 500


@treatment_bp.route('/treatment/list', methods=['GET'])
def list_diseases():
    """
    Get list of all available diseases in treatment database
    GET /api/treatment/list
    
    Returns:
        JSON with list of diseases
    """
    try:
        diseases = TreatmentController.get_all_diseases()
        
        # Sort alphabetically
        diseases.sort()
        
        return jsonify({
            'success': True,
            'total': len(diseases),
            'diseases': diseases,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"List diseases error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching disease list'
        }), 500


@treatment_bp.route('/treatment/search', methods=['GET'])
def search_treatment():
    """
    Search for treatment by disease name
    GET /api/treatment/search?q=late+blight
    
    Returns:
        JSON with search results
    """
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided',
                'message': 'Please provide a search query using ?q='
            }), 400
        
        results = TreatmentController.search_treatment(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'total': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Search treatment error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while searching for treatments'
        }), 500


@treatment_bp.route('/treatment/summary/<string:disease_name>', methods=['GET'])
def get_treatment_summary(disease_name):
    """
    Get a brief summary of treatment for a disease
    GET /api/treatment/summary/Tomato%20Late%20Blight
    
    Returns:
        JSON with treatment summary
    """
    try:
        summary = TreatmentController.get_disease_summary(disease_name)
        
        return jsonify({
            'success': True,
            'disease': summary.get('disease'),
            'chemical_treatment': summary.get('chemical_treatment'),
            'organic_treatment': summary.get('organic_treatment'),
            'severity': summary.get('severity'),
            'urgency': summary.get('urgency'),
            'key_prevention': summary.get('key_prevention'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Treatment summary error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Could not find treatment summary for {disease_name}'
        }), 404


@treatment_bp.route('/treatment/crop/<string:crop_name>', methods=['GET'])
def get_treatments_by_crop(crop_name):
    """
    Get all treatments for a specific crop
    GET /api/treatment/crop/Tomato
    
    Returns:
        JSON with treatments for the crop
    """
    try:
        results = TreatmentController.get_treatment_by_crop(crop_name)
        
        return jsonify({
            'success': True,
            'crop': crop_name,
            'total': len(results),
            'treatments': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Treatments by crop error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'An error occurred while fetching treatments for {crop_name}'
        }), 500


@treatment_bp.route('/treatment/emergency', methods=['GET'])
def get_emergency_treatments():
    """
    Get treatments for high-urgency diseases
    GET /api/treatment/emergency
    
    Returns:
        JSON with emergency treatments
    """
    try:
        emergencies = TreatmentController.get_emergency_treatments()
        
        return jsonify({
            'success': True,
            'total': len(emergencies),
            'emergency_treatments': emergencies,
            'message': 'These diseases require immediate action',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Emergency treatments error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching emergency treatments'
        }), 500


@treatment_bp.route('/treatment/health', methods=['GET'])
def treatment_health():
    """
    Check treatment service health
    GET /api/treatment/health
    
    Returns:
        JSON with service status
    """
    return jsonify({
        'success': True,
        'service': 'treatment_recommendations',
        'diseases_available': len(TreatmentController.get_all_diseases()),
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })