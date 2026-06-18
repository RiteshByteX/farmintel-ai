"""
Helpers Utility - General helper functions for the application
Provides utility functions for file handling, date formatting, validation, etc.
"""

import os
import re
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Union, List, Dict, Any, Optional, Tuple
import random
import string


def validate_file(filename: str, allowed_extensions: set = None) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (default: {'jpg', 'jpeg', 'png', 'gif'})
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_size(file_path: str) -> str:
    """
    Get human-readable file size
    
    Args:
        file_path: Path to the file
        
    Returns:
        Formatted file size string (e.g., "2.5 MB")
    """
    try:
        size_bytes = os.path.getsize(file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    except:
        return "Unknown"


def format_date(date_str: str, input_format: str = None, output_format: str = '%B %d, %Y') -> str:
    """
    Format date string to readable format
    
    Args:
        date_str: Date string to format
        input_format: Input date format (auto-detected if None)
        output_format: Output format (default: 'Month DD, YYYY')
        
    Returns:
        Formatted date string
    """
    if not date_str:
        return ''
    
    try:
        # Try to parse ISO format
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            if input_format:
                dt = datetime.strptime(date_str, input_format)
            else:
                # Try common formats
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%Y%m%d']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return date_str
        
        return dt.strftime(output_format)
        
    except Exception:
        return date_str


def format_datetime(dt: datetime = None, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format datetime to string
    
    Args:
        dt: Datetime object (default: now)
        format: Output format
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime(format)


def generate_id(prefix: str = '', length: int = 8) -> str:
    """
    Generate a unique ID
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of the random part
        
    Returns:
        Unique ID string
    """
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    if prefix:
        return f"{prefix}_{random_part}"
    return random_part


def generate_uuid() -> str:
    """
    Generate a UUID
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing unsafe characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove special characters
    filename = re.sub(r'[^\w\-\.]', '', filename)
    
    # Ensure lowercase
    filename = filename.lower()
    
    return filename


def create_directory(directory_path: str) -> bool:
    """
    Create directory if it doesn't exist
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception:
        return False


def safe_delete_file(file_path: str) -> bool:
    """
    Safely delete a file if it exists
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file was deleted or didn't exist, False on error
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception:
        return False


def calculate_percentage(value: Union[int, float], total: Union[int, float]) -> float:
    """
    Calculate percentage
    
    Args:
        value: The value
        total: The total
        
    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    
    return round((value / total) * 100, 2)


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_json_safe(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def dict_to_json(data: Dict, pretty: bool = True) -> str:
    """
    Convert dictionary to JSON string
    
    Args:
        data: Dictionary to convert
        pretty: Whether to format with indentation
        
    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Create hash of a string
    
    Args:
        text: Input string
        algorithm: Hash algorithm ('md5', 'sha256', 'sha512')
        
    Returns:
        Hash string
    """
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(text.encode()).hexdigest()
    else:
        return hashlib.sha256(text.encode()).hexdigest()


def is_valid_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    """
    Validate phone number (Indian format)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove any spaces or dashes
    phone = re.sub(r'[\s\-]', '', phone)
    
    # Check Indian phone number format
    pattern = r'^(\+91|0)?[6-9]\d{9}$'
    return re.match(pattern, phone) is not None


def is_valid_pincode(pincode: str) -> bool:
    """
    Validate Indian pincode
    
    Args:
        pincode: Pincode to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[1-9][0-9]{5}$'
    return re.match(pattern, pincode) is not None


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split a list into chunks
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO format timestamp
    """
    return datetime.now().isoformat()


def get_date_range(days: int = 7) -> Tuple[str, str]:
    """
    Get date range from today to past days
    
    Args:
        days: Number of days to go back
        
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def format_currency(amount: float, currency: str = '₹') -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    return f"{currency}{amount:,.2f}"


def calculate_average(numbers: List[Union[int, float]]) -> float:
    """
    Calculate average of a list of numbers
    
    Args:
        numbers: List of numbers
        
    Returns:
        Average value
    """
    if not numbers:
        return 0.0
    
    return sum(numbers) / len(numbers)


def get_random_color() -> str:
    """
    Generate a random hex color
    
    Returns:
        Random hex color string
    """
    return '#{:06x}'.format(random.randint(0, 0xFFFFFF))


def get_status_color(status: str) -> str:
    """
    Get color for status
    
    Args:
        status: Status string (success, error, warning, info)
        
    Returns:
        Color hex code
    """
    colors = {
        'success': '#10B981',
        'error': '#EF4444',
        'warning': '#F59E0B',
        'info': '#3B82F6',
        'severe': '#EF4444',
        'moderate': '#F59E0B',
        'mild': '#10B981',
        'low': '#6B7280'
    }
    
    return colors.get(status.lower(), '#6B7280')


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recursively merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (overrides dict1)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def filter_dict(data: Dict, keys: List[str]) -> Dict:
    """
    Filter dictionary to only include specified keys
    
    Args:
        data: Input dictionary
        keys: Keys to keep
        
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in keys}


def exclude_keys(data: Dict, keys: List[str]) -> Dict:
    """
    Exclude specified keys from dictionary
    
    Args:
        data: Input dictionary
        keys: Keys to exclude
        
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k not in keys}