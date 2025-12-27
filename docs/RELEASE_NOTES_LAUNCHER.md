Launcher & Defender Notes (for release)
--------------------------------------

1) Include `tools/launcher_win7.bat` in the release and recommend users start the app via the launcher.

2) Explain in release notes / installer that adding a Defender exclusion for `%LOCALAPPDATA%\PropertyManager\MEI` reduces unpack-time AV interference.

3) If users see the "file already exists but should not" error:
   - Run `fix_defender_issue.ps1` as administrator to auto-clean and attempt to add exclusions.
   - Or manually add exclusion in Windows Security → Virus & threat protection → Manage settings → Exclusions.

4) Test the final release on a clean Windows VM with Defender enabled and repeat starts to ensure stability.


