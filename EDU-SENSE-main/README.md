# EDU-SENSE: AI-Powered Learning Gap Detection System

An intelligent system that detects early learning gaps in students by analyzing mistake patterns and recommending timely micro-interventions.

## 🎯 Project Overview

EDU-SENSE is designed to support teachers by:
- **Detecting** learning gaps early before students fail
- **Analyzing** student mistake patterns and behavior
- **Recommending** specific, actionable interventions
- **Tracking** student progress and improvement

## ✨ Key Features

- 🔍 **Smart Gap Detection**: Identifies concept gaps, confidence issues, and speed problems
- ⚡ **Real-time Analysis**: Instant feedback from student behavior patterns
- 🎯 **Personalized Recommendations**: Specific intervention suggestions for each student
- 📊 **Teacher Dashboard**: Visual reports and student status tracking
- 🔐 **Privacy-First**: Works with synthetic data, maintains anonymity
- 📱 **User-Friendly Interface**: Built with Streamlit for easy interaction

## 🛠️ Technology Stack

- **Python 3.8+**: Core programming language
- **Streamlit**: Interactive web UI
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning utilities

## 📋 Installation & Setup

### 1. Install Python (if not already installed)
Download from [python.org](https://www.python.org/downloads/) and ensure Python 3.8+ is installed.

### 2. Install Required Packages
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 How to Use

### Dashboard
- View system overview and student statistics
- Load sample synthetic data for testing

### Student Analysis
1. Load sample data from Dashboard
2. Select a student from the dropdown
3. Click "Analyze Selected Student"
4. View detected learning gaps and their severity

### Pattern Report
- View detailed analysis metrics
- See affected topics and questions
- Download analysis as CSV file

### Recommendations
- Review personalized intervention suggestions
- Get priority-ordered recommendations
- See expected impact of each intervention
- Implementation guide for teachers and students

### About
- Learn about the project mission
- Understand the technology stack
- See all features and how they work

## 📁 Project Structure

```
EDU-SENSE/
├── app.py                      # Main Streamlit application
├── gap_detector.py             # Learning gap detection engine
├── recommendation_engine.py    # Intervention recommendation system
├── data_generator.py           # Synthetic data generation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Core Components

### 1. LearningGapDetector (gap_detector.py)
- Analyzes student question attempts
- Detects three types of gaps:
  - **Concept Gaps**: Weak understanding of topics
  - **Confidence Gaps**: Hesitation and uncertainty
  - **Speed Gaps**: Rushing without understanding
- Calculates overall performance score

### 2. RecommendationEngine (recommendation_engine.py)
- Generates personalized interventions
- Provides step-by-step action plans
- Estimates improvement timeline
- Prioritizes recommendations by severity

### 3. DataGenerator (data_generator.py)
- Creates realistic synthetic student data
- Models 5 different student profiles
- Generates 5 topics with realistic patterns
- Respects privacy while maintaining realism

## 📊 Data Structure

### Student Question Attempts
```
Student_ID       | STU_1001, STU_1002, ...
Question_ID      | Q_1, Q_2, ...
Topic            | Arithmetic, Fractions, Algebra, ...
Correct          | 0 or 1
Time_Taken       | Seconds (float)
Attempt_Number   | Sequential attempt number
Timestamp        | Date and time of attempt
Profile          | Student learning profile
```

## 🎯 Gap Detection Algorithm

### Concept Gaps
- Tracks accuracy by topic
- Flags topics with <60% accuracy
- Calculates confidence score

### Confidence Gaps
- Identifies excessive time spent with wrong answers
- Detects hesitation patterns
- Severity based on ratio of wrong answers

### Speed Gaps
- Finds fast but incorrect answers
- Indicates rushing behavior
- Suggests deliberate practice

## 📈 Example Workflow

1. **Data Input**: Upload or generate student attempt data
2. **Gap Analysis**: System analyzes patterns automatically
3. **Gap Classification**: Identifies specific types of gaps
4. **Recommendations**: Generates intervention plan
5. **Action**: Teacher implements recommendations
6. **Tracking**: Monitor student progress over time

## 🔐 Privacy & Ethics

- ✅ Uses synthetic data, never stores real student information
- ✅ Focuses on learning patterns, not demographic data
- ✅ Designed to support, not label students
- ✅ Teacher maintains final decision-making authority
- ✅ Fully transparent and explainable

## 🚀 Demo Scenario

### Sample Students Included:
1. **STU_1001**: Strong learner (85% accuracy)
2. **STU_1002**: Average learner (65% accuracy)
3. **STU_1003**: Struggling with Fractions (55% in Fractions, 65% overall)
4. **STU_1004**: Struggling with Algebra
5. **STU_1005-STU_1012**: Various profiles

Each has 15-20 practice attempts across multiple topics.

## 💡 Example Detections

### High Priority Gap
- Student: STU_1003
- Gap: Concept Gap in Fractions
- Severity: HIGH
- Confidence: 55% accuracy vs 65% overall
- Recommendation: 2-3 days focused Fractions review

### Medium Priority Gap
- Student: STU_1005
- Gap: Confidence Gap (slow with wrong answers)
- Severity: MEDIUM
- Recommendation: 1-2 weeks guided problem-solving

## 🎓 Educational Approach

EDU-SENSE follows these principles:
- **Early Intervention**: Catch gaps before they become problems
- **Precision**: Target specific, identifiable gaps
- **Support**: Help students, don't just evaluate them
- **Actionable**: Every recommendation is specific and implementable
- **Ethical**: Respects student privacy and dignity

## 📝 Future Enhancements

- Real-time classroom data integration
- Multilingual support
- Adaptive content generation
- School-level analytics and reporting
- Mobile app for students
- Parent notification system

## ⚙️ Configuration

### Adjust Detection Sensitivity
Edit in `gap_detector.py`:
```python
self.min_attempts_threshold = 3  # Minimum attempts before detecting gaps
```

### Customize Topics
Edit in `data_generator.py`:
```python
topics = ['Arithmetic', 'Fractions', 'Algebra', 'Geometry', 'Data Analysis']
```

## 📞 Support

For questions or feature requests, contact the development team.

## 📄 License

This project is developed for educational purposes.

## 👥 Contributing

To contribute improvements:
1. Make changes in a test environment
2. Validate with sample data
3. Document any new features
4. Test thoroughly before deployment

## 🎉 Acknowledgments

- Inspired by real classroom challenges
- Built with educator feedback
- Focused on practical, usable solutions

---

**Version**: 1.0.0  
**Status**: Demo & Testing  
**Last Updated**: 2025

EDU-SENSE: An AI Second-Teacher for Early Learning Gap Detection
