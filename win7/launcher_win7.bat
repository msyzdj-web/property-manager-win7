@echo off
rem 启动器：为每次运行创建唯一 TEMP 目录，避免 PyInstaller 解包到已存在 _MEI* 导致冲突弹窗
rem 将本脚本放在和 "物业收费管理系统_Win7.exe" 同一目录，并双击本脚本启动程序。

setlocal enabledelayedexpansion

rem 生成唯一目录名（时间 + 随机数）
for /f "tokens=1-6 delims=:-/. " %%a in ("%date% %time%") do (
  set YY=%%f
  set MM=%%b
  set DD=%%c
  set HH=%%d
  set MN=%%e
)
set RAND=%RANDOM%
set UID=%YY%%MM%%DD%_%HH%%MN%_%RAND%
set TMPDIR=%TEMP%\PM_%UID%

rem 创建临时目录并导出为 TMP 和 TEMP（PyInstaller bootloader 会读取这些环境变量）
if not exist "%TMPDIR%" mkdir "%TMPDIR%"
set TMP=%TMPDIR%
set TEMP=%TMPDIR%

rem 可选：打印到控制台便于诊断
echo Using TEMP=%TMPDIR%

rem 启动 exe（若文件名不同请改为你的 exe 名称）
rem 为了诊断在临时目录写入日志并以同步方式运行，以便捕获任何异常输出
set LOGFILE=%TMPDIR%\launcher_log.txt
echo Launch time: %DATE% %TIME% > "%LOGFILE%"
echo Source exe: "%~dp0\物业收费管理系统_Win7.exe" >> "%LOGFILE%"

rem Copy exe into the unique temp dir and run it from there to ensure PyInstaller unpacks into a unique _MEI dir.
set SRC="%~dp0\物业收费管理系统_Win7.exe"
set DST="%TMPDIR%\物业收费管理系统_Win7.exe"
echo Copying %SRC% to %DST% >> "%LOGFILE%"
copy %SRC% %DST% /Y >> "%LOGFILE%" 2>&1

rem Set TEMP/TMP so the bootloader unpacks into our unique tmpdir
set TMP=%TMPDIR%
set TEMP=%TMPDIR%

rem Change to temp dir and run synchronously, capturing output
pushd "%TMPDIR%"
echo Running: "%DST%" >> "%LOGFILE%"
start "" /wait "%DST%" >> "%LOGFILE%" 2>&1
set RC=%ERRORLEVEL%
echo Exit code: %RC% >> "%LOGFILE%"
popd

echo Exit time: %DATE% %TIME% >> "%LOGFILE%"

endlocal


