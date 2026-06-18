"""
PDF Service - PDF Report Generation Service
Handles creation of professional PDF reports for disease detection
"""

import os
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import numpy as np


class PDFService:
    """
    Service for generating PDF reports
    Creates professional disease detection reports with charts and tables
    """
    
    # Color palette
    COLORS = {
        'primary': '#4F46E5',      # Indigo
        'secondary': '#10B981',    # Green
        'warning': '#F59E0B',      # Amber
        'danger': '#EF4444',       # Red
        'dark': '#1F2937',         # Gray-800
        'medium': '#374151',       # Gray-700
        'light': '#4B5563',        # Gray-600
        'border': '#E5E7EB',       # Gray-200
        'background': '#F9FAFB'    # Gray-50
    }
    
    def __init__(self):
        """Initialize PDF service"""
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create custom styles for PDF"""
        # Get base styles (as StyleSheet object)
        styles = getSampleStyleSheet()
        
        # Create a dictionary from stylesheet
        styles_dict = {
            'Normal': styles['Normal'],
            'Heading1': styles['Heading1'],
            'Heading2': styles['Heading2'],
            'Title': styles['Title']
        }
        
        # Create custom styles
        custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=self.COLORS['primary'],
                alignment=1,  # Center
                spaceAfter=30
            ),
            'CustomHeading': ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.COLORS['secondary'],
                spaceAfter=12,
                spaceBefore=12
            ),
            'CustomNormal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.COLORS['dark'],
                spaceAfter=6
            ),
            'Footer': ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.COLORS['light'],
                alignment=1  # Center
            ),
            'Success': ParagraphStyle(
                'Success',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.COLORS['secondary'],
                spaceAfter=6
            ),
            'Warning': ParagraphStyle(
                'Warning',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.COLORS['warning'],
                spaceAfter=6
            ),
            'Critical': ParagraphStyle(
                'Critical',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.COLORS['danger'],
                spaceAfter=6
            )
        }
        
        # Merge dictionaries (not stylesheet objects)
        all_styles = {**styles_dict, **custom_styles}
        return all_styles

    def generate_detection_report(self, detection_data: dict, 
                                   history_data: list = None,
                                   include_charts: bool = True) -> BytesIO:
        """
        Generate a PDF report for disease detection
        
        Args:
            detection_data: Dictionary with detection results
            history_data: Optional list of historical scans
            include_charts: Whether to include charts
            
        Returns:
            BytesIO buffer with PDF content
        """
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=f"FarmIntel AI - Disease Report",
            author="FarmIntel AI",
            subject="Disease Detection Report"
        )
        
        story = []
        
        # Add header
        story.extend(self._add_header("Disease Detection Report"))
        
        # Add detection results
        story.extend(self._add_detection_section(detection_data))
        
        # Add treatment section
        story.extend(self._add_treatment_section(detection_data))
        
        # Add prevention tips
        story.extend(self._add_prevention_section(detection_data))
        
        # Add history section if available
        if history_data and len(history_data) > 0:
            story.extend(self._add_history_section(history_data))
        
        # Add charts if requested
        if include_charts and history_data and len(history_data) > 5:
            story.append(PageBreak())
            story.extend(self._add_distribution_chart(history_data))
        
        # Add footer
        story.extend(self._add_footer())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_summary_report(self, stats_data: dict, 
                                 history_data: list,
                                 date_range: str = "All Time") -> BytesIO:
        """
        Generate a summary report with statistics
        
        Args:
            stats_data: Dictionary with statistics
            history_data: List of historical scans
            date_range: Date range description
            
        Returns:
            BytesIO buffer with PDF content
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title="FarmIntel AI - Summary Report"
        )
        
        story = []
        
        # Add header
        story.extend(self._add_header(f"Summary Report ({date_range})"))
        
        # Add statistics section
        story.extend(self._add_statistics_section(stats_data))
        
        # Add disease distribution chart
        story.extend(self._add_distribution_chart(history_data))
        
        # Add severity breakdown
        story.extend(self._add_severity_breakdown(stats_data))
        
        # Add recent scans
        if history_data:
            story.extend(self._add_recent_scans_section(history_data[:15]))
        
        # Add footer
        story.extend(self._add_footer())
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_weather_report(self, weather_data: dict) -> BytesIO:
        """
        Generate a weather analysis report
        
        Args:
            weather_data: Dictionary with weather data
            
        Returns:
            BytesIO buffer with PDF content
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title="FarmIntel AI - Weather Report"
        )
        
        story = []
        
        # Add header
        story.extend(self._add_header("Weather Analysis Report"))
        
        # Add current weather section
        story.extend(self._add_weather_section(weather_data))
        
        # Add disease risk section
        story.extend(self._add_weather_risk_section(weather_data))
        
        # Add forecast section
        if weather_data.get('forecast'):
            story.extend(self._add_forecast_section(weather_data['forecast']))
        
        # Add alerts section
        if weather_data.get('alerts'):
            story.extend(self._add_alerts_section(weather_data['alerts']))
        
        # Add recommendations
        story.extend(self._add_weather_recommendations(weather_data))
        
        # Add footer
        story.extend(self._add_footer())
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_history_report(self, history_data: List[dict], 
                                 start_date: str = None,
                                 end_date: str = None) -> BytesIO:
        """
        Generate a history report
        
        Args:
            history_data: List of historical scans
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            BytesIO buffer with PDF content
        """
        buffer = BytesIO()
        
        date_range = "All Time"
        if start_date and end_date:
            date_range = f"{start_date} to {end_date}"
        elif start_date:
            date_range = f"From {start_date}"
        elif end_date:
            date_range = f"Until {end_date}"
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=36,
            leftMargin=36,
            topMargin=72,
            bottomMargin=72,
            title="FarmIntel AI - History Report"
        )
        
        story = []
        
        # Add header
        story.extend(self._add_header(f"Scan History Report ({date_range})"))
        
        # Add summary stats
        total = len(history_data)
        diseased = len([h for h in history_data if 'healthy' not in h.get('disease', '').lower()])
        healthy = total - diseased
        
        story.append(Paragraph(f"Total Scans: {total}", self.styles['normal']))
        story.append(Paragraph(f"Diseased: {diseased} | Healthy: {healthy}", self.styles['normal']))
        story.append(Spacer(1, 10))
        
        # Add history table
        story.extend(self._add_history_table(history_data))
        
        # Add footer
        story.extend(self._add_footer())
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _add_header(self, title: str) -> list:
        """Add report header"""
        elements = []
        
        # Logo/title
        elements.append(Paragraph("🌾 FarmIntel AI", self.styles['title']))
        elements.append(Paragraph(f"<b>{title}</b>", self.styles['heading1']))
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['small']
        ))
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(self.COLORS['border'])))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_footer(self) -> list:
        """Add report footer"""
        elements = []
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(self.COLORS['border'])))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "FarmIntel AI - Empowering Farmers with AI Technology",
            self.styles['header']
        ))
        elements.append(Paragraph(
            "This report is automatically generated. For specific advice, consult a local agronomist.",
            self.styles['header']
        ))
        
        return elements
    
    def _add_detection_section(self, data: dict) -> list:
        """Add disease detection results section"""
        elements = []
        
        elements.append(Paragraph("Detection Results", self.styles['heading1']))
        
        # Create detection table
        table_data = [
            ['Parameter', 'Value'],
            ['Disease', data.get('disease', 'N/A')],
            ['Confidence', f"{data.get('confidence', 0)}%"],
            ['Severity', data.get('severity', 'N/A')],
            ['Severity Action', data.get('severity_action', 'Monitor closely')],
            ['Scan Date', data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))],
            ['Crop', data.get('crop', 'N/A')],
            ['Health Status', data.get('health_status', 'N/A')]
        ]
        
        table = Table(table_data, colWidths=[150, 300])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.COLORS['background'])]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_treatment_section(self, data: dict) -> list:
        """Add treatment recommendations section"""
        elements = []
        
        elements.append(Paragraph("Treatment Recommendations", self.styles['heading1']))
        
        # Chemical treatment
        chemical = data.get('chemical_treatment', '')
        if chemical:
            elements.append(Paragraph("<b>Chemical Treatment</b>", self.styles['heading2']))
            
            if isinstance(chemical, dict):
                elements.append(Paragraph(f"<b>Name:</b> {chemical.get('name', 'N/A')}", self.styles['normal']))
                elements.append(Paragraph(f"<b>Dosage:</b> {chemical.get('dosage', 'N/A')}", self.styles['normal']))
                elements.append(Paragraph(f"<b>Frequency:</b> {chemical.get('frequency', 'N/A')}", self.styles['normal']))
                elements.append(Paragraph(f"<b>Method:</b> {chemical.get('method', 'N/A')}", self.styles['normal']))
                elements.append(Paragraph(f"<b>Precautions:</b> {chemical.get('precautions', 'N/A')}", self.styles['small']))
            else:
                elements.append(Paragraph(chemical, self.styles['normal']))
            elements.append(Spacer(1, 10))
        
        # Organic treatment
        organic = data.get('organic_treatment', '')
        if organic:
            elements.append(Paragraph("<b>Organic Treatment</b>", self.styles['heading2']))
            if isinstance(organic, dict):
                elements.append(Paragraph(f"<b>Name:</b> {organic.get('name', 'N/A')}", self.styles['normal']))
                elements.append(Paragraph(f"<b>Dosage:</b> {organic.get('dosage', 'N/A')}", self.styles['normal']))
                elements.append(Paragraph(f"<b>Frequency:</b> {organic.get('frequency', 'N/A')}", self.styles['normal']))
            else:
                elements.append(Paragraph(organic, self.styles['normal']))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _add_prevention_section(self, data: dict) -> list:
        """Add prevention tips section"""
        elements = []
        
        cultural = data.get('cultural_practices', [])
        prevention = data.get('prevention_tips', [])
        
        if cultural or prevention:
            elements.append(Paragraph("Cultural Practices & Prevention", self.styles['heading1']))
            
            if cultural:
                elements.append(Paragraph("<b>Recommended Practices</b>", self.styles['heading2']))
                if isinstance(cultural, list):
                    for practice in cultural:
                        elements.append(Paragraph(f"• {practice}", self.styles['normal']))
                else:
                    elements.append(Paragraph(cultural, self.styles['normal']))
                elements.append(Spacer(1, 10))
            
            if prevention:
                elements.append(Paragraph("<b>Prevention Tips</b>", self.styles['heading2']))
                if isinstance(prevention, list):
                    for tip in prevention:
                        elements.append(Paragraph(f"• {tip}", self.styles['normal']))
                else:
                    elements.append(Paragraph(prevention, self.styles['normal']))
            
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_history_section(self, history: list, limit: int = 10) -> list:
        """Add scan history section"""
        elements = []
        
        elements.append(Paragraph("Recent Scan History", self.styles['heading1']))
        
        # Create history table
        table_data = [['Date', 'Disease', 'Confidence', 'Severity']]
        
        for record in history[:limit]:
            table_data.append([
                record.get('date', 'N/A')[:16],
                record.get('disease', 'N/A'),
                f"{record.get('confidence', 0)}%",
                record.get('severity', 'N/A')
            ])
        
        table = Table(table_data, colWidths=[120, 200, 80, 80])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['dark'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.COLORS['background'])]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_history_table(self, history: list) -> list:
        """Add full history table for history report"""
        elements = []
        
        # Create history table
        table_data = [['Date', 'Disease', 'Confidence', 'Severity', 'Crop']]
        
        for record in history:
            table_data.append([
                record.get('date', 'N/A')[:16],
                record.get('disease', 'N/A')[:40],
                f"{record.get('confidence', 0)}%",
                record.get('severity', 'N/A'),
                record.get('crop', 'N/A')
            ])
        
        table = Table(table_data, colWidths=[110, 160, 70, 70, 80])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.COLORS['background'])]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_statistics_section(self, stats: dict) -> list:
        """Add statistics section"""
        elements = []
        
        elements.append(Paragraph("Statistics Overview", self.styles['heading1']))
        
        # Create statistics table
        table_data = [
            ['Metric', 'Value'],
            ['Total Scans', str(stats.get('total_scans', 0))],
            ['Diseased Crops', str(stats.get('diseased_count', 0))],
            ['Healthy Crops', str(stats.get('healthy_count', 0))],
            ['Disease Rate', f"{stats.get('disease_rate', 0)}%"],
            ['Average Confidence', f"{stats.get('avg_confidence', 0)}%"],
            ['Recovery Rate', f"{stats.get('recovery_rate', 0)}%"],
            ['Most Common Disease', stats.get('most_common_disease', 'N/A')],
            ['Most Common Severity', stats.get('most_common_severity', 'N/A')]
        ]
        
        table = Table(table_data, colWidths=[200, 150])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['secondary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.COLORS['background'])]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_severity_breakdown(self, stats: dict) -> list:
        """Add severity breakdown section"""
        elements = []
        
        severity_breakdown = stats.get('severity_breakdown', {})
        if severity_breakdown:
            elements.append(Paragraph("Severity Breakdown", self.styles['heading1']))
            
            table_data = [['Severity', 'Count', 'Percentage']]
            total = stats.get('total_scans', 1)
            for severity, count in severity_breakdown.items():
                percentage = (count / total) * 100
                table_data.append([severity, str(count), f"{percentage:.1f}%"])
            
            table = Table(table_data, colWidths=[120, 100, 100])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['warning'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_distribution_chart(self, history: list, limit: int = 8) -> list:
        """Add disease distribution chart"""
        elements = []
        
        elements.append(Paragraph("Disease Distribution", self.styles['heading1']))
        
        # Count diseases (exclude healthy)
        disease_counts = {}
        for record in history:
            disease = record.get('disease', 'Unknown')
            if 'healthy' not in disease.lower():
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        if disease_counts:
            # Sort and limit
            sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            diseases = [d[0] for d in sorted_diseases]
            counts = [d[1] for d in sorted_diseases]
            
            # Create chart
            fig, ax = plt.subplots(figsize=(6, 4))
            
            colors_list = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', 
                          '#EC4899', '#06B6D4', '#84CC16']
            
            bars = ax.barh(diseases, counts, color=colors_list[:len(diseases)])
            ax.set_xlabel('Number of Detections', fontsize=10)
            ax.set_title('Top Diseases Detected', fontsize=12, fontweight='bold')
            ax.invert_yaxis()
            
            # Add value labels
            for bar, count in zip(bars, counts):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                       str(count), va='center', fontsize=9)
            
            plt.tight_layout()
            
            # Save chart to buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # Add chart to PDF
            img = Image(img_buffer, width=450, height=300)
            elements.append(img)
        else:
            elements.append(Paragraph("No disease data available for chart", self.styles['normal']))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_recent_scans_section(self, history: list) -> list:
        """Add recent scans section"""
        elements = []
        
        elements.append(Paragraph("Recent Scans", self.styles['heading1']))
        
        # Create table
        table_data = [['Date', 'Disease', 'Confidence', 'Severity']]
        for record in history:
            table_data.append([
                record.get('date', 'N/A')[:16],
                record.get('disease', 'N/A'),
                f"{record.get('confidence', 0)}%",
                record.get('severity', 'N/A')
            ])
        
        table = Table(table_data, colWidths=[120, 200, 80, 80])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.COLORS['background'])]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_weather_section(self, data: dict) -> list:
        """Add weather section"""
        elements = []
        
        elements.append(Paragraph("Current Weather Conditions", self.styles['heading1']))
        
        # Create weather table
        table_data = [
            ['Parameter', 'Value'],
            ['Location', data.get('city', 'N/A')],
            ['Temperature', f"{data.get('temperature', 'N/A')}°C"],
            ['Feels Like', f"{data.get('feels_like', 'N/A')}°C"],
            ['Humidity', f"{data.get('humidity', 'N/A')}%"],
            ['Wind Speed', f"{data.get('wind_speed', 'N/A')} km/h"],
            ['Rainfall', f"{data.get('rainfall', 'N/A')} mm"],
            ['Condition', data.get('condition', 'N/A')],
            ['Sunrise', data.get('sunrise', 'N/A')],
            ['Sunset', data.get('sunset', 'N/A')]
        ]
        
        table = Table(table_data, colWidths=[130, 200])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['warning'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_weather_risk_section(self, data: dict) -> list:
        """Add weather risk section"""
        elements = []
        
        elements.append(Paragraph("Disease Risk Analysis", self.styles['heading1']))
        
        risk_level = data.get('disease_risk', 'Low')
        risk_style = self.styles.get(f'risk_{risk_level.lower()}', self.styles['normal'])
        
        elements.append(Paragraph(
            f"<b>Current Risk Level:</b> {risk_level}",
            risk_style
        ))
        elements.append(Paragraph(data.get('risk_message', 'No risk assessment available'), self.styles['normal']))
        elements.append(Spacer(1, 15))
        
        # Add spray advisory
        spray_advisory = data.get('spray_advisory', {})
        if spray_advisory:
            elements.append(Paragraph("<b>Spray Advisory</b>", self.styles['heading2']))
            elements.append(Paragraph(spray_advisory.get('message', 'No advisory available'), self.styles['normal']))
            if spray_advisory.get('recommendation'):
                elements.append(Paragraph(
                    f"<b>Recommendation:</b> {spray_advisory.get('recommendation')}",
                    self.styles['small']
                ))
            elements.append(Spacer(1, 15))
        
        # Add disease-specific risks
        disease_risks = data.get('disease_risks', [])
        if disease_risks:
            elements.append(Paragraph("<b>Disease-Specific Risks</b>", self.styles['heading2']))
            for risk in disease_risks[:5]:
                risk_text = f"• {risk.get('disease')}: {risk.get('risk')} risk"
                elements.append(Paragraph(risk_text, self.styles['small']))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_forecast_section(self, forecast: list) -> list:
        """Add forecast section"""
        elements = []
        
        elements.append(Paragraph("7-Day Forecast", self.styles['heading1']))
        
        # Create forecast table
        table_data = [['Day', 'Date', 'Temp (°C)', 'Humidity (%)', 'Rain (mm)', 'Risk']]
        
        for day in forecast[:7]:
            table_data.append([
                day.get('day', 'N/A'),
                day.get('date', 'N/A'),
                str(day.get('temperature', 'N/A')),
                str(day.get('humidity', 'N/A')),
                str(day.get('rainfall', 'N/A')),
                day.get('disease_risk', 'N/A')
            ])
        
        table = Table(table_data, colWidths=[50, 70, 50, 50, 50, 60])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_alerts_section(self, alerts: list) -> list:
        """Add alerts section"""
        elements = []
        
        if alerts:
            elements.append(Paragraph("Weather Alerts", self.styles['heading1']))
            
            for alert in alerts:
                severity = alert.get('severity', 'info')
                color = {
                    'critical': self.COLORS['danger'],
                    'high': self.COLORS['danger'],
                    'warning': self.COLORS['warning'],
                    'info': self.COLORS['primary'],
                    'success': self.COLORS['secondary']
                }.get(severity, self.COLORS['light'])
                
                elements.append(Paragraph(
                    f"<font color='{color}'><b>⚠️ {alert.get('title', 'Alert')}</b></font>",
                    self.styles['heading2']
                ))
                elements.append(Paragraph(alert.get('message', ''), self.styles['normal']))
                if alert.get('recommendation'):
                    elements.append(Paragraph(
                        f"<b>Recommendation:</b> {alert.get('recommendation')}",
                        self.styles['small']
                    ))
                elements.append(Spacer(1, 8))
        
        return elements
    
    def _add_weather_recommendations(self, data: dict) -> list:
        """Add weather recommendations section"""
        elements = []
        
        elements.append(Paragraph("Recommendations", self.styles['heading1']))
        
        humidity = data.get('humidity', 0)
        temp = data.get('temperature', 25)
        wind = data.get('wind_speed', 10)
        
        recommendations = []
        
        if humidity > 80:
            recommendations.append("• Apply preventive fungicide due to high humidity")
            recommendations.append("• Monitor crops twice daily for disease symptoms")
            recommendations.append("• Improve air circulation between plants")
        elif humidity > 65:
            recommendations.append("• Increase monitoring for fungal diseases")
            recommendations.append("• Avoid overhead irrigation")
        
        if temp > 35:
            recommendations.append("• Provide shade or irrigation during peak heat")
            recommendations.append("• Avoid spraying during hot hours (10 AM - 4 PM)")
        elif temp < 15:
            recommendations.append("• Protect young plants from cold stress")
            recommendations.append("• Delay planting until temperatures rise")
        
        if wind > 20:
            recommendations.append("• Avoid spraying due to high wind conditions")
            recommendations.append("• Provide wind breaks for sensitive crops")
        
        if not recommendations:
            recommendations = [
                "• Continue regular monitoring and crop management",
                "• Maintain standard irrigation schedule",
                "• Keep records of weather conditions for trend analysis"
            ]
        
        for rec in recommendations:
            elements.append(Paragraph(rec, self.styles['normal']))
        
        elements.append(Spacer(1, 20))
        
        return elements


# Singleton instance
pdf_service = PDFService()