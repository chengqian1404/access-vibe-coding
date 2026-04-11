# 贡献指南

感谢你愿意为直播学习分析工具做出贡献！

---

## 报告 Bug

1. 在 [Issues](../../issues) 页面搜索，确认该 Bug 未被报告
2. 点击 **New Issue**，选择 **Bug Report** 模板
3. 填写以下信息：
   - 操作系统与版本
   - Python / Node.js 版本
   - 复现步骤（越详细越好）
   - 期望行为 vs 实际行为
   - 相关日志（`backend/storage/app.log`）

---

## 提交功能请求

1. 在 Issues 页面创建 **Feature Request**
2. 描述你希望实现的功能及使用场景
3. 如有可能，提供界面原型或技术方案草图

---

## 开发环境搭建

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/your-username/access-vibe-coding.git
cd access-vibe-coding

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 初始化开发环境
bash scripts/setup-dev.sh

# 4. 配置 API 密钥
cp backend/.env.example backend/.env
```

---

## 代码风格规范

### Python（后端）

- 格式化工具：**Black**（行宽 88）
- Linter：**Flake8**（配置见 `backend/setup.cfg`）
- 类型注解：所有公共函数必须添加类型注解
- 文档字符串：使用 Google 风格 docstring

```bash
# 格式化
cd backend && black app/

# Lint 检查
cd backend && flake8 app/
```

### JavaScript / TypeScript（前端）

- Linter：**ESLint**（配置见 `frontend/.eslintrc.js`）
- 格式化：**Prettier**
- 组件：函数式组件 + React Hooks
- 禁止直接修改 props

```bash
cd frontend && npm run lint
cd frontend && npm run format
```

---

## Pull Request 流程

1. **确保所有测试通过**：
   ```bash
   cd .. && pytest tests/ -v
   ```

2. **遵守提交信息格式**（Conventional Commits）：
   ```
   feat: 添加导出 PDF 功能
   fix: 修复 Windows 下 ffmpeg 路径解析错误
   docs: 更新 API 文档
   refactor: 重构 AudioRecorder 设备检测逻辑
   test: 为 ReportGenerator 添加单元测试
   ```

3. **PR 描述应包含**：
   - 变更内容摘要
   - 关联的 Issue 编号（如 `Closes #42`）
   - 如有 UI 变更，附上截图

4. **等待 Code Review**，根据反馈修改后合并

---

## 目录结构说明

```
access-vibe-coding/
├── backend/app/
│   ├── api/          # FastAPI 路由与 WebSocket
│   ├── services/     # 核心业务逻辑
│   ├── config/       # 配置与设置
│   └── utils/        # 工具函数
├── frontend/src/
│   ├── pages/        # 页面组件
│   ├── components/   # 通用 UI 组件
│   ├── hooks/        # 自定义 Hooks
│   └── services/     # API 调用封装
├── tests/            # 后端单元测试
├── scripts/          # 构建与部署脚本
└── docs/             # 项目文档
```

---

## 行为准则

请保持友善、尊重的沟通方式。我们遵循 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。
