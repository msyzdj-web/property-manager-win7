# Launcher cleanup helper for launcher_win7.bat
# Ensures old PyInstaller _MEI* and app runtime tmp folders are removed safely
# Usage (from batch): powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launcher_cleanup.ps1" -TempPath "%TEMP%" -AppMEIDir "%LOCALAPPDATA%\PropertyManager\MEI"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Continue'

param(
    [string]$TempPath = $env:TEMP,
    [string]$AppMEIDir = "$env:LOCALAPPDATA\PropertyManager\MEI"
)

Write-Output "Launcher cleanup starting..."
Write-Output ("Cleaning old _MEI* in: " + $TempPath)
try {
    Get-ChildItem -Path $TempPath -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue |
      Where-Object { $_.LastWriteTime -lt (Get-Date).AddSeconds(-30) } |
      ForEach-Object {
        Write-Output ("Removing: " + $_.FullName)
        Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
      }
} catch {
    Write-Output ("Warning: cleanup of TEMP failed: " + $_.Exception.Message)
}

Write-Output ("Cleaning app runtime tmpdir: " + $AppMEIDir)
try {
    if (Test-Path -Path $AppMEIDir) {
        Get-ChildItem -Path $AppMEIDir -Directory -ErrorAction SilentlyContinue |
          Where-Object { $_.LastWriteTime -lt (Get-Date).AddSeconds(-30) } |
          ForEach-Object {
            Write-Output ("Removing app tmp: " + $_.FullName)
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
          }
    } else {
        New-Item -ItemType Directory -Path $AppMEIDir -Force | Out-Null
        Write-Output ("Created app runtime tmpdir: " + $AppMEIDir)
    }
} catch {
    Write-Output ("Warning: cleanup of app runtime tmpdir failed: " + $_.Exception.Message)
}

Write-Output "Launcher cleanup completed."


