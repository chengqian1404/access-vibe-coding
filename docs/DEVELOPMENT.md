# 开发指南

## 开发环境搭建

### 前提条件

- Python 3.9+
- Node.js 18+
- Git

### 快速设置

```bash
# 克隆仓库
git clone https://github.com/chengqian1404/access-vibe-coding.git
cd access-vibe-coding

# 运行设置脚本（Linux/macOS）
chmod +x scripts/setup-dev.sh && ./scripts/setup-dev.sh
```

### 手动设置

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 前端
cd frontend
npm install
```

## 运行开发服务

```bash
# 终端 1 - 后端
cd backend
python main.py
# 后端运行在 http://127.0.0.1:8765

# 终端 2 - 前端（Vite）
cd frontend
npm run start:react
# React 运行在 http://localhost:5173

# 或者同时启动 Electron + React
cd frontend
npm start
```

## 目录结构

```
backend/
├── app/
│   ├── api/
│   │   ├── routes.py        # REST API 路由
│   │   └── websocket.py     # WebSocket 处理
│   ├── services/
│   │   ├── llm_service.py        # LLM 调用
│   │   ├── instruction_parser.py # 指令解析
│   │   ├── access_automation.py  # Access 自动化
│   │   ├── screenshot_service.py # 截图
│   │   ├── session_manager.py    # 会话管理
│   │   └── config_manager.py     # 配置管理
│   ├── models/              # Pydantic 数据模型
│   ├── config/              # 配置和常量
│   └── utils/               # 工具函数
└── main.py                  # 应用入口

frontend/
├── src/
│   ├── components/          # React 组件
│   ├── pages/               # 页面组件
│   ├── styles/              # CSS 样式
│   ├── App.jsx              # 根组件
│   └── config.js            # 前端配置
├── main.js                  # Electron 主进程
└── preload.js               # Electron 预加载
```

## 运行测试

```bash
cd tests
pip install pytest pytest-asyncio
pytest -v
```

## 代码风格

- Python: 遵循 PEP 8，使用 ruff 检查
- JavaScript: ESLint + React 规范
- 类型注解: Python 使用 typing，必要时使用

## 添加新 LLM 提供商

1. 在 `backend/app/config/llm_providers.py` 添加提供商配置
2. 在 `LLMService` 中添加对应的 `_call_xxx` 方法
3. 更新前端 `LLMConfig.jsx`（如有特殊配置需求）

## 添加新自动化操作

1. 在 `app/models/instruction.py` 的 `ActionType` 添加新类型
2. 在 `InstructionParser._generate_default_steps` 添加步骤生成逻辑
3. 在 `AccessAutomation` 中实现具体操作（如需要）
4. 更新 `llm_providers.py` 中的 prompt 说明

## 提交规范

```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码格式调整
refactor: 重构
test: 添加测试
chore: 构建/工具相关
```
