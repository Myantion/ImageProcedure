# 图像处理工具集

一个功能丰富的图像处理工具，集成了**像素画转换**、**画质增强**和**AI超分辨率**三大功能，支持图形界面操作，简单易用。

## ✨ 功能特点

### 1. 像素画转换
- 🎨 将普通图片转换为清晰的像素艺术风格（类似星露谷风格）
- ⚙️ 可自定义像素大小、颜色数量、插值方法
- 📐 支持保持宽高比或强制正方形
- 🔧 多种插值算法：最近邻、双线性、三次卷积、Lanczos

### 2. 画质增强
- 🔍 智能锐化/模糊处理（参数可调，支持强化和柔化）
- 🎯 对比度和饱和度增强
- 🧹 智能去噪功能
- 📈 可选放大处理

### 3. AI 超分辨率（Real-ESRGAN）
- 🤖 基于 Real-ESRGAN 深度学习模型
- 🎭 支持通用图像和动漫图像超分
- ⚡ 自动选择最佳模型
- 🔄 支持 2x、3x、4x 放大

## 📦 安装与使用

### 方式一：直接运行（推荐）

**下载打包好的 exe：**

前往 [Releases](https://github.com/你的用户名/你的仓库名/releases) 页面下载最新版本的 `pixel_art_gui.exe`，双击即可使用，无需安装 Python 环境。

> ⚠️ 注意：exe 文件较大（包含所有依赖和模型），请从 Releases 下载，不要从源码目录下载。

### 方式二：从源码运行

#### 环境要求
- Python 3.7+
- Pillow（PIL）

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 运行 GUI
```bash
python pixel_art_gui.py
```

#### 命令行模式（像素画转换）
```bash
python pixel_art_converter.py
```
> 注意：命令行模式需要在代码顶部配置 `INPUT_IMAGE` 和 `OUTPUT_IMAGE` 路径

## 🚀 使用说明

### 图形界面（GUI）

运行程序后，界面包含三个标签页：

1. **像素画转换**
   - 选择输入/输出图片
   - 调整像素大小（16-256）
   - 设置颜色数量（16-256）
   - 选择插值方法
   - 点击"开始转换"

2. **画质增强**
   - 选择输入/输出图片
   - 调整锐化/模糊强度（0.1-3.0，<1为模糊，>1为锐化）
   - 调整对比度（0.5-1.5）
   - 调整饱和度（0.5-1.3）
   - 启用/关闭去噪
   - 可选放大倍数
   - 点击"开始增强"

3. **AI 超分 (Real-ESRGAN)**
   - 选择输入/输出图片
   - 设置放大倍数（2/3/4）
   - 点击"开始 AI 超分"
   - 处理时间较长，请耐心等待

### 参数说明

#### 像素画转换
- **像素大小**：数值越小，像素感越强（推荐：32-128）
- **颜色数量**：数值越小，颜色越少，像素艺术感越强（推荐：64-256）
- **插值方法**：
  - 最近邻：最快，像素感最强
  - 双线性：平滑过渡
  - 三次卷积：推荐，平衡效果
  - Lanczos：高质量，细节保留

#### 画质增强
- **锐化/模糊**：0.1-3.0
  - < 1.0：模糊效果（数值越小越模糊）
  - = 1.0：无变化
  - > 1.0：锐化效果（数值越大越锐利）
- **对比度**：0.5-1.5（<1降低，>1增强）
- **饱和度**：0.5-1.3（<1降低，>1增强）

## 📁 项目结构

```
pythonProject/
├── pixel_art_gui.py          # GUI 主程序
├── pixel_art_converter.py    # 核心转换算法
├── requirements.txt          # Python 依赖
├── README.md                 # 本文件
└── realesrgan-ncnn-vulkan-20220424-windows/  # AI 超分工具（需单独下载）
    ├── realesrgan-ncnn-vulkan.exe
    └── models/                 # 模型文件目录
```

## 🔧 打包说明

### 打包为 exe（单文件）

1. 安装 PyInstaller：
```bash
pip install pyinstaller
```

2. 执行打包命令：
```bash
pyinstaller -F -w --collect-all PIL --collect-all Pillow --add-data "realesrgan-ncnn-vulkan-20220424-windows;realesrgan-ncnn-vulkan-20220424-windows" pixel_art_gui.py
```

3. 打包完成后，exe 文件位于 `dist/pixel_art_gui.exe`

### 注意事项

- 打包前需确保 `realesrgan-ncnn-vulkan-20220424-windows` 目录存在且包含 `models` 文件夹
- 打包后的 exe 体积较大（包含所有依赖和模型）
- 首次运行可能较慢（自解压过程）

## 📝 AI 超分工具下载（仅源码运行需要）

如果从源码运行且需要使用 AI 超分功能，需要单独下载 Real-ESRGAN：

1. 访问：https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan/releases
2. 下载 Windows 版本（需包含 `models` 文件夹的完整版本，如 `realesrgan-ncnn-vulkan-20220424-windows.zip`）
3. 解压到项目根目录，确保目录名为 `realesrgan-ncnn-vulkan-20220424-windows`
4. 或修改 `pixel_art_gui.py` 中的 `REALESRGAN_EXE` 路径

> 💡 如果使用打包好的 exe，已内置 Real-ESRGAN，无需单独下载。

## ⚠️ 注意事项

- **支持的图片格式**：JPEG, PNG, BMP, GIF 等（PIL 支持的所有格式）
- **输出格式**：由文件扩展名决定，建议使用 PNG 格式保存
- **AI 超分**：处理时间取决于图片大小和放大倍数，CPU 模式下可能较慢
- **无独显设备**：AI 超分会使用 CPU/核显，速度较慢但可用

## 🐛 常见问题

### Q: 运行 exe 提示缺少 DLL？
A: 确保使用 `--collect-all PIL` 参数重新打包，或升级 Pillow 和 PyInstaller。

### Q: AI 超分失败？
A: 检查 `realesrgan-ncnn-vulkan-20220424-windows/models` 目录是否存在且包含 `.param` 和 `.bin` 文件。

### Q: 界面显示"未响应"？
A: AI 超分处理时间较长，请耐心等待。已优化为后台处理，界面不会真正卡死。

### Q: 模糊效果不明显？
A: 将"锐化/模糊"参数调到最小值（0.1），同时降低对比度和饱和度。

## 📄 许可证

本项目仅供学习和个人使用。

## 🙏 致谢

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - AI 超分辨率算法
- [Pillow (PIL)](https://python-pillow.org/) - 图像处理库
- [PyInstaller](https://www.pyinstaller.org/) - Python 打包工具

## 📧 反馈

如有问题或建议，欢迎提交 Issue。
