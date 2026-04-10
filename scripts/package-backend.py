#!/usr/bin/env python3
"""
PyInstaller backend packaging script
"""
import os
import sys
import platform
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
OUTPUT_DIR = ROOT_DIR / "backend-dist"

PYINSTALLER_ARGS = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    f"--distpath={OUTPUT_DIR}",
    "--name=main",
    "--onedir",  # One directory (not one file) for faster startup
    "--windowed" if platform.system() != "Linux" else "",
    str(BACKEND_DIR / "main.py"),
    # Hidden imports
    "--hidden-import=uvicorn.logging",
    "--hidden-import=uvicorn.loops",
    "--hidden-import=uvicorn.loops.auto",
    "--hidden-import=uvicorn.protocols",
    "--hidden-import=uvicorn.protocols.http",
    "--hidden-import=uvicorn.protocols.http.auto",
    "--hidden-import=uvicorn.protocols.websockets",
    "--hidden-import=uvicorn.protocols.websockets.auto",
    "--hidden-import=uvicorn.lifespan",
    "--hidden-import=uvicorn.lifespan.on",
    "--hidden-import=fastapi",
    "--hidden-import=pydantic",
    "--hidden-import=loguru",
    "--hidden-import=aiohttp",
    "--hidden-import=cryptography",
]

# Remove empty args
PYINSTALLER_ARGS = [a for a in PYINSTALLER_ARGS if a]

if __name__ == "__main__":
    print(f"Building backend from: {BACKEND_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    os.chdir(BACKEND_DIR)

    result = subprocess.run(PYINSTALLER_ARGS, check=True)
    if result.returncode == 0:
        print(f"\n✅ Backend built successfully to: {OUTPUT_DIR}")
    else:
        print(f"\n❌ Backend build failed with code: {result.returncode}")
        sys.exit(1)
