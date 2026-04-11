#!/usr/bin/env bash
# setup-dev.sh — 一键初始化开发环境

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

info "=== 直播学习分析工具 — 开发环境初始化 ==="
echo ""

# ── 1. 检查 Python 3.10+ ──────────────────────────────────────────────────────
info "检查 Python 版本..."
PYTHON_BIN=""
for cmd in python3.11 python3.10 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_BIN="$cmd"
            info "找到 Python $VER ($cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    error "未找到 Python 3.10+。请先安装 Python 3.10 或更高版本。"
fi

# ── 2. 创建 Python 虚拟环境 ────────────────────────────────────────────────────
info "创建 Python 虚拟环境 backend/venv..."
if [ ! -d "backend/venv" ]; then
    "$PYTHON_BIN" -m venv backend/venv
    info "虚拟环境创建成功"
else
    warn "虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source backend/venv/bin/activate 2>/dev/null || source backend/venv/Scripts/activate 2>/dev/null || \
    error "无法激活虚拟环境，请手动运行：source backend/venv/bin/activate"

# ── 3. 安装 Python 依赖 ────────────────────────────────────────────────────────
info "安装 Python 依赖（backend/requirements.txt）..."
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet
info "Python 依赖安装完成"

# ── 4. 检查 Node.js 18+ ────────────────────────────────────────────────────────
info "检查 Node.js 版本..."
if ! command -v node &>/dev/null; then
    error "未找到 Node.js。请先安装 Node.js 18 或更高版本。"
fi

NODE_VER=$(node -e "process.stdout.write(process.version.slice(1).split('.')[0])" 2>/dev/null || echo "0")
if [ "$NODE_VER" -lt 18 ]; then
    error "Node.js 版本过低（当前 v$NODE_VER），请升级到 18+。"
fi
info "找到 Node.js v$(node --version | tr -d v)"

# ── 5. 安装前端依赖 ────────────────────────────────────────────────────────────
info "安装前端依赖（frontend/）..."
cd frontend && npm install --silent
cd "$REPO_ROOT"
info "前端依赖安装完成"

# ── 6. 创建 .env 文件 ──────────────────────────────────────────────────────────
info "检查配置文件..."
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        info "已从 .env.example 创建 backend/.env，请填写 API 密钥"
    else
        warn "未找到 backend/.env.example，请手动创建 backend/.env"
    fi
else
    warn "backend/.env 已存在，跳过创建"
fi

# ── 7. 创建存储目录 ────────────────────────────────────────────────────────────
info "创建存储目录..."
mkdir -p backend/storage/recordings \
         backend/storage/analyses \
         backend/storage/cache

for dir in recordings analyses cache; do
    if [ ! -f "backend/storage/$dir/.gitkeep" ]; then
        touch "backend/storage/$dir/.gitkeep"
    fi
done
info "存储目录准备完成"

# ── 完成 ───────────────────────────────────────────────────────────────────────
echo ""
info "=== 初始化完成！==="
echo ""
echo "下一步："
echo "  1. 编辑 backend/.env，填写 API 密钥"
echo "  2. 启动后端：cd backend && source venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload"
echo "  3. 启动前端：cd frontend && npm run dev"
echo ""
