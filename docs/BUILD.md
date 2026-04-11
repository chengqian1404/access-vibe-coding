# 构建指南

---

## 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/access-vibe-coding.git
cd access-vibe-coding

# 2. 一键初始化（推荐）
bash scripts/setup-dev.sh
```

---

## 开发模式运行

开发模式下前后端分离运行，支持热重载。

### 启动后端

```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload
```

### 启动前端（另一个终端）

```bash
cd frontend
npm run dev
```

前端 Vite 开发服务器运行于 `http://localhost:5173`，
Electron 将自动加载该地址。

---

## 生产构建

### Windows

```bat
scripts\build-win.bat
```

### macOS

```bash
bash scripts/build-mac.sh
```

### Linux

```bash
bash scripts/build-linux.sh
```

---

## 构建步骤详解

### 1. 构建 React 前端

```bash
cd frontend
npm run build:react
# 产物：frontend/dist/
```

### 2. 打包 Python 后端（PyInstaller）

```bash
python scripts/package_backend.py
# 产物：frontend/resources/backend/backend（可执行文件）
```

PyInstaller 将后端打包为独立可执行文件，包含 Python 解释器和所有依赖，无需用户安装 Python。

**主要打包参数：**
- `--onedir`：单目录模式（更快启动）
- `--hidden-import`：显式声明动态导入
- `--add-data`：打包静态数据文件

### 3. 打包 Electron 应用

```bash
cd frontend
# Windows
npx electron-builder --win
# macOS
npx electron-builder --mac
# Linux
npx electron-builder --linux
```

---

## 输出产物

| 平台 | 产物 | 路径 |
|------|------|------|
| Windows | NSIS 安装包 `.exe` | `frontend/release/*.exe` |
| Windows | 便携版 `.zip` | `frontend/release/*.zip` |
| macOS | DMG 磁盘镜像 | `frontend/release/*.dmg` |
| Linux | AppImage | `frontend/release/*.AppImage` |
| Linux | deb 包 | `frontend/release/*.deb` |

---

## 分发注意事项

### macOS 代码签名

macOS 发布需要 Apple Developer 证书：

```bash
# 设置环境变量
export CSC_LINK=path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password

bash scripts/build-mac.sh
```

未签名的应用在 macOS 上打开时需要用户在「安全性与隐私」中手动允许。

### Windows 代码签名

```bat
# 在 electron-builder.json 中配置证书
set CSC_LINK=path\to\cert.pfx
set CSC_KEY_PASSWORD=password
```

### Linux AppImage

AppImage 为自包含格式，无需安装，赋予执行权限后可直接运行：

```bash
chmod +x AccessVibe-1.0.0.AppImage
./AccessVibe-1.0.0.AppImage
```

---

## 常见构建问题

**PyInstaller 找不到模块**  
在 `scripts/package_backend.py` 的 `hiddenimports` 列表中添加缺失模块。

**Electron Builder 签名失败**  
检查证书路径与密码是否正确，或跳过签名（仅用于测试）。

**资源文件未打包**  
确认 `electron-builder.json` 的 `extraResources` 配置正确引用了 `resources/backend` 目录。
