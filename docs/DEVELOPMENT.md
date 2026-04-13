# 开发指南

## 环境要求

- Python 3.10 或更高版本
- pip 或 uv 包管理器
- （Windows）Microsoft Access 或 Access 数据库引擎
- Git

## 本地开发环境搭建

### 1. 克隆仓库

```bash
git clone https://github.com/chengqian1404/access-vibe-coding.git
cd access-vibe-coding
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制示例配置文件并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 选择默认 LLM 提供商
LLM_PROVIDER=qwen          # qwen / openai / claude / deepseek

# 通义千问（推荐）
DASHSCOPE_API_KEY=your_key_here

# OpenAI（备选）
OPENAI_API_KEY=your_key_here

# Claude（备选）
ANTHROPIC_API_KEY=your_key_here

# DeepSeek（备选）
DEEPSEEK_API_KEY=your_key_here
```

## 运行测试

```bash
pytest tests/ -v
```

## 代码风格

本项目遵循以下代码风格规范：

- [PEP 8](https://pep8.org/) Python 代码风格
- 使用 `black` 格式化代码
- 使用 `ruff` 进行代码检查
- 所有公共函数和类必须有文档字符串

格式化代码：

```bash
black agent/ tests/
ruff check agent/ tests/
```

## 项目结构

```
access-vibe-coding/
├── agent/              # 主要源代码
│   ├── core/           # Agent 核心逻辑
│   ├── nlp/            # 自然语言处理
│   ├── llm/            # LLM 提供商适配器
│   ├── adapters/       # 外部系统适配器
│   └── config/         # 配置管理
├── docs/               # 项目文档
│   ├── ARCHITECTURE.md # 架构说明
│   └── DEVELOPMENT.md  # 本文件
├── tests/              # 测试文件
├── examples/           # 使用示例
├── .env.example        # 环境变量示例
├── requirements.txt    # Python 依赖（待创建）
├── package.json        # 项目元数据
└── README.md           # 项目说明
```

## 贡献指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交代码：`git commit -m "Add: 描述你的改动"`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### 提交信息格式

```
类型: 简短描述

类型可以是：
- Add: 新增功能
- Fix: 修复 Bug
- Update: 更新现有功能
- Refactor: 重构代码
- Docs: 更新文档
- Test: 添加或更新测试
- Chore: 构建配置等杂项
```

## 支持的 LLM 提供商

| 提供商 | 模型 | 特点 |
|--------|------|------|
| 通义千问 | qwen-plus / qwen-max | 中文支持好，价格实惠（推荐） |
| OpenAI | gpt-4o / gpt-4o-mini | 功能强大，通用性好 |
| Claude | claude-3-5-sonnet | 代码理解能力强 |
| DeepSeek | deepseek-chat | 价格低廉，中文支持好 |
| Ollama | llama3 / qwen2.5 | 本地运行，无需 API 密钥 |

## 常见问题

### Q: 在 macOS/Linux 上如何使用 Access 数据库？

A: 可以使用 [mdbtools](https://github.com/mdbtools/mdbtools)（只读）或通过 ODBC 驱动访问。完整的读写支持建议在 Windows 环境下运行，或使用 Wine。

### Q: 支持哪些 Access 版本？

A: 支持 `.mdb`（Access 97-2003）和 `.accdb`（Access 2007+）格式。

### Q: 如何报告 Bug？

A: 请在 GitHub Issues 中创建新的 Issue，附上：
- 操作系统和版本
- Python 版本
- 错误信息和堆栈跟踪
- 复现步骤
