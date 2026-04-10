# 故障排查指南

## 常见问题

### 后端无法启动

**症状：** 主页显示"后端离线"

**解决方案：**

1. 确认 Python 3.9+ 已安装：
   ```bash
   python --version
   ```

2. 安装依赖：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. 手动启动后端：
   ```bash
   cd backend
   python main.py
   ```

4. 检查端口是否被占用：
   ```bash
   # Windows
   netstat -ano | findstr 8765
   # Linux/Mac
   lsof -i :8765
   ```

---

### LLM 连接失败

**症状：** 测试连接失败或执行报错

**解决方案：**

1. 检查 API Key 是否正确（注意不要有多余空格）
2. 检查网络连接（尤其是访问 OpenAI 等境外服务）
3. 尝试其他提供商（通义千问、DeepSeek 国内访问更稳定）
4. 检查 API 账户余额

---

### Access 自动化不工作

**症状：** 步骤执行但 Access 没有响应

**解决方案：**

1. 确认使用 Windows 系统（自动化仅支持 Windows）
2. 确认 Microsoft Access 已安装且正在运行
3. 确认 Access 窗口在前台（未被其他窗口遮挡）
4. 以管理员权限运行应用
5. 安装 pywin32：
   ```bash
   pip install pywin32
   python -m pywin32_postinstall -install
   ```

---

### 截图失败

**症状：** 截图区域空白或报错

**解决方案：**

1. 安装 Pillow：
   ```bash
   pip install Pillow
   ```

2. 在虚拟机中需要特殊权限，请在实体机上使用

---

### 指令解析结果不准确

**解决方案：**

1. 使用更强大的模型（GPT-4o、Claude 3.5 Sonnet）
2. 提供更详细的指令描述
3. 指定具体的表名、字段名等

---

## 日志位置

- 后端日志：`~/.access-vibe-coding/logs/access-vibe-coding.log`
- 前端日志：Electron DevTools Console

## 获取帮助

提交 Issue：https://github.com/chengqian1404/access-vibe-coding/issues
