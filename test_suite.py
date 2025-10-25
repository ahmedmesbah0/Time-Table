"""
Comprehensive Test Suite for CSIT Timetable Generator
Professional testing with unit tests, integration tests, and performance tests
"""

import unittest
import tempfile
import shutil
import os
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sqlite3

# Import our modules
from csp_timetable import TimetableCSP, TimeSlot, Room, Instructor, Course, Section, Session
from data_processor import DataProcessor
from config_manager import ConfigManager
from logger import TimetableLogger


class TestDataStructures(unittest.TestCase):
    """Test data structure classes"""
    
    def test_time_slot_creation(self):
        """Test TimeSlot creation and properties"""
        ts = TimeSlot("Monday", "09:00 AM", "10:30 AM", 1)
        self.assertEqual(ts.day, "Monday")
        self.assertEqual(ts.start_time, "09:00 AM")
        self.assertEqual(ts.end_time, "10:30 AM")
        self.assertEqual(ts.slot_id, 1)
    
    def test_room_creation(self):
        """Test Room creation and properties"""
        room = Room("B07-F1.01", "Lecture", 25, "Classroom")
        self.assertEqual(room.room_id, "B07-F1.01")
        self.assertEqual(room.room_type, "Lecture")
        self.assertEqual(room.capacity, 25)
        self.assertEqual(room.space_type, "Classroom")
    
    def test_instructor_creation(self):
        """Test Instructor creation and properties"""
        instructor = Instructor("1", "John Doe", ["CSC111", "CSC211"], "Morning")
        self.assertEqual(instructor.instructor_id, "1")
        self.assertEqual(instructor.name, "John Doe")
        self.assertEqual(instructor.qualified_courses, ["CSC111", "CSC211"])
        self.assertEqual(instructor.preference, "Morning")
    
    def test_course_creation(self):
        """Test Course creation and properties"""
        course = Course("CSC111", "Programming", 3, "CSIT", "LEC/LAB", ["John Doe"])
        self.assertEqual(course.course_id, "CSC111")
        self.assertEqual(course.course_name, "Programming")
        self.assertEqual(course.credits, 3)
        self.assertEqual(course.department, "CSIT")
        self.assertEqual(course.course_type, "LEC/LAB")
        self.assertEqual(course.instructors, ["John Doe"])
    
    def test_session_creation(self):
        """Test Session creation and properties"""
        session = Session("SESS_001", "CSC111", "LAB", "Level1_Group1")
        self.assertEqual(session.session_id, "SESS_001")
        self.assertEqual(session.course_id, "CSC111")
        self.assertEqual(session.session_type, "LAB")
        self.assertEqual(session.section_id, "Level1_Group1")


class TestCSPCore(unittest.TestCase):
    """Test CSP core functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.csp = TimetableCSP()
        
        # Create test data
        self.csp.time_slots = [
            TimeSlot("Monday", "09:00 AM", "10:30 AM", 0),
            TimeSlot("Monday", "10:45 AM", "12:15 PM", 1),
            TimeSlot("Tuesday", "09:00 AM", "10:30 AM", 2)
        ]
        
        self.csp.rooms = [
            Room("Room1", "Lecture", 30, "Classroom"),
            Room("Room2", "Lab", 20, "Classroom")
        ]
        
        self.csp.instructors = [
            Instructor("1", "John Doe", ["CSC111"], "Morning"),
            Instructor("2", "Jane Smith", ["CSC111"], "Afternoon")
        ]
        
        self.csp.sessions = [
            Session("SESS_001", "CSC111", "LAB", "Level1_Group1"),
            Session("SESS_002", "CSC111", "TUT", "Level1_Group1")
        ]
    
    def test_room_suitability(self):
        """Test room suitability checking"""
        lab_session = Session("SESS_001", "CSC111", "LAB", "Level1_Group1")
        tut_session = Session("SESS_002", "CSC111", "TUT", "Level1_Group1")
        
        lecture_room = Room("Room1", "Lecture", 30, "Classroom")
        lab_room = Room("Room2", "Lab", 20, "Classroom")
        
        # Lab sessions need Lab rooms
        self.assertFalse(self.csp._is_room_suitable(lab_session, lecture_room))
        self.assertTrue(self.csp._is_room_suitable(lab_session, lab_room))
        
        # TUT sessions can use Lecture rooms
        self.assertTrue(self.csp._is_room_suitable(tut_session, lecture_room))
        self.assertFalse(self.csp._is_room_suitable(tut_session, lab_room))
    
    def test_hard_constraints(self):
        """Test hard constraint checking"""
        session1 = Session("SESS_001", "CSC111", "LAB", "Level1_Group1")
        session2 = Session("SESS_002", "CSC111", "TUT", "Level1_Group1")
        
        time_slot = TimeSlot("Monday", "09:00 AM", "10:30 AM", 0)
        room = Room("Room1", "Lecture", 30, "Classroom")
        instructor = Instructor("1", "John Doe", ["CSC111"], "Morning")
        
        # Test instructor double-booking constraint
        self.csp.assignments = {
            "SESS_001": (time_slot, room, instructor)
        }
        
        # Same instructor, same time should fail
        self.assertFalse(self.csp._check_hard_constraints(session2, time_slot, room, instructor))
        
        # Different instructor should pass
        different_instructor = Instructor("2", "Jane Smith", ["CSC111"], "Afternoon")
        self.assertTrue(self.csp._check_hard_constraints(session2, time_slot, room, different_instructor))
    
    def test_soft_constraints(self):
        """Test soft constraint evaluation"""
        session = Session("SESS_001", "CSC111", "LAB", "Level1_Group1")
        
        # Morning instructor assigned to afternoon slot
        morning_instructor = Instructor("1", "John Doe", ["CSC111"], "Morning")
        afternoon_time = TimeSlot("Monday", "02:15 PM", "03:45 PM", 1)
        room = Room("Room1", "Lecture", 30, "Classroom")
        
        self.csp.assignments = {
            "SESS_001": (afternoon_time, room, morning_instructor)
        }
        
        self.csp.evaluate_soft_constraints()
        
        # Should have soft constraint violations
        self.assertGreater(len(self.csp.soft_constraint_violations), 0)


class TestDataProcessor(unittest.TestCase):
    """Test data processing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = DataProcessor()
        self.processor.data_dir = self.temp_dir
        self.processor.db_path = os.path.join(self.temp_dir, "test.db")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_csv_validation(self):
        """Test CSV file validation"""
        # Create valid CSV file
        valid_csv = os.path.join(self.temp_dir, "valid.csv")
        with open(valid_csv, 'w', encoding='utf-8') as f:
            f.write("Day,StartTime,EndTime\n")
            f.write("Monday,09:00 AM,10:30 AM\n")
        
        # Create invalid CSV file (missing column)
        invalid_csv = os.path.join(self.temp_dir, "invalid.csv")
        with open(invalid_csv, 'w', encoding='utf-8') as f:
            f.write("Day,StartTime\n")  # Missing EndTime column
            f.write("Monday,09:00 AM\n")
        
        # Test validation
        results = self.processor.validate_csv_files(self.temp_dir)
        
        # Should find validation errors for invalid file
        self.assertIn("invalid.csv", results)
        self.assertGreater(len(results["invalid.csv"]), 0)
    
    def test_database_creation(self):
        """Test database creation and operations"""
        # Create test CSV files
        self._create_test_csv_files()
        
        # Create database
        self.processor.create_database()
        
        # Verify database was created
        self.assertTrue(os.path.exists(self.processor.db_path))
        
        # Test database operations
        conn = sqlite3.connect(self.processor.db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['time_slots', 'rooms', 'instructors', 'courses', 'sections', 'sessions']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def _create_test_csv_files(self):
        """Create test CSV files"""
        # Timeslots.csv
        timeslots_file = os.path.join(self.temp_dir, "Timeslots.csv")
        with open(timeslots_file, 'w', encoding='utf-8') as f:
            f.write("Day,StartTime,EndTime\n")
            f.write("Monday,09:00 AM,10:30 AM\n")
        
        # Rooms.csv
        rooms_file = os.path.join(self.temp_dir, "Rooms.csv")
        with open(rooms_file, 'w', encoding='utf-8') as f:
            f.write("RoomID,Type,Capacity,Type_of_spaces\n")
            f.write("Room1,Lecture,30,Classroom\n")
        
        # Instructors_data.csv
        instructors_file = os.path.join(self.temp_dir, "Instructors_data.csv")
        with open(instructors_file, 'w', encoding='utf-8') as f:
            f.write("InstructorID,Name,QualifiedCourses,Preference\n")
            f.write("1,John Doe,CSC111,Morning\n")
        
        # Groups.csv
        groups_file = os.path.join(self.temp_dir, "Groups.csv")
        with open(groups_file, 'w', encoding='utf-8') as f:
            f.write("SectionID,Semester,StudentCount\n")
            f.write("Level1_Group1,Fall 2025,30\n")
        
        # Sections.csv
        sections_file = os.path.join(self.temp_dir, "Sections.csv")
        with open(sections_file, 'w', encoding='utf-8') as f:
            f.write("Session_ID,Assigned_Course,Session_Type,Assigned_Section\n")
            f.write("SESS_001,CSC111,LAB,Level1_Group1\n")
        
        # Timetable.csv
        timetable_file = os.path.join(self.temp_dir, "Timetable.csv")
        with open(timetable_file, 'w', encoding='utf-8') as f:
            f.write("Courses,Course Code,Credits,Department,Type,Instructor(s)\n")
            f.write("Programming,CSC111,3,CSIT,LEC/LAB,John Doe\n")


class TestPerformance(unittest.TestCase):
    """Test system performance"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.csp = TimetableCSP()
        self._create_large_dataset()
    
    def _create_large_dataset(self):
        """Create a large dataset for performance testing"""
        # Create 50 time slots
        self.csp.time_slots = []
        for i in range(50):
            day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][i % 5]
            self.csp.time_slots.append(TimeSlot(day, "09:00 AM", "10:30 AM", i))
        
        # Create 100 rooms
        self.csp.rooms = []
        for i in range(100):
            room_type = "Lecture" if i % 2 == 0 else "Lab"
            self.csp.rooms.append(Room(f"Room{i}", room_type, 30, "Classroom"))
        
        # Create 50 instructors
        self.csp.instructors = []
        for i in range(50):
            self.csp.instructors.append(Instructor(f"{i}", f"Instructor{i}", ["CSC111"], "Any"))
        
        # Create 200 sessions
        self.csp.sessions = []
        for i in range(200):
            session_type = "LAB" if i % 3 == 0 else "TUT"
            self.csp.sessions.append(Session(f"SESS_{i}", "CSC111", session_type, f"Group{i%10}"))
    
    def test_csp_performance(self):
        """Test CSP solving performance"""
        # Build CSP model
        start_time = time.time()
        self.csp.build_csp_model()
        build_time = time.time() - start_time
        
        # Should build model quickly
        self.assertLess(build_time, 5.0, "CSP model building took too long")
        
        # Test solving performance
        start_time = time.time()
        success = self.csp.solve(max_iterations=1000)
        solve_time = time.time() - start_time
        
        # Should solve within reasonable time
        self.assertLess(solve_time, 30.0, "CSP solving took too long")
        
        if success:
            # Should have reasonable number of assignments
            self.assertGreater(len(self.csp.assignments), 0)
            self.assertLessEqual(len(self.csp.assignments), len(self.csp.sessions))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = DataProcessor()
        self.processor.data_dir = self.temp_dir
        self.processor.db_path = os.path.join(self.temp_dir, "integration_test.db")
        
        # Create comprehensive test data
        self._create_comprehensive_test_data()
    
    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Step 1: Validate data
        validation_results = self.processor.validate_csv_files(self.temp_dir)
        self.assertTrue(all(len(errors) == 0 for errors in validation_results.values()))
        
        # Step 2: Create database
        self.processor.create_database()
        self.assertTrue(os.path.exists(self.processor.db_path))
        
        # Step 3: Load data into CSP
        csp = TimetableCSP()
        csp.load_data_from_csv(self.temp_dir)
        
        # Verify data loaded correctly
        self.assertGreater(len(csp.time_slots), 0)
        self.assertGreater(len(csp.rooms), 0)
        self.assertGreater(len(csp.instructors), 0)
        self.assertGreater(len(csp.sessions), 0)
        
        # Step 4: Build CSP model
        csp.build_csp_model()
        self.assertGreater(len(csp.variables), 0)
        self.assertGreater(len(csp.domains), 0)
        
        # Step 5: Solve CSP
        success = csp.solve(max_iterations=2000)
        
        if success:
            # Step 6: Save results
            self.processor.save_timetable_to_db(csp.assignments, {}, csp)
            
            # Step 7: Verify results
            timetable_data = self.processor.get_timetable_from_db()
            self.assertGreater(len(timetable_data), 0)
    
    def _create_comprehensive_test_data(self):
        """Create comprehensive test data for integration testing"""
        # Timeslots.csv
        timeslots_file = os.path.join(self.temp_dir, "Timeslots.csv")
        with open(timeslots_file, 'w', encoding='utf-8') as f:
            f.write("Day,StartTime,EndTime\n")
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                for hour in range(9, 16):
                    f.write(f"{day},{hour:02d}:00 AM,{hour+1:02d}:30 AM\n")
        
        # Rooms.csv
        rooms_file = os.path.join(self.temp_dir, "Rooms.csv")
        with open(rooms_file, 'w', encoding='utf-8') as f:
            f.write("RoomID,Type,Capacity,Type_of_spaces\n")
            for i in range(20):
                room_type = "Lecture" if i % 2 == 0 else "Lab"
                f.write(f"Room{i},{room_type},30,Classroom\n")
        
        # Instructors_data.csv
        instructors_file = os.path.join(self.temp_dir, "Instructors_data.csv")
        with open(instructors_file, 'w', encoding='utf-8') as f:
            f.write("InstructorID,Name,QualifiedCourses,Preference\n")
            for i in range(10):
                f.write(f"{i},Instructor{i},CSC111,Any\n")
        
        # Groups.csv
        groups_file = os.path.join(self.temp_dir, "Groups.csv")
        with open(groups_file, 'w', encoding='utf-8') as f:
            f.write("SectionID,Semester,StudentCount\n")
            for i in range(5):
                f.write(f"Group{i},Fall 2025,30\n")
        
        # Sections.csv
        sections_file = os.path.join(self.temp_dir, "Sections.csv")
        with open(sections_file, 'w', encoding='utf-8') as f:
            f.write("Session_ID,Assigned_Course,Session_Type,Assigned_Section\n")
            for i in range(30):
                session_type = "LAB" if i % 3 == 0 else "TUT"
                f.write(f"SESS_{i},CSC111,{session_type},Group{i%5}\n")
        
        # Timetable.csv
        timetable_file = os.path.join(self.temp_dir, "Timetable.csv")
        with open(timetable_file, 'w', encoding='utf-8') as f:
            f.write("Courses,Course Code,Credits,Department,Type,Instructor(s)\n")
            f.write("Programming,CSC111,3,CSIT,LEC/LAB,Instructor0\n")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        csp = TimetableCSP()
        
        # Test with empty data
        csp.time_slots = []
        csp.rooms = []
        csp.instructors = []
        csp.sessions = []
        
        # Should handle empty data gracefully
        csp.build_csp_model()
        self.assertEqual(len(csp.variables), 0)
        self.assertEqual(len(csp.domains), 0)
    
    def test_malformed_csv_handling(self):
        """Test handling of malformed CSV files"""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create malformed CSV
            malformed_file = os.path.join(temp_dir, "malformed.csv")
            with open(malformed_file, 'w', encoding='utf-8') as f:
                f.write("Invalid,CSV,Content\n")
                f.write("Missing,Columns\n")
            
            processor = DataProcessor()
            processor.data_dir = temp_dir
            
            # Should handle malformed CSV gracefully
            results = processor.validate_csv_files(temp_dir)
            self.assertIn("malformed.csv", results)
            self.assertGreater(len(results["malformed.csv"]), 0)
        
        finally:
            shutil.rmtree(temp_dir)


def run_performance_benchmark():
    """Run performance benchmark tests"""
    print("Running Performance Benchmark...")
    
    # Test with different dataset sizes
    sizes = [50, 100, 200, 500]
    
    for size in sizes:
        print(f"\nTesting with {size} sessions...")
        
        csp = TimetableCSP()
        
        # Create test data
        csp.time_slots = [TimeSlot("Monday", "09:00 AM", "10:30 AM", i) for i in range(20)]
        csp.rooms = [Room(f"Room{i}", "Lecture", 30, "Classroom") for i in range(20)]
        csp.instructors = [Instructor(f"{i}", f"Instructor{i}", ["CSC111"], "Any") for i in range(10)]
        csp.sessions = [Session(f"SESS_{i}", "CSC111", "TUT", f"Group{i%5}") for i in range(size)]
        
        # Measure performance
        start_time = time.time()
        csp.build_csp_model()
        build_time = time.time() - start_time
        
        start_time = time.time()
        success = csp.solve(max_iterations=1000)
        solve_time = time.time() - start_time
        
        print(f"  Build time: {build_time:.3f}s")
        print(f"  Solve time: {solve_time:.3f}s")
        print(f"  Success: {success}")
        if success:
            print(f"  Sessions scheduled: {len(csp.assignments)}")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
    
    # Run performance benchmark
    run_performance_benchmark()
