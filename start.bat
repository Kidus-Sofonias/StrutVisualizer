@echo off
title Structural Engineering Analysis
color 0B

echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║  STRUCTURAL ENGINEERING ANALYSIS                     ║
echo  ║  Section 3.2 — Structural Regularity                 ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Install dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] Some dependencies may not have installed correctly.
)
echo [OK] Dependencies ready.
echo.

REM Build frontend if needed
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    call npm install --silent
    cd ..
    echo [OK] Frontend dependencies ready.
    echo.
)

REM Start backend
echo [INFO] Starting backend server on http://localhost:8000
echo [INFO] Starting frontend dev server on http://localhost:5173
echo.
echo Press Ctrl+C to stop.
echo.

REM Start both servers
start "Backend" cmd /c "cd backend && python -m uvicorn main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo  Application is running!
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
pause
