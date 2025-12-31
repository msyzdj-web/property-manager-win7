# OneClickCleanAndTest.ps1
# Purpose: check for running instances, safely remove old PyInstaller temp dirs,
# add Defender exclusions for runtime and unpack folder, then run the launcher multiple times
# and collect a run log.
#
# Usage (run as Administrator):
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\7z\OneClickCleanAndTest.ps1"

$launcherPath = "D:\7z\launcher_win7.ps1"
$workDir = "D:\7z"
$runLog = Join-Path $workDir 'oneclick_run_log.txt'

Write-Output "=== OneClick start: $(Get-Date) ===" | Tee-Object -FilePath $runLog -Append

# 1) 检查是否有正在运行的 PropertyManager 实例（中文/英文名）
$procs = Get-Process | Where-Object { $_.ProcessName -like '*物业*' -or $_.ProcessName -like '*PropertyManager*' }
if ($procs) {
  Write-Output "Found running processes (please close them first):" | Tee-Object -FilePath $runLog -Append
  $procs | Select Id,ProcessName,StartTime | Tee-Object -FilePath $runLog -Append
  Write-Output "Aborting. Close the processes then re-run this script." | Tee-Object -FilePath $runLog -Append
  exit 1
}

# 2) 列当前 MEI 实例 & TEMP _MEI*
Write-Output "`nCurrent MEI instances:" | Tee-Object -FilePath $runLog -Append
Get-ChildItem -Path "$env:LOCALAPPDATA\PropertyManager\MEI" -Directory -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending | Select Name,FullName,LastWriteTime | Tee-Object -FilePath $runLog -Append

Write-Output "`nTEMP _MEI* (if any):" | Tee-Object -FilePath $runLog -Append
Get-ChildItem -Path $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue |
  Select FullName,LastWriteTime | Tee-Object -FilePath $runLog -Append

# 3) 删除 MEI 子目录（保留最新1个）
$dirs = Get-ChildItem -Path "$env:LOCALAPPDATA\PropertyManager\MEI" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($dirs.Count -gt 1) {
  $toRemove = $dirs | Select-Object -Skip 1
  Write-Output "`nRemoving older MEI instances (keeping newest):" | Tee-Object -FilePath $runLog -Append
  $toRemove | Select FullName,LastWriteTime | Tee-Object -FilePath $runLog -Append
  $toRemove | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
} else {
  Write-Output "`nNo extra MEI instances to remove." | Tee-Object -FilePath $runLog -Append
}

# 4) 删除 TEMP 下较旧的 _MEI*（只删除 2 分钟前的，避免删正在使用的）
$oldTemp = Get-ChildItem -Path $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue |
           Where-Object { $_.LastWriteTime -lt (Get-Date).AddMinutes(-2) }
if ($oldTemp) {
  Write-Output "`nRemoving old TEMP _MEI* dirs:" | Tee-Object -FilePath $runLog -Append
  $oldTemp | Select FullName,LastWriteTime | Tee-Object -FilePath $runLog -Append
  $oldTemp | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
} else {
  Write-Output "`nNo old TEMP _MEI* dirs to remove." | Tee-Object -FilePath $runLog -Append
}

# 5) 添加 Defender 排除（若当前会话无管理员权限，此步会失败）
try {
  Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\PropertyManager\MEI" -ErrorAction Stop
  Add-MpPreference -ExclusionPath "$workDir" -ErrorAction Stop
  Write-Output "`nAdded Defender exclusions for runtime and $workDir" | Tee-Object -FilePath $runLog -Append
} catch {
  Write-Output "`nWarning: failed to add Defender exclusions (need admin). Error: $_" | Tee-Object -FilePath $runLog -Append
}

# 6) 快速复测：使用 launcher 启动若干次（5 次），每次间隔 1 秒
Write-Output "`nStarting quick test runs (5x)..." | Tee-Object -FilePath $runLog -Append
for ($i=1; $i -le 5; $i++) {
  Write-Output "Run #${i}: $(Get-Date)" | Tee-Object -FilePath $runLog -Append
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File $launcherPath *> $null
  Start-Sleep -Seconds 1
}

# 7) 测试后列出 MEI 与 TEMP 状态、并显示最新 pm_err.txt 的尾部
Write-Output "`nAfter test — MEI instances:" | Tee-Object -FilePath $runLog -Append
Get-ChildItem -Path "$env:LOCALAPPDATA\PropertyManager\MEI" -Directory -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending | Select Name,FullName,LastWriteTime | Tee-Object -FilePath $runLog -Append

Write-Output "`nAfter test — TEMP _MEI* (if any):" | Tee-Object -FilePath $runLog -Append
Get-ChildItem -Path $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue |
  Select FullName,LastWriteTime | Tee-Object -FilePath $runLog -Append

$latestLog = Get-ChildItem "$env:LOCALAPPDATA\PropertyManager\MEI" -Recurse -Filter pm_err.txt -ErrorAction SilentlyContinue |
             Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
if ($latestLog) {
  Write-Output "`nLatest pm_err.txt: $latestLog" | Tee-Object -FilePath $runLog -Append
  Write-Output "`n--- last 200 lines of pm_err.txt ---" | Tee-Object -FilePath $runLog -Append
  Get-Content $latestLog -Tail 200 | Tee-Object -FilePath $runLog -Append
} else {
  Write-Output "`nNo pm_err.txt found after test." | Tee-Object -FilePath $runLog -Append
}

Write-Output "`n=== OneClick finished: $(Get-Date) ===" | Tee-Object -FilePath $runLog -Append
Write-Output "Run log saved to: $runLog"


