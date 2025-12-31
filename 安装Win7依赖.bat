@echo off
chcp 65001
echo ========================================
echo 安装 Windows 7 兼容依赖
echo ========================================
echo.

echo [1/3] 检查 Python 3.8...
py -3.8 --version
if errorlevel 1 (
    echo 错误: 未找到 Python 3.8
    pause
    exit /b 1
)
echo.

echo [2/3] 安装依赖包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

py -3.8 -m pip install PyQt5==5.15.10
if errorlevel 1 (
    echo 警告: PyQt5 安装可能失败，继续安装其他依赖...
)

py -3.8 -m pip install SQLAlchemy==1.4.46
if errorlevel 1 (
    echo 错误: SQLAlchemy 安装失败
    pause
    exit /b 1
)

py -3.8 -m pip install pyinstaller==4.10
if errorlevel 1 (
    echo 错误: PyInstaller 安装失败
    pause
    exit /b 1
)

py -3.8 -m pip install openpyxl==3.1.2
if errorlevel 1 (
    echo 警告: openpyxl 安装可能失败，继续安装...
)

py -3.8 -m pip install pandas==1.5.3
if errorlevel 1 (
    echo 警告: pandas 安装可能失败，继续安装...
)

echo.

echo [3/3] 验证安装...
py -3.8 -m pip list | findstr /i "PyQt5 SQLAlchemy pyinstaller openpyxl pandas"
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步：运行 build-win7.bat 进行打包
echo.
pause

