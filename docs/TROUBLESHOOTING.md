# 常见问题排查

---

## 后端无法启动

### 症状：端口 8765 被占用

```
ERROR: [Errno 48] Address already in use
```

**解决方案：**

macOS/Linux — 使用 `lsof -i :8765` 找到占用进程的 PID，然后终止该进程。

Windows — 使用 `netstat -ano | findstr 8765` 查找 PID，然后用任务管理器结束该进程。

### 症状：Python 未找到

```
python3: command not found
```

**解决方案：**
- 确认 Python 3.10+ 已安装
- 重新运行 `bash scripts/setup-dev.sh`
- Windows 用户确认安装时勾选了「Add to PATH」

### 症状：模块导入失败

```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案：**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## 音频录制问题

### 症状：无法获取音频设备列表

**macOS**：系统偏好设置 → 安全性与隐私 → 麦克风 → 允许应用访问

**Windows**：设置 → 隐私 → 麦克风 → 开启应用访问权限

### 症状：录制的音频只有静音

**可能原因：**
1. 选择了错误的音频设备
2. 系统静音

**解决方案：**
- 在设置中尝试切换不同的音频设备
- macOS 录制系统音频需安装 BlackHole 虚拟声卡：
  `brew install blackhole-2ch`

---

## 屏幕录制黑屏（macOS）

**症状**：录制视频全程黑屏

**原因**：macOS 13+ 需要屏幕录制权限

**解决方案：**
1. 系统设置 → 隐私与安全性 → 屏幕录制
2. 找到本应用并开启权限
3. 重启应用

---

## Whisper 转录失败

### 症状：`AuthenticationError`

- 检查 `backend/.env` 中 `OPENAI_API_KEY` 是否正确
- 验证 API Key 余额是否充足

### 症状：`Connection timeout`

- 检查网络连接
- 如使用代理，在 `.env` 中配置：
  ```env
  HTTP_PROXY=http://127.0.0.1:7890
  HTTPS_PROXY=http://127.0.0.1:7890
  ```

### 症状：文件过大错误

- 在设置中调小「音频分片大小」（建议 20MB）
- Whisper API 单文件限制为 25MB

---

## OCR 无法识别中文

### 症状：转录结果乱码或只有英文

**解决方案：**

1. 确认安装了中文语言包：
   ```bash
   tesseract --list-langs | grep chi
   ```
   应输出 `chi_sim` 或 `chi_tra`

2. 如未显示，手动安装：
   - Ubuntu：`sudo apt install tesseract-ocr-chi-sim`
   - macOS：`brew install tesseract-lang`
   - Windows：重新运行 Tesseract 安装程序，勾选 Chinese Simplified

---

## 微信窗口检测失败

### 症状：监控运行但始终未检测到直播

**解决方案：**
1. 确认微信已登录且直播窗口在前台可见
2. 检查「检测关键词」设置是否与实际窗口标题匹配
3. 调整检测间隔（建议不超过 60 秒）

---

## 构建失败

### PyInstaller RecursionError

在 `scripts/package_backend.py` 开头添加：
```python
import sys
sys.setrecursionlimit(5000)
```

### Electron Builder 下载超时

```bash
export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
export ELECTRON_BUILDER_BINARIES_MIRROR=https://npmmirror.com/mirrors/electron-builder-binaries/
```

---

## 数据库错误

### 症状：`database is locked`

- 确保只有一个应用实例在运行
- 重启应用后再试

### 症状：数据库迁移失败

```bash
# 备份后删除旧数据库，重新初始化
cp backend/storage/app.db backend/storage/app.db.bak
rm backend/storage/app.db
# 重启应用自动创建新数据库
```

---

## 常见错误信息速查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `ffmpeg: command not found` | FFmpeg 未安装 | 安装 FFmpeg 并加入 PATH |
| `tesseract: command not found` | Tesseract 未安装 | 安装 Tesseract OCR |
| `CUDA out of memory` | GPU 内存不足 | 在设置中切换为 CPU 模式 |
| `Rate limit exceeded` | API 调用过于频繁 | 增加请求间隔或升级 API 套餐 |
| `No space left on device` | 磁盘空间不足 | 清理旧录制文件 |
