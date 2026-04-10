# API 文档

基础 URL: `http://127.0.0.1:8765`

## 健康检查

```
GET /health
```

响应：
```json
{"status": "ok", "version": "1.0.0"}
```

---

## 指令 API

### 解析指令

```
POST /api/v1/instruction/parse
```

请求体：
```json
{
  "instruction": "创建一个员工表，包含ID、姓名、工资字段",
  "provider": "openai",   // 可选
  "model": "gpt-4-turbo"  // 可选
}
```

响应：
```json
{
  "success": true,
  "parsed": {
    "action": "create_table",
    "description": "创建员工数据表",
    "params": {
      "table_name": "Employees",
      "fields": [...]
    },
    "steps": [...],
    "confidence": 0.95,
    "warnings": []
  }
}
```

### 执行指令（一步完成）

```
POST /api/v1/instruction/run
```

请求体同 `/instruction/parse`

响应：
```json
{
  "success": true,
  "parsed": {...},
  "result": {
    "success": true,
    "total_steps": 8,
    "completed_steps": 8,
    "step_results": [...],
    "final_screenshot": "base64...",
    "execution_time": 3.2
  }
}
```

---

## 截图 API

```
GET /api/v1/screenshot
```

响应：
```json
{
  "success": true,
  "screenshot": "base64_jpeg_string"
}
```

---

## 配置 API

### 获取配置

```
GET /api/v1/config
```

### 保存提供商配置

```
POST /api/v1/config/provider
```

请求体：
```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "base_url": null,
  "model": "gpt-4-turbo"
}
```

### 测试连接

```
POST /api/v1/config/provider/test
```

请求体同上

### 删除配置

```
DELETE /api/v1/config/provider/{provider}
```

---

## 历史记录 API

```
GET /api/v1/history?limit=20&offset=0
DELETE /api/v1/history
DELETE /api/v1/history/{item_id}
```

---

## WebSocket

```
WS ws://127.0.0.1:8765/ws/execution
```

连接后发送消息：
```json
{"type": "execute", "instruction": "你的指令"}
```

接收消息类型：
- `connected` - 连接成功
- `progress` - 执行进度
- `complete` - 执行完成
- `error` - 执行出错
