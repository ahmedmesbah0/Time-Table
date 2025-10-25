"""
Professional Test Runner for CSIT Timetable Generator
Comprehensive test execution with detailed reporting
"""

import unittest
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import tempfile
import shutil

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import (
    TestDataStructures, TestCSPCore, TestDataProcessor, 
    TestPerformance, TestIntegration, TestErrorHandling,
    run_performance_benchmark
)
from performance_monitor import monitor
from logger import logger
from error_handling import error_handler, ErrorSeverity, ErrorCategory


class TestRunner:
    """Professional test runner with comprehensive reporting"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.test_details = []
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and return comprehensive results"""
        self.start_time = datetime.now()
        logger.info("Starting comprehensive test suite execution")
        
        # Test suites to run
        test_suites = [
            ("Data Structures", TestDataStructures),
            ("CSP Core", TestCSPCore),
            ("Data Processor", TestDataProcessor),
            ("Performance", TestPerformance),
            ("Integration", TestIntegration),
            ("Error Handling", TestErrorHandling)
        ]
        
        # Run each test suite
        for suite_name, test_class in test_suites:
            logger.info(f"Running {suite_name} tests")
            suite_result = self._run_test_suite(suite_name, test_class)
            self.test_results[suite_name] = suite_result
        
        # Run performance benchmark
        logger.info("Running performance benchmark")
        benchmark_result = self._run_performance_benchmark()
        self.test_results["Performance Benchmark"] = benchmark_result
        
        self.end_time = datetime.now()
        
        # Generate comprehensive report
        report = self._generate_report()
        
        # Save report to file
        self._save_report(report)
        
        logger.info("Test suite execution completed")
        return report
    
    def _run_test_suite(self, suite_name: str, test_class) -> Dict[str, Any]:
        """Run a specific test suite"""
        suite_start_time = time.time()
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        suite_end_time = time.time()
        duration = suite_end_time - suite_start_time
        
        # Update counters
        self.total_tests += result.testsRun
        self.passed_tests += result.testsRun - len(result.failures) - len(result.errors)
        self.failed_tests += len(result.failures)
        self.error_tests += len(result.errors)
        
        # Store test details
        for test, traceback in result.failures + result.errors:
            self.test_details.append({
                "suite": suite_name,
                "test": str(test),
                "status": "FAILED" if test in [f[0] for f in result.failures] else "ERROR",
                "traceback": traceback
            })
        
        return {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "duration": duration,
            "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
        }
    
    def _run_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmark tests"""
        benchmark_start_time = time.time()
        
        try:
            # Run benchmark in a separate process to avoid interference
            result = subprocess.run([
                sys.executable, "-c", 
                "from test_suite import run_performance_benchmark; run_performance_benchmark()"
            ], capture_output=True, text=True, timeout=300)
            
            benchmark_end_time = time.time()
            duration = benchmark_end_time - benchmark_start_time
            
            return {
                "success": result.returncode == 0,
                "duration": duration,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "duration": 300,
                "output": "",
                "error": "Benchmark timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - benchmark_start_time,
                "output": "",
                "error": str(e)
            }
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        report = {
            "test_execution": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration": total_duration,
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "error_tests": self.error_tests,
                "success_rate": self.passed_tests / self.total_tests if self.total_tests > 0 else 0
            },
            "test_suites": self.test_results,
            "failed_tests": self.test_details,
            "performance_metrics": monitor.get_performance_summary(),
            "error_summary": error_handler.get_error_summary(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd()
            }
        }
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to {report_file}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print test summary to console"""
        print("\n" + "="*80)
        print("CSIT TIMETABLE GENERATOR - TEST EXECUTION SUMMARY")
        print("="*80)
        
        execution = report["test_execution"]
        print(f"Execution Time: {execution['total_duration']:.2f} seconds")
        print(f"Total Tests: {execution['total_tests']}")
        print(f"Passed: {execution['passed_tests']}")
        print(f"Failed: {execution['failed_tests']}")
        print(f"Errors: {execution['error_tests']}")
        print(f"Success Rate: {execution['success_rate']:.2%}")
        
        print("\nTest Suite Results:")
        print("-" * 40)
        for suite_name, result in report["test_suites"].items():
            if suite_name == "Performance Benchmark":
                status = "PASSED" if result["success"] else "FAILED"
                print(f"{suite_name}: {status} ({result['duration']:.2f}s)")
            else:
                success_rate = result["success_rate"]
                status = "PASSED" if success_rate >= 0.8 else "FAILED"
                print(f"{suite_name}: {status} ({success_rate:.2%} - {result['tests_run']} tests)")
        
        if report["failed_tests"]:
            print("\nFailed Tests:")
            print("-" * 40)
            for test in report["failed_tests"][:10]:  # Show first 10 failures
                print(f"  {test['suite']}.{test['test']}: {test['status']}")
        
        print("\n" + "="*80)


def run_strict_tests():
    """Run strict testing with high standards"""
    print("Running STRICT testing mode...")
    print("This will test all components with high standards")
    
    runner = TestRunner()
    report = runner.run_all_tests()
    
    # Print summary
    runner.print_summary(report)
    
    # Check if tests meet strict standards
    success_rate = report["test_execution"]["success_rate"]
    if success_rate < 0.95:  # Require 95% success rate
        print(f"\nFAILED STRICT TESTING: Success rate {success_rate:.2%} is below 95%")
        return False
    else:
        print(f"\nPASSED STRICT TESTING: Success rate {success_rate:.2%} meets standards")
        return True


def run_quick_tests():
    """Run quick tests for development"""
    print("Running QUICK testing mode...")
    
    # Run only essential tests
    essential_suites = [TestDataStructures, TestCSPCore]
    
    total_tests = 0
    passed_tests = 0
    
    for suite_class in essential_suites:
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        passed_tests += result.testsRun - len(result.failures) - len(result.errors)
    
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    print(f"Quick tests completed: {passed_tests}/{total_tests} passed ({success_rate:.2%})")
    
    return success_rate >= 0.8


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "strict":
        success = run_strict_tests()
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == "quick":
        success = run_quick_tests()
        sys.exit(0 if success else 1)
    else:
        print("Usage:")
        print("  python test_runner.py strict  - Run comprehensive strict tests")
        print("  python test_runner.py quick    - Run quick development tests")
        print("  python test_runner.py         - Run all tests with standard reporting")
        
        runner = TestRunner()
        report = runner.run_all_tests()
        runner.print_summary(report)
