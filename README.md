# Access Vibe Coding

> AI 驱动的 Microsoft Access 自动化工具 - 通过自然语言指令自动操作 Access 数据库

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-blue)](https://github.com/chengqian1404/access-vibe-coding)

## ✨ 功能特性

- 🗣️ **自然语言控制** - 用中文描述操作，AI 自动执行
- 🤖 **多 LLM 支持** - OpenAI、通义千问、Claude、DeepSeek、Ollama（本地）
- 🖥️ **跨平台** - Windows、macOS、Linux 统一体验
- 📊 **Access 自动化** - 创建表、导入数据、查询、窗体、报表
- 📋 **操作历史** - 记录所有操作，支持重复执行
- 📸 **截图预览** - 实时查看 Access 当前状态
- ⚡ **快速响应** - API 调用，无需本地大模型

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- Microsoft Access（用于实际自动化，仅 Windows）

### 开发环境

```bash
# 1. 克隆仓库
git clone https://github.com/chengqian1404/access-vibe-coding.git
cd access-vibe-coding

# 2. 一键设置开发环境
chmod +x scripts/setup-dev.sh && ./scripts/setup-dev.sh

# 3. 配置 API 密钥
# 编辑 backend/.env 文件，填入你的 LLM API 密钥

# 4. 启动后端（终端1）
cd backend && python main.py

# 5. 启动前端（终端2）
cd frontend && npm start
```

### 使用预编译版本

从 [Releases](https://github.com/chengqian1404/access-vibe-coding/releases) 下载适合你系统的安装包：

- Windows: `Access-Vibe-Coding-Setup-x64.exe`
- macOS: `Access-Vibe-Coding-x64.dmg`
- Linux: `Access-Vibe-Coding-x86_64.AppImage`

## 🔧 配置 LLM

启动应用后，进入 **设置** 页面配置 LLM 提供商：

| 提供商 | 特点 | 官网 |
|--------|------|------|
| **OpenAI** | GPT-4 Turbo，高质量 | [platform.openai.com](https://platform.openai.com) |
| **通义千问** | 国产，中文优化 | [dashscope.aliyuncs.com](https://dashscope.aliyuncs.com) |
| **Claude** | 长上下文，安全 | [console.anthropic.com](https://console.anthropic.com) |
| **DeepSeek** | 低成本，高性能 | [platform.deepseek.com](https://platform.deepseek.com) |
| **Ollama** | 完全离线，本地 | [ollama.ai](https://ollama.ai) |

## 📖 使用示例

```
# 创建数据表
创建一个"员工信息"表，包含员工ID、姓名、部门、工资、入职日期字段

# 导入数据
从桌面的 sales.xlsx 导入数据到"销售记录"表

# 创建查询
查询工资大于8000的员工，显示姓名、部门和工资

# 创建窗体
为"员工信息"表创建一个数据录入窗体

# 生成报表
生成一份按部门统计工资总额的报表
```

## 🏗️ 项目架构

```
access-vibe-coding/
├── frontend/          # Electron + React 跨平台前端
├── backend/           # Python FastAPI 后端服务
├── scripts/           # 构建和部署脚本
├── docs/              # 项目文档
├── resources/         # 图标和模板资源
└── tests/             # 自动化测试
```

详见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 📦 构建可执行文件

```bash
# Windows
scripts/build-win.bat

# macOS
chmod +x scripts/build-mac.sh && ./scripts/build-mac.sh

# Linux
chmod +x scripts/build-linux.sh && ./scripts/build-linux.sh
```

详见 [docs/BUILD.md](docs/BUILD.md)

## 📚 文档

- [架构文档](docs/ARCHITECTURE.md)
- [LLM 配置指南](docs/LLM_CONFIG.md)
- [用户指南](docs/USER_GUIDE.md)
- [API 文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)
- [构建指南](docs/BUILD.md)
- [故障排查](docs/TROUBLESHOOTING.md)

## 🤝 贡献

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

<p align="center">Made with ❤️ for Microsoft Access users</p>