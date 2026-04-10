@echo off
REM ── Access Vibe Coding - Windows Build Script ────────────────────────────────
echo Building Access Vibe Coding for Windows...

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Please install Python 3.9+
    exit /b 1
)

REM Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    exit /b 1
)

echo.
echo [1/5] Installing Python dependencies...
cd backend
pip install -r requirements.txt
pip install pyinstaller
cd ..

echo.
echo [2/5] Building Python backend with PyInstaller...
cd backend
python ../scripts/package-backend.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Backend build failed
    exit /b 1
)
cd ..

echo.
echo [3/5] Installing Node.js dependencies...
cd frontend
call npm install
cd ..

echo.
echo [4/5] Building React frontend...
cd frontend
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ERROR: Frontend build failed
    exit /b 1
)
cd ..

echo.
echo [5/5] Packaging with electron-builder...
cd frontend
call npx electron-builder --win
if %ERRORLEVEL% neq 0 (
    echo ERROR: Electron build failed
    exit /b 1
)
cd ..

echo.
echo ✅ Build complete! Check frontend/dist/ for the installer.
echo.
pause
