"""
Test file upload functionality for CSV and Excel files.
This verifies that the data_ingestion module correctly handles both formats.
"""

import pandas as pd
import io
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_ingestion import load_data, transform_data

class MockUploadFile:
    """Mock Streamlit file_uploader object for testing"""
    def __init__(self, data_bytes, filename):
        self.data = data_bytes
        self.name = filename
    
    def getvalue(self):
        return self.data


def test_csv_upload():
    """Test CSV file upload and loading"""
    print("\n" + "="*50)
    print("Testing CSV Upload...")
    print("="*50)
    
    # Create sample CSV data
    sample_data = {
        'student_id': ['STU_1001', 'STU_1001', 'STU_1002', 'STU_1002'],
        'question_id': ['Q_1', 'Q_2', 'Q_1', 'Q_3'],
        'topic': ['Arithmetic', 'Fractions', 'Arithmetic', 'Algebra'],
        'correct': [1, 0, 1, 1],
        'time_taken': [45.5, 120.3, 38.2, 55.0],
        'timestamp': ['2025-01-15 10:30:00', '2025-01-15 10:35:00', '2025-01-16 09:20:00', '2025-01-16 09:45:00']
    }
    
    df = pd.DataFrame(sample_data)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    
    # Create mock file
    mock_file = MockUploadFile(csv_bytes, 'test_data.csv')
    
    try:
        # Test load_data function
        loaded_df = load_data(mock_file, 'csv')
        print(f"✅ CSV loaded successfully!")
        print(f"   Records: {len(loaded_df)}")
        print(f"   Columns: {list(loaded_df.columns)}")
        
        # Test transform_data function
        transformed_df = transform_data(loaded_df)
        print(f"✅ CSV transformed successfully!")
        print(f"   Records: {len(transformed_df)}")
        print(f"   Columns: {list(transformed_df.columns)}")
        print(f"\n   First 2 rows:")
        print(transformed_df.head(2).to_string())
        
        return True
    except Exception as e:
        print(f"❌ CSV test failed: {e}")
        return False


def test_xlsx_upload():
    """Test Excel (.xlsx) file upload and loading"""
    print("\n" + "="*50)
    print("Testing XLSX Upload...")
    print("="*50)
    
    # Create sample Excel data
    sample_data = {
        'Student_ID': ['STU_2001', 'STU_2001', 'STU_2002', 'STU_2002'],
        'Question_ID': ['Q_101', 'Q_102', 'Q_101', 'Q_103'],
        'Topic': ['Geometry', 'Data Analysis', 'Geometry', 'Algebra'],
        'Correct': [1, 0, 1, 1],
        'Time_Taken': [50.0, 150.5, 42.1, 60.3],
        'Timestamp': ['2025-01-20 11:00:00', '2025-01-20 11:15:00', '2025-01-21 10:00:00', '2025-01-21 10:30:00']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Save to BytesIO as Excel
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name='Sheet1', engine='openpyxl')
    buffer.seek(0)
    xlsx_bytes = buffer.getvalue()
    
    # Create mock file
    mock_file = MockUploadFile(xlsx_bytes, 'test_data.xlsx')
    
    try:
        # Test load_data function
        loaded_df = load_data(mock_file, 'xlsx')
        print(f"✅ XLSX loaded successfully!")
        print(f"   Records: {len(loaded_df)}")
        print(f"   Columns: {list(loaded_df.columns)}")
        
        # Test transform_data function
        transformed_df = transform_data(loaded_df)
        print(f"✅ XLSX transformed successfully!")
        print(f"   Records: {len(transformed_df)}")
        print(f"   Columns: {list(transformed_df.columns)}")
        print(f"\n   First 2 rows:")
        print(transformed_df.head(2).to_string())
        
        return True
    except Exception as e:
        print(f"❌ XLSX test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_xls_upload():
    """Test Excel (.xls) file upload and loading"""
    print("\n" + "="*50)
    print("Testing XLS Upload...")
    print("="*50)
    
    # Create sample Excel data
    sample_data = {
        'student_id': ['STU_3001', 'STU_3001', 'STU_3002'],
        'question_id': ['Q_201', 'Q_202', 'Q_201'],
        'topic': ['Physics', 'Chemistry', 'Physics'],
        'correct': [1, 1, 0],
        'time_taken': [35.2, 40.1, 95.5],
        'timestamp': ['2025-02-01 09:00:00', '2025-02-01 09:15:00', '2025-02-02 14:30:00']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Save to BytesIO as Excel
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name='Sheet1', engine='openpyxl')
    buffer.seek(0)
    xls_bytes = buffer.getvalue()
    
    # Create mock file
    mock_file = MockUploadFile(xls_bytes, 'test_data.xls')
    
    try:
        # Test load_data function
        loaded_df = load_data(mock_file, 'xls')
        print(f"✅ XLS loaded successfully!")
        print(f"   Records: {len(loaded_df)}")
        print(f"   Columns: {list(loaded_df.columns)}")
        
        # Test transform_data function
        transformed_df = transform_data(loaded_df)
        print(f"✅ XLS transformed successfully!")
        print(f"   Records: {len(transformed_df)}")
        print(f"   Columns: {list(transformed_df.columns)}")
        
        return True
    except Exception as e:
        print(f"❌ XLS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling for invalid files"""
    print("\n" + "="*50)
    print("Testing Error Handling...")
    print("="*50)
    
    test_cases = [
        ("empty file", MockUploadFile(b'', 'empty.csv'), 'csv', False),
        ("invalid type", MockUploadFile(b'invalid', 'test.txt'), 'txt', False),
    ]
    
    results = []
    for test_name, mock_file, file_type, should_succeed in test_cases:
        try:
            loaded_df = load_data(mock_file, file_type)
            if should_succeed:
                print(f"✅ {test_name}: Correctly handled")
                results.append(True)
            else:
                print(f"❌ {test_name}: Should have failed but didn't")
                results.append(False)
        except Exception as e:
            if not should_succeed:
                print(f"✅ {test_name}: Correctly rejected - {str(e)[:50]}...")
                results.append(True)
            else:
                print(f"❌ {test_name}: Unexpected error - {e}")
                results.append(False)
    
    return all(results)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("EDU-SENSE FILE UPLOAD TEST SUITE")
    print("="*50)
    
    results = []
    
    # Run all tests
    results.append(("CSV Upload", test_csv_upload()))
    results.append(("XLSX Upload", test_xlsx_upload()))
    results.append(("XLS Upload", test_xls_upload()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if all_passed:
        print("\n🎉 All tests passed! File upload feature is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        sys.exit(1)
