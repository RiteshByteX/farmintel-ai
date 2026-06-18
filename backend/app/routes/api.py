"""
Main API Router - Root endpoints, health checks, and API documentation
"""

import os
import sys
from flask import Blueprint, jsonify, request, current_app, send_from_directory
from datetime import datetime
import platform

api_bp = Blueprint('api', __name__)


@api_bp.route('', methods=['GET'])
def api_root():
    """
    API root endpoint - Returns API information and available endpoints
    GET /api/
    """
    return jsonify({
        'name': current_app.config.get('APP_NAME', 'FarmIntel AI'),
        'version': current_app.config.get('APP_VERSION', '1.0.0'),
        'description': current_app.config.get('APP_DESCRIPTION', 'AI-powered crop disease detection and farm advisory system'),
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'root': {
                'method': 'GET',
                'path': '/api/',
                'description': 'API information'
            },
            'health': {
                'method': 'GET',
                'path': '/api/health',
                'description': 'Health check'
            },
            'upload': {
                'method': 'POST',
                'path': '/api/upload',
                'description': 'Upload image for disease detection'
            },
            'detect': {
                'method': 'POST',
                'path': '/api/detect',
                'description': 'Detect disease from uploaded image'
            },
            'treatment': {
                'method': 'POST',
                'path': '/api/treatment',
                'description': 'Get treatment recommendations'
            },
            'weather': {
                'method': 'GET',
                'path': '/api/weather',
                'description': 'Get weather data for location'
            },
            'history': {
                'method': 'GET',
                'path': '/api/history',
                'description': 'Get scan history'
            },
            'history_save': {
                'method': 'POST',
                'path': '/api/history',
                'description': 'Save detection to history'
            },
            'history_delete': {
                'method': 'DELETE',
                'path': '/api/history/{id}',
                'description': 'Delete history record'
            },
            'reports_pdf': {
                'method': 'POST',
                'path': '/api/report/pdf',
                'description': 'Generate PDF report'
            },
            'reports_csv': {
                'method': 'POST',
                'path': '/api/report/csv',
                'description': 'Generate CSV report'
            },
            'statistics': {
                'method': 'GET',
                'path': '/api/statistics',
                'description': 'Get scan statistics'
            }
        }
    })


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint - Returns service status
    GET /api/health
    """
    from app.services.ml_service import ml_service
    from app.services.weather_service import weather_service
    from app.models.history_model import history_model
    
    # Check ML service status
    ml_status = {
        'loaded': ml_service is not None and ml_service.is_model_loaded() if ml_service else False,
        'model_path': current_app.config.get('MODEL_PATH', 'Not configured')
    }
    
    # Check weather service status
    weather_status = {
        'configured': weather_service is not None,
        'api_key_set': bool(current_app.config.get('WEATHER_API_KEY'))
    }
    
    # Check database
    try:
        record_count = history_model.get_count()
        db_status = 'connected'
    except Exception as e:
        record_count = 0
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ml_service': ml_status,
            'weather_service': weather_status,
            'database': {
                'status': db_status,
                'record_count': record_count
            }
        },
        'system': {
            'python_version': sys.version.split()[0],
            'platform': platform.platform(),
            'environment': current_app.config.get('ENV', 'development')
        },
        'version': current_app.config.get('APP_VERSION', '1.0.0')
    })


@api_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check endpoint - For debugging
    GET /api/health/detailed
    """
    from app.services.ml_service import ml_service
    from app.services.weather_service import weather_service
    from app.models.history_model import history_model
    
    # Get detailed ML info
    ml_info = {}
    if ml_service:
        ml_info = ml_service.get_model_info()
    else:
        ml_info = {'loaded': False, 'message': 'ML service not initialized'}
    
    # Get weather service info
    weather_info = {
        'configured': weather_service is not None,
        'api_key_set': bool(current_app.config.get('WEATHER_API_KEY')),
        'api_url': current_app.config.get('WEATHER_API_BASE_URL', 'Not configured')
    }
    
    # Get database info
    try:
        stats = history_model.get_statistics()
        db_info = {
            'status': 'connected',
            'total_records': stats.get('total_scans', 0),
            'file_path': history_model.db_path
        }
    except Exception as e:
        db_info = {
            'status': 'error',
            'error': str(e)
        }
    
    # Get configuration
    config_info = {
        'debug': current_app.debug,
        'testing': current_app.testing,
        'upload_folder': current_app.config.get('UPLOAD_FOLDER'),
        'max_content_length': current_app.config.get('MAX_CONTENT_LENGTH'),
        'allowed_extensions': list(current_app.config.get('ALLOWED_EXTENSIONS', [])),
        'model_path': current_app.config.get('MODEL_PATH'),
        'weather_api_configured': bool(current_app.config.get('WEATHER_API_KEY'))
    }
    
    return jsonify({
        'status': 'healthy' if ml_info.get('loaded', False) else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ml_service': ml_info,
            'weather_service': weather_info,
            'database': db_info
        },
        'configuration': config_info,
        'system': {
            'python_version': sys.version,
            'platform': platform.platform(),
            'processor': platform.processor(),
            'machine': platform.machine()
        }
    })


@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get overall application statistics
    GET /api/statistics
    """
    from app.models.history_model import history_model
    from app.controllers.treatment_controller import TreatmentController
    
    try:
        # Get history statistics
        history_stats = history_model.get_statistics()
        
        # Get disease count
        total_diseases = len(TreatmentController.get_all_diseases())
        
        return jsonify({
            'success': True,
            'statistics': {
                'scans': {
                    'total': history_stats.get('total_scans', 0),
                    'diseased': history_stats.get('diseased_count', 0),
                    'healthy': history_stats.get('healthy_count', 0),
                    'disease_rate': history_stats.get('disease_rate', 0),
                    'avg_confidence': history_stats.get('avg_confidence', 0)
                },
                'diseases': {
                    'total_available': total_diseases,
                    'most_common': history_stats.get('most_common_disease'),
                    'breakdown': history_stats.get('disease_breakdown', {})
                },
                'severity': {
                    'most_common': history_stats.get('most_common_severity'),
                    'breakdown': history_stats.get('severity_breakdown', {})
                },
                'timeline': {
                    'first_scan': history_stats.get('first_scan'),
                    'last_scan': history_stats.get('last_scan'),
                    'scans_by_month': history_stats.get('scans_by_month', {})
                },
                'health': {
                    'recovery_rate': history_stats.get('recovery_rate', 0)
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/info', methods=['GET'])
def app_info():
    """
    Get application information
    GET /api/info
    """
    return jsonify({
        'name': current_app.config.get('APP_NAME', 'FarmIntel AI'),
        'version': current_app.config.get('APP_VERSION', '1.0.0'),
        'description': current_app.config.get('APP_DESCRIPTION', 'AI-powered crop disease detection'),
        'author': current_app.config.get('APP_AUTHOR', 'FarmIntel AI Team'),
        'features': [
            'Disease detection from leaf images',
            'Treatment recommendations (chemical & organic)',
            'Weather analysis and disease risk forecasting',
            'Scan history with statistics',
            'PDF and CSV report generation',
            'Disease library with 29+ diseases'
        ],
        'supported_crops': [
            'Apple', 'Bell Pepper', 'Cherry', 'Corn', 'Grape', 
            'Peach', 'Potato', 'Strawberry', 'Tomato'
        ],
        'api_version': '1.0.0'
    })


@api_bp.route('/docs', methods=['GET'])
def api_documentation():
    """
    Simple API documentation page
    GET /api/docs
    """
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FarmIntel AI - API Documentation</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #0F0F1A;
                color: #E5E7EB;
            }
            h1 { color: #818CF8; border-bottom: 2px solid #4F46E5; padding-bottom: 10px; }
            h2 { color: #A5B4FC; margin-top: 30px; }
            h3 { color: #C7D2FE; margin-top: 20px; }
            .endpoint {
                background: #1E293B;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid #4F46E5;
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            .GET { background: #10B981; color: white; }
            .POST { background: #3B82F6; color: white; }
            .DELETE { background: #EF4444; color: white; }
            .PUT { background: #F59E0B; color: white; }
            .path {
                font-family: monospace;
                font-size: 1.1em;
            }
            .description { color: #94A3B8; margin-top: 8px; }
            pre {
                background: #0F172A;
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
                font-size: 13px;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #334155;
                text-align: center;
                color: #64748B;
            }
        </style>
    </head>
    <body>
        <h1>🌾 FarmIntel AI API Documentation</h1>
        <p>Base URL: <code>http://localhost:5000/api</code></p>
        
        <h2>📡 Endpoints</h2>
        
        <div class="endpoint">
            <span class="method GET">GET</span>
            <span class="path">/</span>
            <div class="description">Get API information and available endpoints</div>
        </div>
        
        <div class="endpoint">
            <span class="method GET">GET</span>
            <span class="path">/health</span>
            <div class="description">Health check endpoint</div>
        </div>
        
        <div class="endpoint">
            <span class="method GET">GET</span>
            <span class="path">/statistics</span>
            <div class="description">Get application statistics</div>
        </div>
        
        <div class="endpoint">
            <span class="method POST">POST</span>
            <span class="path">/upload</span>
            <div class="description">Upload an image for disease detection</div>
            <pre>multipart/form-data with 'image' file</pre>
        </div>
        
        <div class="endpoint">
            <span class="method POST">POST</span>
            <span class="path">/detect</span>
            <div class="description">Detect disease from uploaded image</div>
            <pre>{"image_path": "path/to/image.jpg"}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method POST">POST</span>
            <span class="path">/treatment</span>
            <div class="description">Get treatment recommendations for a disease</div>
            <pre>{"disease_name": "Tomato Late Blight", "confidence": 94.2}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method GET">GET</span>
            <span class="path">/weather?city=Mumbai</span>
            <div class="description">Get weather data for a location</div>
            <pre>Query params: city, lat, lon, or pincode</pre>
        </div>
        
        <div class="endpoint">
            <span class="method GET">GET</span>
            <span class="path">/history</span>
            <div class="description">Get scan history (limit, offset params)</div>
        </div>
        
        <div class="endpoint">
            <span class="method POST">POST</span>
            <span class="path">/history</span>
            <div class="description">Save a detection to history</div>
            <pre>{"disease": "...", "confidence": 94.2, ...}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method DELETE">DELETE</span>
            <span class="path">/history/{id}</span>
            <div class="description">Delete a history record by ID</div>
        </div>
        
        <div class="endpoint">
            <span class="method POST">POST</span>
            <span class="path">/report/pdf</span>
            <div class="description">Generate PDF report</div>
        </div>
        
        <div class="endpoint">
            <span class="method POST">POST</span>
            <span class="path">/report/csv</span>
            <div class="description">Generate CSV report</div>
        </div>
        
        <h2>📋 Response Format</h2>
        <pre>{
    "success": true/false,
    "data": {...},
    "message": "...",
    "timestamp": "2024-01-01T00:00:00"
}</pre>
        
        <h2>🔧 Error Codes</h2>
        <ul>
            <li><strong>400</strong> - Bad Request - Invalid parameters</li>
            <li><strong>404</strong> - Not Found - Resource not found</li>
            <li><strong>413</strong> - Payload Too Large - File too big</li>
            <li><strong>500</strong> - Internal Server Error</li>
        </ul>
        
        <div class="footer">
            <p>FarmIntel AI - Empowering Farmers with AI Technology</p>
            <p>Version 1.0.0</p>
        </div>
    </body>
    </html>
    """
    return docs_html, 200, {'Content-Type': 'text/html'}


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': f'The endpoint {request.path} does not exist',
        'available_endpoints': [
            '/api/',
            '/api/health',
            '/api/upload',
            '/api/detect',
            '/api/treatment',
            '/api/weather',
            '/api/history',
            '/api/report/pdf',
            '/api/report/csv',
            '/api/statistics'
        ]
    }), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'message': f'{request.method} is not allowed for {request.path}'
    }), 405