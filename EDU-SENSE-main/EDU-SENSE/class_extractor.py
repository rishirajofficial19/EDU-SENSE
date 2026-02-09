"""
Utility to extract class/grade level from Student_ID
Supports multiple formats:
- STU_1001_Class6
- STU_1001_6
- STU_1001_class6
- STU1001C6
- etc.
"""

import re


def extract_class_from_student_id(student_id: str) -> int:
    """
    Extract class/grade level from Student_ID.
    
    Args:
        student_id: Student ID string (e.g., "STU_1001_Class6", "STU_1001_6")
        
    Returns:
        Integer class number (e.g., 6, 9, 10, 11, 12) or None if not found
    """
    if not student_id or not isinstance(student_id, str):
        return None
    
    # Convert to lowercase for case-insensitive matching
    sid_lower = student_id.lower()
    
    # Pattern 1: "class" followed by a number (e.g., "Class6", "class 6", "CLASS_6")
    match = re.search(r'class\s*[_-]?\s*(\d+)', sid_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "c" or "gr" or "grade" followed by a number (e.g., "C6", "GR10", "GRADE_9")
    match = re.search(r'(?:c|gr|grade)\s*[_-]?\s*(\d+)', sid_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 3: Just a number at the end (e.g., "STU_1001_6")
    match = re.search(r'[_-](\d)$', sid_lower)
    if match:
        class_num = int(match.group(1))
        # Only accept single digits that are valid class numbers (1-12)
        if 1 <= class_num <= 12:
            return class_num
    
    # Pattern 4: Two digit number (e.g., "STU_1001_09", "STU_1001_12")
    match = re.search(r'[_-](\d{2})$', sid_lower)
    if match:
        class_num = int(match.group(1))
        # Only accept valid class numbers (1-12)
        if 1 <= class_num <= 12:
            return class_num
    
    return None


def extract_classes_from_dataframe(df):
    """
    Extract class from Student_ID for all rows in dataframe.
    
    Args:
        df: DataFrame with Student_ID column
        
    Returns:
        Series with extracted class numbers
    """
    return df['Student_ID'].apply(extract_class_from_student_id)
