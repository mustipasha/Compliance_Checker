#!/usr/bin/env bash
set -e

echo "🚀 Starting Compliance Checker Tool..."

# --- Backend ---
echo "🐍 Starting Backend..."
cd backend

# activate venv
source .venv/bin/activate

# start backend with venv python
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
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait