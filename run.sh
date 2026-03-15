#!/usr/bin/env bash
set -e

echo "🚀 Starting Compliance Checker Tool..."

# --- Kill existing processes on ports ---
echo "🧹 Cleaning up existing processes on ports 8000 and 5173..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# --- Backend ---
echo "🐍 Starting Backend..."
cd backend
source .venv/bin/activate
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# --- Frontend ---
echo "🎨 Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🛑 Press Ctrl+C to stop both services."

# kill both on Ctrl+C
trap "kill -9 $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait