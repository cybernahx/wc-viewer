@echo off
echo 🚀 Starting WhatsApp Chat Viewer - Professional Edition
echo =====================================================

REM Navigate to project root
cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please ensure the .venv folder exists with Python installed.
    pause
    exit /b 1
)

echo 📱 Launching AI-Enhanced Chat Analysis Tool...
echo 🏗️  Using Professional Project Structure...
echo.

REM Run the launcher from project root
".venv\Scripts\python.exe" launcher.py

REM If there's an error, pause to see the message
if errorlevel 1 (
    echo.
    echo ❌ Application exited with an error.
    pause
)

echo.
echo ✅ Application closed successfully.
pause
