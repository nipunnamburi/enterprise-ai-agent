#!/usr/bin/env bash
set -e

echo "================================================================="
echo "  Setting up Enterprise AI Research & Automation Agent"
echo "================================================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# 1. Setup Backend Virtualenv
echo "\n[1/4] Setting up Python virtual environment..."
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
fi
backend/venv/bin/pip install -r backend/requirements.txt

# 2. Generate Sample PDF Documents
echo "\n[2/4] Generating enterprise sample PDF policies..."
backend/venv/bin/python scripts/generate_sample_docs.py

# 3. Seed Database and Vector Store
echo "\n[3/4] Seeding database & Chroma vector store..."
backend/venv/bin/python data/seed/seed_data.py

# 4. Install Frontend Dependencies
echo "\n[4/4] Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "\n================================================================="
echo "  Setup Complete! To start the platform:"
echo "  1. Start Backend:  cd backend && ./venv/bin/uvicorn app.main:app --reload --port 8000"
echo "  2. Start Frontend: cd frontend && npm run dev"
echo "  3. Open Browser:   http://localhost:3000"
echo "================================================================="
