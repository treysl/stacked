@echo off
echo Stopping E-Commerce Backend Server...
echo.

REM Find process using port 8001 and kill it
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001 ^| findstr LISTENING') do (
    echo Found process on port 8001 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
    if errorlevel 1 (
        echo Failed to stop process %%a
    ) else (
        echo Successfully stopped process %%a
    )
)

REM Also try to kill any python processes running uvicorn
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /I "PID"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /I "uvicorn" >nul
    if not errorlevel 1 (
        echo Stopping uvicorn process (PID: %%a)...
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo.
echo Server stopped (if it was running).
pause

