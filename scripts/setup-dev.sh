#!/usr/bin/env bash
# ── Access Vibe Coding - Development Setup Script ─────────────────────────────
set -e

echo "Setting up Access Vibe Coding development environment..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# ── Python Backend ────────────────────────────────────────────────────────────
echo ""
echo "[1/3] Setting up Python backend..."
cd "$ROOT_DIR/backend"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate || .venv/Scripts/activate 2>/dev/null || true
pip install -r requirements.txt

# Copy .env.example if .env doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created backend/.env from .env.example - please fill in your API keys"
fi

# ── Node.js Frontend ──────────────────────────────────────────────────────────
echo ""
echo "[2/3] Setting up Node.js frontend..."
cd "$ROOT_DIR/frontend"
npm install

# Copy .env.example if .env doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "No .env.example found for frontend"
fi

# ── Final instructions ────────────────────────────────────────────────────────
echo ""
echo "[3/3] Setup complete!"
echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  To start development:                                       │"
echo "│                                                              │"
echo "│  Terminal 1 (Backend):                                       │"
echo "│    cd backend && python main.py                              │"
echo "│                                                              │"
echo "│  Terminal 2 (Frontend):                                      │"
echo "│    cd frontend && npm start                                  │"
echo "│                                                              │"
echo "│  Don't forget to configure your LLM API keys in:            │"
echo "│    backend/.env                                              │"
echo "│  Or via the Settings page in the app                        │"
echo "└─────────────────────────────────────────────────────────────┘"
