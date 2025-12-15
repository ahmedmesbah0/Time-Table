"""
Automated Timetable Generation using Constraint Satisfaction Problem (CSP)
Intelligent Systems Fall 2025/2026 - Project 1

This program generates timetables for the CSIT department by treating it as a CSP.
It assigns each class session to a time slot, room, and instructor while satisfying
all the scheduling constraints.
"""

import csv
import pandas as pd
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, time
import random
import copy
from collections import defaultdict
import json


@dataclass
class TimeSlot:
    """Represents a time slot in the timetable"""
    day: str
    start_time: str
    end_time: str
    slot_id: int
    
    def __str__(self):
        return f"{self.day} {self.start_time}-{self.end_time}"


@dataclass
class Room:
    """Represents a room with its properties"""
    room_id: str
    room_type: str  # Lecture, Lab
    capacity: int
    space_type: str
    
    def __str__(self):
        return f"{self.room_id} ({self.room_type}, {self.capacity})"


@dataclass
class Instructor:
    """Represents an instructor with their qualifications and preferences"""
    instructor_id: str
    name: str
    qualified_courses: List[str]
    preference: str  # Morning, Afternoon, No_Thursday, Any
    
    def __str__(self):
        return f"{self.name} (ID: {self.instructor_id})"


@dataclass
class Course:
    """Represents a course with its requirements"""
    course_id: str
    course_name: str
    credits: int
    department: str
    course_type: str  # LEC, LAB, TUT, etc.
    instructors: List[str]
    
    def __str__(self):
        return f"{self.course_id}: {self.course_name}"


@dataclass
class Section:
    """Represents a section/group of students"""
    section_id: str
    semester: str
    student_count: int
    
    def __str__(self):
        return f"{self.section_id} ({self.student_count} students)"


@dataclass
class Session:
    """Represents a teaching session that needs to be scheduled"""
    session_id: str
    course_id: str
    session_type: str  # LAB, TUT, LEC
    section_id: str
    
    def __str__(self):
        return f"{self.session_id}: {self.course_id} {self.session_type} for {self.section_id}"


@dataclass
class Assignment:
    """Represents an assignment of a session to time slot, room, and instructor"""
    session: Session
    time_slot: TimeSlot
    room: Room
    instructor: Instructor
    
    def __str__(self):
        return f"{self.session} -> {self.time_slot} in {self.room} with {self.instructor.name}"


class TimetableCSP:
    """
    Constraint Satisfaction Problem for Timetable Generation
    
    Variables: Each session that needs to be scheduled
    Domains: All possible combinations of (time_slot, room, instructor)
    Constraints: Hard and soft constraints for valid scheduling
    """
    
    def __init__(self):
        self.sessions: List[Session] = []
        self.time_slots: List[TimeSlot] = []
        self.rooms: List[Room] = []
        self.instructors: List[Instructor] = []
        self.courses: List[Course] = []
        self.sections: List[Section] = []
        
        # CSP Variables and Domains
        self.variables: List[Session] = []
        self.domains: Dict[str, List[Tuple[TimeSlot, Room, Instructor]]] = {}
        self.assignments: Dict[str, Tuple[TimeSlot, Room, Instructor]] = {}
        
        # Constraint tracking
        self.constraint_violations: List[str] = []
        self.soft_constraint_violations: List[str] = []
        
    def load_data_from_csv(self, data_dir: str = "data"):
        """Load all data from CSV files"""
        print("Loading data from CSV files...")
        
        try:
            # Load time slots
            self._load_time_slots(f"{data_dir}/Timeslots.csv")
            
            # Load rooms
            self._load_rooms(f"{data_dir}/Rooms.csv")
            
            # Load instructors
            self._load_instructors(f"{data_dir}/Instructors_data.csv")
            
            # Load courses (from Timetable.csv)
            self._load_courses(f"{data_dir}/Timetable.csv")
            
            # Load sections
            self._load_sections(f"{data_dir}/Groups.csv")
            
            # Load sessions (from Sections.csv - this contains the actual sessions to schedule)
            self._load_sessions(f"{data_dir}/Sections.csv")
            
            print(f"Loaded {len(self.time_slots)} time slots, {len(self.rooms)} rooms, "
                  f"{len(self.instructors)} instructors, {len(self.courses)} courses, "
                  f"{len(self.sections)} sections, {len(self.sessions)} sessions")
            
        except Exception as e:
            print(f"Error loading data from CSV files: {str(e)}")
            raise
    
    def _load_time_slots(self, filename: str):
        """Load time slots from CSV"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                time_slot = TimeSlot(
                    day=row['Day'],
                    start_time=row['StartTime'],
                    end_time=row['EndTime'],
                    slot_id=i
                )
                self.time_slots.append(time_slot)
    
    def _load_rooms(self, filename: str):
        """Load rooms from CSV"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['RoomID']:  # Skip empty rows
                    room = Room(
                        room_id=row['RoomID'],
                        room_type=row['Type'],
                        capacity=int(row['Capacity']),
                        space_type=row['Type_of_spaces']
                    )
                    self.rooms.append(room)
    
    def _load_instructors(self, filename: str):
        """Load instructors from CSV"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['InstructorID']:  # Skip empty rows
                    # Parse qualified courses (comma-separated)
                    qualified_courses = [course.strip() for course in row['QualifiedCourses'].split(',')]
                    
                    instructor = Instructor(
                        instructor_id=row['InstructorID'],
                        name=row['Name'],
                        qualified_courses=qualified_courses,
                        preference=row['Preference']
                    )
                    self.instructors.append(instructor)
    
    def _load_courses(self, filename: str):
        """Load courses from CSV"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Course Code']:  # Skip empty rows
                    # Parse instructors (comma-separated)
                    instructors = [instructor.strip() for instructor in row['Instructor(s)'].split(',')]
                    
                    course = Course(
                        course_id=row['Course Code'],
                        course_name=row['Courses'],
                        credits=int(row['Credits']),
                        department=row['Department'],
                        course_type=row['Type'],
                        instructors=instructors
                    )
                    self.courses.append(course)
    
    def _load_sections(self, filename: str):
        """Load sections from CSV"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['SectionID']:  # Skip empty rows
                    section = Section(
                        section_id=row['SectionID'],
                        semester=row['Semester'],
                        student_count=int(row['StudentCount'])
                    )
                    self.sections.append(section)
    
    def _load_sessions(self, filename: str):
        """Load sessions from CSV (this is the actual data from Sections.csv)"""
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Session_ID']:  # Skip empty rows
                    session = Session(
                        session_id=row['Session_ID'],
                        course_id=row['Assigned_Course'],
                        session_type=row['Session_Type'],
                        section_id=row['Assigned_Section']
                    )
                    self.sessions.append(session)
    
    def build_csp_model(self):
        """Build the CSP model with variables, domains, and constraints"""
        print("Building CSP model...")
        
        # Set variables (all sessions that need to be scheduled)
        self.variables = self.sessions.copy()
        
        # Build domains for each variable
        self._build_domains()
        
        print(f"Built CSP model with {len(self.variables)} variables")
        print(f"Average domain size: {sum(len(domain) for domain in self.domains.values()) / len(self.domains) if self.domains else 0:.1f}")
    
    def _build_domains(self):
        """Build domains for each variable (session)"""
        for session in self.variables:
            domain = []
            
            # Find the course for this session - try exact match first, then partial match
            course = next((c for c in self.courses if c.course_id == session.course_id), None)
            
            # If no exact match, try to find a course that contains this course code
            if not course:
                course = next((c for c in self.courses if session.course_id in c.course_id), None)
            
            # If still no match, create a dummy course for this session
            if not course:
                print(f"Warning: Course {session.course_id} not found, creating dummy course")
                course = Course(
                    course_id=session.course_id,
                    course_name=f"Dummy Course {session.course_id}",
                    credits=3,
                    department="Unknown",
                    course_type="LEC/LAB",
                    instructors=[]
                )
                self.courses.append(course)
            
            # Find qualified instructors for this course
            qualified_instructors = []
            for instructor in self.instructors:
                # Check if instructor is qualified for this course
                if (course.course_id in instructor.qualified_courses or 
                    any(course.course_id in course_code for course_code in instructor.qualified_courses)):
                    qualified_instructors.append(instructor)
            
            # If no qualified instructors found, use all instructors as fallback
            if not qualified_instructors:
                print(f"Warning: No qualified instructors found for course {course.course_id}, using all instructors")
                qualified_instructors = self.instructors
            
            # Find suitable rooms based on session type
            suitable_rooms = []
            for room in self.rooms:
                if self._is_room_suitable(session, room):
                    suitable_rooms.append(room)
            
            if not suitable_rooms:
                print(f"Warning: No suitable rooms found for session {session.session_id}")
                continue
            
            # Generate all valid combinations
            for time_slot in self.time_slots:
                for room in suitable_rooms:
                    for instructor in qualified_instructors:
                        domain.append((time_slot, room, instructor))
            
            self.domains[session.session_id] = domain
    
    def _is_room_suitable(self, session: Session, room: Room) -> bool:
        """Check if a room is suitable for a session"""
        # Lab sessions need Lab rooms
        if session.session_type == "LAB" and room.room_type != "Lab":
            return False
        
        # Lecture/TUT sessions can use Lecture rooms
        if session.session_type in ["TUT", "LEC"] and room.room_type != "Lecture":
            return False
        
        return True
    
    def solve(self, max_iterations: int = 1000) -> bool:
        """
        Solve the CSP using backtracking algorithm
        """
        print("Starting CSP solving...")
        start_time = datetime.now()
        
        # Initialize assignments
        self.assignments = {}
        self.constraint_violations = []
        self.soft_constraint_violations = []
    
        # Use backtracking to find a solution
        success = self._backtrack(0, max_iterations)
        
        end_time = datetime.now()
        solving_time = (end_time - start_time).total_seconds()
        
        if success:
            print(f"Solution found in {solving_time:.2f} seconds!")
            print(f"Hard violations: {len(self.constraint_violations)}, Soft violations: {len(self.soft_constraint_violations)}")
        else:
            print(f"No solution found after {solving_time:.2f} seconds.")
            print(f"Hard violations: {len(self.constraint_violations)}")
        
        return success
    
    def _backtrack(self, variable_index: int, max_iterations: int) -> bool:
        """Recursive backtracking algorithm"""
        if variable_index >= len(self.variables):
            return True  # All variables assigned
        
        if max_iterations <= 0:
            return False  # Max iterations reached
        
        session = self.variables[variable_index]
        
        # Try each value in the domain
        domain = self.domains.get(session.session_id, [])
        random.shuffle(domain)  # Randomize for better exploration
        
        for time_slot, room, instructor in domain:
            # Check if this assignment violates hard constraints
            if self._check_hard_constraints(session, time_slot, room, instructor):
                # Make assignment
                self.assignments[session.session_id] = (time_slot, room, instructor)
                
                # Recursively solve remaining variables
                if self._backtrack(variable_index + 1, max_iterations - 1):
                    return True
                
                # Backtrack
                del self.assignments[session.session_id]
        
        return False
    
    def _check_hard_constraints(self, session: Session, time_slot: TimeSlot, 
                              room: Room, instructor: Instructor) -> bool:
        """Check hard constraints for a potential assignment"""
        
        # Constraint 1: No instructor can teach more than one class at the same time
        for assigned_session_id, (assigned_time, assigned_room, assigned_instructor) in self.assignments.items():
            if (assigned_instructor.instructor_id == instructor.instructor_id and 
                assigned_time.slot_id == time_slot.slot_id):
                self.constraint_violations.append(
                    f"Instructor {instructor.name} double-booked at {time_slot}"
                )
                return False
        
        # Constraint 2: No room can host more than one class at the same time
        for assigned_session_id, (assigned_time, assigned_room, assigned_instructor) in self.assignments.items():
            if (assigned_room.room_id == room.room_id and 
                assigned_time.slot_id == time_slot.slot_id):
                self.constraint_violations.append(
                    f"Room {room.room_id} double-booked at {time_slot}"
                )
                return False
        
        # Constraint 3: Room capacity must be sufficient
        section = next((s for s in self.sections if s.section_id == session.section_id), None)
        if section and room.capacity < section.student_count:
            self.constraint_violations.append(
                f"Room {room.room_id} capacity {room.capacity} insufficient for section {section.section_id} ({section.student_count} students)"
            )
            return False
        
        # Constraint 4: Room type must match session type
        if not self._is_room_suitable(session, room):
            self.constraint_violations.append(
                f"Room {room.room_id} type {room.room_type} unsuitable for session type {session.session_type}"
            )
            return False
        
        return True
    
    def evaluate_soft_constraints(self):
        """Evaluate soft constraints for the current assignment"""
        self.soft_constraint_violations = []
        
        for session_id, (time_slot, room, instructor) in self.assignments.items():
            # Find the session object
            session = next((s for s in self.variables if s.session_id == session_id), None)
            if not session:
                continue
                
            # Soft constraint 1: Avoid early morning slots (before 10 AM)
            if time_slot.start_time in ["09:00 AM", "09:45 AM"]:
                self.soft_constraint_violations.append(
                    f"Early morning slot for {session.session_id} at {time_slot}"
                )
            
            # Soft constraint 2: Avoid late evening slots (after 3 PM)
            if time_slot.start_time in ["02:15 PM", "03:00 PM"]:
                self.soft_constraint_violations.append(
                    f"Late evening slot for {session.session_id} at {time_slot}"
                )
            
            # Soft constraint 3: Respect instructor preferences
            if instructor.preference == "Morning" and time_slot.start_time in ["02:15 PM", "03:00 PM"]:
                self.soft_constraint_violations.append(
                    f"Instructor {instructor.name} prefers morning but assigned to {time_slot}"
                )
            elif instructor.preference == "Afternoon" and time_slot.start_time in ["09:00 AM", "09:45 AM"]:
                self.soft_constraint_violations.append(
                    f"Instructor {instructor.name} prefers afternoon but assigned to {time_slot}"
                )
            elif instructor.preference == "No_Thursday" and time_slot.day == "Thursday":
                self.soft_constraint_violations.append(
                    f"Instructor {instructor.name} prefers no Thursday but assigned to {time_slot}"
                )
    
    def get_timetable_summary(self) -> Dict[str, Any]:
        """Get a summary of the generated timetable"""
        if not self.assignments:
            return {"error": "No timetable generated"}
        
        summary = {
            "total_sessions": len(self.assignments),
            "hard_constraint_violations": len(self.constraint_violations),
            "soft_constraint_violations": len(self.soft_constraint_violations),
            "sessions_by_day": defaultdict(int),
            "sessions_by_time": defaultdict(int),
            "room_utilization": defaultdict(int),
            "instructor_load": defaultdict(int),
            "assignments": []
        }
        
        for session_id, (time_slot, room, instructor) in self.assignments.items():
            # Find the session object
            session = next((s for s in self.variables if s.session_id == session_id), None)
            if not session:
                continue
                
            summary["sessions_by_day"][time_slot.day] += 1
            summary["sessions_by_time"][time_slot.start_time] += 1
            summary["room_utilization"][room.room_id] += 1
            summary["instructor_load"][instructor.name] += 1
            
            summary["assignments"].append({
                "session_id": session.session_id,
                "course": session.course_id,
                "type": session.session_type,
                "section": session.section_id,
                "day": time_slot.day,
                "time": f"{time_slot.start_time}-{time_slot.end_time}",
                "room": room.room_id,
                "instructor": instructor.name
            })
        
        return summary
    
    def export_timetable_to_csv(self, filename: str = "output/generated_timetable.csv"):
        """Export the generated timetable to CSV"""
        if not self.assignments:
            print("No timetable to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Session_ID', 'Course', 'Session_Type', 'Section', 
                'Day', 'Start_Time', 'End_Time', 'Room', 'Instructor'
            ])
            
            for session_id, (time_slot, room, instructor) in self.assignments.items():
                # Find the session object
                session = next((s for s in self.variables if s.session_id == session_id), None)
                if not session:
                    continue
                    
                writer.writerow([
                    session.session_id,
                    session.course_id,
                    session.session_type,
                    session.section_id,
                    time_slot.day,
                    time_slot.start_time,
                    time_slot.end_time,
                    room.room_id,
                    instructor.name
                ])
        
        print(f"Timetable exported to {filename}")
    
    def print_timetable(self):
        """Print the generated timetable in a readable format"""
        if not self.assignments:
            print("No timetable generated")
            return
        
        print("\n" + "="*80)
        print("GENERATED TIMETABLE")
        print("="*80)
        
        # Group by day
        by_day = defaultdict(list)
        for session_id, (time_slot, room, instructor) in self.assignments.items():
            # Find the session object
            session = next((s for s in self.variables if s.session_id == session_id), None)
            if not session:
                continue
            by_day[time_slot.day].append((session, time_slot, room, instructor))
        
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        for day in days:
            if day in by_day:
                print(f"\n{day.upper()}")
                print("-" * 40)
                
                # Sort by time
                sessions_today = sorted(by_day[day], key=lambda x: x[1].start_time)
                
                for session, time_slot, room, instructor in sessions_today:
                    print(f"{time_slot.start_time}-{time_slot.end_time} | "
                          f"{room.room_id:15} | {session.course_id:8} | "
                          f"{session.session_type:3} | {session.section_id:20} | "
                          f"{instructor.name}")
        
        print(f"\nTotal sessions scheduled: {len(self.assignments)}")
        print(f"Hard constraint violations: {len(self.constraint_violations)}")
        print(f"Soft constraint violations: {len(self.soft_constraint_violations)}")


def main():
    """Main function to demonstrate the CSP timetable generator"""
    print("Automated Timetable Generation as CSP")
    print("=" * 50)
    
    # Create CSP instance
    csp = TimetableCSP()
    
    # Load data
    csp.load_data_from_csv()
    
    # Build CSP model
    csp.build_csp_model()
    
    # Solve the CSP
    success = csp.solve(max_iterations=5000)
    
    if success:
        # Evaluate soft constraints
        csp.evaluate_soft_constraints()
        
        # Print results
        csp.print_timetable()
        
        # Export to CSV
        csp.export_timetable_to_csv()
        
        # Get summary
        summary = csp.get_timetable_summary()
        print(f"\nTimetable Summary:")
        print(f"- Total sessions: {summary['total_sessions']}")
        print(f"- Hard violations: {summary['hard_constraint_violations']}")
        print(f"- Soft violations: {summary['soft_constraint_violations']}")
        
    else:
        print("Failed to generate a valid timetable")
        if csp.constraint_violations:
            print("\nConstraint violations encountered:")
            for violation in csp.constraint_violations[:10]:  # Show first 10
                print(f"- {violation}")


if __name__ == "__main__":
    main()
