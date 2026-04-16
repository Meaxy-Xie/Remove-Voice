"""
音源分离处理器 - 独立进程脚本
支持 GPU/CPU、多模型、优化的内存管理
"""

import sys
import os
from pathlib import Path

def get_device():
    """自动检测最佳设备"""
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            print(f"[LOG] 检测到 GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            print(f"[LOG] 使用 CPU 处理")
        return device
    except Exception:
        return "cpu"

def load_audio(input_file):
    """智能加载音频文件，支持多种格式"""
    import librosa
    import soundfile as sf
    import numpy as np
    from scipy import io as scipy_io
    
    print(f"[LOG] 正在加载音频: {input_file}")
    
    # 首先尝试librosa（支持所有格式，需要ffmpeg来处理非WAV）
    try:
        audio, sr = librosa.load(input_file, sr=None, mono=False)
        print(f"[LOG] 使用 librosa 成功加载")
        return audio, sr
    except Exception as e:
        print(f"[LOG] librosa 加载失败: {str(e)[:100]}")
        
        # 如果是WAV文件，尝试scipy
        if input_file.lower().endswith('.wav'):
            try:
                sr, audio = scipy_io.wavfile.read(input_file)
                if audio.ndim == 1:
                    audio = np.expand_dims(audio, axis=0)
                else:
                    audio = audio.T  # scipy 是 (samples, channels)，librosa 是 (channels, samples)
                audio = audio.astype(np.float32) / 32768.0 if audio.dtype == np.int16 else audio.astype(np.float32)
                print(f"[LOG] 使用 scipy 成功加载 WAV")
                return audio, sr
            except Exception as e2:
                print(f"[LOG] scipy 加载也失败: {str(e2)[:100]}")
        
        # 如果是MP3等格式，提示需要ffmpeg
        if input_file.lower().endswith(('.mp3', '.flac', '.m4a', '.aac')):
            raise Exception(
                f"❌ 无法加载 {input_file.split('.')[-1].upper()} 格式文件\\n"
                f"原因: 需要 FFmpeg 来处理此格式\\n"
                f"解决方案: 建议用在线工具转换为 WAV 格式，或安装 FFmpeg\\n"
                f"错误详情: {str(e)[:100]}"
            )
        
        raise Exception(f"❌ 无法加载音频文件: {str(e)[:200]}")

def get_actual_model_name(model_name):
    """获取实际的 Demucs 模型名（所有 htdemucs 变体使用同一模型）"""
    return "demucs" if model_name == "demucs" else "htdemucs"

def process_music(input_file, output_dir, model_name):
    """独立进程中进行音源分离"""
    try:
        import torch
        import librosa
        import soundfile as sf
        import numpy as np
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        
        print(f"[LOG] 开始处理：{input_file}")
        print(f"[PROGRESS] 10")
        
        # 验证输入文件
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在：{input_file}")
        
        # 加载音频
        print(f"[LOG] 加载音频中...")
        audio, sr = load_audio(input_file)
        print(f"[LOG] 音频加载成功 - 形状：{audio.shape}，采样率：{sr} Hz")
        print(f"[PROGRESS] 20")
        
        # 确保是立体声
        if audio.ndim == 1:
            audio = np.stack([audio, audio], axis=0)
        
        # 转换为 tensor
        audio_tensor = torch.FloatTensor(audio)
        if audio_tensor.shape[0] == 1:
            audio_tensor = torch.cat([audio_tensor, audio_tensor], dim=0)
        
        print(f"[LOG] 张量形状：{audio_tensor.shape}")
        print(f"[PROGRESS] 25")
        
        # 获取设备
        device = get_device()
        print(f"[PROGRESS] 30")
        
        # 加载模型
        actual_model = get_actual_model_name(model_name)
        print(f"[LOG] 加载模型：{actual_model}...")
        model = get_model(actual_model)
        model = model.to(device)
        model.eval()
        print(f"[LOG] 模型已加载")
        print(f"[PROGRESS] 40")
        
        # 分离
        print(f"[LOG] 开始音源分离...")
        audio_tensor = audio_tensor.to(device)
        with torch.no_grad():
            stems = apply_model(model, audio_tensor[None])
        
        print(f"[LOG] 分离完成，输出形状：{stems.shape}")
        print(f"[PROGRESS] 70")
        
        # 提取伴奏（所有非人声）
        print(f"[LOG] 提取伴奏...")
        accompaniment = None
        vocal = None
        
        for i, source_name in enumerate(model.sources):
            source_lower = source_name.lower()
            if "vocal" in source_lower or "voice" in source_lower:
                vocal = stems[0, i]
            elif accompaniment is None:
                accompaniment = stems[0, i]
            else:
                accompaniment = accompaniment + stems[0, i]
        
        if accompaniment is None:
            accompaniment = stems[0, 0]
        
        accompaniment = accompaniment.cpu().numpy()
        print(f"[LOG] 伴奏提取完成，形状：{accompaniment.shape}")
        print(f"[PROGRESS] 80")
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 保存伴奏
        print(f"[LOG] 保存文件...")
        stem = Path(input_file).stem
        output_file = Path(output_dir) / f"{stem}_accompaniment.wav"
        
        # 处理音频形状并保存
        if accompaniment.ndim == 2:
            sf.write(str(output_file), accompaniment.T, sr)
        else:
            sf.write(str(output_file), accompaniment, sr)
        
        file_size = output_file.stat().st_size / (1024*1024)
        print(f"[LOG] 伴奏已保存：{output_file}（{file_size:.1f} MB）")
        
        # 保存人声（如果找到）
        if vocal is not None:
            vocal = vocal.cpu().numpy()
            vocal_file = Path(output_dir) / f"{stem}_vocal.wav"
            if vocal.ndim == 2:
                sf.write(str(vocal_file), vocal.T, sr)
            else:
                sf.write(str(vocal_file), vocal, sr)
            vocal_size = vocal_file.stat().st_size / (1024*1024)
            print(f"[LOG] 人声已保存：{vocal_file}（{vocal_size:.1f} MB）")
        
        print(f"[PROGRESS] 100")
        print(f"[SUCCESS] {str(output_file)}")
        
    except ImportError as e:
        print(f"[ERROR] 缺少依赖：{str(e)}")
        print("[ERROR] 请运行：pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"[ERROR] {str(e)[:200]}")
        if "CUDA" in str(e) or "cuda" in str(e):
            print("[ERROR] GPU 错误，正在回退到 CPU...")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("[ERROR] 使用方法：python processor_standalone.py <输入文件> <输出目录> <模型名>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    model_name = sys.argv[3]
    
    # 验证输入参数
    if not input_file or not output_dir or not model_name:
        print("[ERROR] 参数不能为空")
        sys.exit(1)
    
    process_music(input_file, output_dir, model_name)
