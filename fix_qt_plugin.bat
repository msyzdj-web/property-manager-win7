@echo off
echo 正在修复Qt插件问题...
echo.

echo 方法1: 重新安装PyQt5
pip uninstall PyQt5 -y
pip install PyQt5==5.15.10

echo.
echo 方法2: 如果还有问题，尝试安装完整版本
pip install PyQt5==5.15.10 PyQt5-Qt5==5.15.2 PyQt5-sip==12.12.2

echo.
echo 修复完成！请重新运行程序。
pause

