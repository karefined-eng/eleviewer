; EleViewer Inno Setup Script
; This script generates the highly compressed Windows installer for EleViewer
; and sets up file associations and context menus.

[Setup]
AppName=EleViewer
AppVersion=1.2.0
AppPublisher=Elevon (ka.refined)
AppPublisherURL=https://eleviewer.vercel.app
AppSupportURL=https://github.com/karefined-eng/eleviewer/issues
AppUpdatesURL=https://github.com/karefined-eng/eleviewer/releases
DefaultDirName={autopf}\EleViewer
DisableProgramGroupPage=yes
; Compression settings for maximum reduction of PyInstaller .exe
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=EleViewer_Setup_v1.2.0
SetupIconFile=icons\eleviewer.ico
UninstallDisplayIcon={app}\EleViewer.exe
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associate"; Description: "Register as default editor for .md, .pdf, .txt, .docx, .xlsx"; GroupDescription: "File Associations"
Name: "contextmenu"; Description: "Add 'Open with EleViewer' to right-click menu"; GroupDescription: "Windows Explorer"

[Files]
; The source is the single portable executable created by PyInstaller.
Source: "dist\EleViewer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\EleViewer"; Filename: "{app}\EleViewer.exe"
Name: "{autodesktop}\EleViewer"; Filename: "{app}\EleViewer.exe"; Tasks: desktopicon

[Registry]
; Context Menu (Right-Click "Open with EleViewer")
Root: HKCR; Subkey: "*\shell\EleViewer"; ValueType: string; ValueName: ""; ValueData: "Open with EleViewer"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: "*\shell\EleViewer"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\EleViewer.exe"""; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCR; Subkey: "*\shell\EleViewer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; File Associations (.md)
Root: HKCR; Subkey: ".md"; ValueType: string; ValueName: ""; ValueData: "EleViewer.Markdown"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Markdown"; ValueType: string; ValueName: ""; ValueData: "Markdown File"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Markdown\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Markdown\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate

; File Associations (.pdf)
Root: HKCR; Subkey: ".pdf"; ValueType: string; ValueName: ""; ValueData: "EleViewer.PDF"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.PDF"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.PDF\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.PDF\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate
