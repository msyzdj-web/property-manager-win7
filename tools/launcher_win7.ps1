param(
  [string]$ExeName = '物业收费管理系统_Win7.exe'
)

# 脚本目录（假设 launcher 与 exe 放同一目录）
# 使用更稳健的方式获取脚本目录：优先 $PSScriptRoot，然后尝试 MyInvocation.MyCommand.Path，最后回退到当前工作目录
if ($PSBoundParameters.ContainsKey('PSScriptRoot')) {
    $scriptDir = $PSScriptRoot
} elseif ($PSScriptRoot) {
    $scriptDir = $PSScriptRoot
} elseif ($MyInvocation -and $MyInvocation.MyCommand -and $MyInvocation.MyCommand.Path) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $scriptDir = (Get-Location).ProviderPath
}
$exePath = Join-Path $scriptDir $ExeName

if (-not (Test-Path $exePath)) {
    # 尝试在脚本目录自动查找 exe（避免编码/参数传递导致的名称不匹配）
    # 计算 launcher 名称以排除自身（如果可用）
    $launcherName = ''
    if ($MyInvocation -and $MyInvocation.MyCommand) {
        if ($MyInvocation.MyCommand.Name) { $launcherName = $MyInvocation.MyCommand.Name }
        elseif ($MyInvocation.MyCommand.Path) { $launcherName = Split-Path -Leaf $MyInvocation.MyCommand.Path }
    }
    $found = Get-ChildItem -Path $scriptDir -Filter '*.exe' -File -ErrorAction SilentlyContinue |
        Where-Object { if ($launcherName) { $_.Name -ne $launcherName } else { $true } } |
        Sort-Object Length -Descending
    if ($found -and $found.Count -gt 0) {
        $exePath = $found[0].FullName
        Write-Output "EXE not provided or not found by name. Auto-selected: $exePath"
    } else {
        Write-Error "EXE not found: $exePath. Please place the EXE in the same folder as the launcher or run with -ExeName '<name>.exe'."
        exit 1
    }
}

# runtime 根目录（每次运行在这里创建独立子目录）
$runtimeRoot = Join-Path $env:LOCALAPPDATA 'PropertyManager\MEI'
New-Item -Path $runtimeRoot -ItemType Directory -Force | Out-Null

# 创建唯一实例目录
$instanceDir = Join-Path $runtimeRoot ("MEI_{0}" -f ([guid]::NewGuid().ToString()))
New-Item -Path $instanceDir -ItemType Directory -Force | Out-Null

# 复制 exe 到实例目录（避免与原 exe 或其它实例争用同一解包文件）
$instanceExe = Join-Path $instanceDir 'app.exe'
Copy-Item -Path $exePath -Destination $instanceExe -Force

# 复制同目录下的数据库与资源文件到实例目录，避免实例运行时找不到 property.db 等数据文件
$dataPatterns = @('property.db','*.db','*.db3','*.sqlite','logo.*','*.ico','*.jpg','property.db*')
try {
    $dataFiles = Get-ChildItem -Path $scriptDir -Include $dataPatterns -File -ErrorAction SilentlyContinue
    foreach ($f in $dataFiles) {
        Copy-Item -Path $f.FullName -Destination (Join-Path $instanceDir $f.Name) -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Output "No extra data files copied: $_"
}

# 准备日志路径
$outLog = Join-Path $instanceDir 'pm_out.txt'
$errLog = Join-Path $instanceDir 'pm_err.txt'

Push-Location $instanceDir

# 尝试用 Start-Process 重定向输出（在新版本 PowerShell 可用）
try {
    Start-Process -FilePath $instanceExe -NoNewWindow -Wait -RedirectStandardOutput $outLog -RedirectStandardError $errLog
} catch {
    # 如果上面参数在当前 PowerShell 不被支持，则回退为直接调用并将输出重定向到日志（适用于多数环境）
    Write-Output "Start-Process redirection not available; falling back to direct invocation (GUI apps may not produce logs)."
    try {
        # 直接调用并将 stdout/stderr 合并输出到文件（注意：若程序为 GUI，这通常不会输出内容）
        & $instanceExe *> $outLog 2>&1
    } catch {
        Write-Output "Direct invocation also failed: $_"
        # 最后退回到无重定向的直接启动（用户仍会看到 GUI）
        Start-Process -FilePath $instanceExe -WorkingDirectory $instanceDir
    }
}

# 等待并输出日志位置提示（如果使用了重定向）
Write-Output "Started: $instanceExe. Logs: `n$outLog`n$errLog"
Pop-Location

# （可选）如果你希望运行结束后自动清理实例目录，可以取消下一行注释
# Remove-Item -LiteralPath $instanceDir -Recurse -Force


