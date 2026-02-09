"""
Utility functions for EDU-SENSE system.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class AnalysisUtils:
    """Utility functions for data analysis and processing."""
    
    @staticmethod
    def get_student_progress_trend(student_df: pd.DataFrame) -> Dict:
        """
        Calculate student's progress trend over time.
        
        Args:
            student_df: DataFrame with student's attempts
            
        Returns:
            Dictionary with progress metrics
        """
        if len(student_df) < 2:
            return {'trend': 'insufficient_data', 'improvement': 0}
        
        # Sort by timestamp
        student_df = student_df.sort_values('Timestamp')
        
        # Split into two halves
        mid_point = len(student_df) // 2
        first_half = student_df.iloc[:mid_point]
        second_half = student_df.iloc[mid_point:]
        
        # Calculate accuracy for each half
        first_half_acc = (first_half['Correct'] == 1).sum() / len(first_half) if len(first_half) > 0 else 0
        second_half_acc = (second_half['Correct'] == 1).sum() / len(second_half) if len(second_half) > 0 else 0
        
        improvement = second_half_acc - first_half_acc
        
        if improvement > 0.1:
            trend = 'improving'
        elif improvement < -0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'improvement': improvement,
            'first_half_accuracy': first_half_acc,
            'second_half_accuracy': second_half_acc
        }
    
    @staticmethod
    def get_topic_wise_performance(student_df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Get performance breakdown by topic.
        
        Args:
            student_df: DataFrame with student's attempts
            
        Returns:
            Dictionary with topic-wise metrics
        """
        if 'Topic' not in student_df.columns:
            return {}
        
        topic_stats = {}
        
        for topic in student_df['Topic'].unique():
            topic_data = student_df[student_df['Topic'] == topic]
            attempts = len(topic_data)
            correct = (topic_data['Correct'] == 1).sum()
            accuracy = correct / attempts if attempts > 0 else 0
            avg_time = topic_data['Time_Taken'].mean() if attempts > 0 else 0
            
            topic_stats[topic] = {
                'attempts': attempts,
                'correct': correct,
                'accuracy': accuracy,
                'avg_time': avg_time
            }
        
        return topic_stats
    
    @staticmethod
    def identify_weak_topics(student_df: pd.DataFrame, threshold: float = 0.65) -> List[str]:
        """
        Identify topics where student is struggling.
        
        Args:
            student_df: DataFrame with student's attempts
            threshold: Accuracy threshold (default 65%)
            
        Returns:
            List of weak topics
        """
        topic_stats = AnalysisUtils.get_topic_wise_performance(student_df)
        
        weak_topics = [
            topic for topic, stats in topic_stats.items()
            if stats['accuracy'] < threshold and stats['attempts'] >= 3
        ]
        
        return weak_topics
    
    @staticmethod
    def calculate_consistency_score(student_df: pd.DataFrame) -> float:
        """
        Calculate consistency of student performance (0-1).
        Higher score means more consistent.
        
        Args:
            student_df: DataFrame with student's attempts
            
        Returns:
            Consistency score
        """
        if 'Time_Taken' not in student_df.columns or len(student_df) < 2:
            return 0.5
        
        # Standard deviation of time taken
        time_std = student_df['Time_Taken'].std()
        time_mean = student_df['Time_Taken'].mean()
        
        # Coefficient of variation
        cv = time_std / time_mean if time_mean > 0 else float('inf')
        
        # Convert to consistency score (0-1)
        # Lower CV = higher consistency
        consistency = 1 - min(1, cv / 2)  # Normalize to 0-1
        
        return consistency


class ReportGenerator:
    """Generate reports and summaries from analysis results."""
    
    @staticmethod
    def generate_text_summary(analysis_results: Dict, recommendations: List[Dict]) -> str:
        """
        Generate a text summary of the analysis.
        
        Args:
            analysis_results: Dictionary from LearningGapDetector
            recommendations: List of recommendations
            
        Returns:
            Formatted text summary
        """
        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║              EDU-SENSE LEARNING GAP ANALYSIS REPORT             ║
╚════════════════════════════════════════════════════════════════╝

STUDENT: {analysis_results.get('student_id', 'Unknown')}
DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PERFORMANCE METRICS
──────────────────────────────────────────────────────────────────
• Total Attempts: {analysis_results['total_attempts']}
• Correct Answers: {analysis_results['correct_answers']}/{analysis_results['total_attempts']}
• Accuracy: {analysis_results['accuracy']:.1%}
• Average Time Per Question: {analysis_results['avg_time']:.1f} seconds
• Overall Performance Score: {analysis_results['overall_score']:.1%}

DETECTED GAPS
──────────────────────────────────────────────────────────────────
"""
        
        gaps = analysis_results.get('gaps', {})
        if gaps:
            for gap_name, details in gaps.items():
                summary += f"""
Gap Type: {gap_name.replace('_', ' ').title()}
├─ Severity: {details['severity'].upper()}
├─ Confidence: {details['confidence']:.1%}
└─ Details: {details['description']}
"""
        else:
            summary += "\nNo significant learning gaps detected - Student is on track!\n"
        
        summary += "\n\nRECOMMENDED INTERVENTIONS\n"
        summary += "──────────────────────────────────────────────────────────────────\n"
        
        for i, rec in enumerate(recommendations, 1):
            summary += f"""
{i}. {rec['title']}
   Priority: {rec['priority']}
   Duration: {rec['duration']}
   Expected Impact: {rec['expected_impact']:.0%}
"""
        
        summary += "\n" + "="*66 + "\n"
        return summary
    
    @staticmethod
    def generate_csv_export(analysis_results: Dict) -> str:
        """
        Generate CSV format of analysis results.
        
        Args:
            analysis_results: Dictionary from LearningGapDetector
            
        Returns:
            CSV formatted string
        """
        csv_content = "Metric,Value\n"
        csv_content += f"Student ID,{analysis_results.get('student_id', 'Unknown')}\n"
        csv_content += f"Total Attempts,{analysis_results['total_attempts']}\n"
        csv_content += f"Correct Answers,{analysis_results['correct_answers']}\n"
        csv_content += f"Accuracy,{analysis_results['accuracy']:.1%}\n"
        csv_content += f"Average Time,{analysis_results['avg_time']:.1f}\n"
        csv_content += f"Overall Score,{analysis_results['overall_score']:.1%}\n"
        csv_content += f"Number of Gaps,{len(analysis_results.get('gaps', {}))}\n"
        
        if analysis_results.get('gaps'):
            csv_content += "\nGap Details\n"
            csv_content += "Gap Type,Severity,Confidence,Description\n"
            for gap_name, details in analysis_results['gaps'].items():
                csv_content += f"{gap_name},{details['severity']},{details['confidence']:.1%},{details['description']}\n"
        
        return csv_content


class DataValidator:
    """Validate and clean data."""
    
    @staticmethod
    def validate_student_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate student data structure and content.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns
        required_cols = ['Student_ID', 'Question_ID', 'Topic', 'Correct', 'Time_Taken']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {', '.join(missing_cols)}")
        
        # Check data types
        if 'Correct' in df.columns:
            if not df['Correct'].isin([0, 1]).all():
                errors.append("'Correct' column must contain only 0 or 1")
        
        if 'Time_Taken' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['Time_Taken']):
                errors.append("'Time_Taken' must be numeric")
            if (df['Time_Taken'] < 0).any():
                errors.append("'Time_Taken' cannot be negative")
        
        # Check for empty data
        if len(df) == 0:
            errors.append("DataFrame is empty")
        
        return len(errors) == 0, errors


class PerformanceMetrics:
    """Calculate advanced performance metrics."""
    
    @staticmethod
    def calculate_learning_velocity(student_df: pd.DataFrame) -> float:
        """
        Calculate how fast a student is improving.
        Positive = improving, Negative = declining, Near 0 = stable.
        
        Args:
            student_df: DataFrame with student's attempts
            
        Returns:
            Learning velocity score
        """
        if len(student_df) < 3:
            return 0
        
        student_df = student_df.sort_values('Timestamp').reset_index(drop=True)
        
        # Create rolling accuracy windows
        window_size = max(3, len(student_df) // 3)
        
        rolling_accuracy = []
        for i in range(len(student_df) - window_size + 1):
            window_acc = (student_df.iloc[i:i+window_size]['Correct'] == 1).sum() / window_size
            rolling_accuracy.append(window_acc)
        
        if len(rolling_accuracy) < 2:
            return 0
        
        # Calculate trend
        velocity = (rolling_accuracy[-1] - rolling_accuracy[0]) / (len(rolling_accuracy) - 1)
        return velocity
    
    @staticmethod
    def get_engagement_level(student_df: pd.DataFrame) -> str:
        """
        Determine student engagement level based on attempt frequency.
        
        Args:
            student_df: DataFrame with student's attempts
            
        Returns:
            Engagement level: 'high', 'medium', or 'low'
        """
        if len(student_df) < 1:
            return 'low'
        
        # Check time span and number of attempts
        if 'Timestamp' in student_df.columns:
            time_span = (student_df['Timestamp'].max() - student_df['Timestamp'].min()).days
            attempts = len(student_df)
            
            if time_span > 0:
                attempts_per_day = attempts / time_span
            else:
                attempts_per_day = attempts
            
            if attempts_per_day >= 1:
                return 'high'
            elif attempts_per_day >= 0.5:
                return 'medium'
        
        return 'low'
