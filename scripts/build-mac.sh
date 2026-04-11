#!/usr/bin/env bash
# build-mac.sh — macOS 生产构建脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo "=============================================="
echo "  直播学习分析工具 - macOS 构建脚本"
echo "=============================================="
echo ""

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# ── 检查依赖 ──────────────────────────────────────────────────────────────────
info "检查 Python..."
PYTHON_BIN=""
for cmd in python3.11 python3.10 python3; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_BIN="$cmd"
            break
        fi
    fi
done
[ -z "$PYTHON_BIN" ] && error "未找到 Python 3.10+，请先安装"
info "Python: $("$PYTHON_BIN" --version)"

info "检查 Node.js..."
command -v node &>/dev/null || error "未找到 Node.js，请先安装"
NODE_VER=$(node -e "process.stdout.write(process.version.slice(1).split('.')[0])")
[ "$NODE_VER" -lt 18 ] && error "Node.js 版本过低，需要 18+"
info "Node.js: $(node --version)"

# ── 1. 构建 React 前端 ────────────────────────────────────────────────────────
info ""
info "安装前端依赖并构建 React..."
cd "$REPO_ROOT/frontend"
npm install
npm run build:react
info "React 构建完成"

# ── 2. 打包 Python 后端 ───────────────────────────────────────────────────────
info ""
info "打包 Python 后端（PyInstaller）..."
cd "$REPO_ROOT"

if [ -f "backend/venv/bin/activate" ]; then
    source backend/venv/bin/activate
fi

pip install pyinstaller --quiet
"$PYTHON_BIN" scripts/package_backend.py
info "后端打包完成"

# ── 3. 打包 Electron 应用 ─────────────────────────────────────────────────────
info ""
info "打包 Electron 应用（macOS）..."
cd "$REPO_ROOT/frontend"
npx electron-builder --mac

# ── 完成 ─────────────────────────────────────────────────────────────────────
echo ""
echo "=============================================="
info "构建完成！"
echo "  DMG 位于：$REPO_ROOT/frontend/release/"
echo "=============================================="
