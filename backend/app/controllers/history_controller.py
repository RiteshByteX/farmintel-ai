"""
History Controller
Handles CRUD operations for scan history storage
"""

import json
import os
from datetime import datetime, timedelta
from flask import current_app

from app.models.history_model import ScanRecord


class HistoryController:
    """
    Controller for history operations
    Manages saving, retrieving, updating, and deleting scan records
    """
    
    @classmethod
    def _get_history_file(cls):
        """Get path to history JSON file"""
        return current_app.config.get('HISTORY_FILE', 'database/history.json')
    
    @classmethod
    def _ensure_db_exists(cls):
        """Ensure the history file and directory exist"""
        history_file = cls._get_history_file()
        db_dir = os.path.dirname(history_file)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        if not os.path.exists(history_file):
            cls._write_data([])
    
    @classmethod
    def _read_data(cls):
        """Read all records from database"""
        cls._ensure_db_exists()
        try:
            with open(cls._get_history_file(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    @classmethod
    def _write_data(cls, data):
        """Write records to database"""
        with open(cls._get_history_file(), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def get_all(cls, limit=None, offset=0, sort_desc=True):
        """
        Get all history records with pagination
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
            sort_desc: Sort by timestamp descending if True
            
        Returns:
            list: List of ScanRecord objects
        """
        data = cls._read_data()
        
        # Sort by timestamp
        data.sort(key=lambda x: x.get('timestamp', ''), reverse=sort_desc)
        
        if limit:
            data = data[offset:offset + limit]
        
        return [ScanRecord.from_dict(record) for record in data]
    
    @classmethod
    def get_by_id(cls, record_id):
        """
        Get a specific record by ID
        
        Args:
            record_id: Record ID
            
        Returns:
            ScanRecord or None
        """
        data = cls._read_data()
        for record in data:
            if record.get('id') == record_id:
                return ScanRecord.from_dict(record)
        return None
    
    @classmethod
    def save(cls, record):
        """
        Save a new scan record
        
        Args:
            record: ScanRecord object to save
            
        Returns:
            Saved ScanRecord with updated ID
        """
        data = cls._read_data()
        
        # Generate new ID
        max_id = max([r.get('id', 0) for r in data], default=0)
        record.id = max_id + 1
        
        # Ensure timestamp
        if not record.timestamp:
            record.timestamp = datetime.now().isoformat()
        
        # Save to data
        data.append(record.to_dict())
        cls._write_data(data)
        
        current_app.logger.info(f"Saved history record {record.id} - {record.disease}")
        
        return record
    
    @classmethod
    def save_batch(cls, records):
        """
        Save multiple scan records at once
        
        Args:
            records: List of ScanRecord objects
            
        Returns:
            list: Saved ScanRecord objects
        """
        saved_records = []
        for record in records:
            saved = cls.save(record)
            saved_records.append(saved)
        return saved_records
    
    @classmethod
    def update(cls, record_id, updates):
        """
        Update an existing record
        
        Args:
            record_id: ID of record to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated ScanRecord or None
        """
        data = cls._read_data()
        
        for i, record in enumerate(data):
            if record.get('id') == record_id:
                # Update fields
                for key, value in updates.items():
                    if key != 'id':
                        data[i][key] = value
                data[i]['updated_at'] = datetime.now().isoformat()
                
                cls._write_data(data)
                current_app.logger.info(f"Updated history record {record_id}")
                return ScanRecord.from_dict(data[i])
        
        return None
    
    @classmethod
    def delete(cls, record_id):
        """
        Delete a record by ID
        
        Args:
            record_id: ID of record to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        data = cls._read_data()
        original_length = len(data)
        
        data = [r for r in data if r.get('id') != record_id]
        
        if len(data) < original_length:
            cls._write_data(data)
            current_app.logger.info(f"Deleted history record {record_id}")
            return True
        
        return False
    
    @classmethod
    def delete_batch(cls, record_ids):
        """
        Delete multiple records by IDs
        
        Args:
            record_ids: List of record IDs to delete
            
        Returns:
            int: Number of records deleted
        """
        data = cls._read_data()
        original_length = len(data)
        
        data = [r for r in data if r.get('id') not in record_ids]
        
        deleted_count = original_length - len(data)
        if deleted_count > 0:
            cls._write_data(data)
            current_app.logger.info(f"Deleted {deleted_count} history records")
        
        return deleted_count
    
    @classmethod
    def delete_all(cls):
        """
        Delete all records
        
        Returns:
            int: Number of records deleted
        """
        data = cls._read_data()
        count = len(data)
        cls._write_data([])
        current_app.logger.info(f"Deleted all {count} history records")
        return count
    
    @classmethod
    def clear_old_records(cls, days=30):
        """
        Delete records older than specified days
        
        Args:
            days: Number of days to keep (default 30)
            
        Returns:
            int: Number of records deleted
        """
        data = cls._read_data()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        original_count = len(data)
        new_data = []
        
        for record in data:
            try:
                record_date = datetime.fromisoformat(record.get('timestamp', '2000-01-01'))
                if record_date >= cutoff_date:
                    new_data.append(record)
            except (ValueError, TypeError):
                new_data.append(record)
        
        deleted_count = original_count - len(new_data)
        if deleted_count > 0:
            cls._write_data(new_data)
            current_app.logger.info(f"Cleared {deleted_count} records older than {days} days")
        
        return deleted_count
    
    @classmethod
    def get_statistics(cls):
        """
        Get comprehensive statistics about scan history
        
        Returns:
            dict: Statistics
        """
        records = cls._read_data()
        total = len(records)
        
        if total == 0:
            return {
                'total_scans': 0,
                'diseased_count': 0,
                'healthy_count': 0,
                'disease_rate': 0,
                'avg_confidence': 0,
                'severity_breakdown': {},
                'disease_breakdown': {},
                'most_common_disease': None,
                'most_common_severity': None,
                'last_scan': None,
                'first_scan': None,
                'scans_by_month': {},
                'recovery_rate': 0
            }
        
        # Count diseased vs healthy
        diseased = 0
        healthy = 0
        for r in records:
            if 'healthy' in r.get('disease', '').lower():
                healthy += 1
            else:
                diseased += 1
        
        # Average confidence
        total_confidence = sum(r.get('confidence', 0) for r in records)
        avg_confidence = round(total_confidence / total, 1) if total > 0 else 0
        
        # Severity breakdown
        severity = {}
        for r in records:
            sev = r.get('severity', 'Unknown')
            severity[sev] = severity.get(sev, 0) + 1
        
        # Disease breakdown (top 10)
        disease = {}
        for r in records:
            d = r.get('disease', 'Unknown')
            disease[d] = disease.get(d, 0) + 1
        
        sorted_diseases = sorted(disease.items(), key=lambda x: x[1], reverse=True)
        top_diseases = dict(sorted_diseases[:10])
        most_common_disease = sorted_diseases[0][0] if sorted_diseases else None
        
        # Most common severity
        most_common_severity = max(severity, key=severity.get) if severity else None
        
        # Last and first scan
        timestamps = [r.get('timestamp', '') for r in records if r.get('timestamp')]
        timestamps.sort()
        
        last_scan = timestamps[-1] if timestamps else None
        first_scan = timestamps[0] if timestamps else None
        
        # Scans by month
        scans_by_month = {}
        for r in records:
            try:
                month = datetime.fromisoformat(r.get('timestamp', '')).strftime('%Y-%m')
                scans_by_month[month] = scans_by_month.get(month, 0) + 1
            except (ValueError, TypeError):
                pass
        
        # Recovery rate
        recovery_rate = round((healthy / total) * 100, 1) if total > 0 else 0
        
        return {
            'total_scans': total,
            'diseased_count': diseased,
            'healthy_count': healthy,
            'disease_rate': round((diseased / total) * 100, 1),
            'avg_confidence': avg_confidence,
            'severity_breakdown': severity,
            'disease_breakdown': top_diseases,
            'most_common_disease': most_common_disease,
            'most_common_severity': most_common_severity,
            'last_scan': last_scan,
            'first_scan': first_scan,
            'scans_by_month': scans_by_month,
            'recovery_rate': recovery_rate
        }
    
    @classmethod
    def search(cls, query, field='disease'):
        """
        Search records by field
        
        Args:
            query: Search query string
            field: Field to search in (disease, severity, etc.)
            
        Returns:
            list: Matching ScanRecord objects
        """
        data = cls._read_data()
        query_lower = query.lower()
        
        results = []
        for record in data:
            field_value = str(record.get(field, ''))
            if query_lower in field_value.lower():
                results.append(ScanRecord.from_dict(record))
        
        return results
    
    @classmethod
    def filter_by_date(cls, start_date=None, end_date=None):
        """
        Filter records by date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            list: Filtered ScanRecord objects
        """
        data = cls._read_data()
        results = []
        
        for record in data:
            record_date = record.get('timestamp', '').split('T')[0]
            
            if start_date and record_date < start_date:
                continue
            if end_date and record_date > end_date:
                continue
            
            results.append(ScanRecord.from_dict(record))
        
        return results
    
    @classmethod
    def filter_by_severity(cls, severity):
        """
        Filter records by severity level
        
        Args:
            severity: Severity level (Severe, Moderate, Mild, Low)
            
        Returns:
            list: Filtered ScanRecord objects
        """
        data = cls._read_data()
        severity_lower = severity.lower()
        
        results = [
            ScanRecord.from_dict(r) for r in data
            if r.get('severity', '').lower() == severity_lower
        ]
        
        return results
    
    @classmethod
    def filter_by_disease(cls, disease_name):
        """
        Filter records by disease name
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            list: Filtered ScanRecord objects
        """
        data = cls._read_data()
        disease_lower = disease_name.lower()
        
        results = [
            ScanRecord.from_dict(r) for r in data
            if disease_lower in r.get('disease', '').lower()
        ]
        
        return results
    
    @classmethod
    def get_recent(cls, limit=10):
        """
        Get most recent records
        
        Args:
            limit: Maximum number of records
            
        Returns:
            list: Recent ScanRecord objects
        """
        return cls.get_all(limit=limit)
    
    @classmethod
    def get_timeline_data(cls):
        """
        Get timeline data for charts and graphs
        
        Returns:
            dict: Timeline data
        """
        records = cls._read_data()
        
        # Group by date
        daily_data = {}
        for record in records:
            date = record.get('timestamp', '').split('T')[0]
            if not date:
                continue
            
            if date not in daily_data:
                daily_data[date] = {
                    'total': 0,
                    'diseased': 0,
                    'healthy': 0,
                    'confidences': []
                }
            
            daily_data[date]['total'] += 1
            confidence = record.get('confidence', 0)
            daily_data[date]['confidences'].append(confidence)
            
            if 'healthy' in record.get('disease', '').lower():
                daily_data[date]['healthy'] += 1
            else:
                daily_data[date]['diseased'] += 1
        
        # Calculate averages
        for date, data in daily_data.items():
            if data['confidences']:
                data['avg_confidence'] = round(sum(data['confidences']) / len(data['confidences']), 1)
            del data['confidences']
        
        # Sort by date
        sorted_dates = sorted(daily_data.keys())
        
        return {
            'dates': sorted_dates,
            'data': [daily_data[d] for d in sorted_dates]
        }
    
    @classmethod
    def export_json(cls):
        """
        Export all history as JSON string
        
        Returns:
            str: JSON string
        """
        data = cls._read_data()
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @classmethod
    def export_csv(cls):
        """
        Export all history as CSV string
        
        Returns:
            str: CSV formatted string
        """
        import csv
        from io import StringIO
        
        data = cls._read_data()
        
        if not data:
            return "No data available"
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        headers = ['ID', 'Date', 'Disease', 'Confidence (%)', 'Severity', 
                   'Chemical Treatment', 'Organic Treatment', 'Cultural Practices', 'Prevention Tips']
        writer.writerow(headers)
        
        # Data rows
        for record in data:
            writer.writerow([
                record.get('id', ''),
                record.get('timestamp', ''),
                record.get('disease', ''),
                record.get('confidence', ''),
                record.get('severity', ''),
                record.get('chemical_treatment', '').replace('\n', ' '),
                record.get('organic_treatment', '').replace('\n', ' '),
                record.get('cultural_practices', '').replace('\n', ' '),
                record.get('prevention_tips', '').replace('\n', ' ')
            ])
        
        return output.getvalue()
    
    @classmethod
    def backup(cls, backup_dir=None):
        """
        Create a backup of history data
        
        Args:
            backup_dir: Directory to save backup
            
        Returns:
            str: Path to backup file
        """
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(cls._get_history_file()), 'backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'history_backup_{timestamp}.json')
        
        data = cls._read_data()
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        current_app.logger.info(f"Created backup at {backup_file}")
        return backup_file
    
    @classmethod
    def restore_from_backup(cls, backup_file):
        """
        Restore history from backup file
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            int: Number of records restored
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            cls._write_data(backup_data)
            current_app.logger.info(f"Restored {len(backup_data)} records from {backup_file}")
            return len(backup_data)
            
        except Exception as e:
            current_app.logger.error(f"Error restoring backup: {str(e)}")
            raise
    
    @classmethod
    def get_count(cls):
        """Get total number of records"""
        return len(cls._read_data())
    
    @classmethod
    def get_diseases_list(cls):
        """Get list of unique diseases in history"""
        records = cls._read_data()
        diseases = set(r.get('disease', 'Unknown') for r in records)
        return sorted(list(diseases))