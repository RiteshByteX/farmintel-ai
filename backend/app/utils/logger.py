"""
Logger Utility - Logging configuration and management
Provides centralized logging setup for the entire application
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from flask import request, has_request_context
import traceback
from typing import Optional


class RequestFormatter(logging.Formatter):
    """
    Custom log formatter that includes request information when available
    """
    
    def format(self, record):
        """
        Format log record with request context if available
        
        Args:
            record: Log record
            
        Returns:
            Formatted log string
        """
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
            record.user_agent = request.headers.get('User-Agent', 'Unknown')
        else:
            record.url = ''
            record.method = ''
            record.remote_addr = ''
            record.user_agent = ''
        
        return super().format(record)


class Logger:
    """
    Centralized logger configuration for the application
    Provides consistent logging across all modules
    """
    
    # Log levels
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    # Format strings
    CONSOLE_FORMAT = '%(asctime)s | %(levelname)-8s | %(message)s'
    FILE_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(filename)s:%(lineno)d | %(message)s'
    DETAILED_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'
    REQUEST_FORMAT = '%(asctime)s | %(levelname)-8s | %(remote_addr)-15s | %(method)-6s | %(url)-50s | %(message)s'
    
    # Date format
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure single logger instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger configuration"""
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = logging.getLogger('FarmIntelAI')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create logs directory
        self._ensure_log_directory()
        
        # Add handlers
        self._add_console_handler()
        self._add_file_handler()
        self._add_error_file_handler()
        self._add_request_file_handler()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _ensure_log_directory(self):
        """Ensure logs directory exists"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def _add_console_handler(self):
        """Add console handler for stdout output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(self.CONSOLE_FORMAT, self.DATE_FORMAT)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """Add rotating file handler for all logs"""
        file_handler = RotatingFileHandler(
            'logs/farmintel.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(self.FILE_FORMAT, self.DATE_FORMAT)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def _add_error_file_handler(self):
        """Add separate file handler for error logs only"""
        error_handler = RotatingFileHandler(
            'logs/errors.log',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=20,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(self.DETAILED_FORMAT, self.DATE_FORMAT)
        error_handler.setFormatter(formatter)
        
        self.logger.addHandler(error_handler)
    
    def _add_request_file_handler(self):
        """Add timed rotating file handler for request logs"""
        request_handler = TimedRotatingFileHandler(
            'logs/requests.log',
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        request_handler.setLevel(logging.INFO)
        
        formatter = RequestFormatter(self.REQUEST_FORMAT, self.DATE_FORMAT)
        request_handler.setFormatter(formatter)
        
        self.logger.addHandler(request_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get logger instance with optional name suffix
        
        Args:
            name: Optional name to append to logger
            
        Returns:
            Logger instance
        """
        if name:
            return self.logger.getChild(name)
        return self.logger
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, *args, **kwargs)
    
    def log_request(self, method: str, url: str, status_code: int, duration_ms: float):
        """
        Log API request details
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: Response status code
            duration_ms: Request duration in milliseconds
        """
        level = logging.INFO if status_code < 400 else logging.WARNING if status_code < 500 else logging.ERROR
        
        self.logger.log(
            level,
            f"REQUEST | {method} | {url} | Status: {status_code} | Duration: {duration_ms:.2f}ms"
        )
    
    def log_prediction(self, disease: str, confidence: float, severity: str):
        """
        Log disease prediction details
        
        Args:
            disease: Detected disease name
            confidence: Confidence score
            severity: Severity level
        """
        self.logger.info(
            f"PREDICTION | Disease: {disease} | Confidence: {confidence:.1f}% | Severity: {severity}"
        )
    
    def log_weather_fetch(self, city: str, success: bool, response_time_ms: float):
        """
        Log weather API fetch details
        
        Args:
            city: City name
            success: Whether fetch was successful
            response_time_ms: Response time in milliseconds
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"WEATHER | City: {city} | Status: {status} | Response Time: {response_time_ms:.2f}ms"
        )
    
    def log_model_load(self, model_path: str, success: bool):
        """
        Log model loading details
        
        Args:
            model_path: Path to model file
            success: Whether load was successful
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"MODEL | Path: {model_path} | Status: {status}")
    
    def log_database_operation(self, operation: str, collection: str, success: bool, details: str = ''):
        """
        Log database operation details
        
        Args:
            operation: Operation type (INSERT, UPDATE, DELETE, SELECT)
            collection: Collection/table name
            success: Whether operation was successful
            details: Additional details
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.debug(f"DB | {operation} | {collection} | Status: {status} | {details}")
    
    def log_user_action(self, user_id: str, action: str, details: str = ''):
        """
        Log user action details
        
        Args:
            user_id: User identifier
            action: Action performed
            details: Additional details
        """
        self.logger.info(f"USER | User: {user_id} | Action: {action} | {details}")
    
    def log_performance(self, operation: str, duration_ms: float):
        """
        Log performance metrics
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
        """
        if duration_ms > 1000:
            level = logging.WARNING
            message = f"PERFORMANCE | {operation} | Duration: {duration_ms:.2f}ms | SLOW (>1s)"
        else:
            level = logging.DEBUG
            message = f"PERFORMANCE | {operation} | Duration: {duration_ms:.2f}ms"
        
        self.logger.log(level, message)
    
    def log_training_progress(self, epoch: int, total_epochs: int, loss: float, accuracy: float, val_loss: float = None, val_accuracy: float = None):
        """
        Log model training progress
        
        Args:
            epoch: Current epoch
            total_epochs: Total epochs
            loss: Training loss
            accuracy: Training accuracy
            val_loss: Validation loss (optional)
            val_accuracy: Validation accuracy (optional)
        """
        message = f"TRAINING | Epoch {epoch}/{total_epochs} | Loss: {loss:.4f} | Acc: {accuracy:.4f}"
        
        if val_loss is not None:
            message += f" | Val Loss: {val_loss:.4f} | Val Acc: {val_accuracy:.4f}"
        
        self.logger.info(message)


# Global logger instance
_logger = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get the global logger instance
    
    Args:
        name: Optional name for child logger
        
    Returns:
        Logger instance
    """
    global _logger
    if _logger is None:
        _logger = Logger()
    
    return _logger.get_logger(name)


def log_exception(e: Exception, context: str = ''):
    """
    Log an exception with full traceback
    
    Args:
        e: Exception object
        context: Additional context information
    """
    logger = get_logger()
    
    error_msg = f"Exception in {context}: {str(e)}" if context else str(e)
    logger.exception(error_msg)


def log_api_call(func):
    """
    Decorator to log API call details
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            if has_request_context():
                logger.log_request(
                    method=request.method,
                    url=request.url,
                    status_code=result[1] if isinstance(result, tuple) else 200,
                    duration_ms=duration_ms
                )
            
            return result
            
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"API call failed: {str(e)} | Duration: {duration_ms:.2f}ms")
            logger.exception(e)
            raise
    
    return wrapper


class LoggerContext:
    """
    Context manager for temporary log level changes
    """
    
    def __init__(self, logger: logging.Logger, level: int):
        """
        Initialize context manager
        
        Args:
            logger: Logger instance
            level: Temporary log level
        """
        self.logger = logger
        self.level = level
        self.old_level = None
    
    def __enter__(self):
        """Set temporary log level"""
        self.old_level = self.logger.level
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original log level"""
        self.logger.setLevel(self.old_level)