"""
Configuration file for EDU-SENSE system.
Adjust these settings to customize the system behavior.
"""

# ===== GAP DETECTION CONFIGURATION =====
GAP_DETECTION = {
    'min_attempts_threshold': 3,      # Minimum attempts before detecting gaps
    'concept_gap_threshold': 0.60,    # Accuracy threshold for concept gaps
    'confidence_time_multiplier': 1.5, # Time multiplier for confidence gaps
    'speed_time_multiplier': 0.5,     # Time multiplier for speed gaps
}

# ===== SEVERITY THRESHOLDS =====
SEVERITY_THRESHOLDS = {
    'concept_gap': {
        'high': 0.40,    # Accuracy below 40% = high severity
        'medium': 0.70,  # Accuracy below 70% = medium severity
    },
    'confidence_gap': {
        'high': 0.70,    # Wrong answer ratio above 70% = high severity
        'medium': 0.50,  # Wrong answer ratio above 50% = medium severity
    }
}

# ===== STUDENT PROFILES FOR DATA GENERATION =====
STUDENT_PROFILES = {
    'Strong': {
        'accuracy': 0.85,
        'base_time': 45,
        'time_variance': 15,
        'improvement_trend': 0.02,
        'count': 3
    },
    'Average': {
        'accuracy': 0.65,
        'base_time': 60,
        'time_variance': 20,
        'improvement_trend': 0.01,
        'count': 4
    },
    'Struggling': {
        'accuracy': 0.45,
        'base_time': 80,
        'time_variance': 25,
        'improvement_trend': -0.01,
        'count': 2
    },
    'Gap_in_Fractions': {
        'accuracy': 0.55,
        'base_time': 70,
        'time_variance': 20,
        'improvement_trend': 0.005,
        'weak_topic': 'Fractions',
        'count': 2
    },
    'Gap_in_Algebra': {
        'accuracy': 0.60,
        'base_time': 75,
        'time_variance': 25,
        'improvement_trend': 0.005,
        'weak_topic': 'Algebra',
        'count': 1
    }
}

# ===== TOPICS =====
TOPICS = [
    'Arithmetic',
    'Fractions',
    'Algebra',
    'Geometry',
    'Data Analysis',
    'Physics',
    'Chemistry'
]

# ===== DATA GENERATION SETTINGS =====
DATA_GENERATION = {
    'num_students': 12,
    'num_questions': 50,
    'attempts_per_student_min': 15,
    'attempts_per_student_max': 20,
    'days_back_max': 30,
    'min_time_taken': 10,  # seconds
    'random_seed': 42  # For reproducibility
}

# ===== RECOMMENDATION SETTINGS =====
RECOMMENDATIONS = {
    'max_recommendations': 5,
    'time_estimates': {
        'high': '2-3 weeks',
        'medium': '1-2 weeks',
        'low': '3-5 days'
    },
    'expected_impact': {
        'concept_gap': 0.25,
        'confidence_gap': 0.20,
        'speed_gap': 0.15,
        'maintenance': 0.10
    }
}

# ===== UI SETTINGS =====
UI = {
    'page_title': 'EDU-SENSE: Learning Gap Detection',
    'page_icon': '🧠',
    'layout': 'wide',
    'show_version': True,
    'version': '1.0.0'
}

# ===== LOGGING =====
LOGGING = {
    'enabled': True,
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'save_logs': False,
    'log_file': 'edu_sense.log'
}

# ===== PRIVACY SETTINGS =====
PRIVACY = {
    'anonymize_data': True,
    'use_synthetic_data': True,
    'store_results_locally': False,
    'gdpr_compliant': True
}

# ===== THRESHOLD ADJUSTMENTS FOR DIFFERENT SCENARIOS =====

# For early detection (catch gaps sooner)
EARLY_DETECTION_MODE = {
    'concept_gap_threshold': 0.70,  # Lower threshold = catch earlier
    'min_attempts_threshold': 2,    # Fewer attempts needed
}

# For conservative detection (only clear gaps)
CONSERVATIVE_MODE = {
    'concept_gap_threshold': 0.50,  # Higher threshold = only clear gaps
    'min_attempts_threshold': 5,    # More attempts needed
}

# Default mode
DETECTION_MODE = 'standard'  # 'standard', 'early_detection', or 'conservative'

def get_active_config():
    """Get the currently active configuration."""
    if DETECTION_MODE == 'early_detection':
        config = GAP_DETECTION.copy()
        config.update(EARLY_DETECTION_MODE)
        return config
    elif DETECTION_MODE == 'conservative':
        config = GAP_DETECTION.copy()
        config.update(CONSERVATIVE_MODE)
        return config
    else:
        return GAP_DETECTION
