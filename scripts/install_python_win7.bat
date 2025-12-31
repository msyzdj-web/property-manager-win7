@echo off
rem 安装 Python 3.8 在 Windows 7（离线/非交互式辅助脚本）
rem 使用方法：
rem   将本脚本放到项目根目录，双击运行或在管理员命令提示符中运行：
rem     scripts\install_python_win7.bat 3.8.18
rem 可选参数：指定 Python 3.8 版本（例如 3.8.18）。默认使用 3.8.18。

setlocal enabledelayedexpansion
set PYVER=%1
if "%PYVER%"=="" set PYVER=3.8.18

echo Installing Python %PYVER% for Windows...

rem 下载地址（官方） - x64 安装器（如果需要 x86，请改为 -embed or x86 下载链接）
set BASE_URL=https://www.python.org/ftp/python/%PYVER%
set EXE_NAME=python-%PYVER%-amd64.exe
set DOWNLOAD_URL=%BASE_URL%/%EXE_NAME%

echo Downloading %DOWNLOAD_URL% ...
powershell -Command "try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%EXE_NAME%' -UseBasicParsing } catch { exit 1 }"
if %errorlevel% neq 0 (
  echo 下载失败，请检查网络或手动从 https://www.python.org/downloads/ 下载对应版本。
  exit /b 1
)

echo Running installer (silent) ...
rem 静默安装，InstallAllUsers=1 将默认安装到 Program Files，下列选项会把 Python 添加到 PATH
%EXE_NAME% /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
if %errorlevel% neq 0 (
  echo 安装失败，退出码 %errorlevel%
  exit /b %errorlevel%
)

echo Cleaning installer...
del /f /q %EXE_NAME% 2>nul

echo Creating virtualenv in project folder...
cd /d %~dp0\..
if not exist .venv (
  python -m venv .venv
) else (
  echo .venv already exists
)

echo Activating virtualenv and installing requirements...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
if exist requirements-win7.txt (
  pip install -r requirements-win7.txt
) else (
  pip install -r requirements.txt
)

echo Running DB migration (remember to backup property.db first)...
python migrate_db.py

echo Done. To run the app:
echo   .venv\Scripts\activate.bat
echo   python main.py

endlocal


