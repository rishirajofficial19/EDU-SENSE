import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class LearningGapDetector:
    """
    Detects learning gaps in students based on question attempt patterns.
    Analyzes mistakes, timing, and conceptual weaknesses.
    """
    
    def __init__(self):
        self.gaps_detected = {}
        self.min_attempts_threshold = 3
        
    def analyze_student(self, student_df: pd.DataFrame) -> Dict:
        """
        Comprehensive analysis of a student's learning patterns.
        
        Args:
            student_df: DataFrame with student's question attempts
            
        Returns:
            Dictionary with detected gaps and metrics
        """
        
        if len(student_df) == 0:
            return self._empty_analysis()
        
        # Basic metrics
        total_attempts = len(student_df)
        correct_answers = (student_df['Correct'] == 1).sum()
        accuracy = correct_answers / total_attempts if total_attempts > 0 else 0
        avg_time = student_df['Time_Taken'].mean()
        
        # Detect different types of gaps
        concept_gaps = self._detect_concept_gaps(student_df)
        confidence_gaps = self._detect_confidence_gaps(student_df)
        speed_gaps = self._detect_speed_gaps(student_df)
        
        # Combine all gaps
        all_gaps = {**concept_gaps, **confidence_gaps, **speed_gaps}
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            accuracy, 
            len(all_gaps),
            student_df
        )
        
        return {
            'total_attempts': total_attempts,
            'correct_answers': correct_answers,
            'accuracy': accuracy,
            'avg_time': avg_time,
            'gaps': all_gaps,
            'overall_score': overall_score,
            'student_id': student_df['Student_ID'].iloc[0] if 'Student_ID' in student_df.columns else 'Unknown'
        }
    
    def _detect_concept_gaps(self, student_df: pd.DataFrame) -> Dict:
        """Detect conceptual misunderstandings through repeated mistakes."""
        gaps = {}
        
        # Group by topic
        if 'Topic' not in student_df.columns:
            return gaps
        
        for topic in student_df['Topic'].unique():
            topic_data = student_df[student_df['Topic'] == topic]
            topic_attempts = len(topic_data)
            
            if topic_attempts < self.min_attempts_threshold:
                continue
            
            topic_accuracy = (topic_data['Correct'] == 1).sum() / topic_attempts
            
            # Flag as concept gap if accuracy is low
            if topic_accuracy < 0.6:
                # Analyze difficulty of mistakes and gap type
                difficulty_analysis = self._analyze_mistake_difficulty(topic_data)
                gap_type = self._classify_gap_type(topic, topic_data)  # Pass topic_data for analysis
                
                gaps[f'concept_gap_{topic.lower().replace(" ", "_")}'] = {
                    'severity': self._severity_from_accuracy(topic_accuracy),
                    'confidence': 1 - topic_accuracy,
                    'affected_questions': topic_attempts,
                    'description': f"Struggling with {topic}: {topic_accuracy:.1%} accuracy",
                    'difficulty_mistakes': difficulty_analysis,
                    'gap_type': gap_type
                }
        
        return gaps
    
    def _analyze_mistake_difficulty(self, topic_data: pd.DataFrame) -> Dict:
        """
        Analyze what difficulty level questions the student made mistakes on.
        Categorizes incorrect attempts by difficulty.
        """
        if 'Time_Taken' not in topic_data.columns:
            return {'easy': 0, 'moderate': 0, 'hard': 0, 'most_frequent': 'unknown'}
        
        avg_time = topic_data['Time_Taken'].mean()
        std_time = topic_data['Time_Taken'].std()
        
        # Get only incorrect attempts
        wrong_attempts = topic_data[topic_data['Correct'] == 0]
        
        if len(wrong_attempts) == 0:
            return {'easy': 0, 'moderate': 0, 'hard': 0, 'most_frequent': 'none'}
        
        difficulty_counts = {'easy': 0, 'moderate': 0, 'hard': 0}
        
        for _, attempt in wrong_attempts.iterrows():
            time_taken = attempt['Time_Taken']
            
            # Classify by time taken relative to average
            if time_taken < avg_time - std_time:
                # Fast question - likely easy
                difficulty_counts['easy'] += 1
            elif time_taken > avg_time + std_time:
                # Slow question - likely hard
                difficulty_counts['hard'] += 1
            else:
                # Medium time - moderate difficulty
                difficulty_counts['moderate'] += 1
        
        # Find most frequent mistake type
        most_frequent = max(difficulty_counts, key=difficulty_counts.get)
        
        return {
            'easy': difficulty_counts['easy'],
            'moderate': difficulty_counts['moderate'],
            'hard': difficulty_counts['hard'],
            'total_mistakes': len(wrong_attempts),
            'most_frequent': most_frequent
        }
    
    def _classify_gap_type(self, topic: str, topic_data: pd.DataFrame = None) -> str:
        """
        Classify gap as Conceptual or Theoretical based on actual error patterns in data.
        
        THEORETICAL GAP: Student lacks formula/calculation skills for complex problems
        - Gets easy problems RIGHT, hard problems WRONG  
        - Indicates can understand basics but struggles with application/complexity
        - Formula or complex calculation failures
        
        CONCEPTUAL GAP: Student doesn't understand fundamental concept
        - Makes mistakes scattered across all difficulty levels
        - Spends time on problems but still gets them wrong
        - Indicates fundamental misunderstanding
        """
        if topic_data is None or len(topic_data) < 3:
            return 'Unknown'
        
        # Get only incorrect attempts
        wrong_attempts = topic_data[topic_data['Correct'] == 0]
        if len(wrong_attempts) < 1:
            return 'Theoretical'
        
        if 'Time_Taken' not in topic_data.columns:
            return 'Unknown'
        
        # Calculate statistics
        avg_time = topic_data['Time_Taken'].mean()
        std_time = topic_data['Time_Taken'].std()
        if std_time == 0:
            std_time = 1
        
        # Categorize by difficulty level
        easy_threshold = avg_time - std_time
        hard_threshold = avg_time + std_time
        
        easy_all = topic_data[topic_data['Time_Taken'] < easy_threshold]
        hard_all = topic_data[topic_data['Time_Taken'] > hard_threshold]
        
        # Calculate accuracy by difficulty
        easy_accuracy = (easy_all['Correct'].sum() / len(easy_all)) if len(easy_all) > 0 else 0
        hard_accuracy = (hard_all['Correct'].sum() / len(hard_all)) if len(hard_all) > 0 else 0
        
        # PRIMARY INDICATOR: Difficulty Progression
        # Theoretical: Easy correct (>60%), Hard wrong (<40%)
        difficulty_progression = easy_accuracy - hard_accuracy
        
        # If we have clear progression pattern
        if len(easy_all) > 1 and len(hard_all) > 1:
            # THEORETICAL PATTERN: Easy right, Hard wrong (can do basics, fails on complex)
            if easy_accuracy > 0.5 and hard_accuracy < 0.5 and difficulty_progression > 0.2:
                return 'Theoretical'
            
            # CONCEPTUAL PATTERN: Struggles equally across all difficulties
            if abs(easy_accuracy - hard_accuracy) < 0.2:
                return 'Conceptual'
        
        # SECONDARY INDICATOR: Time-Accuracy Relationship
        # Conceptual: Spends lots of time but still wrong (confused/rethinking)
        # Theoretical: Quick wrong answers (careless/skipped formula)
        
        high_time_wrong = len(wrong_attempts[wrong_attempts['Time_Taken'] > avg_time + std_time])
        low_time_wrong = len(wrong_attempts[wrong_attempts['Time_Taken'] < avg_time - std_time])
        
        if len(wrong_attempts) > 0:
            high_time_ratio = high_time_wrong / len(wrong_attempts)
            low_time_ratio = low_time_wrong / len(wrong_attempts)
            
            # Conceptual: Spends time (>50% of mistakes are on hard problems)
            if high_time_ratio > 0.5 and low_time_ratio < 0.2:
                return 'Conceptual'
            
            # Theoretical: Quick answers (>40% of mistakes are on easy problems)
            if low_time_ratio > 0.4 and high_time_ratio < 0.3:
                return 'Theoretical'
        
        # TERTIARY: Overall accuracy
        overall_accuracy = (topic_data['Correct'].sum() / len(topic_data))
        return 'Conceptual' if overall_accuracy < 0.35 else 'Theoretical'




    
    def _detect_confidence_gaps(self, student_df: pd.DataFrame) -> Dict:
        """Detect confidence issues through hesitation patterns."""
        gaps = {}
        
        # Analyze time patterns - too much time might indicate confusion/hesitation
        avg_time = student_df['Time_Taken'].mean()
        high_time_attempts = student_df[student_df['Time_Taken'] > avg_time * 1.5]
        
        if len(high_time_attempts) > 0:
            high_time_wrong = (high_time_attempts['Correct'] == 0).sum()
            error_rate_on_slow = high_time_wrong / len(high_time_attempts)
            
            if error_rate_on_slow > 0.5:
                gaps['confidence_gap'] = {
                    'severity': 'medium' if error_rate_on_slow < 0.7 else 'high',
                    'hesitation_severity': error_rate_on_slow,  # Renamed from 'confidence' for clarity
                    'affected_questions': len(high_time_attempts),
                    'description': f"Hesitates on {error_rate_on_slow:.0%} of slow attempts ({avg_time*1.5:.1f}s+) but still gets them wrong"
                }
        
        return gaps
    
    def _detect_speed_gaps(self, student_df: pd.DataFrame) -> Dict:
        """Detect speed-related gaps."""
        gaps = {}
        
        # Fast but wrong answers indicate rushing or lack of understanding
        avg_time = student_df['Time_Taken'].mean()
        fast_attempts = student_df[student_df['Time_Taken'] < avg_time * 0.5]
        
        if len(fast_attempts) > 2:
            fast_wrong = (fast_attempts['Correct'] == 0).sum()
            fast_ratio = fast_wrong / len(fast_attempts)
            
            if fast_ratio > 0.4:
                gaps['speed_gap'] = {
                    'severity': 'medium',
                    'confidence': fast_ratio,
                    'affected_questions': len(fast_attempts),
                    'description': "Answers too quickly without careful consideration"
                }
        
        return gaps
    
    def _severity_from_accuracy(self, accuracy: float) -> str:
        """Convert accuracy to severity level."""
        if accuracy < 0.4:
            return 'high'
        elif accuracy < 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_overall_score(self, accuracy: float, num_gaps: int, df: pd.DataFrame) -> float:
        """Calculate overall performance score (0-1)."""
        # Base score from accuracy
        base_score = accuracy
        
        # Penalty for gaps
        gap_penalty = num_gaps * 0.1
        
        # Bonus for consistency
        if 'Time_Taken' in df.columns:
            time_std = df['Time_Taken'].std()
            time_mean = df['Time_Taken'].mean()
            consistency_bonus = 0.05 if time_std < time_mean * 0.5 else 0
        else:
            consistency_bonus = 0
        
        overall = max(0, min(1, base_score - gap_penalty + consistency_bonus))
        return overall
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure."""
        return {
            'total_attempts': 0,
            'correct_answers': 0,
            'accuracy': 0,
            'avg_time': 0,
            'gaps': {},
            'overall_score': 0,
            'student_id': 'Unknown'
        }
