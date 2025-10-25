# CSIT Timetable Generator - Professional Documentation

## 🎯 Project Overview

The **CSIT Timetable Generator** is a professional-grade automated timetable generation system implemented as a Constraint Satisfaction Problem (CSP). This system provides comprehensive solutions for academic scheduling with advanced error handling, performance monitoring, and extensive testing capabilities.

## 🏗️ Architecture

### Core Components

1. **CSP Engine** (`csp_timetable.py`)
   - Professional CSP implementation with backtracking algorithm
   - Comprehensive constraint handling (hard and soft constraints)
   - Performance monitoring and error handling integration

2. **Data Management** (`data_processor.py`)
   - CSV data validation and processing
   - SQLite database integration
   - Backup and recovery mechanisms

3. **Professional Features**
   - **Configuration Management** (`config_manager.py`)
   - **Logging System** (`logger.py`)
   - **Error Handling** (`error_handling.py`)
   - **Performance Monitoring** (`performance_monitor.py`)

4. **User Interface** (`timetable_ui.py`)
   - Streamlit-based web interface
   - Interactive data visualization
   - Real-time analysis and reporting

5. **Testing Framework**
   - **Comprehensive Test Suite** (`test_suite.py`)
   - **Professional Test Runner** (`test_runner.py`)
   - Unit, integration, and performance tests

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd csit-timetable-generator

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
python test_runner.py strict
```

### Basic Usage

```bash
# Start the web interface
streamlit run timetable_ui.py

# Run comprehensive tests
python test_runner.py strict

# Run quick development tests
python test_runner.py quick
```

## 📊 Professional Features

### 1. Configuration Management

The system includes a centralized configuration system:

```python
from config_manager import config

# Access configuration
max_iterations = config.solver.max_iterations
log_level = config.system.log_level
```

### 2. Professional Logging

Comprehensive logging with multiple levels and performance tracking:

```python
from logger import logger

logger.info("Operation completed successfully")
logger.error("Operation failed", exception=e)
logger.performance("data_loading", 2.5)
```

### 3. Error Handling

Structured error handling with custom exceptions:

```python
from error_handling import CSPSolvingError, DataValidationError

try:
    csp.solve()
except CSPSolvingError as e:
    print(f"CSP solving failed: {e.message}")
```

### 4. Performance Monitoring

Real-time performance monitoring and metrics:

```python
from performance_monitor import monitor

# Get performance summary
summary = monitor.get_performance_summary()
print(f"Average operation duration: {summary['average_operation_duration']}")
```

## 🧪 Testing Framework

### Test Types

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end workflow testing
3. **Performance Tests**: Scalability and performance validation
4. **Error Handling Tests**: Exception and edge case testing

### Running Tests

```bash
# Strict testing (95% success rate required)
python test_runner.py strict

# Quick testing for development
python test_runner.py quick

# Standard testing with detailed reporting
python test_runner.py
```

### Test Coverage

The test suite covers:
- ✅ Data structure validation
- ✅ CSP core functionality
- ✅ Data processing operations
- ✅ Performance benchmarks
- ✅ Integration workflows
- ✅ Error handling scenarios

## 📈 Performance Metrics

### Key Performance Indicators

- **CSP Solving Time**: Average time to find solutions
- **Memory Usage**: System resource consumption
- **Success Rate**: Percentage of successful timetable generations
- **Constraint Violations**: Hard and soft constraint analysis

### Monitoring Dashboard

Access real-time performance metrics through the web interface:
- System resource usage
- Operation performance statistics
- Error rates and patterns
- Constraint satisfaction analysis

## 🔧 Configuration Options

### Solver Configuration

```json
{
  "solver": {
    "max_iterations": 5000,
    "timeout_seconds": 300,
    "hard_constraint_weight": 5.0,
    "soft_constraint_weight": 1.0,
    "enable_constraint_propagation": true,
    "enable_forward_checking": true,
    "randomization_factor": 0.1
  }
}
```

### System Configuration

```json
{
  "system": {
    "version": "1.0.0",
    "debug_mode": false,
    "log_level": "INFO",
    "log_file": "timetable_generator.log",
    "enable_performance_monitoring": true,
    "max_log_size_mb": 10,
    "log_retention_days": 7
  }
}
```

## 📋 Data Requirements

### Required CSV Files

1. **Timeslots.csv**: Time slot definitions
2. **Rooms.csv**: Room information and capacity
3. **Instructors_data.csv**: Instructor qualifications and preferences
4. **Groups.csv**: Section/group information
5. **Sections.csv**: Session definitions
6. **Timetable.csv**: Course information

### Data Validation

The system includes comprehensive data validation:
- Required field validation
- Data type checking
- Business rule validation
- Consistency checks

## 🎨 User Interface

### Web Interface Features

- **Data Management**: Upload and validate CSV files
- **Timetable Generation**: Generate and visualize timetables
- **Analysis Dashboard**: Performance metrics and statistics
- **Settings**: Configuration management

### Visualization Components

- Interactive charts and graphs
- Real-time performance monitoring
- Constraint violation analysis
- Resource utilization reports

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Data Validation Errors**: Check CSV file format and content
3. **CSP Solving Failures**: Verify constraint definitions and data consistency
4. **Performance Issues**: Monitor system resources and adjust configuration

### Debug Mode

Enable debug mode for detailed logging:

```python
config.system.debug_mode = True
config.system.log_level = "DEBUG"
```

## 📚 API Reference

### Core Classes

- `TimetableCSP`: Main CSP solver class
- `DataProcessor`: Data management and validation
- `ConfigManager`: Configuration management
- `TimetableLogger`: Professional logging system
- `PerformanceMonitor`: Performance tracking
- `ErrorHandler`: Error management

### Key Methods

- `TimetableCSP.solve()`: Solve the CSP problem
- `DataProcessor.validate_csv_files()`: Validate input data
- `PerformanceMonitor.get_performance_summary()`: Get performance metrics
- `ErrorHandler.get_error_summary()`: Get error statistics

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run code formatting
black .

# Run linting
flake8 .

# Run type checking
mypy .

# Run tests
python test_runner.py strict
```

### Code Standards

- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Write unit tests for all new features
- Maintain test coverage above 90%

## 📄 License

This project is developed for educational purposes as part of the Intelligent Systems course at CSIT department.

## 🏆 Professional Standards

This implementation follows professional software development standards:

- ✅ Comprehensive error handling
- ✅ Performance monitoring and optimization
- ✅ Extensive testing framework
- ✅ Professional logging and debugging
- ✅ Configuration management
- ✅ Documentation and code quality
- ✅ Scalable architecture
- ✅ User-friendly interface

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Maintainer**: CSIT Department
