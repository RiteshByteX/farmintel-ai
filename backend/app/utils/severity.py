"""
Severity Calculator Utility
Calculates disease severity levels based on confidence scores and disease type
"""

from typing import Dict, Tuple, Optional


class SeverityCalculator:
    """
    Utility class for calculating disease severity levels
    Based on confidence scores and disease characteristics
    """
    
    # Severity thresholds (confidence percentage)
    SEVERITY_THRESHOLDS = {
        'severe': 85,
        'moderate': 70,
        'mild': 50,
        'low': 0
    }
    
    # Severity levels with details
    SEVERITY_LEVELS = {
        'severe': {
            'level': 'Severe',
            'color': '#EF4444',
            'bg_color': '#FEE2E2',
            'icon': '🔴',
            'action': 'Immediate action required - Apply treatment today',
            'timeframe': 'Apply within 24 hours',
            'description': 'Disease is widespread. Immediate treatment needed to prevent crop loss.'
        },
        'moderate': {
            'level': 'Moderate',
            'color': '#F59E0B',
            'bg_color': '#FEF3C7',
            'icon': '🟠',
            'action': 'Action within 3 days - Monitor closely',
            'timeframe': 'Apply within 3-5 days',
            'description': 'Disease is present but manageable. Timely treatment recommended.'
        },
        'mild': {
            'level': 'Mild',
            'color': '#10B981',
            'bg_color': '#D1FAE5',
            'icon': '🟢',
            'action': 'Monitor and treat if spreads',
            'timeframe': 'Monitor weekly',
            'description': 'Early stage disease. Preventive measures recommended.'
        },
        'low': {
            'level': 'Low',
            'color': '#6B7280',
            'bg_color': '#F3F4F6',
            'icon': '⚪',
            'action': 'No immediate action needed - Continue monitoring',
            'timeframe': 'Regular monitoring',
            'description': 'Low confidence detection. Consider re-testing for confirmation.'
        }
    }
    
    # Disease-specific severity adjustments
    DISEASE_SEVERITY_MAP = {
        # Severe diseases (always severe regardless of confidence)
        'Late Blight': {'base_severity': 'severe', 'multiplier': 1.2},
        'Black Rot': {'base_severity': 'severe', 'multiplier': 1.15},
        'Esca': {'base_severity': 'severe', 'multiplier': 1.15},
        'Northern Leaf Blight': {'base_severity': 'severe', 'multiplier': 1.1},
        'Yellow Leaf Curl Virus': {'base_severity': 'severe', 'multiplier': 1.2},
        
        # Moderate diseases
        'Early Blight': {'base_severity': 'moderate', 'multiplier': 1.0},
        'Bacterial Spot': {'base_severity': 'moderate', 'multiplier': 1.0},
        'Powdery Mildew': {'base_severity': 'moderate', 'multiplier': 0.9},
        'Cercospora Leaf Spot': {'base_severity': 'moderate', 'multiplier': 1.0},
        'Leaf Blight': {'base_severity': 'moderate', 'multiplier': 1.0},
        'Septoria Leaf Spot': {'base_severity': 'moderate', 'multiplier': 1.0},
        'Common Rust': {'base_severity': 'moderate', 'multiplier': 0.9},
        'Apple Scab': {'base_severity': 'moderate', 'multiplier': 1.0},
        'Cedar Apple Rust': {'base_severity': 'moderate', 'multiplier': 1.0},
        'Leaf Scorch': {'base_severity': 'moderate', 'multiplier': 1.0},
        
        # Mild diseases (lower severity)
        'Leaf Spot': {'base_severity': 'mild', 'multiplier': 0.8},
        
        # Healthy plants
        'Healthy': {'base_severity': 'low', 'multiplier': 0.5}
    }
    
    @classmethod
    def calculate(cls, confidence: float, disease_name: str = None) -> Dict:
        """
        Calculate severity level based on confidence and disease type
        
        Args:
            confidence: Confidence score (0-100)
            disease_name: Name of the detected disease (optional)
            
        Returns:
            Dictionary with severity details
        """
        # Get base severity from confidence
        base_severity_key = cls._get_severity_from_confidence(confidence)
        
        # Adjust for disease-specific factors if disease name provided
        if disease_name:
            severity_key = cls._adjust_for_disease(disease_name, base_severity_key, confidence)
        else:
            severity_key = base_severity_key
        
        # Get severity details
        severity_details = cls.SEVERITY_LEVELS.get(severity_key, cls.SEVERITY_LEVELS['low'])
        
        # Calculate affected area estimate
        affected_area = cls._calculate_affected_area(confidence, severity_key)
        
        # Calculate urgency level
        urgency = cls._calculate_urgency(severity_key, disease_name)
        
        # Calculate risk level
        risk = cls._calculate_risk(severity_key, confidence)
        
        return {
            'level': severity_details['level'],
            'key': severity_key,
            'color': severity_details['color'],
            'bg_color': severity_details['bg_color'],
            'icon': severity_details['icon'],
            'action': severity_details['action'],
            'timeframe': severity_details['timeframe'],
            'description': severity_details['description'],
            'confidence': round(confidence, 1),
            'affected_area': affected_area,
            'urgency': urgency,
            'risk': risk
        }
    
    @classmethod
    def _get_severity_from_confidence(cls, confidence: float) -> str:
        """
        Get severity key from confidence score
        
        Args:
            confidence: Confidence score (0-100)
            
        Returns:
            Severity key (severe, moderate, mild, low)
        """
        if confidence >= cls.SEVERITY_THRESHOLDS['severe']:
            return 'severe'
        elif confidence >= cls.SEVERITY_THRESHOLDS['moderate']:
            return 'moderate'
        elif confidence >= cls.SEVERITY_THRESHOLDS['mild']:
            return 'mild'
        else:
            return 'low'
    
    @classmethod
    def _adjust_for_disease(cls, disease_name: str, current_severity: str, confidence: float) -> str:
        """
        Adjust severity based on disease type
        
        Args:
            disease_name: Name of the disease
            current_severity: Current severity key
            confidence: Confidence score
            
        Returns:
            Adjusted severity key
        """
        # Check if disease has specific severity mapping
        for disease_key, info in cls.DISEASE_SEVERITY_MAP.items():
            if disease_key.lower() in disease_name.lower():
                base_severity = info['base_severity']
                multiplier = info['multiplier']
                
                # Adjust confidence with multiplier
                adjusted_confidence = min(confidence * multiplier, 100)
                
                # Recalculate severity with adjusted confidence
                if adjusted_confidence >= cls.SEVERITY_THRESHOLDS['severe']:
                    return 'severe'
                elif adjusted_confidence >= cls.SEVERITY_THRESHOLDS['moderate']:
                    return 'moderate'
                elif adjusted_confidence >= cls.SEVERITY_THRESHOLDS['mild']:
                    return 'mild'
                else:
                    return 'low'
        
        return current_severity
    
    @classmethod
    def _calculate_affected_area(cls, confidence: float, severity_key: str) -> str:
        """
        Calculate estimated affected area percentage
        
        Args:
            confidence: Confidence score
            severity_key: Severity level
            
        Returns:
            Estimated affected area description
        """
        if severity_key == 'severe':
            if confidence >= 95:
                return '75-100%'
            elif confidence >= 85:
                return '50-75%'
            else:
                return '40-60%'
        elif severity_key == 'moderate':
            if confidence >= 80:
                return '25-50%'
            else:
                return '15-30%'
        elif severity_key == 'mild':
            return '5-15%'
        else:
            return '<5%'
    
    @classmethod
    def _calculate_urgency(cls, severity_key: str, disease_name: str = None) -> str:
        """
        Calculate urgency level
        
        Args:
            severity_key: Severity level
            disease_name: Disease name for special cases
            
        Returns:
            Urgency description
        """
        if severity_key == 'severe':
            return 'Critical - Immediate action required within 24 hours'
        elif severity_key == 'moderate':
            return 'High - Action recommended within 3-5 days'
        elif severity_key == 'mild':
            return 'Medium - Monitor and plan treatment'
        else:
            return 'Low - Continue regular monitoring'
    
    @classmethod
    def _calculate_risk(cls, severity_key: str, confidence: float) -> Dict:
        """
        Calculate risk level
        
        Args:
            severity_key: Severity level
            confidence: Confidence score
            
        Returns:
            Risk assessment dictionary
        """
        risk_levels = {
            'severe': {
                'level': 'Very High',
                'color': '#EF4444',
                'score': 90,
                'description': 'High risk of crop loss. Immediate action required.'
            },
            'moderate': {
                'level': 'High',
                'color': '#F59E0B',
                'score': 70,
                'description': 'Significant risk. Timely treatment recommended.'
            },
            'mild': {
                'level': 'Medium',
                'color': '#10B981',
                'score': 50,
                'description': 'Moderate risk. Monitor and treat if necessary.'
            },
            'low': {
                'level': 'Low',
                'color': '#6B7280',
                'score': 30,
                'description': 'Low risk. Continue standard practices.'
            }
        }
        
        risk = risk_levels.get(severity_key, risk_levels['low'])
        
        # Adjust risk based on confidence
        if confidence >= 90 and severity_key == 'severe':
            risk['score'] = 95
            risk['description'] = 'Extremely high risk. Immediate action critical!'
        
        return risk
    
    @classmethod
    def get_severity_color(cls, severity: str) -> str:
        """
        Get color code for severity level
        
        Args:
            severity: Severity level string
            
        Returns:
            Hex color code
        """
        severity_lower = severity.lower()
        for key, details in cls.SEVERITY_LEVELS.items():
            if details['level'].lower() == severity_lower:
                return details['color']
        return cls.SEVERITY_LEVELS['low']['color']
    
    @classmethod
    def get_severity_icon(cls, severity: str) -> str:
        """
        Get icon for severity level
        
        Args:
            severity: Severity level string
            
        Returns:
            Icon character
        """
        severity_lower = severity.lower()
        for key, details in cls.SEVERITY_LEVELS.items():
            if details['level'].lower() == severity_lower:
                return details['icon']
        return cls.SEVERITY_LEVELS['low']['icon']
    
    @classmethod
    def get_action_message(cls, severity: str) -> str:
        """
        Get action message for severity level
        
        Args:
            severity: Severity level string
            
        Returns:
            Action message
        """
        severity_lower = severity.lower()
        for key, details in cls.SEVERITY_LEVELS.items():
            if details['level'].lower() == severity_lower:
                return details['action']
        return cls.SEVERITY_LEVELS['low']['action']
    
    @classmethod
    def get_all_severity_levels(cls) -> Dict:
        """
        Get all severity levels with their details
        
        Returns:
            Dictionary of all severity levels
        """
        return cls.SEVERITY_LEVELS
    
    @classmethod
    def get_severity_thresholds(cls) -> Dict:
        """
        Get severity thresholds
        
        Returns:
            Dictionary of threshold values
        """
        return cls.SEVERITY_THRESHOLDS