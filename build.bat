@echo off
chcp 65001
echo 正在清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo 正在打包物业收费管理系统 (GUI模式)...
:: 使用英文名进行打包，避免 PyInstaller 处理中文参数时的编码乱码问题
pyinstaller --noconsole --onefile --clean --collect-all=openpyxl --add-data "logo.jpg;." --icon="logo.ico" --name="PropertyManager" main.py

echo 正在重命名...
if exist "dist\PropertyManager.exe" (
    ren "dist\PropertyManager.exe" "物业收费管理系统.exe"
    echo 打包完成！文件的位置: dist\物业收费管理系统.exe
) else (
    echo [错误] 打包似乎失败了，未找到 dist\PropertyManager.exe
)

pause

