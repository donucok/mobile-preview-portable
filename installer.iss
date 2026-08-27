[Setup]
AppName=Mobile Web Previewer
AppVersion=2.0.0
AppPublisher=donucok
DefaultDirName={autopf}\MobileWebPreviewer
DefaultGroupName=Mobile Web Previewer
UninstallDisplayIcon={app}\MobilePreviewer.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=MobilePreviewer_Setup_v2.0.0
SetupIconFile=app_icon.ico

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\MobilePreviewer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Mobile Web Previewer"; Filename: "{app}\MobilePreviewer.exe"
Name: "{group}\{cm:UninstallProgram,Mobile Web Previewer}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Mobile Web Previewer"; Filename: "{app}\MobilePreviewer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MobilePreviewer.exe"; Description: "{cm:LaunchProgram,Mobile Web Previewer}"; Flags: nowait postinstall skipifsilent