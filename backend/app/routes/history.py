"""
History Routes - Scan history CRUD operations
Handles storing, retrieving, updating, and deleting scan records
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from app.controllers.history_controller import HistoryController
from app.models.history_model import ScanRecord
from app.models.schemas import HistoryRequest, HistorySearchRequest, ValidationError

history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
def get_history():
    """
    Get all scan history records
    GET /api/history
    GET /api/history?limit=10&offset=0
    
    Query Parameters:
        limit: Maximum number of records (default 50, max 1000)
        offset: Number of records to skip (default 0)
        sort_by: Field to sort by (default timestamp)
        sort_order: asc or desc (default desc)
        
    Returns:
        JSON with history records and pagination info
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate
        history_request = HistoryRequest(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        history_request.validate()
        
        # Get history records
        records = HistoryController.get_all(limit=limit, offset=offset)
        
        # Convert to dict for JSON response
        history_list = []
        for record in records:
            history_list.append({
                'id': record.id,
                'disease': record.disease,
                'confidence': record.confidence,
                'severity': record.severity,
                'chemical_treatment': record.chemical_treatment,
                'organic_treatment': record.organic_treatment,
                'cultural_practices': record.cultural_practices,
                'prevention_tips': record.prevention_tips,
                'timestamp': record.timestamp,
                'date': record.get_formatted_date(),
                'is_healthy': record.is_healthy()
            })
        
        # Get total count
        total = HistoryController.get_count()
        
        return jsonify({
            'success': True,
            'total': total,
            'count': len(history_list),
            'offset': offset,
            'limit': limit,
            'history': history_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': e.message,
            'field': e.field
        }), 400
    except Exception as e:
        current_app.logger.error(f"Get history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching history'
        }), 500


@history_bp.route('/history', methods=['POST'])
def save_history():
    """
    Save a detection record to history
    POST /api/history
    Content-Type: application/json
    Body: {
        "disease": "Tomato Late Blight",
        "confidence": 94.2,
        "severity": "Severe",
        "chemical_treatment": "...",
        "organic_treatment": "...",
        "cultural_practices": "...",
        "prevention_tips": "...",
        "image_path": "optional/path/to/image.jpg",
        "location": "optional location",
        "notes": "optional notes"
    }
    
    Returns:
        JSON with saved record ID
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'message': 'Please provide detection data'
            }), 400
        
        # Required fields
        required_fields = ['disease', 'confidence', 'severity', 
                          'chemical_treatment', 'organic_treatment', 
                          'cultural_practices', 'prevention_tips']
        
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Create scan record
        record = ScanRecord(
            id=0,  # Will be auto-generated
            disease=data['disease'],
            confidence=data['confidence'],
            severity=data['severity'],
            chemical_treatment=data['chemical_treatment'],
            organic_treatment=data['organic_treatment'],
            cultural_practices=data['cultural_practices'],
            prevention_tips=data['prevention_tips'],
            image_path=data.get('image_path'),
            location=data.get('location'),
            notes=data.get('notes')
        )
        
        # Save to history
        saved_record = HistoryController.save(record)
        
        return jsonify({
            'success': True,
            'id': saved_record.id,
            'message': 'Detection saved to history successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Save history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while saving to history'
        }), 500


@history_bp.route('/history/<int:record_id>', methods=['GET'])
def get_history_by_id(record_id):
    """
    Get a specific history record by ID
    GET /api/history/{id}
    
    Returns:
        JSON with the record details
    """
    try:
        record = HistoryController.get_by_id(record_id)
        
        if record:
            return jsonify({
                'success': True,
                'record': {
                    'id': record.id,
                    'disease': record.disease,
                    'confidence': record.confidence,
                    'severity': record.severity,
                    'chemical_treatment': record.chemical_treatment,
                    'organic_treatment': record.organic_treatment,
                    'cultural_practices': record.cultural_practices,
                    'prevention_tips': record.prevention_tips,
                    'image_path': record.image_path,
                    'location': record.location,
                    'notes': record.notes,
                    'timestamp': record.timestamp,
                    'date': record.get_formatted_date(),
                    'is_healthy': record.is_healthy()
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Record not found',
                'message': f'No record found with ID {record_id}'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Get history by ID error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching the record'
        }), 500


@history_bp.route('/history/<int:record_id>', methods=['PUT'])
def update_history(record_id):
    """
    Update a history record
    PUT /api/history/{id}
    Content-Type: application/json
    Body: {"field": "new_value", ...}
    
    Returns:
        JSON with updated record
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'message': 'Please provide fields to update'
            }), 400
        
        # Update record
        updated_record = HistoryController.update(record_id, data)
        
        if updated_record:
            return jsonify({
                'success': True,
                'record': {
                    'id': updated_record.id,
                    'disease': updated_record.disease,
                    'confidence': updated_record.confidence,
                    'severity': updated_record.severity,
                    'chemical_treatment': updated_record.chemical_treatment,
                    'organic_treatment': updated_record.organic_treatment,
                    'cultural_practices': updated_record.cultural_practices,
                    'prevention_tips': updated_record.prevention_tips,
                    'image_path': updated_record.image_path,
                    'location': updated_record.location,
                    'notes': updated_record.notes,
                    'timestamp': updated_record.timestamp,
                    'updated_at': updated_record.updated_at
                },
                'message': 'Record updated successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Record not found',
                'message': f'No record found with ID {record_id}'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Update history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while updating the record'
        }), 500


@history_bp.route('/history/<int:record_id>', methods=['DELETE'])
def delete_history(record_id):
    """
    Delete a history record by ID
    DELETE /api/history/{id}
    
    Returns:
        JSON with deletion status
    """
    try:
        deleted = HistoryController.delete(record_id)
        
        if deleted:
            return jsonify({
                'success': True,
                'message': f'Record {record_id} deleted successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Record not found',
                'message': f'No record found with ID {record_id}'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Delete history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while deleting the record'
        }), 500


@history_bp.route('/history/batch/delete', methods=['POST'])
def delete_batch_history():
    """
    Delete multiple history records
    POST /api/history/batch/delete
    Content-Type: application/json
    Body: {"record_ids": [1, 2, 3]}
    
    Returns:
        JSON with deletion results
    """
    try:
        data = request.get_json()
        
        if not data or 'record_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'No record IDs provided',
                'message': 'Please provide record_ids array'
            }), 400
        
        record_ids = data['record_ids']
        
        if not isinstance(record_ids, list):
            return jsonify({
                'success': False,
                'error': 'Invalid format',
                'message': 'record_ids must be an array'
            }), 400
        
        deleted_count = HistoryController.delete_batch(record_ids)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'requested_count': len(record_ids),
            'message': f'Successfully deleted {deleted_count} records',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Batch delete history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while deleting records'
        }), 500


@history_bp.route('/history/clear', methods=['DELETE'])
def clear_all_history():
    """
    Delete all history records
    DELETE /api/history/clear
    
    Returns:
        JSON with deletion status
    """
    try:
        deleted_count = HistoryController.delete_all()
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted all {deleted_count} history records',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Clear history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while clearing history'
        }), 500


@history_bp.route('/history/search', methods=['GET'])
def search_history():
    """
    Search history records
    GET /api/history/search?q=late+blight
    GET /api/history/search?q=severe&field=severity
    
    Query Parameters:
        q: Search query
        field: Field to search in (disease, severity, etc.)
        limit: Maximum results (default 50)
        
    Returns:
        JSON with search results
    """
    try:
        query = request.args.get('q', '')
        field = request.args.get('field', 'disease')
        limit = request.args.get('limit', 50, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided',
                'message': 'Please provide a search query using ?q='
            }), 400
        
        # Validate search request
        search_request = HistorySearchRequest(query=query, field=field, limit=limit)
        search_request.validate()
        
        # Search records
        results = HistoryController.search(query, field)
        
        # Limit results
        results = results[:limit]
        
        # Convert to dict
        results_list = []
        for record in results:
            results_list.append({
                'id': record.id,
                'disease': record.disease,
                'confidence': record.confidence,
                'severity': record.severity,
                'timestamp': record.timestamp,
                'date': record.get_formatted_date()
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'field': field,
            'total': len(results),
            'results': results_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': e.message,
            'field': e.field
        }), 400
    except Exception as e:
        current_app.logger.error(f"Search history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while searching history'
        }), 500


@history_bp.route('/history/filter', methods=['GET'])
def filter_history():
    """
    Filter history records
    GET /api/history/filter?start_date=2024-01-01&end_date=2024-12-31
    GET /api/history/filter?severity=Severe
    GET /api/history/filter?disease=Late%20Blight
    
    Query Parameters:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        severity: Severity level
        disease: Disease name
        
    Returns:
        JSON with filtered results
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        severity = request.args.get('severity')
        disease = request.args.get('disease')
        
        results = []
        
        if start_date or end_date:
            results = HistoryController.filter_by_date(start_date, end_date)
        elif severity:
            results = HistoryController.filter_by_severity(severity)
        elif disease:
            results = HistoryController.filter_by_disease(disease)
        else:
            return jsonify({
                'success': False,
                'error': 'No filter parameters provided',
                'message': 'Please provide start_date, end_date, severity, or disease'
            }), 400
        
        # Convert to dict
        results_list = []
        for record in results:
            results_list.append({
                'id': record.id,
                'disease': record.disease,
                'confidence': record.confidence,
                'severity': record.severity,
                'timestamp': record.timestamp,
                'date': record.get_formatted_date()
            })
        
        return jsonify({
            'success': True,
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'severity': severity,
                'disease': disease
            },
            'total': len(results_list),
            'results': results_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Filter history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while filtering history'
        }), 500


@history_bp.route('/history/statistics', methods=['GET'])
def get_history_statistics():
    """
    Get statistics about scan history
    GET /api/history/statistics
    
    Returns:
        JSON with statistics
    """
    try:
        stats = HistoryController.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"History statistics error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching statistics'
        }), 500


@history_bp.route('/history/recent', methods=['GET'])
def get_recent_history():
    """
    Get most recent history records
    GET /api/history/recent?limit=5
    
    Query Parameters:
        limit: Number of records (default 10)
        
    Returns:
        JSON with recent records
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50
        
        records = HistoryController.get_recent(limit)
        
        # Convert to dict
        history_list = []
        for record in records:
            history_list.append({
                'id': record.id,
                'disease': record.disease,
                'confidence': record.confidence,
                'severity': record.severity,
                'timestamp': record.timestamp,
                'date': record.get_formatted_date()
            })
        
        return jsonify({
            'success': True,
            'limit': limit,
            'count': len(history_list),
            'recent_scans': history_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Recent history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching recent scans'
        }), 500


@history_bp.route('/history/export/csv', methods=['GET'])
def export_history_csv():
    """
    Export history as CSV
    GET /api/history/export/csv
    
    Returns:
        CSV file download
    """
    try:
        csv_data = HistoryController.export_csv()
        
        from io import BytesIO
        import csv
        
        output = BytesIO()
        output.write(csv_data.encode('utf-8'))
        output.seek(0)
        
        filename = f"farmintel_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import send_file
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Export CSV error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while exporting CSV'
        }), 500


@history_bp.route('/history/export/json', methods=['GET'])
def export_history_json():
    """
    Export history as JSON
    GET /api/history/export/json
    
    Returns:
        JSON export
    """
    try:
        json_data = HistoryController.export_json()
        
        return jsonify({
            'success': True,
            'data': json.loads(json_data) if isinstance(json_data, str) else json_data,
            'format': 'json',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Export JSON error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while exporting JSON'
        }), 500


@history_bp.route('/history/health', methods=['GET'])
def history_health():
    """
    Check history service health
    GET /api/history/health
    
    Returns:
        JSON with service status
    """
    try:
        total_records = HistoryController.get_count()
        
        return jsonify({
            'success': True,
            'service': 'history',
            'status': 'healthy',
            'total_records': total_records,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'service': 'history',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500