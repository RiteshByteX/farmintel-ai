"""
Reports Routes - PDF and CSV report generation endpoints
Handles generation of disease detection reports and weather analysis reports
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from datetime import datetime
import os
import io
import json

from app.controllers.report_controller import ReportController
from app.controllers.history_controller import HistoryController
from app.controllers.weather_controller import WeatherController
from app.models.schemas import ReportRequest, ReportType, DateRange, ValidationError

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/report/pdf', methods=['POST'])
def generate_pdf_report():
    """
    Generate PDF report for disease detection
    POST /api/report/pdf
    Content-Type: application/json
    Body: {
        "report_type": "detailed",
        "date_range": "month",
        "history_ids": [1, 2, 3],
        "detection_data": {...}
    }
    
    Returns:
        PDF file download
    """
    try:
        data = request.get_json() or {}
        
        # Get report parameters
        report_type = data.get('report_type', 'detailed')
        date_range = data.get('date_range', 'all')
        history_ids = data.get('history_ids')
        detection_data = data.get('detection_data')
        
        # Validate report type
        if report_type not in ['summary', 'detailed', 'weather']:
            return jsonify({
                'success': False,
                'error': 'Invalid report type',
                'message': 'Report type must be summary, detailed, or weather'
            }), 400
        
        # Get history data
        if history_ids:
            # Get specific records by IDs
            history_records = []
            for record_id in history_ids:
                record = HistoryController.get_by_id(record_id)
                if record:
                    history_records.append(record)
        else:
            # Get all records within date range
            all_records = HistoryController.get_all()
            history_records = filter_by_date_range(all_records, date_range)
        
        # Prepare report data
        report_data = {
            'history': [r.to_dict() for r in history_records],
            'detection': detection_data,
            'stats': HistoryController.get_statistics(),
            'generated_at': datetime.now().isoformat()
        }
        
        # Add weather data if weather report
        if report_type == 'weather' and detection_data:
            city = detection_data.get('city', 'Mumbai')
            weather_data = WeatherController.get_weather(city=city)
            report_data['weather'] = weather_data
        
        # Generate PDF
        pdf_buffer = ReportController.generate_pdf_report(report_data, report_type)
        
        # Create filename
        filename = f"farmintel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Send file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': e.message
        }), 400
    except Exception as e:
        current_app.logger.error(f"PDF report error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while generating PDF report'
        }), 500


@reports_bp.route('/report/csv', methods=['POST'])
def generate_csv_report():
    """
    Generate CSV report for disease detection
    POST /api/report/csv
    Content-Type: application/json
    Body: {
        "report_type": "detailed",
        "date_range": "month",
        "history_ids": [1, 2, 3]
    }
    
    Returns:
        CSV file download
    """
    try:
        data = request.get_json() or {}
        
        # Get report parameters
        report_type = data.get('report_type', 'detailed')
        date_range = data.get('date_range', 'all')
        history_ids = data.get('history_ids')
        
        # Validate report type
        if report_type not in ['summary', 'detailed', 'history']:
            report_type = 'detailed'
        
        # Get history data
        if history_ids:
            # Get specific records by IDs
            history_records = []
            for record_id in history_ids:
                record = HistoryController.get_by_id(record_id)
                if record:
                    history_records.append(record)
        else:
            # Get all records within date range
            all_records = HistoryController.get_all()
            history_records = filter_by_date_range(all_records, date_range)
        
        # Prepare report data
        report_data = {
            'history': [r.to_dict() for r in history_records],
            'stats': HistoryController.get_statistics()
        }
        
        # Generate CSV
        csv_buffer = ReportController.generate_csv_report(report_data, report_type)
        
        # Create filename
        filename = f"farmintel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Send file
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"CSV report error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while generating CSV report'
        }), 500


@reports_bp.route('/report/single', methods=['POST'])
def generate_single_detection_report():
    """
    Generate PDF report for a single detection
    POST /api/report/single
    Content-Type: application/json
    Body: {
        "detection_data": {...}
    }
    
    Returns:
        PDF file download
    """
    try:
        data = request.get_json()
        
        if not data or 'detection_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No detection data provided',
                'message': 'Please provide detection_data'
            }), 400
        
        detection_data = data['detection_data']
        
        # Generate PDF
        pdf_buffer = ReportController.generate_single_detection_pdf(detection_data)
        
        # Create filename
        filename = f"farmintel_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Send file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Single detection report error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while generating detection report'
        }), 500


@reports_bp.route('/report/weather', methods=['POST'])
def generate_weather_report():
    """
    Generate PDF report for weather analysis
    POST /api/report/weather
    Content-Type: application/json
    Body: {
        "city": "Mumbai",
        "weather_data": {...}
    }
    
    Returns:
        PDF file download
    """
    try:
        data = request.get_json() or {}
        
        city = data.get('city', 'Mumbai')
        weather_data = data.get('weather_data')
        
        # Get weather data if not provided
        if not weather_data:
            weather_data = WeatherController.get_weather(city=city)
        
        # Generate PDF
        pdf_buffer = ReportController.generate_weather_pdf(weather_data)
        
        # Create filename
        filename = f"farmintel_weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Send file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Weather report error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while generating weather report'
        }), 500


@reports_bp.route('/report/history', methods=['GET'])
def generate_history_report():
    """
    Generate report from history records
    GET /api/report/history?start_date=2024-01-01&end_date=2024-12-31&format=pdf
    
    Query Parameters:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        severity: Filter by severity
        disease: Filter by disease
        format: pdf or csv (default pdf)
        
    Returns:
        Report file download
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        severity = request.args.get('severity')
        disease = request.args.get('disease')
        report_format = request.args.get('format', 'pdf')
        
        # Get filtered records
        records = HistoryController.get_all()
        
        # Apply filters
        if start_date or end_date:
            records = HistoryController.filter_by_date(start_date, end_date)
        if severity:
            records = [r for r in records if r.severity.lower() == severity.lower()]
        if disease:
            records = [r for r in records if disease.lower() in r.disease.lower()]
        
        # Prepare report data
        report_data = {
            'history': [r.to_dict() for r in records],
            'stats': {
                'total': len(records),
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'filters': {
                    'severity': severity,
                    'disease': disease
                }
            }
        }
        
        # Generate report
        if report_format == 'csv':
            csv_buffer = ReportController.generate_csv_report(report_data, 'history')
            filename = f"farmintel_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return send_file(csv_buffer, mimetype='text/csv', as_attachment=True, download_name=filename)
        else:
            pdf_buffer = ReportController.generate_pdf_report(report_data, 'detailed')
            filename = f"farmintel_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)
        
    except Exception as e:
        current_app.logger.error(f"History report error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while generating history report'
        }), 500


@reports_bp.route('/report/summary', methods=['GET'])
def generate_summary_report():
    """
    Generate summary report
    GET /api/report/summary?format=pdf
    
    Query Parameters:
        format: pdf or csv (default pdf)
        
    Returns:
        Report file download
    """
    try:
        report_format = request.args.get('format', 'pdf')
        
        # Get statistics
        stats = HistoryController.get_statistics()
        
        # Get recent records
        recent_records = HistoryController.get_recent(20)
        
        # Prepare report data
        report_data = {
            'stats': stats,
            'recent_scans': [r.to_dict() for r in recent_records],
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate report
        if report_format == 'csv':
            csv_buffer = ReportController.generate_csv_report(report_data, 'summary')
            filename = f"farmintel_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return send_file(csv_buffer, mimetype='text/csv', as_attachment=True, download_name=filename)
        else:
            pdf_buffer = ReportController.generate_pdf_report(report_data, 'summary')
            filename = f"farmintel_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)
        
    except Exception as e:
        current_app.logger.error(f"Summary report error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while generating summary report'
        }), 500


@reports_bp.route('/report/export/all', methods=['GET'])
def export_all_data():
    """
    Export all data (history + statistics)
    GET /api/report/export/all?format=json
    
    Query Parameters:
        format: json or csv (default json)
        
    Returns:
        Data export file
    """
    try:
        export_format = request.args.get('format', 'json')
        
        # Get all data
        records = HistoryController.get_all()
        stats = HistoryController.get_statistics()
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'version': current_app.config.get('APP_VERSION', '1.0.0'),
            'statistics': stats,
            'history': [r.to_dict() for r in records]
        }
        
        if export_format == 'csv':
            # Convert to CSV
            import csv
            from io import StringIO
            
            output = StringIO()
            if records:
                writer = csv.writer(output)
                writer.writerow(['ID', 'Disease', 'Confidence', 'Severity', 'Date', 'Chemical Treatment', 'Organic Treatment'])
                for r in records:
                    writer.writerow([
                        r.id, r.disease, r.confidence, r.severity, 
                        r.timestamp, r.chemical_treatment, r.organic_treatment
                    ])
            
            filename = f"farmintel_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
        else:
            # Return JSON
            return jsonify({
                'success': True,
                'data': export_data,
                'message': 'Data exported successfully',
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        current_app.logger.error(f"Export all error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while exporting data'
        }), 500


@reports_bp.route('/report/health', methods=['GET'])
def reports_health():
    """
    Check reports service health
    GET /api/report/health
    
    Returns:
        JSON with service status
    """
    return jsonify({
        'success': True,
        'service': 'reports',
        'status': 'healthy',
        'supported_formats': ['pdf', 'csv'],
        'supported_report_types': ['summary', 'detailed', 'weather', 'history'],
        'timestamp': datetime.now().isoformat()
    })


# Helper function to filter records by date range
def filter_by_date_range(records, date_range):
    """
    Filter records by date range
    
    Args:
        records: List of ScanRecord objects
        date_range: String ('today', 'week', 'month', 'year', 'all')
        
    Returns:
        Filtered list of records
    """
    if date_range == 'all' or not records:
        return records
    
    now = datetime.now()
    
    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range == 'week':
        start_date = now - timedelta(days=7)
    elif date_range == 'month':
        start_date = now - timedelta(days=30)
    elif date_range == 'year':
        start_date = now - timedelta(days=365)
    else:
        return records
    
    filtered = []
    for record in records:
        try:
            record_date = datetime.fromisoformat(record.timestamp)
            if record_date >= start_date:
                filtered.append(record)
        except (ValueError, TypeError):
            # Keep records with invalid dates
            filtered.append(record)
    
    return filtered


# Import timedelta for date filtering
from datetime import timedelta