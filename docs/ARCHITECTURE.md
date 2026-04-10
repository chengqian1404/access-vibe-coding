# 系统架构文档

## 概述

Access Vibe Coding 是一个跨平台桌面应用，使用 Electron + React 作为前端，Python FastAPI 作为后端，通过 LLM API 理解自然语言指令，并使用 pyautogui/pywin32 控制 Microsoft Access。

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     用户界面 (Electron)                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              React 前端 (http://localhost:5173)          │ │
│  │  InstructionInput → ExecutionPanel → LogViewer           │ │
│  │  ScreenshotPreview → Sidebar → Settings                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                         ↕ IPC / HTTP                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Electron 主进程 (main.js)                    │ │
│  │  - 窗口管理  - 后端进程管理  - 系统对话框               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         ↕ HTTP REST / WebSocket
┌─────────────────────────────────────────────────────────────┐
│                  后端服务 (FastAPI :8765)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  LLM Service │  │  Instruction  │  │ Access Automation │  │
│  │  - OpenAI    │→ │  Parser       │→ │  - pyautogui     │  │
│  │  - Qwen      │  │  - 解析指令   │  │  - pywin32/COM   │  │
│  │  - Claude    │  │  - 生成步骤   │  │  - 截图服务      │  │
│  │  - DeepSeek  │  └──────────────┘  └──────────────────┘  │
│  │  - Ollama    │                                            │
│  └──────────────┘                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Config Manager + Session Manager                      │   │
│  │  - 加密存储 API Key  - 历史记录  - 会话管理           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         ↕ LLM API
┌─────────────────────────────────────────────────────────────┐
│                      LLM 提供商                               │
│  OpenAI API │ 通义千问 API │ Claude API │ DeepSeek API       │
│  Ollama（本地）                                               │
└─────────────────────────────────────────────────────────────┘
```

## 数据流

```
用户输入指令
    ↓
前端验证 & 发送到后端
    ↓
LLM Service 解析自然语言
    ↓
Instruction Parser 生成操作序列
    ↓
Access Automation 执行鼠标/键盘操作
    ↓
Screenshot Service 截图反馈
    ↓
WebSocket 实时推送进度到前端
    ↓
前端展示结果
```

## 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Electron | ^28 | 桌面应用框架 |
| React | ^18 | UI 框架 |
| Ant Design | ^5 | UI 组件库 |
| Vite | ^5 | 构建工具 |
| React Router | ^6 | 路由管理 |
| Axios | ^1.6 | HTTP 客户端 |

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 运行时 |
| FastAPI | ^0.104 | Web 框架 |
| Uvicorn | ^0.24 | ASGI 服务器 |
| Pydantic | ^2 | 数据验证 |
| OpenAI | ^1.3 | LLM 客户端 |
| Anthropic | ^0.7 | Claude 客户端 |
| pyautogui | ^0.9 | 自动化控制 |
| pywin32 | ^306 | Windows COM |
| Pillow | ^10 | 图像处理 |
| Cryptography | ^41 | API 密钥加密 |

## 安全设计

- API 密钥使用 Fernet 对称加密存储在本地
- 加密密钥存储在 `~/.access-vibe-coding/.key`，权限设为 600
- 前端通过 contextBridge 隔离，禁止直接访问 Node.js API
- Content Security Policy 限制脚本和资源加载
- 所有 API 只监听 127.0.0.1（本地回环）
