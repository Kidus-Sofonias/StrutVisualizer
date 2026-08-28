#!/bin/bash

echo ""
echo "  ╔═══════════════════════════════════════════════════════╗"
echo "  ║  STRUCTURAL ENGINEERING ANALYSIS                     ║"
echo "  ║  Section 3.2 — Structural Regularity                 ║"
echo "  ╚═══════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Please install Python 3.10+ from: https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "[INFO] Installing Python dependencies..."
pip3 install -r requirements.txt --quiet
echo "[OK] Dependencies ready."
echo ""

# Build frontend if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    cd frontend && npm install --silent && cd ..
    echo "[OK] Frontend dependencies ready."
    echo ""
fi

# Start backend
echo "[INFO] Starting backend server on http://localhost:8003"
cd backend && python3 -m uvicorn main:app --reload --port 8003 &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
echo "[INFO] Starting frontend dev server on http://localhost:5173"
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "  Application is running!"
echo "  Backend:  http://localhost:8003"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
