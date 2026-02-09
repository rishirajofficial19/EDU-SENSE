import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gap_detector import LearningGapDetector
from data_generator import generate_synthetic_data
from recommendation_engine import RecommendationEngine
from data_ingestion import load_data, transform_data # Import data_ingestion functions
from class_extractor import extract_class_from_student_id

# Page config
st.set_page_config(
    page_title="EDU-SENSE: Learning Gap Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Animated gradient background */
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient-shift 15s ease infinite;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Title animations */
    .title-main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5em;
        font-weight: 800;
        animation: title-glow 3s ease-in-out infinite;
        margin-bottom: 10px;
    }
    
    @keyframes title-glow {
        0%, 100% { text-shadow: 0 0 20px rgba(102, 126, 234, 0.4); }
        50% { text-shadow: 0 0 40px rgba(118, 75, 162, 0.6); }
    }
    
    .subtitle-main {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.3em;
        font-weight: 600;
        animation: fade-in-up 1s ease-out;
    }
    
    /* Gap severity boxes with animations */
    .gap-alert {
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #d6336c; /* More prominent red border */
        background: linear-gradient(135deg, #ffe3e3 0%, #ffc4c4 100%); /* Slightly less pastel red */
        color: #333; /* Darker text for contrast */
        margin: 15px 0;
        animation: slide-in-left 0.5s ease-out;
        box-shadow: 0 4px 15px rgba(214, 51, 108, 0.2);
        transition: all 0.3s ease;
    }
    
    .gap-alert:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(214, 51, 108, 0.3);
    }
    
    .gap-warning {
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #f08c00; /* More prominent orange border */
        background: linear-gradient(135deg, #fff5e3 0%, #ffe9c4 100%); /* Slightly less pastel orange */
        color: #333; /* Darker text for contrast */
        margin: 15px 0;
        animation: slide-in-left 0.6s ease-out;
        box-shadow: 0 4px 15px rgba(240, 140, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .gap-warning:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(240, 140, 0, 0.3);
    }
    
    .gap-safe {
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #28a745; /* More prominent green border */
        background: linear-gradient(135deg, #e3fff5 0%, #c4ffe9 100%); /* Slightly less pastel green */
        color: #333; /* Darker text for contrast */
        margin: 15px 0;
        animation: slide-in-left 0.7s ease-out;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
        transition: all 0.3s ease;
    }
    
    .gap-safe:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        animation: bounce-in 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        border: 2px solid #667eea;
        animation: fade-in-up 0.7s ease-out;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        border-color: #764ba2;
    }

    /* Darker feature cards for About section */
    .about-dark-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); /* Dark background */
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        border: 2px solid #5d6d7e; /* Lighter border for contrast */
        color: #ecf0f1; /* Light text color */
        animation: fade-in-up 0.7s ease-out;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .about-dark-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border-color: #7f8c8d;
    }

    
    /* Button animations */
    button {
        transition: all 0.3s ease !important;
    }
    
    button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    button:active {
        transform: scale(0.98) !important;
    }
    
    /* Keyframe animations */
    @keyframes fade-in-up {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slide-in-left {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes bounce-in {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Status indicators */
    .status-high-risk {
        color: #ff6b6b;
        font-weight: 700;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .status-medium-risk {
        color: #ffa500;
        font-weight: 700;
    }
    
    .status-on-track {
        color: #51cf66;
        font-weight: 700;
    }
    
    /* Divider enhancement */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 30px 0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    h1, h2, h3 {
        animation: fade-in-up 0.6s ease-out;
    }
    
    /* Info box enhancement */
    .stAlert {
        border-radius: 12px;
        animation: fade-in-up 0.5s ease-out;
    }
    
    /* Container for better spacing */
    .container {
        padding: 20px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.95);
        margin: 15px 0;
        animation: fade-in-up 0.6s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'detector' not in st.session_state:
    st.session_state.detector = LearningGapDetector()
    st.session_state.recommendation_engine = RecommendationEngine()
    st.session_state.student_data = pd.DataFrame()  # Initialize as empty DataFrame
    st.session_state.analysis_results = None # For single student analysis
    st.session_state.data_loaded = False # New flag to track if data has been loaded
    st.session_state.overall_analysis_results = None # For dashboard overview

# --- Helper Functions ---
def _perform_overall_analysis(detector: LearningGapDetector, student_data: pd.DataFrame) -> dict:
    if student_data.empty:
        return {
            'total_gaps_detected': 0,
            'total_attempts': 0,
            'total_correct': 0,
            'overall_accuracy': 0,
            'high_risk_students': 0,
            'medium_risk_students': 0,
            'on_track_students': 0,
        }

    all_student_ids = student_data['Student_ID'].unique()
    total_gaps = 0
    overall_correct_attempts = 0
    overall_total_attempts = 0
    
    high_risk_count = 0
    medium_risk_count = 0
    on_track_count = 0

    for student_id in all_student_ids:
        student_df = student_data[student_data['Student_ID'] == student_id]
        analysis = detector.analyze_student(student_df)
        
        total_gaps += len(analysis['gaps'])
        overall_correct_attempts += analysis['correct_answers']
        overall_total_attempts += analysis['total_attempts']

        # Classify student risk based on overall_score
        # These thresholds can be made configurable in config.py
        if analysis['overall_score'] < 0.5:
            high_risk_count += 1
        elif 0.5 <= analysis['overall_score'] < 0.75:
            medium_risk_count += 1
        else:
            on_track_count += 1

    overall_accuracy = overall_correct_attempts / overall_total_attempts if overall_total_attempts > 0 else 0

    return {
        'total_gaps_detected': total_gaps,
        'total_attempts': overall_total_attempts,
        'total_correct': overall_correct_attempts,
        'overall_accuracy': overall_accuracy,
        'high_risk_students': high_risk_count,
        'medium_risk_students': medium_risk_count,
        'on_track_students': on_track_count,
    }

# Header
# Header with enhanced styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 30px 0;'>
        <div class='title-main'>🧠 EDU-SENSE</div>
        <div class='subtitle-main'>AI-Powered Early Learning Gap Detection System</div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Navigation")
    page = st.radio("Select Module", 
        ["Dashboard", "Student Analysis", "Pattern Report", "Recommendations", "About"])
    
    st.divider()
    st.info("💡 EDU-SENSE analyzes student learning patterns to detect gaps early and suggest interventions before failure occurs.")

# ================== PAGE: DASHBOARD ==================
if page == "Dashboard":
    st.markdown("<h2 style='text-align: center; animation: fade-in-up 0.6s ease-out;'>📊 System Dashboard</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>👥</div>
            <div style='font-size: 1.5em; font-weight: 700;'>{st.session_state.student_data['Student_ID'].nunique() if not st.session_state.student_data.empty else 0}</div>
            <div style='font-size: 0.9em; opacity: 0.9;'>Total Students</div>
            <div style='font-size: 0.8em; margin-top: 5px; opacity: 0.8;'></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>⚠️</div>
            <div style='font-size: 1.5em; font-weight: 700;'>{st.session_state.overall_analysis_results['total_gaps_detected'] if st.session_state.overall_analysis_results else 0}</div>
            <div style='font-size: 0.9em; opacity: 0.9;'>Gaps Detected</div>
            <div style='font-size: 0.8em; margin-top: 5px; opacity: 0.8;'></div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>📈</div>
            <div style='font-size: 1.5em; font-weight: 700;'>{(st.session_state.overall_analysis_results['overall_accuracy'] * 100).round(0).astype(int) if st.session_state.overall_analysis_results else 0}%</div>
            <div style='font-size: 0.9em; opacity: 0.9;'>Overall Accuracy</div>
            <div style='font-size: 0.8em; margin-top: 5px; opacity: 0.8;'></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("<h3 style='text-align: center; margin-top: 30px;'>📂 Data Management</h3>", unsafe_allow_html=True)

    col1_data, col2_data = st.columns(2)

    with col1_data:
        if st.button("🔄 Load Sample Student Data", key="load_sample_data_dashboard"):
            st.session_state.student_data = generate_synthetic_data()
            st.session_state.data_loaded = True
            st.session_state.analysis_results = None # Clear previous single student analysis
            st.session_state.overall_analysis_results = None # Reset overall analysis
            st.rerun() # Force a rerun to perform the analysis in the dedicated block below

    with col2_data:
        uploaded_file = st.file_uploader("Upload External Student Data (CSV/Excel)", type=["csv", "xlsx"], key="upload_data_dashboard")
        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1]
            try:
                raw_df = load_data(uploaded_file, file_type)
                st.session_state.student_data = transform_data(raw_df)
                st.session_state.data_loaded = True
                st.session_state.analysis_results = None # Clear previous single student analysis
                st.session_state.overall_analysis_results = None # Reset overall analysis
                st.rerun() # Force a rerun to perform the analysis
            except Exception as e:
                st.error(f"Error processing uploaded file: {e}")

    # Perform overall analysis if data is loaded and analysis hasn't been run
    if st.session_state.data_loaded and not st.session_state.student_data.empty and st.session_state.overall_analysis_results is None:
        with st.spinner("Performing overall analysis for all students..."):
            st.session_state.overall_analysis_results = _perform_overall_analysis(st.session_state.detector, st.session_state.student_data)
            st.rerun()

    if not st.session_state.data_loaded:
        st.info("Please load sample data or upload your own student data to proceed with analysis.")
    elif not st.session_state.student_data.empty:
        st.markdown("<h3 style='text-align: center; margin-top: 30px;'>📈 Recent Student Activity</h3>", unsafe_allow_html=True)
        # Use st.expander for "Read More" functionality
        with st.expander("View Recent Activity (first 100 rows)"):
            st.dataframe(st.session_state.student_data.head(100), use_container_width=True)
        # Optionally, provide a download button for the full dataset
        st.download_button(
            label="Download Full Dataset as CSV",
            data=st.session_state.student_data.to_csv(index=False).encode('utf-8'),
            file_name="full_student_data.csv",
            mime="text/csv",
            key="download_full_data_dashboard"
        )
        
        st.markdown("<h3 style='text-align: center; margin-top: 30px;'>Student Status Overview</h3>", unsafe_allow_html=True)
        
        # Use the overall analysis results for student status overview
        overall_results = st.session_state.overall_analysis_results
        
        num_high_risk = overall_results['high_risk_students'] if overall_results else 0
        num_medium_risk = overall_results['medium_risk_students'] if overall_results else 0
        num_on_track = overall_results['on_track_students'] if overall_results else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%); text-align: center;'>
                <div style='font-size: 3em;'>🔴</div>
                <div style='font-size: 1.8em; font-weight: 700;'>{num_high_risk}</div>
                <div style='font-size: 1em;'>High Risk Students</div>
                <div style='font-size: 0.85em; margin-top: 5px; opacity: 0.9;'>Needs immediate intervention</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #ffa500 0%, #ffb74d 100%); text-align: center;'>
                <div style='font-size: 3em;'>🟡</div>
                <div style='font-size: 1.8em; font-weight: 700;'>{num_medium_risk}</div>
                <div style='font-size: 1em;'>Medium Risk Students</div>
                <div style='font-size: 0.85em; margin-top: 5px; opacity: 0.9;'>Monitor closely</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #51cf66 0%, #69db7c 100%); text-align: center;'>
                <div style='font-size: 3em;'>🟢</div>
                <div style='font-size: 1.8em; font-weight: 700;'>{num_on_track}</div>
                <div style='font-size: 1em;'>On Track Students</div>
                <div style='font-size: 0.85em; margin-top: 5px; opacity: 0.9;'>Progressing well</div>
            </div>
            """, unsafe_allow_html=True)

# ================== PAGE: STUDENT ANALYSIS ==================
elif page == "Student Analysis":
    st.header("🔍 Analyze Student Learning Patterns")
    
    if st.session_state.data_loaded and not st.session_state.student_data.empty:
        # Student selection
        students = st.session_state.student_data['Student_ID'].unique()
        selected_student = st.selectbox("Select Student", students, key="student_select")
        
        if st.button("🔬 Analyze Selected Student", key="analyze_btn"):
            # Get student data
            student_df = st.session_state.student_data[
                st.session_state.student_data['Student_ID'] == selected_student
            ]
            
            # Run analysis
            analysis = st.session_state.detector.analyze_student(student_df)
            st.session_state.analysis_results = analysis
            st.success(f"Analysis complete for {selected_student}!")
        
        # Display results
        if st.session_state.analysis_results is not None:
            st.divider()
            st.subheader("📊 Analysis Results")
            
            results = st.session_state.analysis_results
            
            # Display detected gaps
            st.subheader("Detected Learning Gaps")
            if not results['gaps']:
                st.info("No significant learning gaps detected for this student.")
            for gap_type, details in results['gaps'].items():
                # Prepare gap type and difficulty info
                gap_name = gap_type.upper().replace('CONCEPT_GAP_', '').replace('_', ' ')
                gap_category = details.get('gap_type', 'Unknown')
                
                # Prepare metric display - different for confidence_gap
                if gap_type == 'confidence_gap':
                    hesitation = details.get('hesitation_severity', 0)
                    metric_str = f"<br>😰 Hesitation Severity: <strong>{hesitation:.0%}</strong> (higher = more hesitation = lower confidence)"
                else:
                    confidence = details.get('confidence', 0)
                    metric_str = f"<br>Confidence: <strong>{confidence:.1%}</strong>"
                
                # Prepare difficulty analysis
                difficulty = details.get('difficulty_mistakes', {})
                most_freq = difficulty.get('most_frequent', 'unknown')
                if most_freq != 'unknown':
                    diff_str = f"<br>❌ Makes mistakes mostly on: <strong>{most_freq.upper()}</strong> difficulty questions"
                else:
                    diff_str = ""
                
                if gap_category != 'Unknown':
                    gap_str = f"<br>🎯 Gap Type: <strong>{gap_category}</strong>"
                else:
                    gap_str = ""
                
                if details['severity'] == 'high':
                    st.markdown(f"""
                    <div class="gap-alert">
                        <strong>🔴 {gap_name}</strong><br>
                        Severity: {details['severity']}{metric_str}{diff_str}{gap_str}
                    </div>
                    """, unsafe_allow_html=True)
                elif details['severity'] == 'medium':
                    st.markdown(f"""
                    <div class="gap-warning">
                        <strong>🟡 {gap_name}</strong><br>
                        Severity: {details['severity']}{metric_str}{diff_str}{gap_str}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="gap-safe">
                        <strong>🟢 {gap_name}</strong><br>
                        Severity: {details['severity']}{metric_str}{diff_str}{gap_str}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Overall score
            st.metric("Overall Performance Score",
                     f"{results['overall_score']:.1%}", 
                     delta=None)
    else:
        st.warning("Please load student data from the Dashboard page to perform analysis.")

# ================== PAGE: PATTERN REPORT ==================
elif page == "Pattern Report":
    st.header("📋 Learning Pattern Analysis Report")
    
    if st.session_state.student_data is not None and st.session_state.analysis_results is not None:
        results = st.session_state.analysis_results
        
        st.subheader("Pattern Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Attempts", results['total_attempts'])
        with col2:
            st.metric("Correct Answers", f"{results['correct_answers']}/{results['total_attempts']}")
        with col3:
            st.metric("Avg Time (sec)", f"{results['avg_time']:.1f}")
        with col4:
            st.metric("Accuracy", f"{results['accuracy']:.1%}")
        
        st.divider()
        
        st.subheader("Detailed Gap Analysis")
        
        # Create detailed report
        report_data = {
            'Gap Type': list(results['gaps'].keys()),
            'Severity': [results['gaps'][g]['severity'] for g in results['gaps'].keys()],
            'Metric': [
                f"{results['gaps'][g].get('hesitation_severity', results['gaps'][g].get('confidence', 0)):.1%}"
                for g in results['gaps'].keys()
            ],
            'Affected Questions': [results['gaps'][g].get('affected_questions', 0) for g in results['gaps'].keys()]
        }
        
        report_df = pd.DataFrame(report_data)
        st.dataframe(report_df, use_container_width=True)
        
        # Export option
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Download Report as CSV"):
                csv = report_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        st.warning("Please complete student analysis first")

# ================== PAGE: RECOMMENDATIONS ==================
elif page == "Recommendations":
    st.header("💡 Personalized Intervention Recommendations")
    
    st.info("""
        These recommendations are AI-generated based on detected learning gaps and trends.
        **For Students:** Follow the steps and explore the linked resources for practice and concept review.
        **For Teachers:** Please review these suggestions and tailor them further based on your knowledge of the student's needs and available classroom resources. Consider these links as starting points for curriculum integration.
    """)
    
    if st.session_state.analysis_results is not None:
        results = st.session_state.analysis_results
        
        # Extract class level from Student_ID
        student_id = st.session_state.analysis_results.get('student_id', '')
        class_level = extract_class_from_student_id(student_id)
        
        # If class not found in Student_ID, try to get from Class column
        if class_level is None and 'Class' in st.session_state.student_data.columns:
            selected_student_id = st.session_state.student_data[
                st.session_state.student_data['Student_ID'] == student_id
            ]
            if len(selected_student_id) > 0:
                class_level = selected_student_id['Class'].iloc[0]
        
        # If still not found, ask user
        if class_level is None:
            st.warning("⚠️ Class information not found in Student_ID. Please select the student's class:")
            class_level = st.selectbox("Select Class", [6, 7, 8, 9, 10, 11, 12], key="class_select")
        
        # Generate recommendations with class level
        recommendations = st.session_state.recommendation_engine.generate_recommendations(results, class_level)
        
        st.subheader("Recommended Actions")
        
        for i, rec in enumerate(recommendations, 1):
            with st.expander(f"🎯 Recommendation {i}: {rec['title']}", expanded=(i==1)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {rec['description']}")
                    st.write(f"**Practice Type:** {rec['practice_type']}")
                    st.write(f"**Suggested Duration:** {rec['duration']}")
                    st.write(f"**Target Topics:** {', '.join(rec['target_topics'])}")
                
                with col2:
                    st.metric("Priority", rec['priority'])
                    st.metric("Expected Impact", f"{rec['expected_impact']:.0%}")
                
                if rec.get('resources'):
                    st.subheader("📚 Learning Resources")
                    for res_name, res_content in rec['resources'].items():
                        if isinstance(res_content, list):
                            # Handle list of links
                            st.write(f"**{res_name}:**")
                            for link in res_content:
                                if link.startswith('http'):
                                    st.markdown(f"  - [{link}]({link})")
                                else:
                                    st.write(f"  - {link}")
                        else:
                            # Handle single link
                            if isinstance(res_content, str) and res_content.startswith('http'):
                                st.markdown(f"**{res_name}:** [{res_content}]({res_content})")
                            else:
                                st.write(f"**{res_name}:** {res_content}")
        
        st.divider()
        st.subheader("Implementation Guide")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**For Teachers:**")
            st.write("""
            1. Review recommended interventions above
            2. Select 2-3 high-priority recommendations
            3. Schedule focused practice sessions
            4. Monitor student progress
            5. Re-assess after 1-2 weeks
            """)
        
        with col2:
            st.write("**For Students:**")
            st.write("""
            1. Attempt recommended practice problems
            2. Focus on target topics first
            3. Spend time on weak areas
            4. Track your improvement
            5. Ask for help when stuck
            """)
    else:
        st.warning("Please complete student analysis first")

# ================== PAGE: ABOUT ==================
elif page == "About":
    st.markdown("<h2 style='text-align: center;'>ℹ️ About EDU-SENSE</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='about-dark-card'>
            <h3>🎯 Mission</h3>
            <p>EDU-SENSE is an AI-powered learning gap detection system designed to:</p>
            <ul>
                <li><strong>Detect</strong> learning gaps early before students fail</li>
                <li><strong>Analyze</strong> student mistake patterns and behavior</li>
                <li><strong>Recommend</strong> timely micro-interventions</li>
                <li><strong>Support</strong> teachers with actionable insights</li>
                <li><strong>Respect</strong> student privacy and maintain transparency</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='about-dark-card'>
            <h3>🛠️ Technology Stack</h3>
            <ul style='list-style: none; padding: 0;'>
                <li>🐍 <strong>Backend:</strong> Python, Pandas, Scikit-learn</li>
                <li>🎨 <strong>Frontend:</strong> Streamlit</li>
                <li>📊 <strong>Data:</strong> Synthetic datasets based on real patterns</li>
                <li>🤖 <strong>ML Approach:</strong> Rule-based + Lightweight ML</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div class='about-dark-card'>
        <h3 style='text-align: center;'>📊 How It Works</h3>
        <table style='width: 100%;'>
            <tr>
                <td style='text-align: center; padding: 10px;'><strong style='font-size: 1.5em;'>1️⃣</strong><br>Input</td>
                <td style='text-align: center; padding: 10px;'>→</td>
                <td style='text-align: center; padding: 10px;'><strong style='font-size: 1.5em;'>2️⃣</strong><br>Analysis</td>
                <td style='text-align: center; padding: 10px;'>→</td>
                <td style='text-align: center; padding: 10px;'><strong style='font-size: 1.5em;'>3️⃣</strong><br>Classification</td>
                <td style='text-align: center; padding: 10px;'>→</td>
                <td style='text-align: center; padding: 10px;'><strong style='font-size: 1.5em;'>4️⃣</strong><br>Recommendation</td>
                <td style='text-align: center; padding: 10px;'>→</td>
                <td style='text-align: center; padding: 10px;'><strong style='font-size: 1.5em;'>5️⃣</strong><br>Action</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("<h3 style='text-align: center;'>✨ Key Features</h3>", unsafe_allow_html=True)
    
    features = {
        "🔍 Pattern Detection": "Identifies repeated mistakes and confusion patterns",
        "⚡ Real-time Analysis": "Instant gap detection from student behavior",
        "🎯 Targeted Recommendations": "Specific, actionable interventions",
        "📊 Visual Reports": "Easy-to-understand dashboards for teachers",
        "🔐 Privacy-First": "Works with synthetic data, respects anonymity",
        "📈 Teacher-Friendly": "Designed with teachers' needs in mind"
    }
    
    feature_cols = st.columns(2)
    for idx, (feature, description) in enumerate(features.items()):
        with feature_cols[idx % 2]:
            st.markdown(f"""
            <div class='about-dark-card'>
                <h4>{feature}</h4>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='about-dark-card'>
            <h3>👥 Team</h3>
            <p>EDU-SENSE - Developed for early learning intervention and student support</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='about-dark-card'>
            <h3>📞 Contact & Support</h3>
            <p>For questions or feedback, please contact the development team.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                border-radius: 12px; color: #ecf0f1;'>
        <strong>Version 1.0.0</strong> | Demo | Last Updated: 2025
    </div>
    """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; padding: 30px; background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%); 
            border-radius: 12px; color: white; animation: fade-in-up 1s ease-out;'>
    <h3 style='margin: 0; margin-bottom: 10px;'>🧠 EDU-SENSE</h3>
    <p style='margin: 5px 0; font-size: 1.1em;'>An AI Second-Teacher for Early Learning Gap Detection</p>
    <p style='margin: 10px 0; opacity: 0.9;'>© 2025 | Ethical AI for Education</p>
    <p style='margin: 5px 0; font-size: 0.9em; opacity: 0.8;'>✨ Making Education Smarter, One Gap at a Time ✨</p>
</div>
""", unsafe_allow_html=True)