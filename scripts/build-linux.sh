#!/usr/bin/env bash
# ── Access Vibe Coding - Linux Build Script ───────────────────────────────────
set -e

echo "Building Access Vibe Coding for Linux..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js 18+"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "[1/5] Installing Python dependencies..."
cd "$ROOT_DIR/backend"
pip3 install -r requirements.txt
pip3 install pyinstaller

echo ""
echo "[2/5] Building Python backend with PyInstaller..."
python3 "$ROOT_DIR/scripts/package-backend.py"

echo ""
echo "[3/5] Installing Node.js dependencies..."
cd "$ROOT_DIR/frontend"
npm install

echo ""
echo "[4/5] Building React frontend..."
npm run build

echo ""
echo "[5/5] Packaging with electron-builder..."
npx electron-builder --linux

echo ""
echo "✅ Build complete! Check frontend/dist/ for the AppImage."
