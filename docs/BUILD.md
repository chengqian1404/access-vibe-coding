# 构建打包指南

## 构建可执行文件

### Windows

**前提条件:** Python 3.9+, Node.js 18+, Windows 10/11

```batch
# 运行构建脚本
scripts\build-win.bat
```

输出：`frontend/dist/Access-Vibe-Coding-Setup-1.0.0-x64.exe`

### macOS

**前提条件:** Python 3.9+, Node.js 18+, Xcode Command Line Tools

```bash
chmod +x scripts/build-mac.sh
./scripts/build-mac.sh
```

输出：`frontend/dist/Access-Vibe-Coding-1.0.0-x64.dmg`

### Linux

**前提条件:** Python 3.9+, Node.js 18+

```bash
chmod +x scripts/build-linux.sh
./scripts/build-linux.sh
```

输出：`frontend/dist/Access-Vibe-Coding-1.0.0-x86_64.AppImage`

---

## 构建流程说明

### 第一阶段：打包 Python 后端

使用 PyInstaller 将 Python 应用打包成独立可执行文件：

```bash
cd backend
pip install pyinstaller
python ../scripts/package-backend.py
# 输出到 backend-dist/main/
```

### 第二阶段：构建 React 前端

```bash
cd frontend
npm run build
# 输出到 frontend/dist/
```

### 第三阶段：打包 Electron 应用

electron-builder 将以下内容打包：
- React 构建产物
- Electron 运行时
- Python 后端可执行文件（作为 extraResources）

```bash
cd frontend
npx electron-builder --win  # 或 --mac / --linux
```

---

## 安装包内容

最终安装包包含：
- Electron 应用（前端 UI）
- Python FastAPI 后端（已编译，无需安装 Python）
- 所有依赖（无需额外安装）

用户安装后即可直接使用，唯一需要配置的是 LLM API Key。

---

## GitHub Actions 自动构建

推送 tag 时自动触发构建：

```bash
git tag v1.0.0
git push origin v1.0.0
```

查看 `.github/workflows/build.yml` 了解详细流程。
