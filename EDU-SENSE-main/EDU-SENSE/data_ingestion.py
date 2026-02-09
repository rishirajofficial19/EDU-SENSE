import pandas as pd
from datetime import datetime
import io

def load_data(uploaded_file, file_type: str) -> pd.DataFrame:
    """
    Loads data from an uploaded file into a Pandas DataFrame.
    Supports CSV and Excel formats (.csv, .xlsx, .xls).
    """
    if uploaded_file is None:
        return pd.DataFrame()

    try:
        # Normalize file type
        file_type = file_type.lower().strip()
        
        if file_type == 'csv':
            # For CSV files, read from StringIO
            df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode('utf-8')))
        elif file_type in ['xlsx', 'xls', 'excel']:
            # For Excel files, use openpyxl engine for both .xlsx and .xls files
            df = pd.read_excel(
                io.BytesIO(uploaded_file.getvalue()),
                engine='openpyxl',
                sheet_name=0  # Read first sheet by default
            )
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Please upload CSV (.csv) or Excel (.xlsx, .xls) files.")
        
        if df.empty:
            raise ValueError("Uploaded file is empty. Please check the file content.")
            
        return df
    except ValueError as e:
        raise Exception(str(e))
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}. Make sure the file format is correct and contains data.")

def transform_data(raw_df: pd.DataFrame, column_mapping: dict = None) -> pd.DataFrame:
    """
    Transforms the raw DataFrame from external sources into the format expected by EDU-SENSE.
    
    Args:
        raw_df: The DataFrame loaded directly from the external file.
        column_mapping: A dictionary to map raw_df column names to expected EDU-SENSE names.
                        Example: {'Student Name': 'Student_ID', 'Score': 'Correct'}
                        Expected EDU-SENSE columns: 'Student_ID', 'Question_ID', 'Topic', 
                                                    'Correct', 'Time_Taken', 'Timestamp'
    Returns:
        A transformed Pandas DataFrame.
    """
    if raw_df.empty:
        return pd.DataFrame()

    # Default mapping (assuming similar names if not provided)
    default_mapping = {
        'student_id': 'Student_ID',
        'student_roll_no': 'Student_ID',
        'student roll no': 'Student_ID',
        'student id': 'Student_ID',
        'question_id': 'Question_ID',
        'question_no': 'Question_ID',
        'question no': 'Question_ID',
        'question id': 'Question_ID',
        'topic': 'Topic',
        'subject': 'Topic',
        'correct': 'Correct',
        'correct_incorrect': 'Correct',
        'is_correct': 'Correct',
        'score': 'Correct',
        'time_taken': 'Time_Taken',
        'time_per_question': 'Time_Taken',
        'time': 'Time_Taken',
        'duration': 'Time_Taken',
        'timestamp': 'Timestamp',
        'date': 'Timestamp',
        'attempt_number': 'Attempt_Number'
    }

    # Merge default mapping with user-provided mapping
    if column_mapping:
        for key, value in column_mapping.items():
            default_mapping[key.lower()] = value # Ensure keys are lowercase for robust matching

    transformed_df = raw_df.copy()
    
    # Rename columns based on mapping
    renamed_cols = {}
    for raw_col, edu_col in default_mapping.items():
        if raw_col in [col.lower() for col in transformed_df.columns]:
            original_col_name = next(col for col in transformed_df.columns if col.lower() == raw_col)
            renamed_cols[original_col_name] = edu_col
    
    transformed_df = transformed_df.rename(columns=renamed_cols)

    # Ensure required columns exist, adding placeholders if necessary
    required_cols = ['Student_ID', 'Question_ID', 'Topic', 'Correct', 'Time_Taken', 'Timestamp']
    for col in required_cols:
        if col not in transformed_df.columns:
            if col == 'Correct':
                # If 'Correct' is missing, default to 1 (assuming successful attempts)
                transformed_df[col] = 1
            elif col == 'Time_Taken':
                transformed_df[col] = transformed_df['Time_Taken'].mean() if 'Time_Taken' in transformed_df.columns else 60.0 # Default avg time
            elif col == 'Timestamp':
                transformed_df[col] = datetime.now() # Default to current time
            elif col == 'Question_ID':
                transformed_df[col] = 'Q_Unknown_' + (transformed_df.index + 1).astype(str) # Unique ID
            else:
                transformed_df[col] = 'Unknown' # Default for others
                
    # Data type conversions
    # Convert 'Correct' to int (0 or 1)
    if 'Correct' in transformed_df.columns:
        transformed_df['Correct'] = transformed_df['Correct'].apply(lambda x: 1 if pd.to_numeric(x, errors='coerce') > 0.5 else 0)
        
    # Convert 'Time_Taken' to float
    if 'Time_Taken' in transformed_df.columns:
        transformed_df['Time_Taken'] = pd.to_numeric(transformed_df['Time_Taken'], errors='coerce').fillna(transformed_df['Time_Taken'].mean() if not transformed_df['Time_Taken'].empty else 60.0)
        transformed_df['Time_Taken'] = transformed_df['Time_Taken'].apply(lambda x: max(10, x)) # Ensure min time

    # Convert 'Timestamp' to datetime
    if 'Timestamp' in transformed_df.columns:
        # Try to convert to datetime, coerce errors to NaT
        transformed_df['Timestamp'] = pd.to_datetime(transformed_df['Timestamp'], errors='coerce')
        # Fill NaT values with a default or current time
        transformed_df['Timestamp'] = transformed_df['Timestamp'].fillna(datetime.now())
        
    # Ensure Student_ID and Topic are strings
    if 'Student_ID' in transformed_df.columns:
        transformed_df['Student_ID'] = transformed_df['Student_ID'].astype(str)
    if 'Topic' in transformed_df.columns:
        transformed_df['Topic'] = transformed_df['Topic'].astype(str)

    # Reorder columns to match expected format and drop extra ones
    final_cols = ['Student_ID', 'Question_ID', 'Topic', 'Correct', 'Time_Taken', 'Timestamp']
    # Add 'Attempt_Number' if it was part of the original and mapped
    if 'Attempt_Number' in transformed_df.columns:
        final_cols.append('Attempt_Number')

    # Keep only the relevant columns in the expected order
    transformed_df = transformed_df[final_cols]
    
    # Sort by student and timestamp for consistency
    transformed_df = transformed_df.sort_values(by=['Student_ID', 'Timestamp']).reset_index(drop=True)

    return transformed_df
