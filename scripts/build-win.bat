@echo off
REM build-win.bat — Windows 生产构建脚本
setlocal enabledelayedexpansion

echo ==============================================
echo   直播学习分析工具 - Windows 构建脚本
echo ==============================================
echo.

REM ── 检查 Python ──────────────────────────────────────────────────────────────
echo [INFO] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.10+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [INFO] Python 版本: %PYVER%

REM ── 检查 Node.js ─────────────────────────────────────────────────────────────
echo [INFO] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 18+
    exit /b 1
)
for /f %%i in ('node --version') do set NODEVER=%%i
echo [INFO] Node.js 版本: %NODEVER%

REM ── 切换到仓库根目录 ─────────────────────────────────────────────────────────
cd /d "%~dp0.."
set REPO_ROOT=%CD%

REM ── 1. 构建 React 前端 ────────────────────────────────────────────────────────
echo.
echo [INFO] 安装前端依赖并构建 React...
cd "%REPO_ROOT%\frontend"
call npm install
if errorlevel 1 ( echo [ERROR] npm install 失败 & exit /b 1 )

call npm run build:react
if errorlevel 1 ( echo [ERROR] React 构建失败 & exit /b 1 )
echo [INFO] React 构建完成

REM ── 2. 打包 Python 后端 ───────────────────────────────────────────────────────
echo.
echo [INFO] 打包 Python 后端（PyInstaller）...
cd "%REPO_ROOT%"

REM 激活虚拟环境（如果存在）
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate.bat
)

pip install pyinstaller --quiet
if errorlevel 1 ( echo [ERROR] PyInstaller 安装失败 & exit /b 1 )

python scripts\package_backend.py
if errorlevel 1 ( echo [ERROR] 后端打包失败 & exit /b 1 )
echo [INFO] 后端打包完成

REM ── 3. 打包 Electron 应用 ─────────────────────────────────────────────────────
echo.
echo [INFO] 打包 Electron 应用（Windows）...
cd "%REPO_ROOT%\frontend"

call npx electron-builder --win
if errorlevel 1 ( echo [ERROR] Electron 打包失败 & exit /b 1 )

REM ── 完成 ─────────────────────────────────────────────────────────────────────
echo.
echo ==============================================
echo   构建完成！
echo   安装包位于：%REPO_ROOT%\frontend\release\
echo ==============================================

cd "%REPO_ROOT%"
endlocal
