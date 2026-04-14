"""
音源分离处理器 - 独立进程脚本
解决 Python 3.14 + PyTorch DLL + 线程问题
"""

import sys
import json
from pathlib import Path

def process_music(input_file, output_dir, model_name):
    """独立进程中进行音源分离"""
    try:
        import torch
        import librosa
        import soundfile as sf
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        
        print(f"[LOG] 开始处理：{input_file}")
        print(f"[PROGRESS] 15")
        
        # 加载音频
        print(f"[LOG] 加载音频...")
        audio, sr = librosa.load(input_file, sr=None, mono=False)
        print(f"[LOG] 音频加载成功：{audio.shape}，采样率 {sr} Hz")
        print(f"[PROGRESS] 25")
        
        # 转换为 tensor
        if audio.ndim == 1:
            audio_tensor = torch.FloatTensor(audio).unsqueeze(0)
        else:
            audio_tensor = torch.FloatTensor(audio)
        
        if audio_tensor.shape[0] == 1:
            audio_tensor = torch.cat([audio_tensor, audio_tensor], dim=0)
        
        print(f"[LOG] 张量形状：{audio_tensor.shape}")
        print(f"[PROGRESS] 30")
        
        # 加载模型
        print(f"[LOG] 加载模型：{model_name}")
        # 使用正确的模型名称
        actual_model_name = "htdemucs" if model_name == "htdemucs_6sources" else model_name
        model = get_model(actual_model_name)
        device = "cpu"
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
        for i, source_name in enumerate(model.sources):
            if "vocals" not in source_name.lower():
                if accompaniment is None:
                    accompaniment = stems[0, i]
                else:
                    accompaniment = accompaniment + stems[0, i]
        
        if accompaniment is None:
            raise Exception("无法提取伴奏")
        
        accompaniment = accompaniment.cpu().numpy()
        print(f"[LOG] 伴奏提取完成，形状：{accompaniment.shape}")
        print(f"[PROGRESS] 80")
        
        # 保存
        print(f"[LOG] 保存文件...")
        stem = Path(input_file).stem
        output_file = Path(output_dir) / f"{stem}_accompaniment.wav"
        
        # 保存为 WAV
        sf.write(str(output_file), accompaniment.T, sr)
        
        file_size = output_file.stat().st_size / (1024*1024)
        print(f"[LOG] 成功保存：{output_file}（{file_size:.1f} MB）")
        print(f"[PROGRESS] 100")
        print(f"[SUCCESS] {str(output_file)}")
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"[ERROR] {str(e)}\n{error_msg[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("[ERROR] Usage: python processor.py <input_file> <output_dir> <model_name>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    model_name = sys.argv[3]
    
    process_music(input_file, output_dir, model_name)
