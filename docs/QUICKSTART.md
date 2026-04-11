# ⚡ 5 分钟快速入门

本文档帮助你在 5 分钟内完成环境搭建并录制第一场直播。

---

## 前置条件

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 18+ | 前端构建与 Electron |
| FFmpeg | 5.0+ | 音视频录制与处理 |
| Tesseract OCR | 5.x | 截图文字识别 |

---

## 安装步骤

**1. 安装系统依赖**

- macOS：`brew install python@3.11 node ffmpeg tesseract tesseract-lang`
- Ubuntu：`sudo apt install python3.11-venv nodejs ffmpeg tesseract-ocr tesseract-ocr-chi-sim`
- Windows：从官网下载并安装 Python、Node.js、FFmpeg、Tesseract

**2. 克隆仓库**

```bash
git clone https://github.com/your-org/access-vibe-coding.git
cd access-vibe-coding
```

**3. 运行一键初始化脚本**

```bash
bash scripts/setup-dev.sh
```

脚本将自动：创建 Python 虚拟环境、安装后端依赖、安装前端依赖、创建配置文件。

**4. 配置 API 密钥**

```bash
# 编辑 backend/.env，填写至少一个 LLM API Key
nano backend/.env
```

最简配置（使用通义千问）：

```env
DASHSCOPE_API_KEY=sk-你的密钥
WHISPER_API_KEY=sk-你的OpenAI密钥
```

**5. 启动应用**

```bash
cd frontend
npm run dev
```

---

## 首次运行配置

应用启动后：

1. 点击顶部导航栏 **⚙️ 设置**
2. 在「LLM 配置」中选择 AI 提供商并填入 API Key
3. 在「录制配置」中选择音频输入设备
4. 点击**保存配置**

---

## 开始第一次录制

1. 打开微信，进入目标视频号直播间
2. 在应用中点击 **🖥️ 监控** 页面
3. 输入目标直播关键词（如主播名称）
4. 点击 **开始监控**
5. 系统检测到直播后自动开始录制，状态栏变为 🔴 录制中

---

## 查看分析结果

录制结束后：

1. 进入 **📊 分析** 页面，选择刚录制的文件
2. 点击 **开始分析**，等待 AI 处理（约 2-5 分钟）
3. 分析完成后进入 **📋 报告** 页面
4. 查看自动提取的问答对、知识摘要
5. 点击 **导出** 下载 Markdown 或 Excel 格式报告
