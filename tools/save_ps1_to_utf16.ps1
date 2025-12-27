<# 
Convert a .ps1 file to UTF-16 LE (BOM) so PowerShell -File reads it correctly on Windows.
Usage (run as administrator if needed):
  powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\save_ps1_to_utf16.ps1" -Source "fix_defender_issue.ps1"
#>
param(
  [string]$Source = "fix_defender_issue.ps1",
  [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$srcPath = Join-Path $RepoRoot $Source
if (-not (Test-Path $srcPath)) {
  Write-Error "Source file not found: $srcPath"
  exit 2
}

$tmp = "$srcPath.tmp"
Write-Output "Converting $srcPath -> UTF-16 LE (BOM) ..."
Get-Content -Raw -Path $srcPath | Out-File -FilePath $tmp -Encoding Unicode
Move-Item -Force $tmp $srcPath
Write-Output "Converted and overwritten: $srcPath"
exit 0


