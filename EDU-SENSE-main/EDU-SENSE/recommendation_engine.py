from typing import Dict, List
from resources import get_resources_for_topic

class RecommendationEngine:
    """
    Generates personalized intervention recommendations based on detected gaps.
    Provides actionable, specific suggestions for teachers and students.
    """
    
    def __init__(self):
        self.intervention_library = self._build_intervention_library()
    
    def generate_recommendations(self, analysis_results: Dict, class_level=None) -> List[Dict]:
        """
        Generate personalized recommendations based on analysis.
        
        Args:
            analysis_results: Dictionary from LearningGapDetector.analyze_student()
            class_level: Optional class/grade level for resource customization
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        gaps = analysis_results['gaps']
        accuracy = analysis_results['accuracy']
        
        # Sort gaps by severity
        sorted_gaps = sorted(
            gaps.items(),
            key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x[1]['severity'], 0),
            reverse=True
        )
        
        for gap_name, gap_details in sorted_gaps:
            rec = self._create_recommendation(gap_name, gap_details, accuracy, class_level)
            if rec:
                recommendations.append(rec)
        
        # Add general recommendations if no specific gaps
        if not recommendations:
            recommendations.append(self._get_maintenance_recommendation())
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _create_recommendation(self, gap_name: str, gap_details: Dict, accuracy: float, class_level=None) -> Dict:
        """Create a specific recommendation for a detected gap."""
        
        gap_type = gap_name.split('_')[0]
        
        if gap_type == 'concept':
            return self._recommend_concept_review(gap_name, gap_details, class_level)
        elif gap_type == 'confidence':
            return self._recommend_confidence_building(gap_details, class_level)
        elif gap_type == 'speed':
            return self._recommend_deliberate_practice(gap_details, class_level)
        
        return None
    
    def _recommend_concept_review(self, gap_name: str, gap_details: Dict, class_level=None) -> Dict:
        """Recommend focused topic review, personalized with trend and library info."""
        topic_raw = gap_name.replace('concept_gap_', '').lower()
        topic_display = topic_raw.replace('_', ' ').title()
        
        library_info = self.intervention_library.get(topic_raw, {})
        
        # Default values
        practice_problems = library_info.get('practice_problems', 10)
        estimated_time = library_info.get('estimated_time', '30-45 min daily')
        key_concepts = ', '.join(library_info.get('key_concepts', ['core concepts']))
        
        trend = gap_details.get('trend', 'stable')
        severity = gap_details['severity']
        
        description_prefix = ""
        action_suffix = ""
        
        if trend == 'declining':
            description_prefix = "Urgent: Student's understanding is deteriorating. "
            action_suffix = "Focus on foundational concepts."
        elif trend == 'improving':
            description_prefix = "Student is showing progress, but still has a gap. "
            action_suffix = "Reinforce learning with varied problems."
        else: # stable
            description_prefix = "Consistent difficulty. "
            action_suffix = "Address specific misconceptions."

        description_text = f"{description_prefix}Struggling with {topic_display} ({gap_details['confidence']:.1%} confidence). {action_suffix}"
        
        # Adjust practice level based on severity and trend
        if severity == 'high' and trend == 'declining':
            practice_type = 'Foundational Review + Intensive Practice'
            duration = '1-2 weeks, 45-60 min daily'
            practice_problems = max(practice_problems, 20) # More problems for high risk
        elif severity == 'medium' and trend == 'declining':
            practice_type = 'Targeted Review + Extra Practice'
            duration = '1 week, 30-45 min daily'
            practice_problems = max(practice_problems, 15)
        elif severity == 'improving' and severity != 'low':
            practice_type = 'Reinforcement + Challenge Problems'
            duration = '3-5 days, 20-30 min daily'
            practice_problems = min(practice_problems, 10) # Fewer but maybe harder
        else:
            practice_type = 'Structured Review + Practice'
            duration = '2-3 days, 30-45 min daily'

        resources = {}
        if library_info.get('practice_resource_link'):
            resources['Practice Questions'] = library_info['practice_resource_link']
        if library_info.get('concept_guide_link'):
            resources['Concept Guide'] = library_info['concept_guide_link']
        if library_info.get('interactive_guide_link'):
            resources['Interactive/Visual Guide'] = library_info['interactive_guide_link']
        
        # Add website and YouTube resources based on topic
        topic_resources = get_resources_for_topic(topic_display, class_level)
        if topic_resources:
            if topic_resources.get('websites'):
                resources['📱 Website Resources'] = topic_resources['websites']
            if topic_resources.get('videos'):
                resources['📹 YouTube Videos'] = topic_resources['videos']
            
        return {
            'title': f'Personalized {topic_display} Intervention ({trend.capitalize()})',
            'description': description_text,
            'priority': severity.upper(),
            'practice_type': practice_type,
            'target_topics': [topic_display],
            'duration': duration,
            'expected_impact': gap_details.get('expected_impact', 0.25),
            'steps': [
                f'1. Revisit key concepts: {key_concepts}',
                f'2. Work through {practice_problems // 2}- {practice_problems // 2 + 5} guided example problems',
                f'3. Practice {practice_problems} varied problems on {topic_display}',
                f'4. Utilize the "Learning Resources" below for deeper understanding and additional practice.',
                f'5. Take a follow-up assessment to check understanding',
                f'6. Seek teacher support for persistent difficulties.'
            ],
            'resources': resources
        }
    
    def _recommend_confidence_building(self, gap_details: Dict, class_level=None) -> Dict:
        """Recommend confidence-building exercises."""
        return {
            'title': 'Confidence & Clarity Building',
            'description': gap_details['description'],
            'priority': gap_details['severity'].upper(),
            'practice_type': 'Guided Problem-Solving',
            'target_topics': ['All covered topics'],
            'duration': '1-2 weeks, 20 min daily',
            'expected_impact': 0.20,
            'steps': [
                '1. Start with easier problems to build momentum',
                '2. Work through step-by-step solutions',
                '3. Write down reasoning before answering',
                '4. Review mistakes carefully',
                '5. Gradually increase difficulty',
            ]
        }
    
    def _recommend_deliberate_practice(self, gap_details: Dict, class_level=None) -> Dict:
        """Recommend slower, more careful practice."""
        return {
            'title': 'Deliberate, Focused Practice',
            'description': gap_details['description'],
            'priority': 'MEDIUM',
            'practice_type': 'Slow & Thoughtful Practice',
            'target_topics': ['Problem-solving strategy'],
            'duration': '1 week, 25 min daily',
            'expected_impact': 0.15,
            'steps': [
                '1. Set a timer for 3-5 minutes per problem',
                '2. Read the question carefully twice',
                '3. Plan your approach before answering',
                '4. Work through each step deliberately',
                '5. Double-check your answer',
            ]
        }
    
    def _get_maintenance_recommendation(self) -> Dict:
        """Recommend continued practice for students on track."""
        return {
            'title': 'Continued Practice & Advancement',
            'description': 'Student is performing well; continue with current pace',
            'priority': 'LOW',
            'practice_type': 'Regular Practice + Challenge',
            'target_topics': ['All topics'],
            'duration': 'Ongoing',
            'expected_impact': 0.10,
            'steps': [
                '1. Continue regular daily practice',
                '2. Try progressively harder problems',
                '3. Explore different problem types',
                '4. Help other students',
            ]
        }
    
    def _build_intervention_library(self) -> Dict:
        """Build library of intervention strategies."""
        return {
            'arithmetic': {
                'practice_problems': 20,
                'estimated_time': '30 minutes',
                'key_concepts': ['Addition', 'Subtraction', 'Multiplication', 'Division'],
                'practice_resource_link': 'https://www.khanacademy.org/math/arithmetic',
                'concept_guide_link': 'https://www.mathplanet.com/education/pre-algebra/discover-basic-math/arithmetic-properties',
                'interactive_guide_link': 'https://www.mathsisfun.com/numbers/index.html'
            },
            'fractions': {
                'practice_problems': 15,
                'estimated_time': '45 minutes',
                'key_concepts': ['Numerator', 'Denominator', 'Simplification', 'Comparison', 'Operations'],
                'practice_resource_link': 'https://www.khanacademy.org/math/arithmetic/fractions',
                'concept_guide_link': 'https://www.mathplanet.com/education/pre-algebra/fractions/what-is-a-fraction',
                'interactive_guide_link': 'https://www.mathsisfun.com/fractions-menu.html'
            },
            'algebra': {
                'practice_problems': 12,
                'estimated_time': '60 minutes',
                'key_concepts': ['Variables', 'Equations', 'Solving', 'Substitution', 'Expressions'],
                'practice_resource_link': 'https://www.khanacademy.org/math/algebra',
                'concept_guide_link': 'https://www.mathplanet.com/education/algebra',
                'interactive_guide_link': 'https://www.desmos.com/calculator'
            },
            'geometry': {
                'practice_problems': 10,
                'estimated_time': '50 minutes',
                'key_concepts': ['Shapes', 'Area', 'Perimeter', 'Angles', 'Theorems'],
                'practice_resource_link': 'https://www.khanacademy.org/math/geometry',
                'concept_guide_link': 'https://www.mathplanet.com/education/geometry',
                'interactive_guide_link': 'https://www.geogebra.org/geometry'
            },
            'data analysis': {
                'practice_problems': 8,
                'estimated_time': '55 minutes',
                'key_concepts': ['Mean', 'Median', 'Mode', 'Graphs', 'Probability'],
                'practice_resource_link': 'https://www.khanacademy.org/math/statistics-probability/displaying-describing-data',
                'concept_guide_link': 'https://www.khanacademy.org/math/statistics-probability',
                'interactive_guide_link': 'https://phet.colorado.edu/en/simulations/filter?subjects=math&type=html&sort=date&view=grid'
            },
            'physics': {
                'practice_problems': 10,
                'estimated_time': '60 minutes',
                'key_concepts': ['Kinematics', 'Forces', 'Energy', 'Momentum'],
                'practice_resource_link': 'https://www.khanacademy.org/science/physics',
                'concept_guide_link': 'https://www.physicsclassroom.com/class',
                'interactive_guide_link': 'https://phet.colorado.edu/en/simulations/filter?subjects=physics&type=html&sort=date&view=grid'
            },
            'chemistry': {
                'practice_problems': 10,
                'estimated_time': '60 minutes',
                'key_concepts': ['Atoms', 'Molecules', 'Stoichiometry', 'Reactions'],
                'practice_resource_link': 'https://www.khanacademy.org/science/chemistry',
                'concept_guide_link': 'https://www.acs.org/education/resources/highschool.html',
                'interactive_guide_link': 'https://phet.colorado.edu/en/simulations/filter?subjects=chemistry&type=html&sort=date&view=grid'
            }
        }
    
    def estimate_improvement_time(self, severity: str) -> str:
        """Estimate time needed to address a gap."""
        time_map = {
            'high': '2-3 weeks',
            'medium': '1-2 weeks',
            'low': '3-5 days'
        }
        return time_map.get(severity, '1 week')