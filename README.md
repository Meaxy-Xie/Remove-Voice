# 🎵 AI 人声分离工具 v3

一个简洁高效的人声分离软件，使用 **Meta Demucs** 深度学习模型，能够从音乐中提取伴奏、去除人声。提供友好的 PyQt5 图形界面，支持多种音频格式。

## ✨ 功能特性

- 🎯 **高精度分离** - 使用 Meta 开源的 Demucs AI 模型
- 🖥️ **图形界面** - 简洁直观的 PyQt5 GUI，点击即用
- 📁 **多格式支持** - 支持 MP3、WAV、FLAC、M4A 等音频格式
- ⚡ **多模型选择** - 3 种模型可选，质量和速度自由权衡
- 💾 **WAV + MP3 输出** - 同时生成无损 WAV 和压缩 MP3 格式

## 📋 系统要求

- **操作系统**：Windows 10/11（64 位）/ macOS / Linux
- **Python**：3.10 或更高版本
- **内存**：8GB+ 推荐
- **GPU**：NVIDIA GPU 推荐（CUDA 支持），CPU 也可运行但较慢
- **磁盘**：至少 3GB（模型缓存）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

### 3. 使用应用

1. 点击 **"选择文件"** 按钮选择音频文件
2. 选择处理模型（默认推荐 `htdemucs`）
3. 点击 **"🚀 开始处理"** 开始分离
4. 处理完成后，伴奏文件保存在输出目录

## ℹ️ 重要提示

### ✅ 支持的音频格式
- **WAV** - 完全支持（推荐）
- **MP3/FLAC/M4A** - 需要安装 FFmpeg

### 📦 FFmpeg 安装（可选但推荐）

**Windows Chocolatey：**
```bash
choco install ffmpeg
```

**Windows 手动安装：**
1. 下载：https://ffmpeg.org/download.html
2. 解压到 `C:\ffmpeg`
3. 添加 `C:\ffmpeg\bin` 到 PATH 环境变量

**验证：**
```bash
ffmpeg -version
```

## � 模型说明

| 模型 | 质量等级 | 速度 | 显存需求 | 场景 |
|------|---------|------|---------|------|
| `htdemucs (推荐)` | ⭐⭐⭐⭐ | 快 | 2GB+ | 日常使用 |
| `htdemucs_6sources` | ⭐⭐⭐⭐⭐ | 中 | 4GB+ | 高质量需求 |
| `htdemucs_ft` | ⭐⭐⭐⭐ | 中等 | 3GB+ | 精调版本 |

## 📊 模型对比

| 模型 | 质量 | 速度 | 显存需求 |
|------|------|------|---------|
| `htdemucs_6sources` | ⭐⭐⭐⭐⭐ | 中等 | 4GB+ |
| `htdemucs` | ⭐⭐⭐⭐ | 快 | 2GB+ |
| `demucs` | ⭐⭐⭐ | 最快 | 1GB+ |

## 💡 常见问题

### Q: 处理速度太慢？
A: 
- 检查是否有 GPU 支持（NVIDIA GPU 推荐）
- 使用 `htdemucs` 或 `demucs` 模型而非 `htdemucs_6sources`
- 关闭其他应用程序释放系统资源

### Q: MP3 导出失败？
A: 确保已安装 FFmpeg，在命令行运行 `ffmpeg -version` 验证

### Q: 人声分离效果不好？
A: 
- 尝试使用 `htdemucs_6sources` 模型提高质量
- 某些特殊音乐风格（如人声极轻的合唱）可能效果一般
- 确保输入音频清晰，避免高度压缩或失真的音频

### Q: 支持哪些音频格式？
A: 支持 MP3、WAV、FLAC、M4A、OGG、OPUS 等主流格式

### Q: 可以处理立体声和单声道吗？
A: 都支持，程序会自动转换

## 📂 输出文件说明

处理完成后，输出目录会包含：
- `原文件名_accompaniment.mp3` - MP3 格式伴奏
- `原文件名_accompaniment.wav` - WAV 格式伴奏

## ⚙️ 高级用法

### 命令行模式（可选）

创建 `process_batch.py` 用于批量处理：

```python
from audio_processor import AudioProcessor

processor = AudioProcessor()

# 批量处理多个文件
files = [
    "song1.mp3",
    "song2.wav",
    "song3.flac"
]

for file in files:
    processor.process(
        input_file=file,
        output_dir="output",
        model="htdemucs",
        output_formats=["mp3", "wav"]
    )
```

## 🔬 技术原理

本应用基于 **Demucs**（Deep Extractor of Music Sources），由 Meta/Facebook 开发的最先进的开源音源分离模型。

**原理**：
1. 使用卷积神经网络（CNN）对音频进行分析
2. 识别并分离不同的音源（人声、贝司、鼓、其他）
3. 通过组合这些源获得高质量的伴奏

**相比传统方法的优势**：
- 基于深度学习，准确率更高
- 能够保留微妙的音乐元素
- 自适应不同的音乐风格

## 📝 项目结构

```
人声分离/
├── app.py                # 主应用程序 (GUI)
├── processor.py          # 音源分离处理器
├── config.json          # 配置文件
├── requirements.txt     # 依赖列表
├── README.md           # 本文件
└── output/             # 输出目录
```

## 📄 许可证

Demucs 模型：[Creative Commons Attribution 4.0 International](https://github.com/facebookresearch/demucs)

## 🔗 资源

- [Demucs GitHub](https://github.com/facebookresearch/demucs)
- [PyQt5 文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Librosa 文档](https://librosa.org/)

---

**版本**：3.0  
**Python**：3.10+  
**最后更新**：2026 年  

💡 **提示**：首次运行会自动下载 Demucs 模型（~200MB），请耐心等待。
