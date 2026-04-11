# 直播学习分析工具 (Live Stream Learning Analyzer)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![Node](https://img.shields.io/badge/node-18%2B-brightgreen.svg)

> 自动录制、转录并智能分析微信视频号直播学习课程，提取知识点与问答对，生成结构化学习报告。

---

## ✨ 功能特性

- 🎥 **自动录屏** — 检测微信直播窗口并自动开始/停止录制
- 🎙️ **音频录制** — 同步录制系统音频，支持多设备选择
- 📝 **语音转文字** — 集成 OpenAI Whisper，自动分段转录
- 🔍 **OCR 识别** — 截取直播截图，识别屏幕文字内容
- 🤖 **AI 智能分析** — 调用 LLM（通义千问/GPT/Claude）分析内容，提取重点
- ❓ **问答对提取** — 自动从转录文本与弹幕中提取 Q&A 知识对
- 📊 **报告生成** — 输出 Markdown / Excel 格式的结构化学习报告
- 🔄 **实时监控** — WebSocket 实时推送录制与分析状态
- ⚙️ **灵活配置** — 支持多种 LLM 后端，可自定义提示词与参数

---

## 🚀 快速开始

```bash
# 1. 克隆仓库并安装依赖
git clone https://github.com/your-org/access-vibe-coding.git
cd access-vibe-coding
bash scripts/setup-dev.sh

# 2. 配置 API 密钥（编辑 backend/.env）
cp backend/.env.example backend/.env
# 填入 OPENAI_API_KEY / DASHSCOPE_API_KEY 等

# 3. 启动应用
cd frontend && npm run dev
```

---

## 📸 界面截图

> 截图占位符 — 发布版本将包含完整界面截图

---

## 🛠️ 技术栈

| 层次 | 技术 |
|------|------|
| 桌面框架 | Electron 28 |
| 前端 UI | React 18 + Ant Design 5 |
| 构建工具 | Vite 5 |
| 后端框架 | Python FastAPI |
| 数据库 | SQLite + SQLAlchemy |
| 音视频 | FFmpeg + PyAudio |
| OCR | Tesseract OCR 5 |
| AI 转录 | OpenAI Whisper API |
| AI 分析 | 通义千问 / GPT-4 / Claude |

---

## 📋 系统要求

- **操作系统**：Windows 10+、macOS 12+、Ubuntu 20.04+
- **Python**：3.10 或更高版本
- **Node.js**：18 或更高版本
- **FFmpeg**：最新稳定版
- **Tesseract OCR**：5.x，含中文语言包（`chi_sim`）
- **内存**：建议 8GB+
- **磁盘**：录制文件较大，建议预留 20GB+

---

## 📥 安装

### Windows

```bat
REM 1. 安装 Python 3.10+（勾选 Add to PATH）
REM 2. 安装 Node.js 18+
REM 3. 安装 FFmpeg（加入 PATH）
REM 4. 安装 Tesseract OCR 并下载 chi_sim.traineddata
REM 5. 克隆并初始化
git clone https://github.com/your-org/access-vibe-coding.git
cd access-vibe-coding
scripts\setup-dev.bat
```

### macOS

```bash
brew install python@3.11 node ffmpeg tesseract tesseract-lang
git clone https://github.com/your-org/access-vibe-coding.git
cd access-vibe-coding
bash scripts/setup-dev.sh
```

### Linux (Ubuntu/Debian)

```bash
sudo apt install python3.11 python3.11-venv nodejs ffmpeg \
     tesseract-ocr tesseract-ocr-chi-sim
git clone https://github.com/your-org/access-vibe-coding.git
cd access-vibe-coding
bash scripts/setup-dev.sh
```

---

## ⚙️ 配置

编辑 `backend/.env` 文件，填写所需 API 密钥：

```env
# LLM 配置（至少填写一个）
DASHSCOPE_API_KEY=sk-xxxxxxxx        # 通义千问
OPENAI_API_KEY=sk-xxxxxxxx           # OpenAI GPT
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx    # Anthropic Claude

# Whisper 语音转文字
WHISPER_API_KEY=sk-xxxxxxxx

# 应用配置
APP_HOST=127.0.0.1
APP_PORT=8765
DEBUG=false
```

---

## 📖 使用指南

1. 启动应用后，进入**设置**页面填写 API 密钥
2. 在**监控**页面配置要监听的微信账号
3. 打开微信视频号直播
4. 点击**开始监控**，系统自动检测直播并录制
5. 直播结束后，在**分析**页面点击**开始分析**
6. 分析完成后，在**报告**页面查看问答对与知识摘要
7. 点击**导出**生成 Markdown 或 Excel 报告

---

## 🔨 从源码构建

```bash
# Windows
scripts\build-win.bat

# macOS
bash scripts/build-mac.sh

# Linux
bash scripts/build-linux.sh
```

构建产物位于 `frontend/release/` 目录。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## ⚠️ 免责声明

本工具**仅供个人学习研究使用**，请勿用于录制、传播他人付费课程或任何商业用途。
使用本工具时请遵守相关平台服务条款及法律法规，一切责任由使用者自行承担。
