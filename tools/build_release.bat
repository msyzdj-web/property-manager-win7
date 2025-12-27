@echo off
rem Build release: runs PyInstaller with the win7 spec, converts ps1 to UTF-16, and packages files.
rem Run this from project root in an elevated cmd.

setlocal
echo Building release...

rem 1) Ensure python & pyinstaller available
where pyinstaller >nul 2>nul
if errorlevel 1 (
  echo PyInstaller not found in PATH. Install or activate your environment first.
  exit /b 1
)

rem 2) Build using win7 spec
pyinstaller PropertyManager-win7.spec
if errorlevel 1 (
  echo PyInstaller build failed.
  exit /b 2
)

rem 3) Ensure fix_defender_issue.ps1 encoded as UTF-16 for distribution
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0save_ps1_to_utf16.ps1" -Source "fix_defender_issue.ps1"

rem 4) Prepare release folder
set RELEASE_DIR=%~dp0release
if exist "%RELEASE_DIR%" rd /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"

rem 5) Copy built exe and helper files
rem adjust path according to PyInstaller output (dist\PropertyManager\PropertyManager.exe or similar)
if exist "%~dp0dist\PropertyManager\PropertyManager.exe" (
  copy "%~dp0dist\PropertyManager\PropertyManager.exe" "%RELEASE_DIR%\" /Y
) else (
  echo Built exe not found at dist\PropertyManager\PropertyManager.exe - check pyinstaller output.
)
copy "%~dp0tools\launcher_win7.bat" "%RELEASE_DIR%\" /Y
copy "%~dp0fix_defender_issue.bat" "%RELEASE_DIR%\" /Y
copy "%~dp0fix_defender_issue.ps1" "%RELEASE_DIR%\" /Y
copy "%~dp0README.md" "%RELEASE_DIR%\" /Y

rem 6) Create zip archive
set ZIP_NAME=PropertyManager-release-%DATE:~0,10%.zip
powershell -NoProfile -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath '%~dp0%ZIP_NAME%' -Force"

echo Release package created: %~dp0%ZIP_NAME%
endlocal
exit /b 0


