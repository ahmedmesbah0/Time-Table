"""
Professional Performance Monitoring System
Comprehensive performance tracking and optimization
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationMetrics:
    """Metrics for a specific operation"""
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    iterations: Optional[int] = None
    constraint_violations: Optional[int] = None


class PerformanceMonitor:
    """Professional performance monitoring system"""
    
    def __init__(self, enable_monitoring: bool = True):
        self.enable_monitoring = enable_monitoring
        self.metrics: List[PerformanceMetric] = []
        self.operations: List[OperationMetrics] = []
        self.system_metrics: List[PerformanceMetric] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring = False
        self.monitoring_interval = 5.0  # seconds
        
        if self.enable_monitoring:
            self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """Start background system monitoring"""
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def _monitor_system(self):
        """Background system monitoring"""
        while not self.stop_monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.add_metric("cpu_usage", cpu_percent, "percent", "system")
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.add_metric("memory_usage", memory.percent, "percent", "system")
                self.add_metric("memory_available_mb", memory.available / (1024 * 1024), "MB", "system")
                
                # Disk usage
                disk = psutil.disk_usage('/')
                self.add_metric("disk_usage", disk.percent, "percent", "system")
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"Error in system monitoring: {e}")
                time.sleep(self.monitoring_interval)
    
    def add_metric(self, name: str, value: float, unit: str, category: str = "general", metadata: Dict = None):
        """Add a performance metric"""
        if not self.enable_monitoring:
            return
        
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            category=category,
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
    
    def start_operation(self, operation_name: str) -> OperationMetrics:
        """Start monitoring an operation"""
        if not self.enable_monitoring:
            return OperationMetrics(operation_name, datetime.now())
        
        operation = OperationMetrics(
            operation_name=operation_name,
            start_time=datetime.now()
        )
        
        self.operations.append(operation)
        return operation
    
    def end_operation(self, operation: OperationMetrics, success: bool = True, error_message: str = None, **kwargs):
        """End monitoring an operation"""
        if not self.enable_monitoring:
            return
        
        operation.end_time = datetime.now()
        operation.duration = (operation.end_time - operation.start_time).total_seconds()
        operation.success = success
        operation.error_message = error_message
        
        # Add additional metrics
        for key, value in kwargs.items():
            setattr(operation, key, value)
        
        # Add operation metrics
        self.add_metric(f"{operation.operation_name}_duration", operation.duration, "seconds", "operation")
        self.add_metric(f"{operation.operation_name}_success", 1 if success else 0, "boolean", "operation")
        
        if operation.iterations:
            self.add_metric(f"{operation.operation_name}_iterations", operation.iterations, "count", "operation")
        
        if operation.constraint_violations is not None:
            self.add_metric(f"{operation.operation_name}_constraint_violations", operation.constraint_violations, "count", "operation")
    
    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for the last time window"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        # Filter recent metrics
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        recent_operations = [o for o in self.operations if o.start_time >= cutoff_time]
        
        # Calculate summary statistics
        summary = {
            "time_window_minutes": time_window_minutes,
            "total_metrics": len(recent_metrics),
            "total_operations": len(recent_operations),
            "successful_operations": len([o for o in recent_operations if o.success]),
            "failed_operations": len([o for o in recent_operations if not o.success]),
            "average_operation_duration": 0,
            "metrics_by_category": {},
            "operation_performance": {},
            "system_performance": {}
        }
        
        if recent_operations:
            durations = [o.duration for o in recent_operations if o.duration is not None]
            if durations:
                summary["average_operation_duration"] = sum(durations) / len(durations)
        
        # Group metrics by category
        for metric in recent_metrics:
            category = metric.category
            if category not in summary["metrics_by_category"]:
                summary["metrics_by_category"][category] = []
            summary["metrics_by_category"][category].append({
                "name": metric.name,
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp.isoformat()
            })
        
        # Operation performance analysis
        for operation in recent_operations:
            op_name = operation.operation_name
            if op_name not in summary["operation_performance"]:
                summary["operation_performance"][op_name] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "average_duration": 0,
                    "min_duration": float('inf'),
                    "max_duration": 0
                }
            
            perf = summary["operation_performance"][op_name]
            perf["total_calls"] += 1
            if operation.success:
                perf["successful_calls"] += 1
            
            if operation.duration is not None:
                perf["min_duration"] = min(perf["min_duration"], operation.duration)
                perf["max_duration"] = max(perf["max_duration"], operation.duration)
        
        # Calculate averages
        for op_name, perf in summary["operation_performance"].items():
            if perf["total_calls"] > 0:
                perf["success_rate"] = perf["successful_calls"] / perf["total_calls"]
                if perf["min_duration"] != float('inf'):
                    perf["average_duration"] = (perf["min_duration"] + perf["max_duration"]) / 2
        
        # System performance
        system_metrics = [m for m in recent_metrics if m.category == "system"]
        if system_metrics:
            cpu_metrics = [m for m in system_metrics if m.name == "cpu_usage"]
            memory_metrics = [m for m in system_metrics if m.name == "memory_usage"]
            
            if cpu_metrics:
                cpu_values = [m.value for m in cpu_metrics]
                summary["system_performance"]["cpu"] = {
                    "average": sum(cpu_values) / len(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values)
                }
            
            if memory_metrics:
                memory_values = [m.value for m in memory_metrics]
                summary["system_performance"]["memory"] = {
                    "average": sum(memory_values) / len(memory_values),
                    "max": max(memory_values),
                    "min": min(memory_values)
                }
        
        return summary
    
    def get_operation_statistics(self, operation_name: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific operation"""
        operations = [o for o in self.operations if o.operation_name == operation_name]
        
        if not operations:
            return {"operation_name": operation_name, "total_calls": 0}
        
        durations = [o.duration for o in operations if o.duration is not None]
        successful = [o for o in operations if o.success]
        
        stats = {
            "operation_name": operation_name,
            "total_calls": len(operations),
            "successful_calls": len(successful),
            "failed_calls": len(operations) - len(successful),
            "success_rate": len(successful) / len(operations) if operations else 0
        }
        
        if durations:
            stats.update({
                "average_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_duration": sum(durations)
            })
        
        return stats
    
    def export_metrics(self, file_path: str):
        """Export metrics to JSON file"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp.isoformat(),
                    "category": m.category,
                    "metadata": m.metadata
                }
                for m in self.metrics
            ],
            "operations": [
                {
                    "operation_name": o.operation_name,
                    "start_time": o.start_time.isoformat(),
                    "end_time": o.end_time.isoformat() if o.end_time else None,
                    "duration": o.duration,
                    "success": o.success,
                    "error_message": o.error_message,
                    "iterations": o.iterations,
                    "constraint_violations": o.constraint_violations
                }
                for o in self.operations
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.operations.clear()
        self.system_metrics.clear()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.stop_monitoring = True
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)


def performance_timer(operation_name: str = None):
    """Decorator for automatic performance timing"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            operation = monitor.start_operation(op_name)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_operation(operation, success=True)
                return result
            except Exception as e:
                monitor.end_operation(operation, success=False, error_message=str(e))
                raise
        
        return wrapper
    return decorator


def csp_performance_timer(operation_name: str = None):
    """Decorator for CSP-specific performance timing"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            operation = monitor.start_operation(op_name)
            
            try:
                result = func(*args, **kwargs)
                
                # Extract CSP-specific metrics
                csp_metrics = {}
                if hasattr(args[0], 'assignments'):
                    csp_metrics['iterations'] = getattr(args[0], 'iterations', 0)
                    csp_metrics['constraint_violations'] = len(getattr(args[0], 'hard_constraint_violations', []))
                
                monitor.end_operation(operation, success=True, **csp_metrics)
                return result
            except Exception as e:
                monitor.end_operation(operation, success=False, error_message=str(e))
                raise
        
        return wrapper
    return decorator


# Global performance monitor instance
monitor = PerformanceMonitor()
