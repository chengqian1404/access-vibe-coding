#!/usr/bin/env python3
"""install_dependencies.py — 自动安装并验证所有项目依赖。"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKEND_DIR = REPO_ROOT / "backend"


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


def check_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def install_python_requirements():
    print("\n[1/4] 安装 Python 依赖...")
    req_file = BACKEND_DIR / "requirements.txt"
    if not req_file.exists():
        print(f"  [SKIP] 未找到 {req_file}")
        return

    result = run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
    )
    if result.returncode != 0:
        print("  [ERROR] pip install 失败")
        sys.exit(1)
    print("  [OK] Python 依赖安装完成")


def check_ffmpeg():
    print("\n[2/4] 检查 FFmpeg...")
    if check_command("ffmpeg"):
        result = run(["ffmpeg", "-version"], capture_output=True, text=True)
        ver = result.stdout.split("\n")[0] if result.returncode == 0 else "unknown"
        print(f"  [OK] {ver}")
        return

    print("  [WARN] 未找到 ffmpeg，尝试安装...")
    if sys.platform == "darwin":
        run(["brew", "install", "ffmpeg"])
    elif sys.platform.startswith("linux"):
        run(["sudo", "apt", "install", "-y", "ffmpeg"])
    else:
        print("  [INFO] Windows 请手动安装 FFmpeg：https://ffmpeg.org/download.html")

    if check_command("ffmpeg"):
        print("  [OK] FFmpeg 安装完成")
    else:
        print("  [ERROR] FFmpeg 安装失败，请手动安装后重试")


def check_tesseract():
    print("\n[3/4] 检查 Tesseract OCR...")
    if check_command("tesseract"):
        result = run(["tesseract", "--version"], capture_output=True, text=True)
        ver = result.stdout.split("\n")[0] if result.returncode == 0 else "unknown"
        print(f"  [OK] {ver}")

        # 检查中文语言包
        lang_result = run(["tesseract", "--list-langs"], capture_output=True, text=True)
        if "chi_sim" in lang_result.stdout:
            print("  [OK] 中文简体语言包已安装")
        else:
            print("  [WARN] 未找到中文语言包（chi_sim）")
            if sys.platform.startswith("linux"):
                run(["sudo", "apt", "install", "-y", "tesseract-ocr-chi-sim"])
            elif sys.platform == "darwin":
                run(["brew", "install", "tesseract-lang"])
            else:
                print("  [INFO] 请手动安装 Tesseract 中文语言包")
        return

    print("  [WARN] 未找到 tesseract，尝试安装...")
    if sys.platform == "darwin":
        run(["brew", "install", "tesseract", "tesseract-lang"])
    elif sys.platform.startswith("linux"):
        run(["sudo", "apt", "install", "-y", "tesseract-ocr", "tesseract-ocr-chi-sim"])
    else:
        print("  [INFO] Windows 请从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装")

    if check_command("tesseract"):
        print("  [OK] Tesseract 安装完成")
    else:
        print("  [ERROR] Tesseract 安装失败，请手动安装")


def setup_env_file():
    print("\n[4/4] 检查配置文件...")
    env_file = BACKEND_DIR / ".env"
    example_file = BACKEND_DIR / ".env.example"

    if env_file.exists():
        print(f"  [OK] {env_file} 已存在")
        return

    if example_file.exists():
        import shutil as sh
        sh.copy(example_file, env_file)
        print(f"  [OK] 已从 .env.example 创建 {env_file}")
        print("  [INFO] 请编辑 backend/.env 填写 API 密钥")
    else:
        env_file.write_text(
            "# 直播学习分析工具配置\n"
            "APP_HOST=127.0.0.1\n"
            "APP_PORT=8765\n"
            "DEBUG=false\n"
            "DASHSCOPE_API_KEY=\n"
            "OPENAI_API_KEY=\n"
            "ANTHROPIC_API_KEY=\n"
        )
        print(f"  [OK] 已创建默认 {env_file}")


def main():
    print("=" * 50)
    print("  直播学习分析工具 — 依赖安装脚本")
    print("=" * 50)

    install_python_requirements()
    check_ffmpeg()
    check_tesseract()
    setup_env_file()

    print("\n" + "=" * 50)
    print("  依赖检查完成！")
    print("  如有 [ERROR] 项，请按提示手动安装后重试。")
    print("=" * 50)


if __name__ == "__main__":
    main()
