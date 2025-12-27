@echo off
chcp 65001
echo ========================================
echo 物业收费管理系统 - Windows 7 兼容打包
echo ========================================
echo.

echo [1/4] 检查Python 3.8环境...
py -3.8 --version
if errorlevel 1 (
    echo 错误: 未找到Python 3.8，请先安装Python 3.8.10
    pause
    exit /b 1
)
echo.

echo [2/4] 检查依赖是否已安装...
py -3.8 -m pip show PyQt5 >nul 2>&1
if errorlevel 1 (
    echo 警告: 依赖未安装，请先安装依赖
    echo 运行: py -3.8 -m pip install -r requirements-win7.txt
    echo 或使用: 安装Win7依赖-使用镜像.bat
    echo.
    echo 是否继续打包？(依赖未安装可能导致打包失败)
    pause
) else (
    echo 依赖已安装，继续打包...
)
echo.
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo.

echo [3/4] 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

echo [4/4] 正在打包物业收费管理系统 (Windows 7兼容模式)...
echo 使用PyInstaller 4.10进行打包，确保Windows 7兼容性...
py -3.8 -m PyInstaller --clean PropertyManager-win7.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo 正在重命名...
if exist "dist\PropertyManager.exe" (
    ren "dist\PropertyManager.exe" "物业收费管理系统_Win7.exe"
    echo.
    echo ========================================
    echo 打包完成！
    echo ========================================
    echo 文件位置: dist\物业收费管理系统_Win7.exe
    echo.
    echo 注意事项:
    echo 1. 请在Windows 7 SP1系统上测试运行
    echo 2. 确保已安装 Visual C++ Redistributable 2015-2022
    echo 3. 首次运行可能需要较长时间解压
    echo ========================================
) else (
    echo [错误] 打包似乎失败了，未找到 dist\PropertyManager.exe
)

echo.
pause

