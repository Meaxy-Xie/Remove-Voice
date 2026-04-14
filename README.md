# 🎵 AI 人声分离 - 去声伴奏生成器

一个简单易用的人声分离软件，使用最新的 **Demucs 模型** 技术，能够从歌曲中自动去除人声，保留高质量的伴奏和和声。

## ✨ 功能特性

- 🎯 **高精度人声分离** - 使用 Meta/Facebook 开源的 Demucs AI 模型
- 🎨 **友好的图形界面** - 简洁直观的 PyQt5 GUI，无需命令行
- 📁 **支持多格式** - 支持 MP3、WAV、FLAC、M4A 等音频格式
- 💾 **双格式输出** - 同时生成 MP3（文件小）和 WAV（无损）
- 🚀 **多个模型选择** - 3 种模型可选，音质和速度可自由权衡
- 🎵 **保留和声和伴奏** - 智能保留除人声外的所有音频元素

## 📋 系统要求

- **操作系统**：Windows 10/11（推荐 64 位）
- **Python**：3.9 或更高版本
- **显存**：GPU 推荐（无 GPU 也可运行，但会较慢）
- **磁盘空间**：至少 2GB（用于模型和处理）

## 🔧 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

如果安装失败，可以逐个安装：

```bash
pip install PyQt5==5.15.9
pip install torch==2.0.1 -i https://download.pytorch.org/whl/cu118
pip install torchaudio==2.0.2
pip install demucs==4.0.1
pip install librosa==0.10.0
pip install soundfile==0.12.1
```

### 2. 安装 FFmpeg（用于 MP3 导出）

**Windows 方式一：使用 Chocolatey**
```bash
choco install ffmpeg
```

**Windows 方式二：手动安装**
1. 从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载 Windows 版本
2. 解压到 `C:\ffmpeg`
3. 将 `C:\ffmpeg\bin` 添加到系统环境变量 PATH

验证安装：
```bash
ffmpeg -version
```

## 🚀 使用方法

### 启动应用

```bash
python main.py
```

应用窗口会弹出，包含以下步骤：

### 使用步骤

1. **点击 "📁 选择音乐文件"** - 选择你要处理的歌曲
2. **选择处理模型**
   - `htdemucs_6sources` (推荐) - 最高质量，处理时长
   - `htdemucs` - 快速高质量
   - `demucs` - 标准版本
3. **选择输出格式**
   - 双格式 - 同时输出 MP3 和 WAV
   - 仅 MP3 - 文件较小
   - 仅 WAV - 无损质量
4. **点击 "🚀 开始去声"**
5. **选择输出目录** - 保存伴奏文件

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

## 📝 许可证

本项目使用 MIT 许可证。Demucs 模型由 Meta 发布，使用 Creative Commons Attribution 4.0 International 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📚 参考资源

- [Demucs GitHub](https://github.com/facebookresearch/demucs)
- [PyQt5 文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Librosa 文档](https://librosa.org/)

---

**开发者**：AI Assistant  
**最后更新**：2024 年  
**版本**：1.0

享受高质量的音乐伴奏吧！🎵
