<#
  ci_download.ps1
  Purpose: trigger (optional), wait for, download and unpack GitHub Actions artifact for build-win7.yml
  Usage:
    # Use gh CLI (must be logged in). Optional: supply a run id.
    powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\ci_download.ps1" [-RunId 123456789]

  The script will:
    - find the latest run id for workflow build-win7.yml if RunId not provided
    - wait for the run to complete (gh run watch)
    - download artifacts into D:\7z\ci_artifact
    - unpack any downloaded zip(s) into D:\7z\ci_artifact\unpacked
#>
param(
  [string]$RunId
)

Set-StrictMode -Version Latest

$repo = 'msyzdj-web/property-manager-win7'
$workflow = 'build-win7.yml'
$outDir = 'D:\7z\ci_artifact'
$unpackDir = Join-Path $outDir 'unpacked'

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "gh CLI not found. Install GitHub CLI and login (gh auth login) before running this script."
    exit 1
}

if (-not $RunId) {
    Write-Output "Determining latest run id for workflow $workflow ..."
    $latest = gh run list --workflow="$workflow" --repo $repo --limit 1 --json id,status,conclusion --jq '.[0] | {id: .id, status: .status, conclusion: .conclusion}' 2>$null
    if (-not $latest) {
        Write-Error "No runs found for workflow $workflow in repo $repo."
        exit 1
    }
    $obj = $latest | ConvertFrom-Json
    $RunId = $obj.id
    Write-Output "Latest run id: $RunId (status: $($obj.status), conclusion: $($obj.conclusion))"
} else {
    Write-Output "Using provided run id: $RunId"
}

Write-Output "Watching run $RunId until completion..."
gh run watch $RunId --repo $repo
if ($LASTEXITCODE -ne 0) {
    Write-Error "gh run watch failed or was interrupted."
    exit 1
}

Write-Output "Creating output directory: $outDir"
New-Item -Path $outDir -ItemType Directory -Force | Out-Null

Write-Output "Downloading artifacts for run $RunId ..."
gh run download $RunId --repo $repo --dir $outDir
if ($LASTEXITCODE -ne 0) {
    Write-Error "gh run download failed."
    exit 1
}

# Unpack any zip files downloaded
Get-ChildItem -Path $outDir -Filter '*.zip' -File -ErrorAction SilentlyContinue | ForEach-Object {
    $zip = $_.FullName
    Write-Output "Unpacking $zip to $unpackDir ..."
    New-Item -Path $unpackDir -ItemType Directory -Force | Out-Null
    try {
        Expand-Archive -LiteralPath $zip -DestinationPath $unpackDir -Force
    } catch {
        Write-Warning ("Failed to unpack {0}: {1}" -f $zip, $_)
    }
}

Write-Output "Listing unpacked files:"
Get-ChildItem -Path $unpackDir -Recurse | Select-Object FullName, Length | Format-Table -AutoSize

Write-Output "`nDone. Check $unpackDir for the dist/ folder. Copy the dist folder to a Windows 7 machine for testing."


