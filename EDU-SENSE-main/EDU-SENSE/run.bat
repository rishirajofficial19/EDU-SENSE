@echo off
REM EDU-SENSE Installation and Launch Script
REM This script installs dependencies and launches the application

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     EDU-SENSE: Learning Gap Detection System                  ║
echo ║     Installation and Launch Script                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✓ Python detected: 
python --version
echo.

REM Install requirements
echo Installing required packages...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to install requirements
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ✓ All packages installed successfully!
echo.

REM Launch Streamlit
echo Launching EDU-SENSE application...
echo.
echo 🚀 The application will open automatically in your browser
echo    Default URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py
