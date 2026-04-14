@echo off
REM 人声分离应用 - 一键启动脚本

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   AI 人声分离 - 去声伴奏生成器
echo ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [✓] Python 已安装

REM 检查依赖
echo.
echo [检查] 正在检查依赖项...
pip show PyQt5 >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖项，这可能需要几分钟...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [✓] 依赖项已就绪

REM 检查 FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [警告] 未检测到 FFmpeg
    echo 如果需要 MP3 导出功能，请安装 FFmpeg
    echo 下载地址: https://ffmpeg.org/download.html
    echo.
    echo 按 Y 继续启动应用，按其他键退出
    set /p choice=
    if /i not "!choice!"=="Y" (
        exit /b 1
    )
) else (
    echo [✓] FFmpeg 已安装
)

REM 启动应用
echo.
echo [启动] 启动应用程序（v3-CLI 子进程方案）...
echo.

python app_v3.py

pause
