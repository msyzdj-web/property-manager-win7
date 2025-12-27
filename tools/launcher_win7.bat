@echo off
chcp 65001 >nul
rem 启动器：为每次运行创建唯一 TEMP 目录，避免 PyInstaller 解包到已存在 _MEI* 导致冲突弹窗
rem 将本脚本放在和 "物业收费管理系统_Win7.exe" 同一目录，并双击本脚本启动程序。

setlocal enabledelayedexpansion

rem 可选：允许通过环境变量跳过旧 _MEI 清理（用于调试）
if /I "%LAUNCHER_SKIP_CLEANUP%"=="1" (
  echo Skipping old _MEI cleanup because LAUNCHER_SKIP_CLEANUP=1
) else (
  rem 使用外部 PowerShell 脚本进行清理，避免命令行内联解析/编码问题
  echo Running cleanup script...
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0launcher_cleanup.ps1" -TempPath "%TEMP%" -AppMEIDir "%LOCALAPPDATA%\PropertyManager\MEI"
)
rem 清理应用专用 runtime_tmpdir（%LOCALAPPDATA%\PropertyManager\MEI）
set APP_MEI_DIR=%LOCALAPPDATA%\PropertyManager\MEI
rem Ensure application runtime tmpdir exists. Actual cleanup is handled by launcher_cleanup.ps1 called earlier.
if not exist "%APP_MEI_DIR%" (
  mkdir "%APP_MEI_DIR%" >nul 2>nul
  echo Created app runtime tmpdir: %APP_MEI_DIR%
) else (
  echo App runtime tmpdir exists: %APP_MEI_DIR%
)

rem 生成唯一目录名（时间 + 随机数），并尝试在应用专用 runtime 目录下创建 tmpdir（更可靠）
setlocal enabledelayedexpansion
set TRIES=0
:make_tmp
set /a TRIES+=1
for /f "tokens=1-6 delims=:-/. " %%a in ("%date% %time%") do (
  set YY=%%f
  set MM=%%b
  set DD=%%c
  set HH=%%d
  set MN=%%e
)
set RAND=%RANDOM%
set UID=%YY%%MM%%DD%_%HH%%MN%_%RAND%
rem Prefer app runtime tmpdir if available
if exist "%APP_MEI_DIR%" (
  set TMPDIR=%APP_MEI_DIR%\PM_%UID%
) else (
  set TMPDIR=%TEMP%\PM_%UID%
)

rem If directory exists already, retry (unlikely)
if exist "%TMPDIR%" (
  if %TRIES% GEQ 5 (
    echo Failed to create unique TMPDIR after %TRIES% attempts. Falling back to %TEMP%.
    set TMPDIR=%TEMP%\PM_%UID%_%RAND%
    mkdir "%TMPDIR%" 2>nul
  ) else (
    timeout /t 1 >nul
    goto make_tmp
  )
)

rem 创建临时目录并导出为 TMP 和 TEMP（PyInstaller bootloader 会读取这些环境变量）
mkdir "%TMPDIR%" 2>nul
set TMP=%TMPDIR%
set TEMP=%TMPDIR%

rem 在继续前检查系统临时目录或应用 runtime_tmpdir 中是否存在其他 _MEI*（避免解包冲突）
set CHECK_TRIES=0
:check_mei
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "if ((Get-ChildItem -Path $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue).Count -gt 0) { exit 1 } else { exit 0 }"
if %ERRORLEVEL% NEQ 0 (
  set /a CHECK_TRIES+=1
  if %CHECK_TRIES% GEQ 5 (
    echo Warning: other _MEI* dirs still exist after %CHECK_TRIES% tries, proceeding anyway >> "%LOGFILE%"
  ) else (
    timeout /t 1 >nul
    goto check_mei
  )
)

rem 可选：打印到控制台便于诊断
echo Using TEMP=%TMPDIR%

rem 启动 exe（若文件名不同请改为你的 exe 名称）
rem 为了诊断在临时目录写入日志并以同步方式运行，以便捕获任何异常输出
set LOGFILE=%TMPDIR%\launcher_log.txt
echo Launch time: %DATE% %TIME% > "%LOGFILE%"
echo Source exe: "%~dp0\物业收费管理系统_Win7.exe" >> "%LOGFILE%"
rem --- Debug mode support ---
set DEBUG_LOG=%APP_MEI_DIR%\launcher_debug.txt
if /I "%LAUNCHER_DEBUG%"=="1" (
  echo === LAUNCHER DEBUG START %DATE% %TIME% > "%DEBUG_LOG%"
  echo Using TMPDIR=%TMPDIR% >> "%DEBUG_LOG%"
  echo LOGFILE=%LOGFILE% >> "%DEBUG_LOG%"
  echo ---- Environment ---- >> "%DEBUG_LOG%"
  set >> "%DEBUG_LOG%"
  echo --------------------- >> "%DEBUG_LOG%"
)

rem Copy exe into the unique temp dir and run it from there to ensure PyInstaller unpacks into a unique _MEI dir.
set SRC="%~dp0\物业收费管理系统_Win7.exe"
set DST="%TMPDIR%\物业收费管理系统_Win7.exe"
echo Copying %SRC% to %DST% >> "%LOGFILE%"
rem Use short (8.3) path for source to avoid encoding issues in cmd on some systems
for %%I in (%SRC%) do set SHORTSRC=%%~sI
if defined SHORTSRC (
  echo Using short source path: %SHORTSRC% >> "%LOGFILE%"
  copy "%SHORTSRC%" %DST% /Y >> "%LOGFILE%" 2>&1
) else (
  echo SHORTSRC not defined, fallback to direct copy >> "%LOGFILE%"
  copy %SRC% %DST% /Y >> "%LOGFILE%" 2>&1
)

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

if /I "%LAUNCHER_DEBUG%"=="1" (
  echo ----- launcher_log.txt ----- >> "%DEBUG_LOG%" 2>nul
  if exist "%LOGFILE%" type "%LOGFILE%" >> "%DEBUG_LOG%" 2>nul
  echo Launcher debug saved to "%DEBUG_LOG%"
  echo Press any key to continue...
  pause
)

endlocal

