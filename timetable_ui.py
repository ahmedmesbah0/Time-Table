"""
Simple Timetable Generator UI
Clean and easy-to-use interface for generating class timetables
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

from csp_timetable import TimetableCSP
from data_processor import DataProcessor


def main():
    """Main application"""
    st.set_page_config(
        page_title="Timetable Generator",
        layout="wide"
    )
    
    # Title and description
    st.title("CSIT Timetable Generator")
    st.markdown("Automatic Timetable Generation using CSP")
    st.markdown("Intelligent Systems - Fall 2025/2026")
    st.divider()
    
    # Initialize session state
    if 'timetable_generated' not in st.session_state:
        st.session_state.timetable_generated = False
    if 'csp' not in st.session_state:
        st.session_state.csp = TimetableCSP()
    if 'processor' not in st.session_state:
        st.session_state.processor = DataProcessor()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select page:",
        ["Home", "Data", "Generate", "Results"]
    )
    
    # Display pages
    if page == "Home":
        show_home()
    elif page == "Data":
        show_data_page()
    elif page == "Generate":
        show_generate_page()
    elif page == "Results":
        show_results_page()


def show_home():
    """Home page with project overview"""
    st.header("Welcome to the Timetable Generator!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("What is this?")
        st.write("""
        This tool automatically creates class timetables for the CSIT department.
        It uses a **Constraint Satisfaction Problem (CSP)** approach to schedule 
        classes while respecting all constraints.
        
        **How it works:**
        1. Load your data (rooms, instructors, courses, etc.)
        2. Click generate to run the CSP solver
        3. View and export your timetable
        """)
        
        st.subheader("CSP Components")
        st.write("""
        - **Variables**: Each class session to schedule
        - **Domains**: Valid (time, room, instructor) combinations
        - **Constraints**: Rules that must be satisfied
          - Hard: No conflicts, correct room types, capacity
          - Soft: Prefer morning/afternoon, balanced workload
        """)
    
    with col2:
        st.subheader("Quick Stats")
        try:
            stats = st.session_state.processor.get_statistics()
            
            metrics = [
                ("Time Slots", stats.get('time_slots_count', 0)),
                ("Rooms", stats.get('rooms_count', 0)),
                ("Instructors", stats.get('instructors_count', 0)),
                ("Courses", stats.get('courses_count', 0)),
                ("Sessions to Schedule", stats.get('sessions_count', 0))
            ]
            
            for label, value in metrics:
                st.metric(label, value)
                
        except Exception as e:
            st.info("Load data files to see statistics")
        
        st.subheader("Getting Started")
        st.write("1. Go to Data tab to load CSV files")
        st.write("2. Go to Generate tab to create timetable")
        st.write("3. Go to Results tab to view and export")


def show_data_page():
    """Data loading and validation page"""
    st.header("Data Management")
    
    tab1, tab2 = st.tabs(["Load Data", "View Data"])
    
    with tab1:
        st.subheader("Load CSV Files")
        st.write("The system needs these CSV files from the `data/` folder:")
        
        required_files = [
            "Timeslots.csv",
            "Rooms.csv", 
            "Instructors_data.csv",
            "Groups.csv",
            "Sections.csv",
            "Timetable.csv"
        ]
        
        # Check which files exist
        st.write("**File Status:**")
        all_exist = True
        for file in required_files:
            file_path = os.path.join("data", file)
            if os.path.exists(file_path):
                st.success(f"{file}")
            else:
                st.error(f"{file} - Missing!")
                all_exist = False
        
        st.divider()
        
        if all_exist:
            if st.button("Load Data", type="primary", use_container_width=True):
                with st.spinner("Loading data..."):
                    try:
                        # Load data
                        st.session_state.csp.load_data_from_csv()
                        st.session_state.processor.create_database()
                        
                        st.success("Data loaded successfully!")
                        
                        # Show summary
                        st.write("**Loaded:**")
                        st.write(f"- {len(st.session_state.csp.time_slots)} time slots")
                        st.write(f"- {len(st.session_state.csp.rooms)} rooms")
                        st.write(f"- {len(st.session_state.csp.instructors)} instructors")
                        st.write(f"- {len(st.session_state.csp.courses)} courses")
                        st.write(f"- {len(st.session_state.csp.sessions)} sessions")
                        
                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")
        else:
            st.warning("Please add all required CSV files to the data/ folder")
    
    with tab2:
        st.subheader("View Loaded Data")
        
        if len(st.session_state.csp.time_slots) == 0:
            st.info("Load data first to view it here")
        else:
            data_type = st.selectbox(
                "Select data to view",
                ["Time Slots", "Rooms", "Instructors", "Courses", "Sessions"]
            )
            
            if data_type == "Time Slots":
                df = pd.DataFrame([
                    {"Day": ts.day, "Start": ts.start_time, "End": ts.end_time}
                    for ts in st.session_state.csp.time_slots
                ])
                st.dataframe(df, use_container_width=True)
                
            elif data_type == "Rooms":
                df = pd.DataFrame([
                    {"Room": r.room_id, "Type": r.room_type, "Capacity": r.capacity}
                    for r in st.session_state.csp.rooms
                ])
                st.dataframe(df, use_container_width=True)
                
            elif data_type == "Instructors":
                df = pd.DataFrame([
                    {"ID": i.instructor_id, "Name": i.name, "Preference": i.preference}
                    for i in st.session_state.csp.instructors
                ])
                st.dataframe(df, use_container_width=True)
                
            elif data_type == "Courses":
                df = pd.DataFrame([
                    {"Code": c.course_id, "Name": c.course_name, "Credits": c.credits}
                    for c in st.session_state.csp.courses
                ])
                st.dataframe(df, use_container_width=True)
                
            elif data_type == "Sessions":
                df = pd.DataFrame([
                    {"ID": s.session_id, "Course": s.course_id, "Type": s.session_type, "Section": s.section_id}
                    for s in st.session_state.csp.sessions
                ])
                st.dataframe(df, use_container_width=True)


def show_generate_page():
    """Timetable generation page"""
    st.header("Generate Timetable")
    
    # Check if data is loaded
    if len(st.session_state.csp.sessions) == 0:
        st.warning("Please load data first (go to Data page)")
        return
    
    st.write(f"Ready to schedule **{len(st.session_state.csp.sessions)} sessions**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Solver Settings")
        
        max_iterations = st.slider(
            "Maximum Iterations",
            min_value=1000,
            max_value=10000,
            value=5000,
            step=500,
            help="How many attempts the solver will make"
        )
        
        st.write("**Algorithm:** Backtracking with Constraint Checking")
        st.write("**Constraints:**")
        st.write("- No instructor conflicts")
        st.write("- No room conflicts")
        st.write("- Correct room types (Lab/Lecture)")
        st.write("- Sufficient room capacity")
        st.write("- Instructor preferences (soft)")
    
    with col2:
        st.subheader("Generate")
        
        st.write("Click the button below to start generating the timetable.")
        st.write("This may take 30-60 seconds depending on the data size.")
        
        if st.button("Generate Timetable", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Build CSP model
                status_text.text("Building CSP model...")
                progress_bar.progress(25)
                st.session_state.csp.build_csp_model()
                
                # Step 2: Solve
                status_text.text("Solving CSP (this may take a minute)...")
                progress_bar.progress(50)
                success = st.session_state.csp.solve(max_iterations=max_iterations)
                
                if success:
                    # Step 3: Evaluate soft constraints
                    status_text.text("Evaluating constraints...")
                    progress_bar.progress(75)
                    st.session_state.csp.evaluate_soft_constraints()
                    
                    # Step 4: Save results
                    status_text.text("Saving results...")
                    progress_bar.progress(90)
                    
                    assignments = st.session_state.csp.assignments
                    generation_info = {
                        'max_iterations': max_iterations,
                        'generation_time': datetime.now().isoformat(),
                        'hard_violations': len(st.session_state.csp.constraint_violations),
                        'soft_violations': len(st.session_state.csp.soft_constraint_violations)
                    }
                    
                    st.session_state.processor.save_timetable_to_db(assignments, generation_info, st.session_state.csp)
                    st.session_state.csp.export_timetable_to_csv()
                    
                    # Complete
                    progress_bar.progress(100)
                    status_text.text("Complete!")
                    
                    st.success("Timetable generated successfully!")
                    
                    # Show summary
                    st.write("**Results:**")
                    st.write(f"- Total sessions scheduled: {len(st.session_state.csp.assignments)}")
                    st.write(f"- Hard constraint violations: {len(st.session_state.csp.constraint_violations)}")
                    st.write(f"- Soft constraint violations: {len(st.session_state.csp.soft_constraint_violations)}")
                    
                    st.session_state.timetable_generated = True
                    
                    st.info("Go to Results page to view and export the timetable")
                    
                else:
                    st.error("Could not find a valid solution. Try increasing max iterations or checking your data.")
                    
            except Exception as e:
                st.error(f"Error during generation: {str(e)}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())


def show_results_page():
    """Results viewing and export page"""
    st.header("Results")
    
    # Check if timetable exists
    try:
        timetable_data = st.session_state.processor.get_timetable_from_db()
        
        if not timetable_data:
            st.info("No timetable generated yet. Go to **⚙️ Generate** page to create one.")
            return
            
    except Exception as e:
        st.info("No timetable generated yet. Go to **⚙️ Generate** page to create one.")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Timetable", "Statistics", "Export"])
    
    with tab1:
        st.subheader("Generated Timetable")
        
        df = pd.DataFrame(timetable_data)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days = ["All"] + sorted(df['day'].unique().tolist())
            selected_day = st.selectbox("Filter by Day", days)
        
        with col2:
            instructors = ["All"] + sorted(df['instructor_id'].unique().tolist())
            selected_instructor = st.selectbox("Filter by Instructor", instructors)
        
        with col3:
            rooms = ["All"] + sorted(df['room_id'].unique().tolist())
            selected_room = st.selectbox("Filter by Room", rooms)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_day != "All":
            filtered_df = filtered_df[filtered_df['day'] == selected_day]
        if selected_instructor != "All":
            filtered_df = filtered_df[filtered_df['instructor_id'] == selected_instructor]
        if selected_room != "All":
            filtered_df = filtered_df[filtered_df['room_id'] == selected_room]
        
        # Display table
        st.dataframe(
            filtered_df[['day', 'start_time', 'end_time', 'course_id', 'session_type', 
                        'section_id', 'room_id', 'instructor_id']],
            use_container_width=True,
            height=400
        )
        
        st.write(f"Showing {len(filtered_df)} of {len(df)} sessions")
    
    with tab2:
        st.subheader("Statistics")
        
        df = pd.DataFrame(timetable_data)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", len(df))
        with col2:
            st.metric("Rooms Used", df['room_id'].nunique())
        with col3:
            st.metric("Instructors", df['instructor_id'].nunique())
        with col4:
            st.metric("Days", df['day'].nunique())
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Sessions by Day**")
            day_counts = df['day'].value_counts()
            fig = px.bar(x=day_counts.index, y=day_counts.values,
                        labels={'x': 'Day', 'y': 'Sessions'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Sessions by Time**")
            time_counts = df['start_time'].value_counts().head(10)
            fig = px.bar(x=time_counts.index, y=time_counts.values,
                        labels={'x': 'Start Time', 'y': 'Sessions'})
            st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top 10 Most Used Rooms**")
            room_counts = df['room_id'].value_counts().head(10)
            fig = px.bar(x=room_counts.index, y=room_counts.values,
                        labels={'x': 'Room', 'y': 'Sessions'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Instructor Workload**")
            inst_counts = df['instructor_id'].value_counts().head(10)
            fig = px.bar(x=inst_counts.index, y=inst_counts.values,
                        labels={'x': 'Instructor', 'y': 'Sessions'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Export Timetable")
        
        st.write("Download the generated timetable in different formats:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            df = pd.DataFrame(timetable_data)
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"timetable_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel export
            if st.button("Export to Excel", use_container_width=True):
                try:
                    st.session_state.processor.export_timetable_to_excel()
                    st.success("Excel file saved to output/timetable.xlsx")
                except Exception as e:
                    st.error(f"Error exporting: {str(e)}")
        
        st.divider()
        st.write("**File Locations:**")
        st.write("- CSV: `output/generated_timetable.csv`")
        st.write("- Database: `output/timetable.db`")
        st.write("- Excel: `output/timetable.xlsx`")


if __name__ == "__main__":
    main()
