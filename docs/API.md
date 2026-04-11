# API 参考文档

后端服务运行于 `http://localhost:8765`，所有接口均为本地调用，无需认证。

---

## REST 接口

### 系统状态

#### `GET /api/status`
获取应用整体运行状态。

**响应示例：**
```json
{
  "recording": false,
  "monitoring": true,
  "analysis_running": false,
  "uptime_seconds": 3600,
  "version": "1.0.0"
}
```

---

### 配置管理

#### `GET /api/config`
获取当前配置。

```json
{
  "llm_provider": "qwen",
  "llm_model": "qwen-max",
  "audio_device": "default",
  "check_interval": 30
}
```

#### `POST /api/config`
更新配置。

**请求体：**
```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "openai_api_key": "sk-xxx"
}
```

**响应：**
```json
{ "success": true, "message": "配置已保存" }
```

---

### 录制控制

#### `GET /api/recordings`
获取录制文件列表。

```json
[
  {
    "id": 1,
    "title": "直播录制_20240101_120000",
    "start_time": "2024-01-01T12:00:00",
    "end_time": "2024-01-01T14:00:00",
    "duration_seconds": 7200,
    "video_path": "storage/recordings/rec_001.mp4",
    "status": "completed"
  }
]
```

#### `POST /api/recordings/start`
开始录制。

**请求体：**
```json
{
  "title": "手动录制",
  "audio_device": "default",
  "screen_region": { "x": 0, "y": 0, "width": 1920, "height": 1080 }
}
```

#### `POST /api/recordings/stop`
停止当前录制。

```json
{ "success": true, "recording_id": 1 }
```

#### `DELETE /api/recordings/{id}`
删除指定录制文件。

---

### 分析任务

#### `GET /api/analyses`
获取所有分析任务列表。

#### `POST /api/analyses`
创建分析任务。

**请求体：**
```json
{
  "recording_id": 1,
  "enable_transcription": true,
  "enable_ocr": true,
  "enable_ai_analysis": true,
  "enable_qa_extraction": true
}
```

**响应：**
```json
{ "analysis_id": 5, "status": "queued" }
```

#### `GET /api/analyses/{id}`
获取分析任务详情与结果。

```json
{
  "id": 5,
  "status": "completed",
  "progress": 100,
  "qa_pairs": [
    {
      "question": "什么是 RAG？",
      "answer": "检索增强生成（Retrieval Augmented Generation）...",
      "confidence": 0.92,
      "topic": "AI 技术"
    }
  ],
  "summary": "本课程介绍了大模型应用开发的核心技术..."
}
```

---

### 报告导出

#### `POST /api/reports/export`
导出报告文件。

**请求体：**
```json
{
  "analysis_id": 5,
  "format": "markdown",
  "output_path": null
}
```

**响应：**
```json
{ "file_path": "storage/analyses/report_5.md", "size_bytes": 12480 }
```

---

### 音频设备

#### `GET /api/audio/devices`
列出可用音频输入设备。

```json
[
  { "index": 0, "name": "MacBook Pro Microphone", "channels": 1 },
  { "index": 1, "name": "BlackHole 2ch", "channels": 2 }
]
```

---

## WebSocket 接口

连接地址：`ws://localhost:8765/ws`

### 连接握手

连接成功后服务端自动推送当前状态：

```json
{ "type": "connected", "data": { "server_time": "2024-01-01T12:00:00Z" } }
```

### 消息类型详解

#### 服务端 → 客户端

| type | 触发时机 | data 字段 |
|------|---------|-----------|
| `status_update` | 状态变更 | `recording`, `monitoring`, `analysis_running` |
| `analysis_progress` | 分析进行中 | `analysis_id`, `progress`, `stage` |
| `recording_started` | 录制开始 | `recording_id`, `start_time` |
| `recording_stopped` | 录制结束 | `recording_id`, `duration` |
| `analysis_completed` | 分析完成 | `analysis_id`, `qa_count` |
| `log_message` | 有新日志 | `level`, `message`, `timestamp` |
| `error` | 发生错误 | `code`, `message` |

#### 客户端 → 服务端

| type | 说明 | data 字段 |
|------|------|-----------|
| `ping` | 心跳 | — |
| `start_monitoring` | 开始监控 | `interval_seconds` |
| `stop_monitoring` | 停止监控 | — |

---

## 错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|----------|------|
| `ERR_001` | 400 | 参数校验失败 |
| `ERR_002` | 404 | 资源不存在 |
| `ERR_003` | 409 | 录制已在进行中 |
| `ERR_004` | 422 | API Key 无效 |
| `ERR_005` | 500 | 内部服务错误 |
| `ERR_006` | 503 | FFmpeg 未安装 |
| `ERR_007` | 503 | Tesseract 未安装 |
