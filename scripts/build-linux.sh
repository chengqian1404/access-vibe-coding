#!/usr/bin/env bash
# build-linux.sh — Linux 生产构建脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo "=============================================="
echo "  直播学习分析工具 - Linux 构建脚本"
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
command -v node &>/dev/null || error "未找到 Node.js，请先安装 Node.js 18+"
NODE_VER=$(node -e "process.stdout.write(process.version.slice(1).split('.')[0])")
[ "$NODE_VER" -lt 18 ] && error "Node.js 版本过低，需要 18+"
info "Node.js: $(node --version)"

# ── 安装系统级构建依赖（AppImage） ───────────────────────────────────────────
info "检查 AppImage 构建依赖..."
if command -v apt &>/dev/null; then
    sudo apt install -y libarchive-tools fakeroot dpkg --quiet 2>/dev/null || \
        info "apt 安装跳过（可能已安装或无权限）"
fi

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
info "打包 Electron 应用（Linux）..."
cd "$REPO_ROOT/frontend"
npx electron-builder --linux

# ── 完成 ─────────────────────────────────────────────────────────────────────
echo ""
echo "=============================================="
info "构建完成！"
echo "  AppImage 位于：$REPO_ROOT/frontend/release/"
echo "  用法：chmod +x *.AppImage && ./*.AppImage"
echo "=============================================="
