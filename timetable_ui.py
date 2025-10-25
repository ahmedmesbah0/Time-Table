"""
User Interface for Timetable Generation System
Provides a web-based interface for data management and timetable generation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from pathlib import Path

# Import our modules
from csp_timetable import TimetableCSP
from data_processor import DataProcessor


class TimetableUI:
    """Web-based user interface for the timetable generation system"""
    
    def __init__(self):
        self.csp = TimetableCSP()
        self.processor = DataProcessor()
        
    def run(self):
        """Run the Streamlit application"""
        st.set_page_config(
            page_title="CSIT Timetable Generator",
            page_icon="📅",
            layout="wide"
        )
        
        st.title("📅 CSIT Automated Timetable Generator")
        st.markdown("**Intelligent Systems Fall 2025/2026 - Project 1**")
        st.markdown("Constraint Satisfaction Problem (CSP) based timetable generation")
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a page",
            ["🏠 Home", "📊 Data Management", "⚙️ Generate Timetable", "📈 Analysis", "🔧 Settings"]
        )
        
        if page == "🏠 Home":
            self.show_home_page()
        elif page == "📊 Data Management":
            self.show_data_management_page()
        elif page == "⚙️ Generate Timetable":
            self.show_generation_page()
        elif page == "📈 Analysis":
            self.show_analysis_page()
        elif page == "🔧 Settings":
            self.show_settings_page()
    
    def show_home_page(self):
        """Display the home page"""
        st.header("Welcome to CSIT Timetable Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Project Overview")
            st.markdown("""
            This system implements an automated timetable generation solution using 
            Constraint Satisfaction Problem (CSP) techniques for the CSIT department.
            
            **Key Features:**
            - CSP-based scheduling algorithm
            - Hard and soft constraint handling
            - Dynamic data management
            - Performance evaluation
            - Interactive web interface
            """)
        
        with col2:
            st.subheader("📋 Quick Stats")
            try:
                stats = self.processor.get_statistics()
                st.metric("Time Slots", stats.get('time_slots_count', 0))
                st.metric("Rooms", stats.get('rooms_count', 0))
                st.metric("Instructors", stats.get('instructors_count', 0))
                st.metric("Courses", stats.get('courses_count', 0))
                st.metric("Sections", stats.get('sections_count', 0))
                st.metric("Sessions", stats.get('sessions_count', 0))
            except:
                st.info("No data loaded yet. Please go to Data Management to load CSV files.")
        
        st.subheader("🚀 Getting Started")
        st.markdown("""
        1. **Data Management**: Load and validate your CSV data files
        2. **Generate Timetable**: Run the CSP solver to create a timetable
        3. **Analysis**: View statistics and performance metrics
        4. **Settings**: Configure solver parameters and preferences
        """)
        
        # Show recent timetable if available
        try:
            recent_timetable = self.processor.get_timetable_from_db()
            if recent_timetable:
                st.subheader("📅 Recent Timetable")
                df = pd.DataFrame(recent_timetable)
                st.dataframe(df.head(10), width='stretch')
                
                if st.button("View Full Timetable"):
                    st.session_state.show_full_timetable = True
        except:
            pass
    
    def show_data_management_page(self):
        """Display the data management page"""
        st.header("📊 Data Management")
        
        tab1, tab2, tab3 = st.tabs(["📁 Load Data", "✅ Validate Data", "💾 Database Operations"])
        
        with tab1:
            st.subheader("Load CSV Data")
            
            # File upload
            uploaded_files = st.file_uploader(
                "Upload CSV files",
                type=['csv'],
                accept_multiple_files=True,
                help="Upload Timeslots.csv, Rooms.csv, Instructors_data.csv, Sections.csv, and Timetable.csv"
            )
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    # Save uploaded file
                    with open(uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"Uploaded {uploaded_file.name}")
            
            # Load data button
            if st.button("🔄 Load Data from CSV Files"):
                with st.spinner("Loading data..."):
                    try:
                        self.csp.load_data_from_csv()
                        self.processor.create_database()
                        st.success("Data loaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")
        
        with tab2:
            st.subheader("Data Validation")
            
            if st.button("🔍 Validate CSV Files"):
                with st.spinner("Validating files..."):
                    validation_results = self.processor.validate_csv_files()
                    
                    for filename, errors in validation_results.items():
                        if errors:
                            st.error(f"❌ {filename}")
                            for error in errors:
                                st.write(f"  - {error}")
                        else:
                            st.success(f"✅ {filename}")
        
        with tab3:
            st.subheader("Database Operations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Create Database"):
                    with st.spinner("Creating database..."):
                        try:
                            self.processor.create_database()
                            st.success("Database created successfully!")
                        except Exception as e:
                            st.error(f"Error creating database: {str(e)}")
                
                if st.button("📊 Show Statistics"):
                    try:
                        stats = self.processor.get_statistics()
                        st.json(stats)
                    except Exception as e:
                        st.error(f"Error getting statistics: {str(e)}")
            
            with col2:
                if st.button("💾 Backup Data"):
                    with st.spinner("Creating backup..."):
                        try:
                            backup_path = self.processor.backup_data()
                            st.success(f"Backup created in {backup_path}")
                        except Exception as e:
                            st.error(f"Error creating backup: {str(e)}")
                
                if st.button("📤 Export to Excel"):
                    with st.spinner("Exporting..."):
                        try:
                            self.processor.export_timetable_to_excel()
                            st.success("Excel file exported successfully!")
                        except Exception as e:
                            st.error(f"Error exporting: {str(e)}")
    
    def show_generation_page(self):
        """Display the timetable generation page"""
        st.header("⚙️ Generate Timetable")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("CSP Solver Configuration")
            
            # Solver parameters
            max_iterations = st.slider(
                "Maximum Iterations",
                min_value=1000,
                max_value=10000,
                value=5000,
                step=1000,
                help="Maximum number of iterations for the CSP solver"
            )
            
            # Constraint preferences
            st.subheader("Constraint Preferences")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                respect_instructor_preferences = st.checkbox(
                    "Respect Instructor Preferences",
                    value=True,
                    help="Consider instructor time preferences (Morning/Afternoon/No Thursday)"
                )
                
                avoid_early_morning = st.checkbox(
                    "Avoid Early Morning Slots",
                    value=True,
                    help="Prefer slots after 10:00 AM"
                )
            
            with col_b:
                avoid_late_evening = st.checkbox(
                    "Avoid Late Evening Slots",
                    value=True,
                    help="Prefer slots before 3:00 PM"
                )
                
                balance_workload = st.checkbox(
                    "Balance Instructor Workload",
                    value=True,
                    help="Distribute sessions evenly among instructors"
                )
        
        with col2:
            st.subheader("Generation Status")
            
            # Check if data is loaded
            try:
                stats = self.processor.get_statistics()
                if stats.get('sessions_count', 0) == 0:
                    st.warning("⚠️ No sessions loaded. Please load data first.")
                    return
                else:
                    st.success(f"✅ {stats['sessions_count']} sessions ready")
            except:
                st.error("❌ No data loaded. Please load CSV files first.")
                return
            
            # Generation button
            if st.button("🚀 Generate Timetable", type="primary"):
                with st.spinner("Generating timetable..."):
                    try:
                        # Build CSP model
                        self.csp.build_csp_model()
                        
                        # Solve CSP
                        success = self.csp.solve(max_iterations=max_iterations)
                        
                        if success:
                            # Evaluate soft constraints
                            
                            self.csp.evaluate_soft_constraints()
                            
                            # Save to database
                            assignments = self.csp.assignments
                            generation_info = {
                                'max_iterations': max_iterations,
                                'generation_time': datetime.now().isoformat(),
                                'hard_violations': len(self.csp.constraint_violations),
                                'soft_violations': len(self.csp.soft_constraint_violations)
                            }
                            
                            self.processor.save_timetable_to_db(assignments, generation_info)
                            
                            st.success("🎉 Timetable generated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate timetable. Check constraints.")
                            
                    except Exception as e:
                        st.error(f"Error generating timetable: {str(e)}")
        
        # Show generation results
        try:
            recent_timetable = self.processor.get_timetable_from_db()
            if recent_timetable:
                st.subheader("📅 Generated Timetable")
                
                # Display timetable
                df = pd.DataFrame(recent_timetable)
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    day_filter = st.selectbox("Filter by Day", ["All"] + list(df['day'].unique()))
                
                with col2:
                    instructor_filter = st.selectbox("Filter by Instructor", ["All"] + list(df['instructor_id'].unique()))
                
                with col3:
                    room_filter = st.selectbox("Filter by Room", ["All"] + list(df['room_id'].unique()))
                
                # Apply filters
                filtered_df = df.copy()
                if day_filter != "All":
                    filtered_df = filtered_df[filtered_df['day'] == day_filter]
                if instructor_filter != "All":
                    filtered_df = filtered_df[filtered_df['instructor_id'] == instructor_filter]
                if room_filter != "All":
                    filtered_df = filtered_df[filtered_df['room_id'] == room_filter]
                
                st.dataframe(filtered_df, width='stretch')
                
                # Download options
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"timetable_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    if st.button("📊 Export to Excel"):
                        self.processor.export_timetable_to_excel()
                        st.success("Excel file exported!")
                        
        except Exception as e:
            st.info("No timetable generated yet.")
    
    def show_analysis_page(self):
        """Display the analysis page"""
        st.header("📈 Timetable Analysis")
        
        try:
            timetable_data = self.processor.get_timetable_from_db()
            if not timetable_data:
                st.info("No timetable data available. Please generate a timetable first.")
                return
            
            df = pd.DataFrame(timetable_data)
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", len(df))
            
            with col2:
                unique_rooms = df['room_id'].nunique()
                st.metric("Rooms Used", unique_rooms)
            
            with col3:
                unique_instructors = df['instructor_id'].nunique()
                st.metric("Instructors", unique_instructors)
            
            with col4:
                unique_courses = df['course_id'].nunique()
                st.metric("Courses", unique_courses)
            
            # Charts
            tab1, tab2, tab3, tab4 = st.tabs(["📅 By Day", "🏢 By Room", "👨‍🏫 By Instructor", "📚 By Course"])
            
            with tab1:
                st.subheader("Sessions by Day")
                day_counts = df['day'].value_counts()
                fig = px.bar(x=day_counts.index, y=day_counts.values, 
                           title="Sessions Distribution by Day")
                fig.update_layout(xaxis_title="Day", yaxis_title="Number of Sessions")
                st.plotly_chart(fig, width='stretch')
            
            with tab2:
                st.subheader("Room Utilization")
                room_counts = df['room_id'].value_counts().head(10)
                fig = px.bar(x=room_counts.index, y=room_counts.values,
                           title="Top 10 Most Used Rooms")
                fig.update_layout(xaxis_title="Room ID", yaxis_title="Number of Sessions")
                st.plotly_chart(fig, width='stretch')
            
            with tab3:
                st.subheader("Instructor Workload")
                instructor_counts = df['instructor_id'].value_counts()
                fig = px.bar(x=instructor_counts.index, y=instructor_counts.values,
                           title="Sessions per Instructor")
                fig.update_layout(xaxis_title="Instructor ID", yaxis_title="Number of Sessions")
                st.plotly_chart(fig, width='stretch')
            
            with tab4:
                st.subheader("Course Distribution")
                course_counts = df['course_id'].value_counts().head(10)
                fig = px.pie(values=course_counts.values, names=course_counts.index,
                           title="Top 10 Courses by Session Count")
                st.plotly_chart(fig, width='stretch')
            
            # Detailed analysis
            st.subheader("📊 Detailed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Room Capacity Analysis**")
                # This would require joining with room data
                st.info("Room capacity analysis requires room data integration")
            
            with col2:
                st.write("**Time Slot Distribution**")
                time_counts = df['start_time'].value_counts()
                fig = px.bar(x=time_counts.index, y=time_counts.values,
                           title="Sessions by Time Slot")
                fig.update_layout(xaxis_title="Start Time", yaxis_title="Number of Sessions")
                st.plotly_chart(fig, width='stretch')
                
        except Exception as e:
            st.error(f"Error loading analysis data: {str(e)}")
    
    def show_settings_page(self):
        """Display the settings page"""
        st.header("🔧 Settings")
        
        tab1, tab2, tab3 = st.tabs(["⚙️ Solver Settings", "📁 Data Settings", "🔒 System Settings"])
        
        with tab1:
            st.subheader("CSP Solver Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Backtracking Parameters**")
                max_iterations = st.number_input(
                    "Default Max Iterations",
                    min_value=1000,
                    max_value=50000,
                    value=5000,
                    step=1000
                )
                
                timeout_seconds = st.number_input(
                    "Timeout (seconds)",
                    min_value=30,
                    max_value=3600,
                    value=300,
                    step=30
                )
            
            with col2:
                st.write("**Constraint Weights**")
                hard_constraint_weight = st.slider(
                    "Hard Constraint Weight",
                    min_value=1.0,
                    max_value=10.0,
                    value=5.0,
                    step=0.5
                )
                
                soft_constraint_weight = st.slider(
                    "Soft Constraint Weight",
                    min_value=0.1,
                    max_value=2.0,
                    value=1.0,
                    step=0.1
                )
        
        with tab2:
            st.subheader("Data Management Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**File Paths**")
                data_directory = st.text_input(
                    "Data Directory",
                    value=".",
                    help="Directory containing CSV files"
                )
                
                database_path = st.text_input(
                    "Database Path",
                    value="timetable.db",
                    help="SQLite database file path"
                )
            
            with col2:
                st.write("**Backup Settings**")
                auto_backup = st.checkbox(
                    "Auto Backup Before Generation",
                    value=True
                )
                
                backup_retention_days = st.number_input(
                    "Backup Retention (days)",
                    min_value=1,
                    max_value=365,
                    value=30
                )
        
        with tab3:
            st.subheader("System Information")
            
            st.write("**Version Information**")
            st.code("""
            CSIT Timetable Generator v1.0
            Intelligent Systems Fall 2025/2026
            CSP-based Automated Timetable Generation
            """)
            
            st.write("**System Status**")
            
            # Check system status
            try:
                stats = self.processor.get_statistics()
                st.success("✅ Database connected")
                st.success(f"✅ {stats.get('sessions_count', 0)} sessions loaded")
            except:
                st.error("❌ Database not connected")
            
            # Clear data button
            if st.button("🗑️ Clear All Data", type="secondary"):
                if st.checkbox("I understand this will delete all data"):
                    try:
                        os.remove("timetable.db")
                        st.success("All data cleared!")
                        st.rerun()
                    except:
                        st.error("Error clearing data")


def main():
    """Main function to run the Streamlit app"""
    ui = TimetableUI()
    ui.run()


if __name__ == "__main__":
    main()
