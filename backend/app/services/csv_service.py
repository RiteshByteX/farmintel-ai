"""
CSV Service - CSV Report Generation Service
Handles creation of CSV files for data export and reporting
"""

import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class CSVService:
    """
    Service for generating CSV reports
    Creates CSV exports for disease detection data, history, and statistics
    """
    
    def __init__(self):
        """Initialize CSV service"""
        self.encoding = 'utf-8-sig'  # UTF-8 with BOM for Excel compatibility
    
    def _create_writer(self, output: BytesIO):
        """Create CSV writer with proper settings"""
        return csv.writer(output)
    
    def _add_bom(self, output: BytesIO):
        """Add BOM for Excel compatibility"""
        output.write(u'\ufeff'.encode('utf-8'))
    
    def _format_datetime(self) -> str:
        """Get formatted current datetime"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_date(self) -> str:
        """Get formatted current date"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _format_list_field(self, field: Any, max_length: int = 500) -> str:
        """
        Format a list field for CSV output
        
        Args:
            field: Field value (could be list, string, or other)
            max_length: Maximum length of the output string
            
        Returns:
            Formatted string
        """
        if field is None:
            return ''
        
        if isinstance(field, list):
            result = '; '.join(str(item) for item in field if item)
        elif isinstance(field, dict):
            result = '; '.join(f"{k}: {v}" for k, v in field.items())
        else:
            result = str(field)
        
        # Clean up for CSV (remove newlines and commas)
        result = result.replace('\n', ' ').replace('\r', ' ').replace(',', ';')
        
        # Truncate if needed
        if len(result) > max_length:
            result = result[:max_length] + '...'
        
        return result
    
    def _write_header(self, writer, title: str, sub_info: List[str] = None):
        """
        Write report header
        
        Args:
            writer: CSV writer
            title: Report title
            sub_info: List of additional info lines
        """
        writer.writerow([f'FarmIntel AI - {title}'])
        writer.writerow([f'Generated: {self._format_datetime()}'])
        if sub_info:
            for info in sub_info:
                writer.writerow([info])
        writer.writerow([])
    
    def _write_section_header(self, writer, title: str):
        """Write section header"""
        writer.writerow([title.upper()])
    
    def generate_detection_csv(self, detection_data: dict) -> BytesIO:
        """
        Generate CSV for a single detection
        
        Args:
            detection_data: Dictionary with detection results
            
        Returns:
            BytesIO buffer with CSV content
        """
        output = BytesIO()
        self._add_bom(output)
        writer = self._create_writer(output)
        
        # Header
        self._write_header(writer, 'Disease Detection Report')
        
        # Detection Results
        self._write_section_header(writer, 'Detection Results')
        writer.writerow(['Parameter', 'Value'])
        writer.writerow(['Disease', detection_data.get('disease', 'N/A')])
        writer.writerow(['Confidence (%)', detection_data.get('confidence', 0)])
        writer.writerow(['Severity', detection_data.get('severity', 'N/A')])
        writer.writerow(['Severity Color', detection_data.get('severity_color', 'N/A')])
        writer.writerow(['Crop', detection_data.get('crop', 'N/A')])
        writer.writerow(['Scan Date', detection_data.get('date', self._format_datetime())])
        writer.writerow(['Health Status', detection_data.get('health_status', 'N/A')])
        writer.writerow(['Is Healthy', 'Yes' if detection_data.get('is_healthy') else 'No'])
        writer.writerow([])
        
        # Treatment Recommendations
        self._write_section_header(writer, 'Treatment Recommendations')
        writer.writerow(['Type', 'Recommendation'])
        
        chemical = detection_data.get('chemical_treatment', {})
        if isinstance(chemical, dict):
            writer.writerow(['Chemical Name', chemical.get('name', 'N/A')])
            writer.writerow(['Chemical Dosage', chemical.get('dosage', 'N/A')])
            writer.writerow(['Chemical Frequency', chemical.get('frequency', 'N/A')])
            writer.writerow(['Chemical Method', chemical.get('method', 'N/A')])
            writer.writerow(['Chemical Precautions', chemical.get('precautions', 'N/A')])
        else:
            writer.writerow(['Chemical Treatment', self._format_list_field(chemical)])
        
        organic = detection_data.get('organic_treatment', {})
        if isinstance(organic, dict):
            writer.writerow(['Organic Name', organic.get('name', 'N/A')])
            writer.writerow(['Organic Dosage', organic.get('dosage', 'N/A')])
            writer.writerow(['Organic Frequency', organic.get('frequency', 'N/A')])
        else:
            writer.writerow(['Organic Treatment', self._format_list_field(organic)])
        
        writer.writerow([])
        
        # Cultural Practices
        cultural = detection_data.get('cultural_practices', [])
        if cultural:
            self._write_section_header(writer, 'Cultural Practices')
            for i, practice in enumerate(cultural, 1):
                writer.writerow([f'Practice {i}', self._format_list_field(practice)])
            writer.writerow([])
        
        # Prevention Tips
        prevention = detection_data.get('prevention_tips', [])
        if prevention:
            self._write_section_header(writer, 'Prevention Tips')
            for i, tip in enumerate(prevention, 1):
                writer.writerow([f'Tip {i}', self._format_list_field(tip)])
        
        output.seek(0)
        return output
    
    def generate_history_csv(self, history_data: List[dict]) -> BytesIO:
        """
        Generate CSV for scan history
        
        Args:
            history_data: List of detection records
            
        Returns:
            BytesIO buffer with CSV content
        """
        output = BytesIO()
        self._add_bom(output)
        writer = self._create_writer(output)
        
        # Header
        self._write_header(writer, 'Scan History Report', [f'Total Records: {len(history_data)}'])
        
        # Column headers
        headers = [
            'ID', 'Date', 'Disease', 'Confidence (%)', 'Severity',
            'Crop', 'Chemical Treatment', 'Organic Treatment',
            'Cultural Practices', 'Prevention Tips', 'Is Healthy'
        ]
        writer.writerow(headers)
        
        # Write data rows
        for record in history_data:
            row = [
                record.get('id', ''),
                record.get('date', '') or record.get('timestamp', ''),
                record.get('disease', ''),
                record.get('confidence', ''),
                record.get('severity', ''),
                record.get('crop', ''),
                self._format_list_field(record.get('chemical_treatment', ''), 300),
                self._format_list_field(record.get('organic_treatment', ''), 300),
                self._format_list_field(record.get('cultural_practices', []), 300),
                self._format_list_field(record.get('prevention_tips', []), 300),
                'Yes' if record.get('is_healthy', False) else 'No'
            ]
            writer.writerow(row)
        
        output.seek(0)
        return output
    
    def generate_summary_csv(self, stats_data: dict, history_data: List[dict]) -> BytesIO:
        """
        Generate CSV summary report
        
        Args:
            stats_data: Dictionary with statistics
            history_data: List of detection records
            
        Returns:
            BytesIO buffer with CSV content
        """
        output = BytesIO()
        self._add_bom(output)
        writer = self._create_writer(output)
        
        # Header
        self._write_header(writer, 'Summary Report')
        
        # Statistics Section
        self._write_section_header(writer, 'Statistics')
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Scans', stats_data.get('total_scans', 0)])
        writer.writerow(['Diseased Crops', stats_data.get('diseased_count', 0)])
        writer.writerow(['Healthy Crops', stats_data.get('healthy_count', 0)])
        writer.writerow(['Disease Rate (%)', stats_data.get('disease_rate', 0)])
        writer.writerow(['Average Confidence (%)', stats_data.get('avg_confidence', 0)])
        writer.writerow(['Recovery Rate (%)', stats_data.get('recovery_rate', 0)])
        writer.writerow(['Most Common Disease', stats_data.get('most_common_disease', 'N/A')])
        writer.writerow(['Most Common Severity', stats_data.get('most_common_severity', 'N/A')])
        writer.writerow([])
        
        # Severity Breakdown
        self._write_section_header(writer, 'Severity Breakdown')
        writer.writerow(['Severity', 'Count', 'Percentage (%)'])
        severity_breakdown = stats_data.get('severity_breakdown', {})
        total = stats_data.get('total_scans', 1)
        for severity, count in severity_breakdown.items():
            percentage = round((count / total) * 100, 1) if total > 0 else 0
            writer.writerow([severity, count, percentage])
        writer.writerow([])
        
        # Disease Breakdown (Top 10)
        self._write_section_header(writer, 'Disease Breakdown (Top 10)')
        writer.writerow(['Disease', 'Count', 'Percentage (%)'])
        disease_breakdown = stats_data.get('disease_breakdown', {})
        for disease, count in list(disease_breakdown.items())[:10]:
            percentage = round((count / total) * 100, 1) if total > 0 else 0
            writer.writerow([disease, count, percentage])
        writer.writerow([])
        
        # Monthly Trend
        scans_by_month = stats_data.get('scans_by_month', {})
        if scans_by_month:
            self._write_section_header(writer, 'Monthly Trend')
            writer.writerow(['Month', 'Scans'])
            for month in sorted(scans_by_month.keys()):
                writer.writerow([month, scans_by_month[month]])
            writer.writerow([])
        
        # Recent Scans
        self._write_section_header(writer, 'Recent Scans (Last 20)')
        writer.writerow(['Date', 'Disease', 'Confidence (%)', 'Severity'])
        for record in history_data[:20]:
            writer.writerow([
                record.get('date', '') or record.get('timestamp', '')[:10],
                record.get('disease', ''),
                record.get('confidence', ''),
                record.get('severity', '')
            ])
        
        output.seek(0)
        return output
    
    def generate_weather_csv(self, weather_data: dict) -> BytesIO:
        """
        Generate CSV for weather data
        
        Args:
            weather_data: Dictionary with weather data
            
        Returns:
            BytesIO buffer with CSV content
        """
        output = BytesIO()
        self._add_bom(output)
        writer = self._create_writer(output)
        
        # Header
        self._write_header(writer, 'Weather Report')
        
        # Current Weather
        self._write_section_header(writer, 'Current Weather')
        writer.writerow(['Parameter', 'Value'])
        writer.writerow(['Location', weather_data.get('city', 'N/A')])
        writer.writerow(['Country', weather_data.get('country', 'N/A')])
        writer.writerow(['Temperature (°C)', weather_data.get('temperature', 'N/A')])
        writer.writerow(['Feels Like (°C)', weather_data.get('feels_like', 'N/A')])
        writer.writerow(['Humidity (%)', weather_data.get('humidity', 'N/A')])
        writer.writerow(['Wind Speed (km/h)', weather_data.get('wind_speed', 'N/A')])
        writer.writerow(['Rainfall (mm)', weather_data.get('rainfall', 'N/A')])
        writer.writerow(['Condition', weather_data.get('condition', 'N/A')])
        writer.writerow(['Disease Risk', weather_data.get('disease_risk', 'N/A')])
        writer.writerow(['Risk Score', weather_data.get('risk_score', 'N/A')])
        writer.writerow(['Spray Advisory', weather_data.get('spray_advisory', {}).get('status', 'N/A')])
        writer.writerow([])
        
        # Alerts
        alerts = weather_data.get('alerts', [])
        if alerts:
            self._write_section_header(writer, 'Weather Alerts')
            writer.writerow(['Alert', 'Severity', 'Message'])
            for alert in alerts:
                writer.writerow([
                    alert.get('title', 'N/A'),
                    alert.get('severity', 'N/A'),
                    alert.get('message', 'N/A')[:200]
                ])
            writer.writerow([])
        
        # Disease-Specific Risks
        disease_risks = weather_data.get('disease_risks', [])
        if disease_risks:
            self._write_section_header(writer, 'Disease-Specific Risks')
            writer.writerow(['Disease', 'Risk Level', 'Risk Score', 'Message'])
            for risk in disease_risks:
                writer.writerow([
                    risk.get('disease', 'N/A'),
                    risk.get('risk', 'N/A'),
                    risk.get('score', 'N/A'),
                    risk.get('message', 'N/A')[:150]
                ])
            writer.writerow([])
        
        # Forecast
        forecast = weather_data.get('forecast', [])
        if forecast:
            self._write_section_header(writer, 'Weather Forecast')
            writer.writerow(['Date', 'Day', 'Temp (°C)', 'Humidity (%)', 'Rain (mm)', 'Condition', 'Disease Risk'])
            for day in forecast:
                writer.writerow([
                    day.get('date', 'N/A'),
                    day.get('day', 'N/A'),
                    day.get('temperature', 'N/A'),
                    day.get('humidity', 'N/A'),
                    day.get('rainfall', 'N/A'),
                    day.get('condition', 'N/A'),
                    day.get('disease_risk', 'N/A')
                ])
        
        output.seek(0)
        return output
    
    def generate_full_export_csv(self, all_data: dict) -> BytesIO:
        """
        Generate complete data export CSV
        
        Args:
            all_data: Dictionary containing all application data
            
        Returns:
            BytesIO buffer with CSV content
        """
        output = BytesIO()
        self._add_bom(output)
        writer = self._create_writer(output)
        
        # Header
        self._write_header(writer, 'Complete Data Export', [
            f'Version: {all_data.get("version", "1.0.0")}',
            f'App Name: {all_data.get("app_name", "FarmIntel AI")}'
        ])
        
        # Statistics
        stats = all_data.get('statistics', {})
        self._write_section_header(writer, 'Statistics Summary')
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Scans', stats.get('total_scans', 0)])
        writer.writerow(['Diseased Crops', stats.get('diseased_count', 0)])
        writer.writerow(['Healthy Crops', stats.get('healthy_count', 0)])
        writer.writerow(['Disease Rate (%)', stats.get('disease_rate', 0)])
        writer.writerow(['Average Confidence (%)', stats.get('avg_confidence', 0)])
        writer.writerow(['Recovery Rate (%)', stats.get('recovery_rate', 0)])
        writer.writerow([])
        
        # Severity Distribution
        severity = stats.get('severity_breakdown', {})
        if severity:
            self._write_section_header(writer, 'Severity Distribution')
            writer.writerow(['Severity', 'Count'])
            for sev, count in severity.items():
                writer.writerow([sev, count])
            writer.writerow([])
        
        # Top Diseases
        top_diseases = stats.get('disease_breakdown', {})
        if top_diseases:
            self._write_section_header(writer, 'Top Diseases')
            writer.writerow(['Disease', 'Count'])
            for disease, count in list(top_diseases.items())[:15]:
                writer.writerow([disease, count])
            writer.writerow([])
        
        # Scan History
        history = all_data.get('history', [])
        self._write_section_header(writer, 'Scan History')
        writer.writerow([
            'ID', 'Date', 'Disease', 'Confidence (%)', 'Severity',
            'Chemical Treatment', 'Organic Treatment'
        ])
        for record in history:
            writer.writerow([
                record.get('id', ''),
                record.get('date', '') or record.get('timestamp', ''),
                record.get('disease', ''),
                record.get('confidence', ''),
                record.get('severity', ''),
                self._format_list_field(record.get('chemical_treatment', ''), 200),
                self._format_list_field(record.get('organic_treatment', ''), 200)
            ])
        
        output.seek(0)
        return output
    
    def generate_disease_library_csv(self, diseases: List[dict]) -> BytesIO:
        """
        Generate CSV for disease library
        
        Args:
            diseases: List of disease information dictionaries
            
        Returns:
            BytesIO buffer with CSV content
        """
        output = BytesIO()
        self._add_bom(output)
        writer = self._create_writer(output)
        
        # Header
        self._write_header(writer, 'Disease Library', [f'Total Diseases: {len(diseases)}'])
        
        # Column headers
        headers = [
            'ID', 'Disease Name', 'Crop', 'Severity', 'Season', 
            'Symptoms', 'Causes', 'Chemical Treatment', 
            'Organic Treatment', 'Prevention Tips'
        ]
        writer.writerow(headers)
        
        # Data rows
        for disease in diseases:
            row = [
                disease.get('id', ''),
                disease.get('name', ''),
                disease.get('crop', ''),
                disease.get('severity', ''),
                disease.get('season', ''),
                self._format_list_field(disease.get('symptoms', ''), 400),
                self._format_list_field(disease.get('causes', ''), 300),
                self._format_list_field(disease.get('treatment', ''), 300),
                self._format_list_field(disease.get('organic_treatment', ''), 300),
                self._format_list_field(disease.get('prevention', ''), 300)
            ]
            writer.writerow(row)
        
        output.seek(0)
        return output
    
    def generate_export_by_date_range(self, history_data: List[dict], 
                                       start_date: str, end_date: str) -> BytesIO:
        """
        Generate CSV for history within date range
        
        Args:
            history_data: List of detection records
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            BytesIO buffer with CSV content
        """
        # Filter by date range
        filtered = []
        for record in history_data:
            record_date = record.get('date', '') or record.get('timestamp', '')[:10]
            if start_date <= record_date <= end_date:
                filtered.append(record)
        
        output = BytesIO()
        self._add_bom(output)
        writer = self._create_writer(output)
        
        # Header
        self._write_header(writer, f'Export ({start_date} to {end_date})', [
            f'Total Records: {len(filtered)}'
        ])
        
        # Column headers
        headers = ['ID', 'Date', 'Disease', 'Confidence (%)', 'Severity', 'Crop']
        writer.writerow(headers)
        
        for record in filtered:
            writer.writerow([
                record.get('id', ''),
                record.get('date', '') or record.get('timestamp', ''),
                record.get('disease', ''),
                record.get('confidence', ''),
                record.get('severity', ''),
                record.get('crop', '')
            ])
        
        output.seek(0)
        return output
    
    def export_to_dataframe(self, history_data: List[dict]):
        """
        Convert history data to pandas DataFrame
        
        Args:
            history_data: List of detection records
            
        Returns:
            pandas DataFrame or None if pandas not available
        """
        try:
            import pandas as pd
        except ImportError:
            logger.warning("pandas not available, returning empty DataFrame")
            return None
        
        if not history_data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(history_data)
        
        # Select and reorder columns
        columns = ['id', 'date', 'timestamp', 'disease', 'confidence', 'severity', 
                   'crop', 'chemical_treatment', 'organic_treatment', 'is_healthy']
        available_columns = [col for col in columns if col in df.columns]
        
        # Ensure date column exists
        if 'date' not in df.columns and 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
            available_columns.insert(1, 'date')
        
        return df[available_columns]
    
    def get_stats_dataframe(self, history_data: List[dict]):
        """
        Generate statistics DataFrame
        
        Args:
            history_data: List of detection records
            
        Returns:
            pandas DataFrame or None if pandas not available
        """
        try:
            import pandas as pd
        except ImportError:
            logger.warning("pandas not available, returning None")
            return None
        
        if not history_data:
            return pd.DataFrame()
        
        df = self.export_to_dataframe(history_data)
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Calculate statistics
        total = len(df)
        diseased = len(df[~df['disease'].str.contains('Healthy', na=False)]) if 'disease' in df else 0
        healthy = total - diseased
        
        stats_df = pd.DataFrame({
            'Metric': ['Total Scans', 'Diseased Crops', 'Healthy Crops', 
                       'Average Confidence', 'Disease Rate'],
            'Value': [
                total,
                diseased,
                healthy,
                round(df['confidence'].mean(), 1) if 'confidence' in df else 0,
                round((diseased / total) * 100, 1) if total > 0 else 0
            ]
        })
        
        return stats_df
    
    def generate_filename(self, prefix: str) -> str:
        """
        Generate filename for CSV export
        
        Args:
            prefix: File prefix (e.g., 'detection', 'history')
            
        Returns:
            Formatted filename
        """
        timestamp = self._format_date()
        return f"farmintel_{prefix}_{timestamp}.csv"
    
    def get_csv_string(self, buffer: BytesIO) -> str:
        """
        Convert BytesIO buffer to string
        
        Args:
            buffer: BytesIO buffer
            
        Returns:
            String content
        """
        buffer.seek(0)
        return buffer.read().decode('utf-8-sig')


# Singleton instance
csv_service = CSVService()