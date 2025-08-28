@echo off
echo ============================================================
echo    Karnataka Village Population Visualization
echo ============================================================
echo.
echo Starting the application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Start the application
python start_app.py

REM If the script exits, pause to see any error messages
pause
