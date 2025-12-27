@echo off
chcp 65001
echo ========================================
echo 安装 Windows 7 兼容依赖（使用国内镜像）
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

echo [2/3] 使用清华镜像源安装依赖包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

echo 正在安装 PyQt5...
py -3.8 -m pip install PyQt5==5.15.10 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 警告: PyQt5 安装可能失败，尝试使用默认源...
    py -3.8 -m pip install PyQt5==5.15.10
)

echo.
echo 正在安装 SQLAlchemy...
py -3.8 -m pip install SQLAlchemy==1.4.46 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 错误: SQLAlchemy 安装失败
    pause
    exit /b 1
)

echo.
echo 正在安装 PyInstaller...
py -3.8 -m pip install pyinstaller==4.10 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 错误: PyInstaller 安装失败
    pause
    exit /b 1
)

echo.
echo 正在安装 openpyxl...
py -3.8 -m pip install openpyxl==3.1.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 警告: openpyxl 安装可能失败，继续安装...
)

echo.
echo 正在安装 pandas...
py -3.8 -m pip install pandas==1.5.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 警告: pandas 安装可能失败，继续安装...
)

echo.

echo [3/3] 验证安装...
echo.
echo 已安装的包：
py -3.8 -m pip list | findstr /i "PyQt5 SQLAlchemy pyinstaller openpyxl pandas"
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步：运行 build-win7.bat 进行打包
echo.
pause

