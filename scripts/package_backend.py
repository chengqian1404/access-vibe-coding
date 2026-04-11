#!/usr/bin/env python3
"""package_backend.py — 使用 PyInstaller 将 FastAPI 后端打包为独立可执行文件。

输出目录：frontend/resources/backend/
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 确保在仓库根目录运行
REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKEND_DIR = REPO_ROOT / "backend"
OUTPUT_DIR = REPO_ROOT / "frontend" / "resources" / "backend"

# PyInstaller 所需的隐式导入（动态加载的模块）
HIDDEN_IMPORTS = [
    # FastAPI / uvicorn
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "fastapi",
    "fastapi.middleware.cors",
    "starlette.routing",
    "starlette.websockets",
    # SQLAlchemy
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.orm",
    "sqlalchemy.ext.asyncio",
    # Pydantic
    "pydantic",
    "pydantic.v1",
    "pydantic_settings",
    # OpenAI / Anthropic / DashScope
    "openai",
    "anthropic",
    "httpx",
    # Audio
    "pyaudio",
    # Image / OCR
    "PIL",
    "PIL.Image",
    "pytesseract",
    "cv2",
    "numpy",
    # Other
    "aiofiles",
    "openpyxl",
    "markdown",
    "psutil",
    "dotenv",
]

# 需要随可执行文件打包的数据文件
DATAS = [
    # (源路径相对 backend/, 目标目录)
    ("storage/recordings/.gitkeep", "storage/recordings"),
    ("storage/analyses/.gitkeep", "storage/analyses"),
    ("storage/cache/.gitkeep", "storage/cache"),
]


def build():
    print("=== 开始打包后端 ===")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    hidden_args = []
    for imp in HIDDEN_IMPORTS:
        hidden_args += ["--hidden-import", imp]

    data_args = []
    for src, dst in DATAS:
        src_abs = BACKEND_DIR / src
        if src_abs.exists():
            sep = ";" if sys.platform == "win32" else ":"
            data_args += ["--add-data", f"{src_abs}{sep}{dst}"]

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name", "backend",
        "--onedir",
        "--noconfirm",
        "--clean",
        f"--distpath={OUTPUT_DIR.parent}",
        f"--workpath={REPO_ROOT / 'build' / 'pyinstaller_work'}",
        f"--specpath={REPO_ROOT / 'build'}",
    ] + hidden_args + data_args + [
        str(BACKEND_DIR / "main.py"),
    ]

    print(f"运行命令：{' '.join(cmd[:6])} ...")
    result = subprocess.run(cmd, cwd=BACKEND_DIR)

    if result.returncode != 0:
        print("[ERROR] PyInstaller 打包失败")
        sys.exit(1)

    print(f"\n[INFO] 打包完成！可执行文件位于：{OUTPUT_DIR}")
    print("=== 后端打包完成 ===")


if __name__ == "__main__":
    build()
