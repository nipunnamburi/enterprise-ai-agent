#!/usr/bin/env bash
set -e

echo "================================================================="
echo "  Setting up Enterprise AI Research & Automation Agent (Native)"
echo "================================================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# 1. Setup Backend Virtualenv
echo "\n[1/4] Setting up Python virtual environment..."
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
fi
backend/venv/bin/pip install -r backend/requirements-api.txt -r backend/requirements-worker.txt

# 2. Ensure local upload directory & sample PDF policies
echo "\n[2/4] Preparing upload directory and sample PDF policies..."
mkdir -p data/uploads
backend/venv/bin/python scripts/generate_sample_docs.py

# 3. Seed Database
echo "\n[3/4] Seeding PostgreSQL database..."
backend/venv/bin/python data/seed/seed_data.py

# 4. Install Frontend Dependencies
echo "\n[4/4] Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "\n================================================================="
echo "  Setup Complete! Start the 3 native processes in separate terminals:"
echo "  1. FastAPI Backend:     cd backend && ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  2. ARQ Ingestion Worker: cd backend && ./venv/bin/arq app.workers.ingestion.WorkerSettings"
echo "  3. Next.js Frontend:    cd frontend && npm run dev"
echo "  Open Browser:           http://localhost:3000"
echo "================================================================="
