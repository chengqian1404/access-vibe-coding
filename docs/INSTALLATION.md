# 详细安装指南

---

## Windows 安装

### 1. 安装 Python 3.10+

1. 访问 https://www.python.org/downloads/ 下载 Python 3.11 安装包
2. 运行安装程序，**务必勾选** "Add Python to PATH"
3. 验证安装：`python --version`

### 2. 安装 Node.js 18+

1. 访问 https://nodejs.org/ 下载 LTS 版本
2. 运行安装程序（默认选项即可）
3. 验证安装：`node --version && npm --version`

### 3. 安装 FFmpeg（Windows）

1. 访问 https://ffmpeg.org/download.html → Windows builds
2. 下载 `ffmpeg-release-essentials.zip`
3. 解压到 `C:\ffmpeg\`
4. 将 `C:\ffmpeg\bin` 添加到系统环境变量 PATH
5. 验证：`ffmpeg -version`

### 4. 安装 Tesseract OCR（Windows）

1. 访问 https://github.com/UB-Mannheim/tesseract/wiki 下载安装包
2. 运行安装程序，安装路径建议保持默认 `C:\Program Files\Tesseract-OCR\`
3. 安装时在「Additional language data」中勾选 **Chinese (Simplified)**
4. 将 `C:\Program Files\Tesseract-OCR\` 添加到 PATH
5. 验证：`tesseract --version`

---

## macOS 安装

### 使用 Homebrew（推荐）

```bash
# 安装 Homebrew（如未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装所有依赖
brew install python@3.11 node ffmpeg tesseract tesseract-lang

# 验证
python3 --version
node --version
ffmpeg -version
tesseract --version
```

### 手动安装

- Python：https://www.python.org/downloads/macos/
- Node.js：https://nodejs.org/
- FFmpeg：https://ffmpeg.org/download.html#build-mac
- Tesseract：`brew install tesseract` 或从源码编译

---

## Linux 安装（Ubuntu/Debian）

```bash
# 更新包列表
sudo apt update

# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# 安装 Node.js 18（通过 NodeSource）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装 FFmpeg
sudo apt install ffmpeg -y

# 安装 Tesseract OCR + 中文包
sudo apt install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra -y

# 音频支持
sudo apt install portaudio19-dev python3-pyaudio -y

# 验证
python3.11 --version && node --version && ffmpeg -version && tesseract --version
```

### Linux（CentOS/RHEL/Rocky）

```bash
# 安装 EPEL
sudo dnf install epel-release -y

# 安装依赖
sudo dnf install python311 python311-venv nodejs ffmpeg tesseract -y

# 中文语言包（需手动下载）
wget https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
sudo mv chi_sim.traineddata /usr/share/tesseract/tessdata/
```

---

## Python 环境配置

```bash
cd access-vibe-coding/backend

# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate.bat

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Node.js 环境配置

```bash
cd access-vibe-coding/frontend

# 安装依赖
npm install

# 验证
npm list --depth=0
```

---

## 安装验证

运行以下命令验证所有依赖是否正确安装：

```bash
bash scripts/setup-dev.sh
```

如无报错，说明环境配置成功。
