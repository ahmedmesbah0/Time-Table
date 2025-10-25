# CSIT Automated Timetable Generation System

## Intelligent Systems Fall 2025/2026 - Project 1

This project implements an automated timetable generation system for the CSIT department using Constraint Satisfaction Problem (CSP) techniques.

## 🎯 Project Overview

The system automatically constructs feasible timetables that meet all defined constraints by modeling timetable generation as a CSP problem with:

- **Variables**: Each lecture/session that needs to be scheduled
- **Domains**: Available time slots × available rooms × available instructors  
- **Constraints**: Hard constraints (must be satisfied) and soft constraints (preferred)

## 🚀 Features

### Core Functionality
- ✅ CSP-based scheduling algorithm using backtracking
- ✅ Hard constraint enforcement (no conflicts, capacity limits)
- ✅ Soft constraint optimization (preferences, workload balance)
- ✅ Dynamic data management (CSV/database integration)
- ✅ Performance evaluation and metrics
- ✅ Interactive web-based user interface

### Hard Constraints (Must be satisfied)
1. No professor can teach more than one class at the same time
2. No room can host more than one class at the same time
3. Room capacity must be sufficient for student count
4. Room type must match course type (lab → practical, classroom → lecture)

### Soft Constraints (Preferred)
1. Respect instructor time preferences (Morning/Afternoon/No Thursday)
2. Avoid early morning slots (before 10 AM)
3. Avoid late evening slots (after 3 PM)
4. Balance instructor workload distribution

## 📁 Project Structure

```
├── csp_timetable.py          # Core CSP implementation
├── data_processor.py         # Data management and validation
├── timetable_ui.py          # Streamlit web interface
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── Groups.csv              # Section/group data
├── Instructors_data.csv    # Instructor information
├── Requirments_Levels.csv  # Course requirements by level
├── Rooms.csv               # Room specifications
├── Sections.csv            # Session definitions
├── TA _ID.csv             # Teaching assistant data
├── Timeslots.csv          # Available time slots
└── Timetable.csv          # Course catalog
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

### Web Interface (Recommended)
1. Start the Streamlit web interface:
   ```bash
   streamlit run timetable_ui.py
   ```
2. Open your browser to `http://localhost:8501`
3. Follow the guided interface:
   - **Data Management**: Load and validate CSV files
   - **Generate Timetable**: Configure solver and generate timetable
   - **Analysis**: View statistics and performance metrics
   - **Settings**: Configure system parameters

### Command Line Interface
1. Run the core CSP solver:
   ```bash
   python csp_timetable.py
   ```

## 📊 Data Format

### Required CSV Files

#### Timeslots.csv
```csv
Day,StartTime,EndTime
Sunday,09:00 AM,09:45 AM
Sunday,09:45 AM,10:30 AM
...
```

#### Rooms.csv
```csv
RoomID,Type,Capacity,Type_of_spaces
B07-F1.01,Lecture,25,Classroom
B26-G.01,Lab,50,Classroom
...
```

#### Instructors_data.csv
```csv
InstructorID,Name,QualifiedCourses,Preference
1,Adel Fathy,"Physics 1",Any
2,Ahmed Abdel-Malk,"Digital Signal Processing",Morning
...
```

#### Sections.csv
```csv
SectionID,Semester,StudentCount
Level1_Group1,Fall 2025,60
Level1_Group2,Fall 2025,60
...
```

#### Timetable.csv
```csv
Courses,Course Code,Credits,Department,Type,Instructor(s)
Fundamentals of Programming,CSC111,3,CSIT,LEC/LAB,Reda Elbasiony
Digital Logic Design,ECE111,3,CSIT,LEC/LAB/TUT,"Ahmed Allam, Sameh Shreif"
...
```

## 🔧 Configuration

### Solver Parameters
- **Max Iterations**: Maximum backtracking iterations (default: 5000)
- **Timeout**: Maximum solving time in seconds (default: 300)
- **Constraint Weights**: Balance between hard and soft constraints

### Data Settings
- **Data Directory**: Path to CSV files (default: current directory)
- **Database Path**: SQLite database file (default: timetable.db)
- **Auto Backup**: Automatic backup before generation

## 📈 Performance Evaluation

The system provides comprehensive performance metrics:

### Generation Metrics
- **Solving Time**: Time taken to find a solution
- **Iterations Used**: Number of backtracking iterations
- **Hard Constraint Violations**: Number of violated hard constraints
- **Soft Constraint Violations**: Number of violated soft constraints

### Timetable Quality Metrics
- **Room Utilization**: Distribution of room usage
- **Instructor Workload**: Balance of teaching assignments
- **Time Distribution**: Spread of sessions across time slots
- **Preference Satisfaction**: Adherence to instructor preferences

## 🎯 CSP Algorithm Details

### Backtracking Algorithm
1. **Variable Selection**: Order sessions by constraint density
2. **Value Selection**: Try assignments in random order
3. **Constraint Checking**: Verify hard constraints before assignment
4. **Backtracking**: Undo assignments when no valid values remain
5. **Solution Found**: When all variables are assigned

### Constraint Propagation
- **Forward Checking**: Eliminate invalid values from domains
- **Arc Consistency**: Maintain consistency between related variables
- **Domain Reduction**: Reduce search space through constraint inference

## 🔍 Troubleshooting

### Common Issues

#### No Solution Found
- **Cause**: Over-constrained problem or insufficient resources
- **Solutions**: 
  - Increase max iterations
  - Add more time slots or rooms
  - Relax soft constraints
  - Check data integrity

#### Data Loading Errors
- **Cause**: Missing or malformed CSV files
- **Solutions**:
  - Validate CSV files using the Data Management page
  - Check column names and data types
  - Ensure all required files are present

#### Performance Issues
- **Cause**: Large problem size or complex constraints
- **Solutions**:
  - Reduce max iterations for faster (but potentially incomplete) solutions
  - Use constraint relaxation techniques
  - Consider problem decomposition

## 📚 Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **Backend**: Python CSP solver with backtracking
- **Data Layer**: SQLite database with CSV import/export
- **Analysis**: Plotly visualizations and pandas analytics

### Data Flow
1. **Load**: CSV files → Data validation → Database storage
2. **Model**: Sessions → Variables, Resources → Domains, Rules → Constraints
3. **Solve**: Backtracking algorithm → Assignment generation
4. **Evaluate**: Constraint checking → Performance metrics
5. **Export**: Database → CSV/Excel → User interface

## 🤝 Contributing

This project was developed as part of the Intelligent Systems course. For improvements or extensions:

1. Fork the repository
2. Create a feature branch
3. Implement changes with proper testing
4. Submit a pull request with detailed description

## 📄 License

This project is developed for educational purposes as part of the Intelligent Systems course at CSIT department.

## 👥 Team

**Intelligent Systems Fall 2025/2026 - Project 1**
- CSP-based Automated Timetable Generation
- Constraint Satisfaction Problem Implementation
- Web-based User Interface Development

## 📞 Support

For technical support or questions about the system:
- Check the troubleshooting section above
- Review the code documentation
- Contact the development team

---

**Note**: This system is designed specifically for the CSIT department's timetable requirements and may need adaptation for other institutions or departments.
