# LLM 配置指南

## 支持的 LLM 提供商

### 1. OpenAI

**获取 API Key:** https://platform.openai.com/api-keys

```
提供商: openai
API URL: https://api.openai.com/v1
推荐模型: gpt-4-turbo 或 gpt-4o
```

**设置步骤:**
1. 访问 platform.openai.com 注册账号
2. 进入 API Keys 页面创建密钥
3. 在应用设置页面选择 OpenAI，填入 API Key

---

### 2. 通义千问（推荐国内用户）

**获取 API Key:** https://dashscope.aliyuncs.com

```
提供商: qwen
API URL: https://dashscope.aliyuncs.com/compatible-mode/v1
推荐模型: qwen-max
```

**特点:**
- 中文支持优秀
- 国内访问无障碍
- 价格相对低廉

---

### 3. Claude (Anthropic)

**获取 API Key:** https://console.anthropic.com

```
提供商: claude
API URL: https://api.anthropic.com
推荐模型: claude-3-5-sonnet-20241022
```

---

### 4. DeepSeek

**获取 API Key:** https://platform.deepseek.com

```
提供商: deepseek
API URL: https://api.deepseek.com
推荐模型: deepseek-chat
```

**特点:**
- 性价比高
- 中文理解强

---

### 5. Ollama（本地离线）

**安装 Ollama:** https://ollama.ai

```bash
# 安装并启动模型
ollama pull qwen:7b
ollama serve
```

```
提供商: ollama
API URL: http://localhost:11434
推荐模型: qwen:7b
不需要 API Key
```

---

## 通过环境变量配置

在 `backend/.env` 文件中设置：

```env
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
QWEN_API_KEY=sk-your-key-here
CLAUDE_API_KEY=sk-ant-your-key-here
DEEPSEEK_API_KEY=sk-your-key-here
```

## 通过应用界面配置

1. 打开应用，进入 **设置** 页面
2. 选择 LLM 提供商
3. 填入 API Key
4. 点击 **测试连接** 验证
5. 点击 **保存配置**

API Key 会使用 AES-256 加密存储在本地，安全可靠。

## 自定义 API 地址

如果你使用中转服务或自托管，可以在设置中填写自定义 API URL，格式与 OpenAI 兼容即可。

## 常见问题

**Q: 推荐使用哪个 LLM？**

A: 
- 国内用户推荐：通义千问（qwen-max）或 DeepSeek
- 效果最好：GPT-4o 或 Claude 3.5 Sonnet
- 离线使用：Ollama + qwen:7b

**Q: 响应速度如何？**

A: 一般指令解析 2-5 秒，取决于网络和模型响应速度。

**Q: 费用如何？**

A: 按 Token 计费，普通使用每天花费约 0.1-1 元（通义千问/DeepSeek），非常经济。
