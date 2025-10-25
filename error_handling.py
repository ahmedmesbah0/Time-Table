"""
Professional Error Handling and Validation System
Comprehensive error handling with custom exceptions and validation
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import traceback


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    DATA_VALIDATION = "data_validation"
    CSP_SOLVING = "csp_solving"
    DATABASE = "database"
    FILE_OPERATION = "file_operation"
    CONFIGURATION = "configuration"
    USER_INPUT = "user_input"
    SYSTEM = "system"


@dataclass
class ErrorInfo:
    """Structured error information"""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    details: Optional[Dict[str, Any]] = None
    exception: Optional[Exception] = None
    timestamp: Optional[str] = None


class TimetableError(Exception):
    """Base exception for timetable generator"""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.SYSTEM, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}


class DataValidationError(TimetableError):
    """Exception for data validation errors"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        
        super().__init__(
            message, 
            ErrorCategory.DATA_VALIDATION, 
            ErrorSeverity.HIGH,
            details
        )


class CSPSolvingError(TimetableError):
    """Exception for CSP solving errors"""
    
    def __init__(self, message: str, constraint_violations: int = 0, iterations: int = 0):
        details = {
            'constraint_violations': constraint_violations,
            'iterations': iterations
        }
        
        super().__init__(
            message,
            ErrorCategory.CSP_SOLVING,
            ErrorSeverity.HIGH,
            details
        )


class DatabaseError(TimetableError):
    """Exception for database errors"""
    
    def __init__(self, message: str, operation: str = None, table: str = None):
        details = {}
        if operation:
            details['operation'] = operation
        if table:
            details['table'] = table
        
        super().__init__(
            message,
            ErrorCategory.DATABASE,
            ErrorSeverity.HIGH,
            details
        )


class FileOperationError(TimetableError):
    """Exception for file operation errors"""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None):
        details = {}
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message,
            ErrorCategory.FILE_OPERATION,
            ErrorSeverity.MEDIUM,
            details
        )


class ConfigurationError(TimetableError):
    """Exception for configuration errors"""
    
    def __init__(self, message: str, config_key: str = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(
            message,
            ErrorCategory.CONFIGURATION,
            ErrorSeverity.MEDIUM,
            details
        )


class ValidationResult:
    """Result of validation operation"""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[ErrorInfo] = []
        self.warnings: List[str] = []
    
    def add_error(self, error: ErrorInfo):
        """Add an error to the result"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result"""
        self.warnings.append(warning)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors"""
        if not self.errors:
            return {"total_errors": 0, "errors_by_category": {}, "errors_by_severity": {}}
        
        errors_by_category = {}
        errors_by_severity = {}
        
        for error in self.errors:
            category = error.category.value
            severity = error.severity.value
            
            errors_by_category[category] = errors_by_category.get(category, 0) + 1
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
        
        return {
            "total_errors": len(self.errors),
            "errors_by_category": errors_by_category,
            "errors_by_severity": errors_by_severity,
            "errors": [{"message": e.message, "category": e.category.value, "severity": e.severity.value} for e in self.errors]
        }


class DataValidator:
    """Comprehensive data validation system"""
    
    @staticmethod
    def validate_time_slot(time_slot_data: Dict[str, Any]) -> ValidationResult:
        """Validate time slot data"""
        result = ValidationResult()
        
        required_fields = ['Day', 'StartTime', 'EndTime']
        for field in required_fields:
            if field not in time_slot_data or not time_slot_data[field]:
                result.add_error(ErrorInfo(
                    f"Missing required field: {field}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.HIGH,
                    {'field': field}
                ))
        
        # Validate day
        if 'Day' in time_slot_data:
            valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Sunday', 'Saturday']
            if time_slot_data['Day'] not in valid_days:
                result.add_error(ErrorInfo(
                    f"Invalid day: {time_slot_data['Day']}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.MEDIUM,
                    {'field': 'Day', 'value': time_slot_data['Day']}
                ))
        
        # Validate time format
        if 'StartTime' in time_slot_data and 'EndTime' in time_slot_data:
            start_time = time_slot_data['StartTime']
            end_time = time_slot_data['EndTime']
            
            if not DataValidator._is_valid_time_format(start_time):
                result.add_error(ErrorInfo(
                    f"Invalid start time format: {start_time}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.MEDIUM,
                    {'field': 'StartTime', 'value': start_time}
                ))
            
            if not DataValidator._is_valid_time_format(end_time):
                result.add_error(ErrorInfo(
                    f"Invalid end time format: {end_time}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.MEDIUM,
                    {'field': 'EndTime', 'value': end_time}
                ))
        
        return result
    
    @staticmethod
    def validate_room(room_data: Dict[str, Any]) -> ValidationResult:
        """Validate room data"""
        result = ValidationResult()
        
        required_fields = ['RoomID', 'Type', 'Capacity', 'Type_of_spaces']
        for field in required_fields:
            if field not in room_data or not room_data[field]:
                result.add_error(ErrorInfo(
                    f"Missing required field: {field}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.HIGH,
                    {'field': field}
                ))
        
        # Validate capacity
        if 'Capacity' in room_data:
            try:
                capacity = int(room_data['Capacity'])
                if capacity <= 0:
                    result.add_error(ErrorInfo(
                        f"Invalid capacity: {capacity}",
                        ErrorCategory.DATA_VALIDATION,
                        ErrorSeverity.MEDIUM,
                        {'field': 'Capacity', 'value': capacity}
                    ))
            except ValueError:
                result.add_error(ErrorInfo(
                    f"Capacity must be a number: {room_data['Capacity']}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.MEDIUM,
                    {'field': 'Capacity', 'value': room_data['Capacity']}
                ))
        
        # Validate room type
        if 'Type' in room_data:
            valid_types = ['Lecture', 'Lab']
            if room_data['Type'] not in valid_types:
                result.add_error(ErrorInfo(
                    f"Invalid room type: {room_data['Type']}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.MEDIUM,
                    {'field': 'Type', 'value': room_data['Type']}
                ))
        
        return result
    
    @staticmethod
    def validate_instructor(instructor_data: Dict[str, Any]) -> ValidationResult:
        """Validate instructor data"""
        result = ValidationResult()
        
        required_fields = ['InstructorID', 'Name', 'QualifiedCourses', 'Preference']
        for field in required_fields:
            if field not in instructor_data or not instructor_data[field]:
                result.add_error(ErrorInfo(
                    f"Missing required field: {field}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.HIGH,
                    {'field': field}
                ))
        
        # Validate preference
        if 'Preference' in instructor_data:
            valid_preferences = ['Morning', 'Afternoon', 'No_Thursday', 'Any']
            if instructor_data['Preference'] not in valid_preferences:
                result.add_error(ErrorInfo(
                    f"Invalid preference: {instructor_data['Preference']}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.LOW,
                    {'field': 'Preference', 'value': instructor_data['Preference']}
                ))
        
        return result
    
    @staticmethod
    def validate_session(session_data: Dict[str, Any]) -> ValidationResult:
        """Validate session data"""
        result = ValidationResult()
        
        required_fields = ['Session_ID', 'Assigned_Course', 'Session_Type', 'Assigned_Section']
        for field in required_fields:
            if field not in session_data or not session_data[field]:
                result.add_error(ErrorInfo(
                    f"Missing required field: {field}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.HIGH,
                    {'field': field}
                ))
        
        # Validate session type
        if 'Session_Type' in session_data:
            valid_types = ['LAB', 'TUT', 'LEC']
            if session_data['Session_Type'] not in valid_types:
                result.add_error(ErrorInfo(
                    f"Invalid session type: {session_data['Session_Type']}",
                    ErrorCategory.DATA_VALIDATION,
                    ErrorSeverity.MEDIUM,
                    {'field': 'Session_Type', 'value': session_data['Session_Type']}
                ))
        
        return result
    
    @staticmethod
    def _is_valid_time_format(time_str: str) -> bool:
        """Check if time string is in valid format"""
        import re
        # Accept formats like "09:00 AM", "9:00 AM", "14:30", etc.
        time_pattern = r'^(0?[1-9]|1[0-2]):[0-5][0-9]\s*(AM|PM)?$|^(0?[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
        return bool(re.match(time_pattern, time_str.strip()))


class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self):
        self.error_log: List[ErrorInfo] = []
    
    def handle_error(self, error: ErrorInfo):
        """Handle an error"""
        self.error_log.append(error)
        
        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self._log_critical_error(error)
        elif error.severity == ErrorSeverity.HIGH:
            self._log_high_error(error)
        elif error.severity == ErrorSeverity.MEDIUM:
            self._log_medium_error(error)
        else:
            self._log_low_error(error)
    
    def _log_critical_error(self, error: ErrorInfo):
        """Log critical error"""
        print(f"CRITICAL ERROR: {error.message}")
        if error.exception:
            traceback.print_exc()
    
    def _log_high_error(self, error: ErrorInfo):
        """Log high severity error"""
        print(f"HIGH ERROR: {error.message}")
    
    def _log_medium_error(self, error: ErrorInfo):
        """Log medium severity error"""
        print(f"MEDIUM ERROR: {error.message}")
    
    def _log_low_error(self, error: ErrorInfo):
        """Log low severity error"""
        print(f"LOW ERROR: {error.message}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors"""
        if not self.error_log:
            return {"total_errors": 0}
        
        errors_by_category = {}
        errors_by_severity = {}
        
        for error in self.error_log:
            category = error.category.value
            severity = error.severity.value
            
            errors_by_category[category] = errors_by_category.get(category, 0) + 1
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "errors_by_category": errors_by_category,
            "errors_by_severity": errors_by_severity,
            "recent_errors": [{"message": e.message, "category": e.category.value, "severity": e.severity.value} for e in self.error_log[-10:]]
        }


# Global error handler instance
error_handler = ErrorHandler()
