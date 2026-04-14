"""
人声分离应用 v3 - 使用 Demucs CLI 子进程
完全避免 PyTorch DLL 在主进程中的初始化问题
"""

import sys
import os
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QFileDialog, QMessageBox,
    QComboBox, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer
from PyQt5.QtGui import QFont


class ProcessingSignals(QObject):
    """处理线程的信号"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    message = pyqtSignal(str)


class ProcessingWorker(QThread):
    """使用 Demucs CLI 的处理线程"""
    
    def __init__(self, input_file, output_dir, model_name):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir
        self.model_name = model_name
        self.signals = ProcessingSignals()
    
    def run(self):
        try:
            import librosa
            import soundfile as sf
            
            self.signals.message.emit("✓ 初始化处理...")
            self.signals.progress.emit(5)
            
            # 验证输入
            if not os.path.exists(self.input_file):
                raise Exception(f"❌ 文件不存在：{self.input_file}")
            
            file_size = os.path.getsize(self.input_file) / (1024*1024)
            self.signals.message.emit(f"✓ 输入文件 ({file_size:.1f} MB)")
            self.signals.progress.emit(10)
            
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            # 获取模型参数
            model_map = {
                "htdemucs (推荐)": "htdemucs",
                "htdemucs_6sources": "htdemucs_6sources",
                "htdemucs_ft": "htdemucs_ft"
            }
            model_param = model_map.get(self.model_name, "htdemucs")
            
            self.signals.message.emit(f"✓ 使用模型: {model_param}")
            self.signals.progress.emit(15)
            
            # 预处理音频：如果是 MP3/FLAC/M4A，先转换为 WAV
            input_for_processing = self.input_file
            temp_wav = None
            
            if self.input_file.lower().endswith(('.mp3', '.flac', '.m4a', '.aac')):
                self.signals.message.emit("📝 预处理音频文件（转换为 WAV）...")
                self.signals.progress.emit(18)
                
                try:
                    # 使用 librosa 加载
                    self.signals.message.emit("  加载音频...")
                    audio, sr = librosa.load(self.input_file, sr=None, mono=False)
                    
                    # 保存为临时 WAV
                    temp_wav = os.path.join(
                        self.output_dir, 
                        f"_temp_{Path(self.input_file).stem}.wav"
                    )
                    self.signals.message.emit(f"  转换为 WAV...")
                    sf.write(temp_wav, audio.T if audio.ndim > 1 else audio, sr)
                    input_for_processing = temp_wav
                    self.signals.message.emit("✓ 预处理完成")
                    
                except Exception as e:
                    raise Exception(f"❌ 音频预处理失败：{str(e)[:150]}")
            
            # 调用独立处理器
            self.signals.message.emit("🔄 启动处理器（此过程可能需要 1-10 分钟）...")
            self.signals.progress.emit(20)
            
            try:
                # 获取当前脚本目录
                script_dir = os.path.dirname(os.path.abspath(__file__))
                processor_script = os.path.join(script_dir, "processor_standalone.py")
                
                if not os.path.exists(processor_script):
                    raise Exception(f"处理器脚本不存在：{processor_script}")
                
                # 运行处理器
                cmd = [
                    sys.executable,
                    processor_script,
                    input_for_processing,
                    self.output_dir,
                    model_param
                ]
                
                self.signals.message.emit(f"执行: processor_standalone.py")
                
                # 运行处理，实时读取输出
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                success = False
                output_file = None
                
                # 实时读取输出
                for line in iter(process.stdout.readline, ''):
                    if line:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if line.startswith("[PROGRESS]"):
                            try:
                                progress = int(line.split("]")[1].strip())
                                self.signals.progress.emit(progress)
                            except:
                                pass
                        elif line.startswith("[LOG]"):
                            msg = line.replace("[LOG]", "").strip()
                            self.signals.message.emit(f"  {msg}")
                        elif line.startswith("[SUCCESS]"):
                            output_file = line.replace("[SUCCESS]", "").strip()
                            self.signals.message.emit(f"✓ 伴奏文件: {output_file}")
                            success = True
                        elif line.startswith("[ERROR]"):
                            error = line.replace("[ERROR]", "").strip()
                            self.signals.message.emit(f"❌ {error}")
                        else:
                            self.signals.message.emit(f"  {line}")
                
                process.wait(timeout=900)  # 15分钟超时
                
                # 清理临时文件
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                        self.signals.message.emit("✓ 临时文件已清理")
                    except:
                        pass
                
                if process.returncode != 0:
                    raise Exception(f"处理器返回错误代码: {process.returncode}")
                
                if not success or not output_file:
                    raise Exception("处理失败或未生成输出文件")
                
                self.signals.progress.emit(100)
                self.signals.message.emit(f"✅ 成功完成！\n文件保存到：{self.output_dir}")
                self.signals.finished.emit()
            
            except subprocess.TimeoutExpired:
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except:
                        pass
                raise Exception("❌ 处理超时（>15分钟）。请尝试更短的音频或重启尝试。")
            except Exception as e:
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except:
                        pass
                raise Exception(f"❌ 处理失败：{str(e)[:300]}")
        
        except Exception as e:
            self.signals.error.emit(f"❌ 处理失败\n\n{str(e)}")


class VocalRemoverApp(QMainWindow):
    """人声分离应用 v3"""
    
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.worker = None
        self.initUI()
        
        # 检查依赖
        self.check_dependencies()
    
    def check_dependencies(self):
        """检查必要的依赖"""
        self.status_label.setText("🔄 检查依赖...")
        QApplication.processEvents()
        
        try:
            # 检查 demucs
            result = subprocess.run(
                [sys.executable, "-m", "demucs", "--help"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.status_label.setText("✅ 所有依赖已就绪，可以开始处理")
                self.process_btn.setEnabled(True)
            else:
                self.status_label.setText("⚠️ Demucs 可能未正确安装")
        
        except Exception as e:
            self.status_label.setText(f"❌ 依赖检查失败：{str(e)[:50]}")
    
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle("🎵 AI 人声分离 - v3 (CLI)")
        self.setGeometry(100, 100, 700, 550)
        
        # 主窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel("🎵 AI 人声分离工具 v3")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        #状态标签
        self.status_label = QLabel("🔄 检查依赖...")
        self.status_label.setStyleSheet("color: #FF8C00; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # 文件选择
        file_frame = QFrame()
        file_frame.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 10px;")
        file_layout = QVBoxLayout(file_frame)
        
        file_label = QLabel("👇 选择音频文件：")
        file_layout.addWidget(file_label)
        
        file_btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择文件 (MP3/WAV/FLAC/M4A)")
        self.select_btn.clicked.connect(self.select_file)
        file_btn_layout.addWidget(self.select_btn)
        
        self.file_info = QLabel("未选择")
        file_btn_layout.addWidget(self.file_info)
        file_layout.addLayout(file_btn_layout)
        
        layout.addWidget(file_frame)
        
        # 模型选择
        model_frame = QFrame()
        model_frame.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 10px;")
        model_layout = QVBoxLayout(model_frame)
        
        model_label = QLabel("⚙️ 选择处理模型：")
        model_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["htdemucs (推荐)", "htdemucs_6sources", "htdemucs_ft"])
        model_layout.addWidget(self.model_combo)
        
        layout.addWidget(model_frame)
        
        # 输出目录
        output_frame = QFrame()
        output_frame.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 10px;")
        output_layout = QVBoxLayout(output_frame)
        
        output_label = QLabel("📂 输出目录：")
        output_layout.addWidget(output_label)
        
        output_btn_layout = QHBoxLayout()
        self.output_btn = QPushButton("选择输出目录")
        self.output_btn.clicked.connect(self.select_output)
        output_btn_layout.addWidget(self.output_btn)
        
        self.output_info = QLabel("output/")
        output_btn_layout.addWidget(self.output_info)
        output_layout.addLayout(output_btn_layout)
        
        layout.addWidget(output_frame)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日志
        log_label = QLabel("📋 处理日志：")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("🚀 开始处理")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        btn_layout.addWidget(self.process_btn)
        
        self.clear_btn = QPushButton("🧹 清除日志")
        self.clear_btn.clicked.connect(self.log_text.clear)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 设置默认输出路径
        self.output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "VocalRemoval_Output")
        self.output_info.setText(self.output_dir)
    
    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件", "",
            "音频文件 (*.mp3 *.wav *.flac *.m4a);;所有文件 (*.*)"
        )
        if file_path:
            self.input_file = file_path
            self.file_info.setText(os.path.basename(file_path))
            self.log_text.append(f"✓ 已选择：{file_path}")
    
    def select_output(self):
        """选择输出目录"""
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_dir = path
            self.output_info.setText(path)
    
    def start_processing(self):
        """开始处理"""
        if not self.input_file:
            QMessageBox.warning(self, "提示", "请先选择音频文件")
            return
        
        # 禁用按钮
        self.process_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.log_text.clear()
        
        # 创建并启动worker
        self.worker = ProcessingWorker(
            self.input_file, 
            self.output_dir, 
            self.model_combo.currentText()
        )
        
        self.worker.signals.message.connect(self.log_message)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.error.connect(self.on_error)
        self.worker.signals.finished.connect(self.on_finished)
        
        self.worker.start()
    
    def log_message(self, msg):
        """添加日志消息"""
        self.log_text.append(msg)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def on_error(self, error):
        """处理错误"""
        self.log_text.append(error)
        QMessageBox.critical(self, "处理失败", error)
        self.process_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def on_finished(self):
        """处理完成"""
        self.process_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VocalRemoverApp()
    window.show()
    sys.exit(app.exec_())
