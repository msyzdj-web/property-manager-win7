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
<<<<<<< HEAD
rem PyInstaller creates PropertyManager.exe.notanexecutable in dist directory
echo Checking for exe in: %~dp0..\dist\
dir "%~dp0..\dist\*.exe*" 2>nul
if exist "%~dp0..\dist\PropertyManager.exe.notanexecutable" (
  echo Found PropertyManager.exe.notanexecutable, copying and renaming...
  copy "%~dp0..\dist\PropertyManager.exe.notanexecutable" "%RELEASE_DIR%\PropertyManager.exe" /Y
) else if exist "%~dp0..\dist\PropertyManager.exe" (
  echo Found PropertyManager.exe, copying...
  copy "%~dp0..\dist\PropertyManager.exe" "%RELEASE_DIR%\" /Y
) else (
  echo Built exe not found - check pyinstaller output.
  rem Try to find any .exe* in dist directory
  for %%f in ("%~dp0..\dist\*.exe*") do (
    echo Found exe: %%~nf%%~xf
    copy "%%f" "%RELEASE_DIR%\PropertyManager.exe" /Y
    goto :found_exe
  )
  echo No exe found in dist directory!
  goto :cleanup
  :found_exe
)
copy "%~dp0launcher_win7.bat" "%RELEASE_DIR%\" /Y
copy "%~dp0..\fix_defender_issue.bat" "%RELEASE_DIR%\" /Y
copy "%~dp0..\fix_defender_issue.ps1" "%RELEASE_DIR%\" /Y
if exist "%~dp0..\README.md" copy "%~dp0..\README.md" "%RELEASE_DIR%\" /Y

rem 6) Create zip archive
rem Ensure zip name predictable and exists at repo root
rem Use YYYY-MM-DD format
for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd'"') do set D=%%a
set ZIP_NAME=PropertyManager-release-%D%.zip
powershell -NoProfile -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath '%~dp0..\%ZIP_NAME%' -Force; if (Test-Path '%~dp0..\%ZIP_NAME%') { Write-Output 'ZIP_CREATED' } else { Write-Output 'ZIP_MISSING'; exit 2 }"

echo Release package created: %~dp0..\%ZIP_NAME%

:cleanup
rd /s /q "%RELEASE_DIR%"
=======
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
>>>>>>> d4fa4ca57bfb62cf8c52ef13d615dd745fa57580
endlocal
exit /b 0


