@echo off
echo ================================================
echo Building E-Commerce Platform Executable
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install required packages
echo Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller pystray Pillow

REM Install app dependencies
echo Installing application dependencies...
python -m pip install -r requirements.txt

REM Create the executable
echo.
echo Building executable...
python -m PyInstaller --clean --noconfirm ecommerce_app.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build complete!
echo ================================================
echo.
echo The executable is located in: dist\ECommerceApp\
echo Run: dist\ECommerceApp\ECommerceApp.exe
echo.
pause

