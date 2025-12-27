@echo off
chcp 65001 >nul
echo ========================================
echo 物业收费管理系统 - 快速修复工具
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)
echo ✓ Python环境正常
echo.

echo [2/3] 检查PyQt5安装...
python -c "import PyQt5; print('✓ PyQt5已安装')" 2>nul
if errorlevel 1 (
    echo ✗ PyQt5未安装，正在安装...
    pip install PyQt5==5.15.10
    if errorlevel 1 (
        echo 错误: PyQt5安装失败
        pause
        exit /b 1
    )
) else (
    echo ✓ PyQt5已安装
)
echo.

echo [3/3] 运行Qt测试...
python test_qt.py
if errorlevel 1 (
    echo.
    echo 检测到问题，正在尝试修复...
    echo.
    pip uninstall PyQt5 -y
    pip install PyQt5==5.15.10
    echo.
    echo 修复完成，请重新运行程序
) else (
    echo.
    echo ✓ 所有检查通过！
    echo.
    echo 现在可以运行程序了：
    echo   python main.py
)
echo.
pause

