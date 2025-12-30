; Inno Setup script to create an installer that bundles the onedir build and optional VC++ redistributables
; Place the onedir contents in "dist\PropertyManager" relative to the script when building the installer.
; If you want the installer to embed VC++ redistributables, put them into "installer_files\":
;   - installer_files\vcredist_x64.exe
;   - installer_files\vcredist_x86.exe
; Build locally with Inno Setup Compiler (ISCC):
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" tools\installer\PropertyManagerInstaller.iss

[Setup]
AppName=PropertyManager
AppVersion=1.0
DefaultDirName={pf}\PropertyManager
DefaultGroupName=PropertyManager
OutputBaseFilename=PropertyManager-Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
DisableDirPage=no
DisableProgramGroupPage=no
Uninstallable=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:";

[Files]
; Copy the entire onedir output (assumes CI or local build created dist\PropertyManager)
Source: "dist\PropertyManager\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

; Optional VC++ redistributables - include here if you have downloaded them into installer_files\
Source: "installer_files\vcredist_x64.exe"; DestDir: "{tmp}"; Flags: ignoremissing
Source: "installer_files\vcredist_x86.exe"; DestDir: "{tmp}"; Flags: ignoremissing

[Icons]
Name: "{group}\PropertyManager"; Filename: "{app}\main\main.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall PropertyManager"; Filename: "{uninstallexe}"
Name: "{commondesktop}\PropertyManager"; Filename: "{app}\main\main.exe"; Tasks: desktopicon

[Run]
; Install the VC++ redistributable if provided (silent install)
Filename: "{tmp}\vcredist_x64.exe"; Parameters: "/install /quiet /norestart"; \
  Check: Is64BitInstallMode and FileExists(ExpandConstant('{tmp}\vcredist_x64.exe')); Flags: waituntilterminated
Filename: "{tmp}\vcredist_x86.exe"; Parameters: "/install /quiet /norestart"; \
  Check: (not Is64BitInstallMode) and FileExists(ExpandConstant('{tmp}\vcredist_x86.exe')); Flags: waituntilterminated

; Show a readme after install (if present)
Filename: "{app}\README.html"; Description: "View the README"; Flags: shellexec postinstall skipifsilent; \
  Check: FileExists(ExpandConstant('{app}\README.html'))

[Code]
function Is64BitInstallMode(): Boolean;
begin
  Result := IsWin64;
end;


