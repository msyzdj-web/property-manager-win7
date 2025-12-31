@echo off
chcp 65001 >nul
echo === PyInstaller弹窗问题修复工具 ===
echo.
echo 此工具将：
echo 1. 清理旧的_MEI临时目录
echo 2. 添加Windows Defender排除
echo 3. 如有需要，临时关闭实时防护
echo.
echo 请确保已关闭所有相关程序后再运行！
echo.
pause

rem 使用 -File 以确保 PowerShell 按文件编码正确读取脚本
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix_defender_issue.ps1"

echo.
echo 脚本执行完成。
echo 现在请尝试运行物业收费管理系统.exe
echo.
pause
