"""
Data Processing Module for Timetable Generation System
Handles CSV/database integration and data validation
"""

import csv
import pandas as pd
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class DataProcessor:
    """Handles data loading, validation, and export for the timetable system"""
    
    def __init__(self):
        self.data_dir = "."
        self.db_path = "timetable.db"
        
    def validate_csv_files(self, data_dir: str = ".") -> Dict[str, List[str]]:
        """Validate CSV files for required columns and data integrity"""
        validation_results = {}
        
        required_files = {
            "Timeslots.csv": ["Day", "StartTime", "EndTime"],
            "Rooms.csv": ["RoomID", "Type", "Capacity", "Type_of_spaces"],
            "Instructors_data.csv": ["InstructorID", "Name", "QualifiedCourses", "Preference"],
            "Groups.csv": ["SectionID", "Semester", "StudentCount"],
            "Sections.csv": ["Session_ID", "Assigned_Course", "Session_Type", "Assigned_Section"],
            "Timetable.csv": ["Courses", "Course Code", "Credits", "Department", "Type", "Instructor(s)"]
        }
        
        for filename, required_columns in required_files.items():
            filepath = Path(data_dir) / filename
            errors = []
            
            if not filepath.exists():
                errors.append(f"File {filename} not found")
                validation_results[filename] = errors
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    headers = reader.fieldnames
                    
                    # Check required columns
                    for col in required_columns:
                        if col not in headers:
                            errors.append(f"Missing required column: {col}")
                    
                    # Check for empty rows
                    row_count = 0
                    for row in reader:
                        row_count += 1
                        # Check for empty required fields
                        for col in required_columns:
                            if col in headers and not row.get(col, '').strip():
                                errors.append(f"Empty {col} in row {row_count}")
                    
                    if row_count == 0:
                        errors.append("No data rows found")
                    
            except Exception as e:
                errors.append(f"Error reading file: {str(e)}")
            
            validation_results[filename] = errors
        
        return validation_results
    
    def create_database(self, data_dir: str = "."):
        """Create SQLite database from CSV files"""
        print("Creating SQLite database...")
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        self._create_tables(cursor)
        
        # Load data from CSV files
        self._load_csv_to_db(cursor, data_dir)
        
        conn.commit()
        conn.close()
        print(f"Database created: {self.db_path}")
    
    def _create_tables(self, cursor):
        """Create database tables"""
        
        # Time slots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_slots (
                slot_id INTEGER PRIMARY KEY,
                day TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            )
        ''')
        
        # Rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                room_id TEXT PRIMARY KEY,
                room_type TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                space_type TEXT NOT NULL
            )
        ''')
        
        # Instructors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instructors (
                instructor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                qualified_courses TEXT NOT NULL,
                preference TEXT NOT NULL
            )
        ''')
        
        # Courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                credits INTEGER NOT NULL,
                department TEXT NOT NULL,
                course_type TEXT NOT NULL,
                instructors TEXT NOT NULL
            )
        ''')
        
        # Sections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                section_id TEXT PRIMARY KEY,
                semester TEXT NOT NULL,
                student_count INTEGER NOT NULL
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                course_id TEXT NOT NULL,
                session_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                FOREIGN KEY (course_id) REFERENCES courses (course_id),
                FOREIGN KEY (section_id) REFERENCES sections (section_id)
            )
        ''')
        
        # Generated timetable table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                session_type TEXT NOT NULL,
                section_id TEXT NOT NULL,
                day TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                room_id TEXT NOT NULL,
                instructor_id TEXT NOT NULL,
                generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (room_id) REFERENCES rooms (room_id),
                FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id)
            )
        ''')
    
    def _load_csv_to_db(self, cursor, data_dir: str):
        """Load data from CSV files to database"""
        
        # Load time slots
        self._load_time_slots_to_db(cursor, f"{data_dir}/Timeslots.csv")
        
        # Load rooms
        self._load_rooms_to_db(cursor, f"{data_dir}/Rooms.csv")
        
        # Load instructors
        self._load_instructors_to_db(cursor, f"{data_dir}/Instructors_data.csv")
        
        # Load courses
        self._load_courses_to_db(cursor, f"{data_dir}/Timetable.csv")
        
        # Load sections
        self._load_sections_to_db(cursor, f"{data_dir}/Groups.csv")
        
        # Load sessions
        self._load_sessions_to_db(cursor, f"{data_dir}/Sections.csv")
    
    def _load_time_slots_to_db(self, cursor, filename: str):
        """Load time slots to database"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                cursor.execute('''
                    INSERT OR REPLACE INTO time_slots 
                    (slot_id, day, start_time, end_time)
                    VALUES (?, ?, ?, ?)
                ''', (i, row['Day'], row['StartTime'], row['EndTime']))
    
    def _load_rooms_to_db(self, cursor, filename: str):
        """Load rooms to database"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['RoomID']:  # Skip empty rows
                    cursor.execute('''
                        INSERT OR REPLACE INTO rooms 
                        (room_id, room_type, capacity, space_type)
                        VALUES (?, ?, ?, ?)
                    ''', (row['RoomID'], row['Type'], int(row['Capacity']), row['Type_of_spaces']))
    
    def _load_instructors_to_db(self, cursor, filename: str):
        """Load instructors to database"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['InstructorID']:  # Skip empty rows
                    cursor.execute('''
                        INSERT OR REPLACE INTO instructors 
                        (instructor_id, name, qualified_courses, preference)
                        VALUES (?, ?, ?, ?)
                    ''', (row['InstructorID'], row['Name'], row['QualifiedCourses'], row['Preference']))
    
    def _load_courses_to_db(self, cursor, filename: str):
        """Load courses to database"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Course Code']:  # Skip empty rows
                    cursor.execute('''
                        INSERT OR REPLACE INTO courses 
                        (course_id, course_name, credits, department, course_type, instructors)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (row['Course Code'], row['Courses'], int(row['Credits']), 
                          row['Department'], row['Type'], row['Instructor(s)']))
    
    def _load_sections_to_db(self, cursor, filename: str):
        """Load sections to database"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['SectionID']:  # Skip empty rows
                    cursor.execute('''
                        INSERT OR REPLACE INTO sections 
                        (section_id, semester, student_count)
                        VALUES (?, ?, ?)
                    ''', (row['SectionID'], row['Semester'], int(row['StudentCount'])))
    
    def _load_sessions_to_db(self, cursor, filename: str):
        """Load sessions to database"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Session_ID']:  # Skip empty rows
                    cursor.execute('''
                        INSERT OR REPLACE INTO sessions 
                        (session_id, course_id, session_type, section_id)
                        VALUES (?, ?, ?, ?)
                    ''', (row['Session_ID'], row['Assigned_Course'], 
                          row['Session_Type'], row['Assigned_Section']))
    
    def save_timetable_to_db(self, assignments: Dict, generation_info: Dict, csp=None):
        """Save generated timetable to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear previous timetable
        cursor.execute('DELETE FROM generated_timetable')
        
        # Insert new timetable
        for session_id, (time_slot, room, instructor) in assignments.items():
            # Find the session object
            if csp:
                session = next((s for s in csp.variables if s.session_id == session_id), None)
            else:
                # Create a dummy session if CSP not provided
                session = type('Session', (), {
                    'session_id': session_id,
                    'course_id': 'Unknown',
                    'session_type': 'Unknown',
                    'section_id': 'Unknown'
                })()
            
            if not session:
                continue
                
            cursor.execute('''
                INSERT INTO generated_timetable 
                (session_id, course_id, session_type, section_id, day, 
                 start_time, end_time, room_id, instructor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session.session_id, session.course_id, session.session_type,
                  session.section_id, time_slot.day, time_slot.start_time,
                  time_slot.end_time, room.room_id, instructor.instructor_id))
        
        conn.commit()
        conn.close()
        print("Timetable saved to database")
    
    def get_timetable_from_db(self) -> List[Dict]:
        """Retrieve timetable from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, course_id, session_type, section_id,
                   day, start_time, end_time, room_id, instructor_id,
                   generation_date
            FROM generated_timetable
            ORDER BY day, start_time
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'session_id': row[0],
                'course_id': row[1],
                'session_type': row[2],
                'section_id': row[3],
                'day': row[4],
                'start_time': row[5],
                'end_time': row[6],
                'room_id': row[7],
                'instructor_id': row[8],
                'generation_date': row[9]
            })
        
        conn.close()
        return results
    
    def export_timetable_to_excel(self, filename: str = "timetable.xlsx"):
        """Export timetable to Excel file"""
        timetable_data = self.get_timetable_from_db()
        
        if not timetable_data:
            print("No timetable data to export")
            return
        
        df = pd.DataFrame(timetable_data)
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main timetable sheet
            df.to_excel(writer, sheet_name='Timetable', index=False)
            
            # Summary sheet
            summary_data = self._create_summary_data(timetable_data)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Timetable exported to {filename}")
    
    def _create_summary_data(self, timetable_data: List[Dict]) -> List[Dict]:
        """Create summary data for Excel export"""
        summary = []
        
        # Count by day
        day_counts = {}
        for entry in timetable_data:
            day = entry['day']
            day_counts[day] = day_counts.get(day, 0) + 1
        
        for day, count in day_counts.items():
            summary.append({'Category': 'Sessions by Day', 'Item': day, 'Count': count})
        
        # Count by room
        room_counts = {}
        for entry in timetable_data:
            room = entry['room_id']
            room_counts[room] = room_counts.get(room, 0) + 1
        
        for room, count in room_counts.items():
            summary.append({'Category': 'Room Utilization', 'Item': room, 'Count': count})
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the current data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        tables = ['time_slots', 'rooms', 'instructors', 'courses', 'sections', 'sessions']
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[f'{table}_count'] = cursor.fetchone()[0]
        
        # Room utilization
        cursor.execute('''
            SELECT room_id, COUNT(*) as usage_count
            FROM generated_timetable
            GROUP BY room_id
            ORDER BY usage_count DESC
        ''')
        stats['room_utilization'] = dict(cursor.fetchall())
        
        # Instructor workload
        cursor.execute('''
            SELECT instructor_id, COUNT(*) as session_count
            FROM generated_timetable
            GROUP BY instructor_id
            ORDER BY session_count DESC
        ''')
        stats['instructor_workload'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def backup_data(self, backup_dir: str = "backups"):
        """Create backup of current data"""
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup database
        backup_db_path = backup_path / f"timetable_backup_{timestamp}.db"
        import shutil
        shutil.copy2(self.db_path, backup_db_path)
        
        # Backup CSV files
        csv_files = ["Timeslots.csv", "Rooms.csv", "Instructors_data.csv", 
                     "Sections.csv", "Timetable.csv"]
        
        for csv_file in csv_files:
            if Path(csv_file).exists():
                backup_csv_path = backup_path / f"{csv_file}_{timestamp}"
                shutil.copy2(csv_file, backup_csv_path)
        
        print(f"Backup created in {backup_dir}")
        return backup_path


def main():
    """Demonstrate data processing functionality"""
    processor = DataProcessor()
    
    # Validate CSV files
    print("Validating CSV files...")
    validation_results = processor.validate_csv_files()
    
    for filename, errors in validation_results.items():
        if errors:
            print(f"{filename}: {errors}")
        else:
            print(f"{filename}: OK")
    
    # Create database
    processor.create_database()
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
