"""
Professional Logging System for CSIT Timetable Generator
Comprehensive logging with performance monitoring
"""

import logging
import logging.handlers
import time
import functools
import traceback
from datetime import datetime
from typing import Any, Callable, Optional
from pathlib import Path
from config_manager import config


class PerformanceLogger:
    """Logs performance metrics for system monitoring"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.metrics[operation] = duration
            del self.start_times[operation]
            return duration
        return 0.0
    
    def get_metrics(self) -> dict:
        """Get all performance metrics"""
        return self.metrics.copy()


class TimetableLogger:
    """Professional logging system for the timetable generator"""
    
    def __init__(self):
        self.logger = None
        self.performance_logger = PerformanceLogger()
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logging system"""
        # Create logger
        self.logger = logging.getLogger('timetable_generator')
        self.logger.setLevel(getattr(logging, config.system.log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if config.system.log_file:
            log_path = Path(config.system.log_file)
            log_path.parent.mkdir(exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=config.system.max_log_size_mb * 1024 * 1024,
                backupCount=config.system.log_retention_days
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception details"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", extra=kwargs)
            if config.system.debug_mode:
                self.logger.debug(traceback.format_exc())
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", extra=kwargs)
            self.logger.critical(traceback.format_exc())
        else:
            self.logger.critical(message, extra=kwargs)
    
    def performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        if config.system.enable_performance_monitoring:
            self.logger.info(f"PERFORMANCE - {operation}: {duration:.3f}s", extra=kwargs)
    
    def start_operation(self, operation: str):
        """Start timing an operation"""
        self.performance_logger.start_timer(operation)
        self.debug(f"Starting operation: {operation}")
    
    def end_operation(self, operation: str):
        """End timing an operation and log performance"""
        duration = self.performance_logger.end_timer(operation)
        self.performance(operation, duration)
        self.debug(f"Completed operation: {operation} in {duration:.3f}s")
    
    def get_performance_metrics(self) -> dict:
        """Get performance metrics"""
        return self.performance_logger.get_metrics()


def log_operation(operation_name: str = None):
    """Decorator to automatically log operation performance"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger.start_operation(op_name)
            try:
                result = func(*args, **kwargs)
                logger.end_operation(op_name)
                return result
            except Exception as e:
                logger.error(f"Operation {op_name} failed", exception=e)
                logger.end_operation(op_name)
                raise
        return wrapper
    return decorator


def log_data_operation(operation_type: str):
    """Decorator for data operations with specific logging"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting {operation_type}: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_type}: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"{operation_type} failed: {func.__name__}", exception=e)
                raise
        return wrapper
    return decorator


def log_csp_operation(operation_type: str):
    """Decorator for CSP operations with detailed logging"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"CSP {operation_type}: {func.__name__} started")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"CSP {operation_type}: {func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"CSP {operation_type}: {func.__name__} failed after {duration:.3f}s", exception=e)
                raise
        return wrapper
    return decorator


# Global logger instance
logger = TimetableLogger()
