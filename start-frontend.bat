@echo off
echo Starting Frontend Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Frontend will be available at http://localhost:8080
echo Open http://localhost:8080/index.html in your browser
echo Press Ctrl+C to stop the server
echo.

cd frontend
python -m http.server 8080

