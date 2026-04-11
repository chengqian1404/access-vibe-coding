# 系统架构文档

---

## 系统总览

```
┌─────────────────────────────────────────────────────┐
│                   Electron 主进程                    │
│  ┌────────────────────────────────────────────────┐  │
│  │              React 渲染进程 (前端)              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │  │
│  │  │ 监控页面 │ │ 录制页面 │ │ 分析/报告页面  │  │  │
│  │  └──────────┘ └──────────┘ └────────────────┘  │  │
│  │           Ant Design 5 UI 组件库                │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │ HTTP REST + WebSocket             │
└───────────────────┼─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│            FastAPI 后端 (Python, :8765)              │
│  ┌─────────────────────────────────────────────────┐ │
│  │                   API 层                        │ │
│  │  routes.py (REST)    websocket.py (WS)          │ │
│  └──────────────────┬──────────────────────────────┘ │
│  ┌───────────────────▼─────────────────────────────┐ │
│  │                 服务层 (Services)               │ │
│  │  MonitorService  ScreenRecorder  AudioRecorder  │ │
│  │  AudioProcessor  OcrEngine       ContentAnalyzer│ │
│  │  QaExtractor     ReportGenerator ConfigManager  │ │
│  └──────────────────┬──────────────────────────────┘ │
│  ┌───────────────────▼─────────────────────────────┐ │
│  │              数据层 (SQLAlchemy + SQLite)        │ │
│  │           backend/storage/app.db                │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │              │               │
    FFmpeg/PyAudio   Tesseract      OpenAI API
                      OCR          / DashScope
```

---

## 前端架构

**技术栈**：Electron 28 + React 18 + Ant Design 5 + Vite 5

```
frontend/
├── main.js          # Electron 主进程入口
├── preload.js       # 安全 IPC 桥接
├── src/
│   ├── App.jsx      # 根组件，路由配置
│   ├── pages/       # 页面级组件
│   ├── components/  # 可复用 UI 组件
│   ├── hooks/       # 自定义 React Hooks
│   ├── services/    # API 调用封装
│   └── store/       # 全局状态（Zustand）
└── vite.config.js
```

### 状态管理

使用 Zustand 轻量状态库，按功能域拆分 store：
- `useRecordingStore` — 录制状态
- `useAnalysisStore` — 分析任务队列
- `useSettingsStore` — 用户配置（持久化）

---

## 后端架构

**技术栈**：FastAPI + SQLAlchemy 2.0 + SQLite + Pydantic v2

```
backend/app/
├── main.py          # FastAPI 应用实例，挂载路由
├── api/
│   ├── routes.py    # REST API 路由定义
│   └── websocket.py # WebSocket 连接管理
├── services/        # 核心业务逻辑
├── config/          # 配置加载（pydantic-settings）
├── models/          # SQLAlchemy ORM 模型
└── utils/           # 工具函数
```

### 服务层说明

| 服务 | 职责 |
|------|------|
| `MonitorService` | 定时检测微信直播窗口是否存在 |
| `ScreenRecorder` | 调用 FFmpeg 录制指定屏幕区域 |
| `AudioRecorder` | 通过 PyAudio / FFmpeg 录制系统音频 |
| `AudioProcessor` | 音频分段、格式转换，调用 Whisper API |
| `OcrEngine` | 截图并调用 Tesseract 识别中文文字 |
| `ContentAnalyzer` | 调用 LLM 分析转录文本，提取知识点 |
| `QaExtractor` | 从分析结果中结构化提取问答对 |
| `ReportGenerator` | 将分析结果渲染为 Markdown / Excel |
| `ConfigManager` | 读写用户配置，验证 API 连通性 |

---

## 数据流

```
直播开始
   │
   ▼
MonitorService 检测到直播
   │
   ├──► ScreenRecorder ──► video.mp4
   │
   └──► AudioRecorder  ──► audio.wav
                              │
                              ▼
                       AudioProcessor
                       (Whisper 转录)
                              │
                              ▼
                       transcript.json
                              │
                 ┌────────────┤
                 │            │
                 ▼            ▼
           OcrEngine    ContentAnalyzer
           (截图识别)    (LLM 分析)
                 │            │
                 └─────┬──────┘
                       │
                       ▼
                  QaExtractor
                  (提取问答对)
                       │
                       ▼
                 ReportGenerator
                 (.md / .xlsx)
```

---

## WebSocket 通信协议

后端在 `ws://localhost:8765/ws` 暴露 WebSocket 端点。

### 消息格式（JSON）

```json
{
  "type": "status_update",
  "data": {
    "recording": false,
    "monitoring": true,
    "analysis_progress": 45
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 消息类型

| type | 方向 | 说明 |
|------|------|------|
| `status_update` | 服务端 → 客户端 | 录制/分析状态变更 |
| `analysis_progress` | 服务端 → 客户端 | 分析进度百分比 |
| `log_message` | 服务端 → 客户端 | 实时日志推送 |
| `start_recording` | 客户端 → 服务端 | 请求开始录制 |
| `stop_recording` | 客户端 → 服务端 | 请求停止录制 |
| `ping` / `pong` | 双向 | 心跳保活 |

---

## 数据库结构

```sql
-- 录制会话
recordings (id, title, start_time, end_time, video_path, audio_path, status)

-- 分析任务
analyses (id, recording_id, status, created_at, completed_at)

-- 转录结果
transcripts (id, analysis_id, start_sec, end_sec, text, speaker)

-- 问答对
qa_pairs (id, analysis_id, question, answer, confidence, topic)

-- 应用配置
configs (key, value, updated_at)
```
