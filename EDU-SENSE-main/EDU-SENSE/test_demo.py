"""
Testing and demo script for EDU-SENSE.
Run this to test the system without using Streamlit UI.
"""

import sys
import pandas as pd
from datetime import datetime

# Import components
from gap_detector import LearningGapDetector
from data_generator import generate_synthetic_data
from recommendation_engine import RecommendationEngine
from utils import AnalysisUtils, ReportGenerator, PerformanceMetrics


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")


def test_data_generation():
    """Test synthetic data generation."""
    print_header("TEST 1: DATA GENERATION")
    
    print("Generating synthetic student data...")
    data = generate_synthetic_data(num_students=12, num_questions=50, random_seed=42)
    
    print(f"✓ Generated {len(data)} question attempts")
    print(f"✓ Across {data['Student_ID'].nunique()} students")
    print(f"✓ Topics: {', '.join(data['Topic'].unique())}")
    
    print("\nSample Data (first 5 rows):")
    print(data.head().to_string())
    
    return data


def test_gap_detection(data):
    """Test learning gap detection."""
    print_header("TEST 2: GAP DETECTION")
    
    detector = LearningGapDetector()
    
    # Analyze first student
    student_id = data['Student_ID'].iloc[0]
    student_data = data[data['Student_ID'] == student_id]
    
    print(f"Analyzing student: {student_id}")
    print(f"Total attempts: {len(student_data)}\n")
    
    results = detector.analyze_student(student_data)
    
    print(f"✓ Accuracy: {results['accuracy']:.1%}")
    print(f"✓ Correct Answers: {results['correct_answers']}/{results['total_attempts']}")
    print(f"✓ Average Time: {results['avg_time']:.1f} seconds")
    print(f"✓ Overall Score: {results['overall_score']:.1%}")
    
    print(f"\nDetected {len(results['gaps'])} gap(s):")
    for gap_name, gap_details in results['gaps'].items():
        print(f"\n  • {gap_name.replace('_', ' ').title()}")
        print(f"    - Severity: {gap_details['severity'].upper()}")
        print(f"    - Confidence: {gap_details['confidence']:.1%}")
        print(f"    - Description: {gap_details['description']}")
    
    return results


def test_recommendations(analysis_results):
    """Test recommendation generation."""
    print_header("TEST 3: RECOMMENDATIONS")
    
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(analysis_results)
    
    print(f"Generated {len(recommendations)} recommendation(s):\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Duration: {rec['duration']}")
        print(f"   Expected Impact: {rec['expected_impact']:.0%}")
        print(f"   Steps:")
        for step in rec['steps']:
            print(f"     {step}")
        print()


def test_analysis_utils(data):
    """Test utility functions."""
    print_header("TEST 4: ANALYSIS UTILITIES")
    
    student_id = data['Student_ID'].iloc[0]
    student_data = data[data['Student_ID'] == student_id]
    
    print(f"Advanced Analysis for {student_id}:\n")
    
    # Progress trend
    trend_info = AnalysisUtils.get_student_progress_trend(student_data)
    print(f"✓ Progress Trend: {trend_info['trend'].upper()}")
    print(f"  - Improvement: {trend_info['improvement']:+.1%}")
    
    # Topic-wise performance
    topic_stats = AnalysisUtils.get_topic_wise_performance(student_data)
    print(f"\n✓ Topic-wise Performance:")
    for topic, stats in topic_stats.items():
        print(f"  - {topic}: {stats['accuracy']:.1%} ({stats['correct']}/{stats['attempts']})")
    
    # Weak topics
    weak_topics = AnalysisUtils.identify_weak_topics(student_data, threshold=0.65)
    print(f"\n✓ Weak Topics: {weak_topics if weak_topics else 'None'}")
    
    # Consistency
    consistency = AnalysisUtils.calculate_consistency_score(student_data)
    print(f"✓ Consistency Score: {consistency:.1%}")
    
    # Learning velocity
    velocity = PerformanceMetrics.calculate_learning_velocity(student_data)
    print(f"✓ Learning Velocity: {velocity:+.4f} (positive = improving)")
    
    # Engagement
    engagement = PerformanceMetrics.get_engagement_level(student_data)
    print(f"✓ Engagement Level: {engagement.upper()}")


def test_report_generation(analysis_results, recommendations):
    """Test report generation."""
    print_header("TEST 5: REPORT GENERATION")
    
    print("Text Summary:")
    summary = ReportGenerator.generate_text_summary(analysis_results, recommendations)
    print(summary)
    
    print("\n" + "-"*70)
    print("CSV Export Sample:")
    print("-"*70)
    csv_content = ReportGenerator.generate_csv_export(analysis_results)
    print(csv_content)


def compare_students(data):
    """Compare analysis across multiple students."""
    print_header("TEST 6: COMPARATIVE ANALYSIS")
    
    detector = LearningGapDetector()
    
    # Analyze all students
    results_list = []
    for student_id in data['Student_ID'].unique()[:5]:  # First 5 students
        student_data = data[data['Student_ID'] == student_id]
        results = detector.analyze_student(student_data)
        results_list.append({
            'Student': student_id,
            'Accuracy': f"{results['accuracy']:.1%}",
            'Score': f"{results['overall_score']:.1%}",
            'Gaps': len(results['gaps']),
            'Attempts': results['total_attempts']
        })
    
    comparison_df = pd.DataFrame(results_list)
    print("Student Comparison (Top 5):")
    print(comparison_df.to_string(index=False))
    
    return comparison_df


def run_full_demo():
    """Run the complete demo."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  EDU-SENSE: AI-Powered Learning Gap Detection System".center(68) + "║")
    print("║" + "  Demo and Testing Suite".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    print(f"\nTest Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Running 6 comprehensive tests...\n")
    
    try:
        # Test 1: Data Generation
        data = test_data_generation()
        
        # Test 2: Gap Detection
        analysis_results = test_gap_detection(data)
        
        # Test 3: Recommendations
        test_recommendations(analysis_results)
        
        # Test 4: Analysis Utilities
        test_analysis_utils(data)
        
        # Test 5: Report Generation
        test_report_generation(analysis_results, [])
        
        # Test 6: Comparative Analysis
        compare_students(data)
        
        # Success message
        print_header("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        print("EDU-SENSE System is working correctly!")
        print("\nNext Steps:")
        print("1. Run 'streamlit run app.py' to start the web interface")
        print("2. Load sample data from the Dashboard")
        print("3. Analyze different students")
        print("4. Review recommendations")
        print("5. Download reports for records")
        
        print(f"\nTest Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED: {str(e)}")
        print("Please check the error details above.")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_full_demo()
    sys.exit(0 if success else 1)
