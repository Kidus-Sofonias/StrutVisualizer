@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo       STRUCTURAL APP - TABLES 3.2.2-3.2.5
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    where python >nul 2>nul
    if errorlevel 1 (
        echo.
        echo ERROR: Python was not found on PATH.
        echo Please install Python 3.13 and make sure "python" is available in Command Prompt.
        pause
        exit /b 1
    )
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: Could not create the virtual environment.
        pause
        exit /b 1
    )
)

echo Installing/checking required packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    echo Check your internet connection and Python installation.
    pause
    exit /b 1
)

echo.
echo Starting Structural App...
echo.
echo The application will be available at:
echo http://127.0.0.1:8000
echo.
echo Keep this window open while using the application.
echo Press CTRL+C to stop the server.
echo.

start "" http://127.0.0.1:8000/
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
