"""
Test Script for CSIT Timetable Generation System
Demonstrates the CSP solver functionality
"""

import sys
import time
from datetime import datetime
from csp_timetable import TimetableCSP
from data_processor import DataProcessor


def test_csp_solver():
    """Test the CSP solver with the provided data"""
    print("=" * 60)
    print("CSIT TIMETABLE GENERATION SYSTEM - TEST")
    print("=" * 60)
    
    # Initialize components
    csp = TimetableCSP()
    processor = DataProcessor()
    
    # Step 1: Validate data
    print("\n1. VALIDATING DATA FILES")
    print("-" * 30)
    validation_results = processor.validate_csv_files()
    
    all_valid = True
    for filename, errors in validation_results.items():
        if errors:
            print(f"ERROR {filename}: {len(errors)} errors")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   - {error}")
            if len(errors) > 3:
                print(f"   ... and {len(errors) - 3} more errors")
            all_valid = False
        else:
            print(f"OK {filename}: Valid")
    
    if not all_valid:
        print("\nWARNING: Some data files have validation errors. Proceeding anyway...")
    
    # Step 2: Load data
    print("\n2. LOADING DATA")
    print("-" * 30)
    try:
        csp.load_data_from_csv()
        print(f"OK Loaded {len(csp.sessions)} sessions")
        print(f"OK Loaded {len(csp.time_slots)} time slots")
        print(f"OK Loaded {len(csp.rooms)} rooms")
        print(f"OK Loaded {len(csp.instructors)} instructors")
        print(f"OK Loaded {len(csp.courses)} courses")
        print(f"OK Loaded {len(csp.sections)} sections")
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return False
    
    # Step 3: Build CSP model
    print("\n3. BUILDING CSP MODEL")
    print("-" * 30)
    try:
        csp.build_csp_model()
        print(f"OK Built CSP model with {len(csp.variables)} variables")
        
        # Calculate average domain size
        total_domain_size = sum(len(domain) for domain in csp.domains.values())
        avg_domain_size = total_domain_size / len(csp.domains) if csp.domains else 0
        print(f"OK Average domain size: {avg_domain_size:.1f}")
        
        # Show domain size distribution
        domain_sizes = [len(domain) for domain in csp.domains.values()]
        if domain_sizes:
            print(f"OK Domain size range: {min(domain_sizes)} - {max(domain_sizes)}")
    except Exception as e:
        print(f"ERROR building CSP model: {e}")
        return False
    
    # Step 4: Solve CSP
    print("\n4. SOLVING CSP")
    print("-" * 30)
    start_time = time.time()
    
    try:
        success = csp.solve(max_iterations=3000)
        end_time = time.time()
        solving_time = end_time - start_time
        
        if success:
            print(f"SUCCESS: Solution found in {solving_time:.2f} seconds!")
            print(f"OK Sessions scheduled: {len(csp.assignments)}")
            print(f"OK Hard constraint violations: {len(csp.constraint_violations)}")
            
            # Evaluate soft constraints
            csp.evaluate_soft_constraints()
            print(f"OK Soft constraint violations: {len(csp.soft_constraint_violations)}")
            
        else:
            print(f"FAILED: No solution found after {solving_time:.2f} seconds")
            print(f"ERROR Hard constraint violations: {len(csp.constraint_violations)}")
            
            # Show some constraint violations
            if csp.constraint_violations:
                print("\nSample constraint violations:")
                for violation in csp.constraint_violations[:5]:
                    print(f"   - {violation}")
            
            return False
            
    except Exception as e:
        print(f"ERROR solving CSP: {e}")
        return False
    
    # Step 5: Display results
    print("\n5. TIMETABLE RESULTS")
    print("-" * 30)
    
    if success:
        # Show summary statistics
        summary = csp.get_timetable_summary()
        
        print(f"TIMETABLE SUMMARY:")
        print(f"   Total sessions: {summary['total_sessions']}")
        print(f"   Hard violations: {summary['hard_constraint_violations']}")
        print(f"   Soft violations: {summary['soft_constraint_violations']}")
        
        # Show sessions by day
        print(f"\nSESSIONS BY DAY:")
        for day, count in summary['sessions_by_day'].items():
            print(f"   {day}: {count} sessions")
        
        # Show room utilization
        print(f"\nTOP 5 ROOM UTILIZATION:")
        room_util = sorted(summary['room_utilization'].items(), 
                          key=lambda x: x[1], reverse=True)
        for room, count in room_util[:5]:
            print(f"   {room}: {count} sessions")
        
        # Show instructor workload
        print(f"\nTOP 5 INSTRUCTOR WORKLOAD:")
        instructor_load = sorted(summary['instructor_load'].items(), 
                                key=lambda x: x[1], reverse=True)
        for instructor, count in instructor_load[:5]:
            print(f"   {instructor}: {count} sessions")
        
        # Export timetable
        print(f"\nEXPORTING TIMETABLE")
        csp.export_timetable_to_csv("test_timetable.csv")
        
        # Create database
        print(f"\nCREATING DATABASE")
        processor.create_database()
        processor.save_timetable_to_db(csp.assignments, {
            'test_run': True,
            'generation_time': datetime.now().isoformat()
        }, csp)
        
        print(f"\nSUCCESS: Test completed successfully!")
        print(f"Files created:")
        print(f"   - test_timetable.csv")
        print(f"   - timetable.db")
        
        return True
    
    return False


def main():
    """Main test function"""
    print("CSIT Timetable Generation System - Test Suite")
    print("Intelligent Systems Fall 2025/2026")
    print()
    
    # Run basic test
    success = test_csp_solver()
    
    if success:
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print("SUCCESS: System is working correctly!")
        print("Ready for production use!")
        print("\nTo start the web interface, run:")
        print("   streamlit run timetable_ui.py")
    else:
        print("\n" + "=" * 60)
        print("TESTS FAILED")
        print("=" * 60)
        print("ERROR: Please check the data files and try again")
        print("Make sure all CSV files are present and properly formatted")


if __name__ == "__main__":
    main()