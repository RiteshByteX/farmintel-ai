"""
History Model - Data model for scan history records
Manages storage, retrieval, and manipulation of disease detection history
"""

import os
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any, Tuple
from flask import current_app


@dataclass
class ScanRecord:
    """
    Data class for a single scan record
    Represents one disease detection event
    """
    id: int
    disease: str
    confidence: float
    severity: str
    chemical_treatment: str
    organic_treatment: str
    cultural_practices: str
    prevention_tips: str
    image_path: Optional[str] = None
    timestamp: str = None
    updated_at: Optional[str] = None
    weather_data: Optional[Dict] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScanRecord':
        """Create ScanRecord from dictionary"""
        return cls(**data)
    
    def get_formatted_date(self) -> str:
        """Get formatted date string"""
        dt = datetime.fromisoformat(self.timestamp)
        return dt.strftime('%B %d, %Y at %I:%M %p')
    
    def get_date_only(self) -> str:
        """Get date only (YYYY-MM-DD)"""
        return self.timestamp.split('T')[0] if self.timestamp else ''
    
    def is_healthy(self) -> bool:
        """Check if this scan indicates a healthy plant"""
        return 'healthy' in self.disease.lower()
    
    def get_severity_color(self) -> str:
        """Get color code for severity level"""
        colors = {
            'Severe': '#EF4444',
            'Moderate': '#F59E0B',
            'Mild': '#10B981',
            'Low': '#6B7280'
        }
        return colors.get(self.severity, '#6B7280')


class HistoryModel:
    """
    Model for managing scan history storage
    Handles CRUD operations, filtering, and statistics
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize history model
        
        Args:
            db_path: Path to history JSON file
        """
        # Don't use current_app at module load time
        if db_path:
            self.db_path = db_path
        else:
            # Try environment variable first
            self.db_path = os.environ.get('HISTORY_FILE', 'database/history.json')
        
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database file and directory exist"""
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
            if not os.path.exists(self.db_path):
                self._write_data([])
                print(f"Created new history database at {self.db_path}")
        except Exception as e:
            print(f"Error creating history database: {str(e)}")
    
    def _read_data(self) -> List[Dict]:
        """Read all records from database"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_data(self, data: List[Dict]):
        """Write records to database"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing history data: {str(e)}")
            raise
    
    def get_all(self, limit: int = None, offset: int = 0, sort_desc: bool = True) -> List[ScanRecord]:
        """Get all scan records with pagination"""
        data = self._read_data()
        
        # Sort by timestamp
        data.sort(key=lambda x: x.get('timestamp', ''), reverse=sort_desc)
        
        if limit:
            data = data[offset:offset + limit]
        
        return [ScanRecord.from_dict(record) for record in data]
    
    def get_by_id(self, record_id: int) -> Optional[ScanRecord]:
        """Get a specific record by ID"""
        data = self._read_data()
        for record in data:
            if record.get('id') == record_id:
                return ScanRecord.from_dict(record)
        return None
    
    def save(self, record: ScanRecord) -> ScanRecord:
        """Save a new scan record"""
        data = self._read_data()
        
        # Generate new ID
        max_id = max([r.get('id', 0) for r in data], default=0)
        record.id = max_id + 1
        
        # Ensure timestamp
        if not record.timestamp:
            record.timestamp = datetime.now().isoformat()
        
        # Add to data
        data.append(record.to_dict())
        self._write_data(data)
        
        print(f"Saved history record {record.id} - {record.disease}")
        
        return record
    
    def delete(self, record_id: int) -> bool:
        """Delete a record by ID"""
        data = self._read_data()
        original_length = len(data)
        
        data = [r for r in data if r.get('id') != record_id]
        
        if len(data) < original_length:
            self._write_data(data)
            print(f"Deleted history record {record_id}")
            return True
        
        return False
    
    def delete_all(self) -> int:
        """Delete all records"""
        data = self._read_data()
        count = len(data)
        self._write_data([])
        print(f"Deleted all {count} history records")
        return count
    
    def get_count(self) -> int:
        """Get total number of records"""
        return len(self._read_data())
    
    def search(self, query: str, field: str = 'disease') -> List[ScanRecord]:
        """Search records by field"""
        data = self._read_data()
        query_lower = query.lower()
        
        results = []
        for record in data:
            field_value = str(record.get(field, ''))
            if query_lower in field_value.lower():
                results.append(ScanRecord.from_dict(record))
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about scan history"""
        records = self._read_data()
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
        
        # Disease breakdown
        disease = {}
        for r in records:
            d = r.get('disease', 'Unknown')
            disease[d] = disease.get(d, 0) + 1
        
        sorted_diseases = sorted(disease.items(), key=lambda x: x[1], reverse=True)
        top_diseases = dict(sorted_diseases[:10])
        most_common_disease = sorted_diseases[0][0] if sorted_diseases else None
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


# Singleton instance
history_model = HistoryModel()