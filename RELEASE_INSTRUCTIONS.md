Release & Launcher Instructions
===============================

Purpose
-------
Provide a minimal release checklist and instructions to avoid PyInstaller unpack-time antivirus popups that can show "file already exists" warnings during runtime.

Files to include in release
- `PropertyManager-win7.exe` (built from `PropertyManager-win7.spec`)
- `tools/launcher_win7.bat` (recommended launch wrapper)
- `fix_defender_issue.ps1` (helper script) — save as UTF-16 LE (BOM) if distributing so Windows PowerShell `-File` can parse Unicode reliably
- `README.md` (updated with launcher instructions)

Recommended release steps
-------------------------
1. Build using the provided spec (application-specific runtime_tmpdir already set):
   - `pyinstaller PropertyManager-win7.spec`

2. Prepare release bundle:
   - Include the exe, `tools/launcher_win7.bat`, `fix_defender_issue.ps1` and `README.md`.
   - Optionally code-sign the exe to reduce AV false positives.

3. Installation / first-run instructions (for users):
   - Right-click `launcher_win7.bat` → Run as administrator (or run from Start Menu "Run as admin").
   - If AV still blocks, run `fix_defender_issue.ps1` as admin to add Defender exclusions or follow manual Defender GUI steps.

PowerShell commands (admin)
--------------------------
Add Defender exclusion for the app runtime tmpdir (recommended):

```powershell
Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\PropertyManager\MEI"
```

Or add exclusion for system TEMP (broader):

```powershell
Add-MpPreference -ExclusionPath $env:TEMP
```

If you temporarily disable realtime protection for testing (not recommended for normal use):

```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
# run tests...
Set-MpPreference -DisableRealtimeMonitoring $false
```

QA checklist (before publishing)
-------------------------------
- Run launcher on a clean Windows VM with Defender enabled (repeat 10+ times).  
- Test concurrent launches.  
- Verify `launcher_log.txt` and `launcher_debug.txt` (when debug enabled) show no unpack conflicts.  
- Document in release notes: "Use launcher to start the app and consider adding `%LOCALAPPDATA%\PropertyManager\MEI` to Defender exclusions."

If you want, I can also create a signed installer that runs the Defender exclusion commands during install (requires admin consent).


