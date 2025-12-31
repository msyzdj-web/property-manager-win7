<#
  show_log.ps1
  Purpose: find the most recent pm_err.txt under %LOCALAPPDATA%\PropertyManager\MEI,
           print its tail, list instance dirs and TEMP _MEI* entries.
  Usage:
    PowerShell (no prompt text) paste and run:
      powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\wykf\tools\show_log.ps1"
    Or copy this file to the folder with your EXE (D:\7z) and run:
      powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\7z\show_log.ps1"
#>

Write-Output "=== show_log.ps1: collecting logs and temp info ===`n"

# Find latest pm_err.txt
$log = Get-ChildItem "$env:LOCALAPPDATA\PropertyManager\MEI" -Recurse -Filter pm_err.txt -ErrorAction SilentlyContinue |
       Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName -ErrorAction SilentlyContinue
if ($log) {
    Write-Output "LOG: $log`n--- last 500 lines ---"
    try {
        Get-Content $log -Tail 500 -ErrorAction SilentlyContinue
    } catch {
        Write-Output "Failed to read log: $_"
    }
} else {
    Write-Output "No pm_err.txt found under $env:LOCALAPPDATA\PropertyManager\MEI"
}

Write-Output "`n=== Instance directories under %LOCALAPPDATA%\\PropertyManager\\MEI ==="
Get-ChildItem -Path "$env:LOCALAPPDATA\PropertyManager\MEI" -Directory -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object Name,FullName,LastWriteTime

Write-Output "`n=== TEMP _MEI* directories ==="
Get-ChildItem -Path $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue |
  Select-Object FullName,LastWriteTime

Write-Output "`n=== Any running processes matching PropertyManager/物业 ==="
Get-Process | Where-Object { $_.ProcessName -like '*物业*' -or $_.ProcessName -like '*PropertyManager*' } |
  Select-Object Id,ProcessName,StartTime

Write-Output "`n=== done ==="


