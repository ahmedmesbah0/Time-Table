# CSIT Timetable Generator

This project automatically generates class timetables for the CSIT department using a Constraint Satisfaction Problem (CSP) approach.

## What it does

The program takes information about courses, rooms, instructors, and time slots, then automatically creates a timetable that satisfies all the scheduling constraints like:
- No instructor teaches two classes at the same time
- No room is double-booked
- Each section gets the right courses
- Room capacities match student counts

## Requirements

Install the required packages:

```bash
# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** Always activate the virtual environment with `source venv/bin/activate` before running the project.

## How to run

### Using the Web Interface (Recommended)

```bash
streamlit run timetable_ui.py
```

This opens a web interface where you can:
- Upload and view your CSV data files
- Generate timetables
- View and export results

### Using Python directly

```python
from csp_timetable import TimetableCSP

# Create and load data
csp = TimetableCSP()
csp.load_data_from_csv(".")

# Build the problem
csp.build_csp_model()

# Solve it
solution = csp.solve(max_iterations=5000)

if solution:
    csp.export_timetable_to_csv("generated_timetable.csv")
    print("Timetable generated successfully!")
```

## Input Files

The program needs these CSV files in the `data/` directory:

- `Timeslots.csv` - Available time slots (day, start time, end time)
- `Rooms.csv` - Available rooms and their capacities
- `Instructors_data.csv` - Instructor names and what they can teach
- `Groups.csv` - Student groups/sections
- `Sections.csv` - Classes that need to be scheduled
- `Timetable.csv` - Course information

## Project Structure

```
Time-Table/
├── data/                    # Input CSV files
│   ├── Timeslots.csv
│   ├── Rooms.csv
│   ├── Instructors_data.csv
│   ├── Groups.csv
│   ├── Sections.csv
│   └── Timetable.csv
├── output/                  # Generated files (auto-created)
│   ├── generated_timetable.csv
│   ├── timetable.db
│   └── timetable.xlsx
├── tests/                   # Test files
│   └── test_suite.py
├── csp_timetable.py        # Main CSP solver
├── data_processor.py       # Data handling
├── timetable_ui.py         # Streamlit web interface
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Running Tests

```bash
python3 tests/test_suite.py
```

## How it works

The program uses a backtracking algorithm to assign each class to a time slot, room, and instructor. It checks all the constraints at each step and backtracks when it hits a dead end. This continues until it finds a valid complete schedule or determines no solution exists.

## Notes

- The solver might take a few minutes for large datasets
- If no solution is found, try adjusting the constraints or adding more resources (rooms, time slots)
- Generated timetables are saved to `generated_timetable.csv` and also stored in the `timetable.db` SQLite database

## Course Project

This was developed as Project 1 for the Intelligent Systems course (Fall 2025/2026) at the CSIT department.
