"""
Report Controller
Handles PDF and CSV report generation for disease detection records
"""

import os
import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ReportController:
    """
    Controller for report generation operations
    Handles PDF and CSV report creation for disease detection records
    """
    
    @classmethod
    def generate_pdf_report(cls, data, report_type='detailed'):
        """
        Generate PDF report for disease detection
        
        Args:
            data: Dictionary containing report data (history, detection results)
            report_type: Type of report (summary, detailed, weather)
            
        Returns:
            BytesIO: PDF file as bytes
        """
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Story container for PDF elements
        story = []
        
        # Add styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4F46E5'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=12,
            spaceBefore=12
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6
        )
        
        # Add Header
        story.append(Paragraph("🌾 FarmIntel AI", title_style))
        story.append(Paragraph("<b>Disease Detection Report</b>", heading_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Add report type specific content
        if report_type == 'summary':
            cls._add_summary_report(story, data, styles, heading_style, normal_style)
        elif report_type == 'weather':
            cls._add_weather_report(story, data, styles, heading_style, normal_style)
        else:
            cls._add_detailed_report(story, data, styles, heading_style, normal_style)
        
        # Add Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "FarmIntel AI - Empowering Farmers with AI Technology",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#9CA3AF'), alignment=TA_CENTER)
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    @classmethod
    def _add_summary_report(cls, story, data, styles, heading_style, normal_style):
        """Add summary report content"""
        history = data.get('history', [])
        stats = data.get('stats', {})
        
        # Summary Statistics
        story.append(Paragraph("Executive Summary", heading_style))
        
        total_scans = len(history)
        diseased_count = len([h for h in history if 'Healthy' not in h.get('disease', '')])
        healthy_count = total_scans - diseased_count
        avg_confidence = sum(h.get('confidence', 0) for h in history) / total_scans if total_scans > 0 else 0
        
        # Create statistics table
        stats_data = [
            ['Metric', 'Value'],
            ['Total Scans', str(total_scans)],
            ['Diseased Crops', str(diseased_count)],
            ['Healthy Crops', str(healthy_count)],
            ['Detection Rate', f"{round((diseased_count/total_scans)*100, 1)}%" if total_scans > 0 else '0%'],
            ['Average Confidence', f"{round(avg_confidence, 1)}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[200, 150])
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Disease Distribution
        story.append(Paragraph("Disease Distribution", heading_style))
        
        disease_counts = {}
        for h in history:
            disease = h.get('disease', 'Unknown')
            if 'Healthy' not in disease:
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if sorted_diseases:
            disease_data = [['Disease', 'Count']] + [[d, str(c)] for d, c in sorted_diseases]
            disease_table = Table(disease_data, colWidths=[300, 100])
            disease_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ]))
            story.append(disease_table)
        else:
            story.append(Paragraph("No disease data available", normal_style))
    
    @classmethod
    def _add_detailed_report(cls, story, data, styles, heading_style, normal_style):
        """Add detailed report content"""
        history = data.get('history', [])
        detection = data.get('detection', {})
        
        if detection:
            # Current Detection Details
            story.append(Paragraph("Current Detection Results", heading_style))
            
            detection_data = [
                ['Parameter', 'Value'],
                ['Disease', detection.get('disease', 'N/A')],
                ['Confidence', f"{detection.get('confidence', 0)}%"],
                ['Severity', detection.get('severity', 'N/A')],
                ['Scan Date', detection.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
            ]
            
            detection_table = Table(detection_data, colWidths=[200, 250])
            detection_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ]))
            story.append(detection_table)
            story.append(Spacer(1, 20))
            
            # Treatment Recommendations
            story.append(Paragraph("Treatment Recommendations", heading_style))
            
            treatment_data = [
                ['Type', 'Recommendation'],
                ['Chemical Treatment', detection.get('chemical_treatment', 'N/A')],
                ['Organic Treatment', detection.get('organic_treatment', 'N/A')],
                ['Cultural Practices', detection.get('cultural_practices', 'N/A')],
                ['Prevention Tips', detection.get('prevention_tips', 'N/A')]
            ]
            
            treatment_table = Table(treatment_data, colWidths=[150, 300])
            treatment_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ]))
            story.append(treatment_table)
            story.append(Spacer(1, 20))
        
        # Scan History
        if history:
            story.append(Paragraph("Recent Scan History", heading_style))
            
            recent_history = history[-20:] if len(history) > 20 else history
            recent_history.reverse()
            
            history_data = [['Date', 'Disease', 'Confidence', 'Severity']]
            for h in recent_history:
                history_data.append([
                    h.get('date', 'N/A')[:16],
                    h.get('disease', 'N/A'),
                    f"{h.get('confidence', 0)}%",
                    h.get('severity', 'N/A')
                ])
            
            history_table = Table(history_data, colWidths=[120, 180, 80, 80])
            history_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6B7280')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ]))
            story.append(history_table)
    
    @classmethod
    def _add_weather_report(cls, story, data, styles, heading_style, normal_style):
        """Add weather impact report content"""
        weather_data = data.get('weather', {})
        history = data.get('history', [])
        
        # Current Weather
        story.append(Paragraph("Current Weather Conditions", heading_style))
        
        weather_info = [
            ['Parameter', 'Value'],
            ['Location', weather_data.get('city', 'N/A')],
            ['Temperature', f"{weather_data.get('temperature', 'N/A')}°C"],
            ['Humidity', f"{weather_data.get('humidity', 'N/A')}%"],
            ['Wind Speed', f"{weather_data.get('wind_speed', 'N/A')} km/h"],
            ['Rainfall', f"{weather_data.get('rainfall', 'N/A')} mm"],
            ['Disease Risk', weather_data.get('disease_risk', 'N/A')]
        ]
        
        weather_table = Table(weather_info, colWidths=[150, 200])
        weather_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        story.append(weather_table)
        story.append(Spacer(1, 20))
        
        # Weather Impact Analysis
        story.append(Paragraph("Weather Impact on Crop Health", heading_style))
        
        risk_level = weather_data.get('disease_risk', 'Low')
        risk_message = cls._get_risk_message(risk_level)
        
        story.append(Paragraph(f"<b>Current Risk Level:</b> {risk_level}", normal_style))
        story.append(Paragraph(risk_message, normal_style))
        story.append(Spacer(1, 10))
        
        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))
        
        humidity = weather_data.get('humidity', 0)
        temp = weather_data.get('temperature', 25)
        
        recommendations = []
        if humidity > 80:
            recommendations.append("• Apply preventive fungicide due to high humidity")
            recommendations.append("• Monitor crops for fungal disease symptoms")
        if temp > 35:
            recommendations.append("• Provide shade or irrigation during peak heat")
            recommendations.append("• Avoid spraying during hot hours")
        if temp < 15:
            recommendations.append("• Protect young plants from cold stress")
            recommendations.append("• Delay planting until temperatures rise")
        if not recommendations:
            recommendations.append("• Continue regular monitoring and crop management")
            recommendations.append("• Maintain standard irrigation schedule")
        
        for rec in recommendations:
            story.append(Paragraph(rec, normal_style))
    
    @classmethod
    def _get_risk_message(cls, risk_level):
        """Get risk level message"""
        messages = {
            'High': "⚠️ High disease risk detected. Immediate preventive action recommended. Apply protective fungicides and increase monitoring frequency.",
            'Medium': "📋 Medium disease risk. Regular monitoring recommended. Be prepared to take action if conditions worsen.",
            'Low': "✅ Low disease risk. Conditions are favorable. Continue regular crop management practices."
        }
        return messages.get(risk_level, "Monitor weather conditions and crop health regularly.")
    
    @classmethod
    def generate_csv_report(cls, data, report_type='detailed'):
        """
        Generate CSV report for disease detection
        
        Args:
            data: Dictionary containing report data
            report_type: Type of report (summary, detailed, history)
            
        Returns:
            StringIO: CSV file as string
        """
        output = StringIO()
        
        if report_type == 'history':
            cls._generate_history_csv(output, data)
        elif report_type == 'summary':
            cls._generate_summary_csv(output, data)
        else:
            cls._generate_detailed_csv(output, data)
        
        output.seek(0)
        return output
    
    @classmethod
    def _generate_history_csv(cls, output, data):
        """Generate history CSV report"""
        history = data.get('history', [])
        
        if not history:
            output.write("No history data available")
            return
        
        writer = csv.writer(output)
        
        # Write headers
        headers = ['ID', 'Date', 'Disease', 'Confidence (%)', 'Severity', 
                   'Chemical Treatment', 'Organic Treatment', 'Cultural Practices', 'Prevention Tips']
        writer.writerow(headers)
        
        # Write data rows
        for record in history:
            writer.writerow([
                record.get('id', ''),
                record.get('date', ''),
                record.get('disease', ''),
                record.get('confidence', ''),
                record.get('severity', ''),
                record.get('chemical_treatment', '').replace('\n', ' '),
                record.get('organic_treatment', '').replace('\n', ' '),
                record.get('cultural_practices', '').replace('\n', ' '),
                record.get('prevention_tips', '').replace('\n', ' ')
            ])
    
    @classmethod
    def _generate_summary_csv(cls, output, data):
        """Generate summary CSV report"""
        history = data.get('history', [])
        stats = data.get('stats', {})
        
        writer = csv.writer(output)
        
        writer.writerow(['FARMINTEL AI - SUMMARY REPORT'])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        writer.writerow(['STATISTICS'])
        writer.writerow(['Total Scans', len(history)])
        
        diseased_count = len([h for h in history if 'Healthy' not in h.get('disease', '')])
        writer.writerow(['Diseased Crops', diseased_count])
        writer.writerow(['Healthy Crops', len(history) - diseased_count])
        
        if history:
            avg_conf = sum(h.get('confidence', 0) for h in history) / len(history)
            writer.writerow(['Average Confidence', f'{round(avg_conf, 1)}%'])
        
        writer.writerow([])
        
        writer.writerow(['DISEASE DISTRIBUTION'])
        writer.writerow(['Disease', 'Count'])
        
        disease_counts = {}
        for h in history:
            disease = h.get('disease', 'Unknown')
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        for disease, count in sorted(disease_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([disease, count])
    
    @classmethod
    def _generate_detailed_csv(cls, output, data):
        """Generate detailed CSV report"""
        detection = data.get('detection', {})
        
        writer = csv.writer(output)
        
        writer.writerow(['FARMINTEL AI - DETAILED REPORT'])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        writer.writerow(['DETECTION RESULTS'])
        writer.writerow(['Parameter', 'Value'])
        writer.writerow(['Disease', detection.get('disease', 'N/A')])
        writer.writerow(['Confidence', f"{detection.get('confidence', 0)}%"])
        writer.writerow(['Severity', detection.get('severity', 'N/A')])
        writer.writerow(['Scan Date', detection.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))])
        writer.writerow([])
        
        writer.writerow(['TREATMENT RECOMMENDATIONS'])
        writer.writerow(['Type', 'Recommendation'])
        writer.writerow(['Chemical Treatment', detection.get('chemical_treatment', 'N/A')])
        writer.writerow(['Organic Treatment', detection.get('organic_treatment', 'N/A')])
        writer.writerow(['Cultural Practices', detection.get('cultural_practices', 'N/A')])
        writer.writerow(['Prevention Tips', detection.get('prevention_tips', 'N/A')])
    
    @classmethod
    def generate_single_detection_pdf(cls, detection_data):
        """
        Generate PDF report for a single detection
        
        Args:
            detection_data: Dictionary containing detection results
            
        Returns:
            BytesIO: PDF file as bytes
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4F46E5'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        story.append(Paragraph("🌾 FarmIntel AI", title_style))
        story.append(Paragraph("<b>Disease Detection Report</b>", styles['Heading2']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Detection Results
        story.append(Paragraph("Detection Results", styles['Heading3']))
        
        detection_table_data = [
            ['Disease', detection_data.get('disease', 'N/A')],
            ['Confidence', f"{detection_data.get('confidence', 0)}%"],
            ['Severity', detection_data.get('severity', 'N/A')],
            ['Scan Date', detection_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
        ]
        
        detection_table = Table(detection_table_data, colWidths=[150, 300])
        detection_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        story.append(detection_table)
        story.append(Spacer(1, 20))
        
        # Treatment
        story.append(Paragraph("Treatment Recommendations", styles['Heading3']))
        
        treatment_data = [
            ['Chemical Treatment', detection_data.get('chemical_treatment', 'N/A')],
            ['Organic Treatment', detection_data.get('organic_treatment', 'N/A')],
            ['Cultural Practices', detection_data.get('cultural_practices', 'N/A')],
            ['Prevention Tips', detection_data.get('prevention_tips', 'N/A')]
        ]
        
        treatment_table = Table(treatment_data, colWidths=[150, 300])
        treatment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        story.append(treatment_table)
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "FarmIntel AI - Empowering Farmers with AI Technology",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#9CA3AF'), alignment=TA_CENTER)
        ))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    @classmethod
    def generate_weather_pdf(cls, weather_data):
        """
        Generate PDF report for weather analysis
        
        Args:
            weather_data: Dictionary containing weather data
            
        Returns:
            BytesIO: PDF file as bytes
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4F46E5'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        story.append(Paragraph("🌾 FarmIntel AI", title_style))
        story.append(Paragraph("<b>Weather Analysis Report</b>", styles['Heading2']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Current Weather
        story.append(Paragraph("Current Weather Conditions", styles['Heading3']))
        
        weather_table_data = [
            ['Location', weather_data.get('city', 'N/A')],
            ['Temperature', f"{weather_data.get('temperature', 'N/A')}°C"],
            ['Humidity', f"{weather_data.get('humidity', 'N/A')}%"],
            ['Wind Speed', f"{weather_data.get('wind_speed', 'N/A')} km/h"],
            ['Rainfall', f"{weather_data.get('rainfall', 'N/A')} mm"],
            ['Disease Risk', weather_data.get('disease_risk', 'N/A')]
        ]
        
        weather_table = Table(weather_table_data, colWidths=[150, 300])
        weather_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        story.append(weather_table)
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading3']))
        
        humidity = weather_data.get('humidity', 0)
        
        if humidity > 80:
            story.append(Paragraph("• Apply preventive fungicide due to high humidity", styles['Normal']))
            story.append(Paragraph("• Monitor crops twice daily for disease symptoms", styles['Normal']))
        elif humidity > 65:
            story.append(Paragraph("• Regular monitoring recommended for fungal diseases", styles['Normal']))
        else:
            story.append(Paragraph("• Continue standard crop management practices", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "FarmIntel AI - Empowering Farmers with AI Technology",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#9CA3AF'), alignment=TA_CENTER)
        ))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer