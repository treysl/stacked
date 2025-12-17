@echo off
echo Starting E-Commerce Backend Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found. Installing requirements...
    echo Upgrading pip first...
    python -m pip install --upgrade pip setuptools wheel
    echo Installing dependencies (this may take a few minutes)...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo.
        echo Please try installing manually:
        echo   pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo.
)

REM Check if database exists, if not initialize it
if not exist "database.db" (
    echo Database not found. Initializing database...
    python backend/init_db.py
    if errorlevel 1 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
    echo.
)

REM Start the FastAPI server
echo Starting FastAPI server on http://localhost:8001
echo API docs available at http://localhost:8001/docs
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001

pause

