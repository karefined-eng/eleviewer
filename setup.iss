; EleViewer Inno Setup Script
; This script generates the highly compressed Windows installer for EleViewer
; and sets up file associations and context menus.

[Setup]
AppName=EleViewer
AppVersion=1.3.0
AppPublisher=karefined-eng
AppPublisherURL=https://eleviewer.vercel.app
AppSupportURL=https://github.com/karefined-eng/eleviewer/issues
AppUpdatesURL=https://github.com/karefined-eng/eleviewer/releases
DefaultDirName={autopf}\EleViewer
DisableProgramGroupPage=yes
; Compression settings for maximum reduction of PyInstaller .exe
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=EleViewer_Setup_v1.3.0
SetupIconFile=icons\eleviewer.ico
UninstallDisplayIcon={app}\EleViewer.exe
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associate"; Description: "Register as default editor for .md, .pdf, .docx, .xlsx, .pptx, .csv, .txt, .html"; GroupDescription: "File Associations"
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

; File Associations (.docx)
Root: HKCR; Subkey: ".docx"; ValueType: string; ValueName: ""; ValueData: "EleViewer.Docx"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Docx"; ValueType: string; ValueName: ""; ValueData: "Word Document"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Docx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Docx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate

; File Associations (.xlsx)
Root: HKCR; Subkey: ".xlsx"; ValueType: string; ValueName: ""; ValueData: "EleViewer.Xlsx"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Xlsx"; ValueType: string; ValueName: ""; ValueData: "Excel Spreadsheet"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Xlsx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Xlsx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate

; File Associations (.pptx)
Root: HKCR; Subkey: ".pptx"; ValueType: string; ValueName: ""; ValueData: "EleViewer.Pptx"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Pptx"; ValueType: string; ValueName: ""; ValueData: "PowerPoint Presentation"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Pptx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Pptx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate

; File Associations (.csv)
Root: HKCR; Subkey: ".csv"; ValueType: string; ValueName: ""; ValueData: "EleViewer.Csv"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Csv"; ValueType: string; ValueName: ""; ValueData: "CSV Spreadsheet"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Csv\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Csv\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate

; File Associations (.txt)
Root: HKCR; Subkey: ".txt"; ValueType: string; ValueName: ""; ValueData: "EleViewer.Txt"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Txt"; ValueType: string; ValueName: ""; ValueData: "Text Document"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Txt\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Txt\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate

; File Associations (.html)
Root: HKCR; Subkey: ".html"; ValueType: string; ValueName: ""; ValueData: "EleViewer.Html"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Html"; ValueType: string; ValueName: ""; ValueData: "HTML Document"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Html\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate
Root: HKCR; Subkey: "EleViewer.Html\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate
