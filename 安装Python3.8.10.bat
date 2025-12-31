@echo off
chcp 65001
echo ========================================
echo Python 3.8.10 安装助手
echo ========================================
echo.

echo 当前 Python 版本检查：
python --version 2>nul
if errorlevel 1 (
    echo 未检测到 Python
) else (
    python --version
)
echo.

echo 检查 py launcher：
py --version 2>nul
if errorlevel 1 (
    echo 未检测到 py launcher
) else (
    echo py launcher 可用
    py --list 2>nul
)
echo.

echo ========================================
echo 安装说明
echo ========================================
echo.
echo 1. 下载 Python 3.8.10：
echo    64位: https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
echo    32位: https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe
echo.
echo 2. 运行安装程序时，请务必：
echo    - 勾选 "Add Python 3.8 to PATH"
echo    - 勾选 "Install for all users"（可选）
echo.
echo 3. 安装完成后，在新的命令提示符中运行：
echo    py -3.8 --version
echo.
echo 4. 如果显示 Python 3.8.10，则安装成功！
echo.
echo ========================================
echo 快速下载链接
echo ========================================
echo.
echo 正在打开下载页面...
start https://www.python.org/downloads/release/python-3810/
echo.
echo 如果浏览器未自动打开，请手动访问：
echo https://www.python.org/downloads/release/python-3810/
echo.
echo ========================================
pause

