; EleViewer Inno Setup Script
; This script generates the highly compressed Windows installer for EleViewer
; and sets up file associations and context menus.

; CI/CD passes version via: iscc /DAppVersion=X.Y.Z setup.iss
; Falls back to 1.3.0 for local manual builds.
#ifndef AppVersion
  #define AppVersion "1.3.1"
#endif

[Setup]
AppId={{F9D3B2A1-8E7C-4D6B-9F5A-3C2E1D0B4A9E}
AppName=EleViewer
AppVersion={#AppVersion}
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
OutputBaseFilename=EleViewer_Setup_v{#AppVersion}
SetupIconFile=icons\eleviewer.ico
UninstallDisplayIcon={app}\EleViewer.exe
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=yes
SetupMutex=EleViewerMutex
ArchitecturesInstallIn64BitMode=x64
; Modern UI & Brand Styling
WizardStyle=modern
WizardResizable=no
; To apply our custom color code (#161616 dark panels and #6cb6ff electric blue accents)
; to the wizard sidebars and headers, place branded bitmaps in the icons/ folder:
WizardImageFile=icons\wizard_banner.bmp
WizardSmallImageFile=icons\wizard_logo.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel1=Welcome to the EleViewer Setup Wizard
WelcomeLabel2=This will install EleViewer on your computer.%n%nEleViewer is a lightweight, offline study workspace that opens PDFs, Word documents, Excel spreadsheets, PowerPoint slides, Markdown notes, and more—all in one place without lag or telemetry.%n%nClick Next to continue.
WizardSelectTasks=Select Shortcuts and File Options
TasksListLabel=Choose how you want EleViewer to open your course materials and documents:
FinishedHeadingLabel=EleViewer is ready for your studies!
FinishedLabelNoIcons=Setup has finished installing EleViewer on your computer.%n%nYour files stay local on your hard drive, your privacy is protected, and your laptop will run fast. Click Finish to exit setup.

[Tasks]
Name: "desktopicon"; Description: "Create a shortcut on my desktop"; GroupDescription: "Desktop Shortcut"; Flags: unchecked
Name: "contextmenu"; Description: "Add 'Open with EleViewer' to my right-click menu in Windows Explorer"; GroupDescription: "Windows Explorer Integration"

Name: "associate"; Description: "Register EleViewer as the default viewer for:"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\pdf"; Description: "PDF Documents (.pdf)"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\md"; Description: "Markdown Notes (.md)"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\docx"; Description: "Word Documents (.docx)"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\xlsx"; Description: "Excel Spreadsheets (.xlsx)"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\pptx"; Description: "PowerPoint Presentations (.pptx)"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\csv"; Description: "CSV/TSV Spreadsheets (.csv, .tsv)"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\txt"; Description: "Plain Text (.txt)"; GroupDescription: "File Associations"; Flags: unchecked
Name: "associate\html"; Description: "Web Documents (.html, .htm)"; GroupDescription: "File Associations"; Flags: unchecked

[Files]
; The source is the Nuitka standalone directory (which includes DLLs and native Rust extensions).
Source: "main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\EleViewer"; Filename: "{app}\EleViewer.exe"
Name: "{autodesktop}\EleViewer"; Filename: "{app}\EleViewer.exe"; Tasks: desktopicon

[Registry]
; Context Menu (Right-Click "Open with EleViewer") — Per-User
Root: HKCU; Subkey: "Software\Classes\*\shell\EleViewer"; ValueType: string; ValueName: ""; ValueData: "Open with EleViewer"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\EleViewer"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\EleViewer.exe"""; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\EleViewer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Application Capabilities for Windows 10/11 "Open With" dialog (Per-User Installation)
Root: HKCU; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "EleViewer"; ValueData: "Software\EleViewer\Capabilities"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCU; Subkey: "Software\EleViewer\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Lightweight Document Viewer & Study Workspace"; Flags: uninsdeletekey; Tasks: associate
Root: HKCU; Subkey: "Software\EleViewer\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "EleViewer"; Flags: uninsdeletekey; Tasks: associate
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".pdf"; ValueData: "EleViewer.PDF"; Flags: uninsdeletevalue; Tasks: associate\pdf
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".md"; ValueData: "EleViewer.Markdown"; Flags: uninsdeletevalue; Tasks: associate\md
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".docx"; ValueData: "EleViewer.Docx"; Flags: uninsdeletevalue; Tasks: associate\docx
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".xlsx"; ValueData: "EleViewer.Xlsx"; Flags: uninsdeletevalue; Tasks: associate\xlsx
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".pptx"; ValueData: "EleViewer.Pptx"; Flags: uninsdeletevalue; Tasks: associate\pptx
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".csv"; ValueData: "EleViewer.Csv"; Flags: uninsdeletevalue; Tasks: associate\csv
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".txt"; ValueData: "EleViewer.Txt"; Flags: uninsdeletevalue; Tasks: associate\txt
Root: HKCU; Subkey: "Software\EleViewer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".html"; ValueData: "EleViewer.Html"; Flags: uninsdeletevalue; Tasks: associate\html

; ProgID: Markdown (.md)
Root: HKCU; Subkey: "Software\Classes\.md\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Markdown"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\md
Root: HKCU; Subkey: "Software\Classes\EleViewer.Markdown"; ValueType: string; ValueName: ""; ValueData: "Markdown File"; Flags: uninsdeletekey; Tasks: associate\md
Root: HKCU; Subkey: "Software\Classes\EleViewer.Markdown"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer Markdown Note"; Flags: uninsdeletekey; Tasks: associate\md
Root: HKCU; Subkey: "Software\Classes\EleViewer.Markdown\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\md
Root: HKCU; Subkey: "Software\Classes\EleViewer.Markdown\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\md

; ProgID: PDF (.pdf)
Root: HKCU; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.PDF"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\pdf
Root: HKCU; Subkey: "Software\Classes\EleViewer.PDF"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associate\pdf
Root: HKCU; Subkey: "Software\Classes\EleViewer.PDF"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer PDF Document"; Flags: uninsdeletekey; Tasks: associate\pdf
Root: HKCU; Subkey: "Software\Classes\EleViewer.PDF\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\pdf
Root: HKCU; Subkey: "Software\Classes\EleViewer.PDF\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\pdf

; ProgID: Word Document (.docx)
Root: HKCU; Subkey: "Software\Classes\.docx\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Docx"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\docx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Docx"; ValueType: string; ValueName: ""; ValueData: "Word Document"; Flags: uninsdeletekey; Tasks: associate\docx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Docx"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer Word Document"; Flags: uninsdeletekey; Tasks: associate\docx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Docx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\docx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Docx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\docx

; ProgID: Excel Spreadsheet (.xlsx)
Root: HKCU; Subkey: "Software\Classes\.xlsx\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Xlsx"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\xlsx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Xlsx"; ValueType: string; ValueName: ""; ValueData: "Excel Spreadsheet"; Flags: uninsdeletekey; Tasks: associate\xlsx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Xlsx"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer Excel Spreadsheet"; Flags: uninsdeletekey; Tasks: associate\xlsx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Xlsx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\xlsx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Xlsx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\xlsx

; ProgID: PowerPoint Presentation (.pptx)
Root: HKCU; Subkey: "Software\Classes\.pptx\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Pptx"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\pptx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Pptx"; ValueType: string; ValueName: ""; ValueData: "PowerPoint Presentation"; Flags: uninsdeletekey; Tasks: associate\pptx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Pptx"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer PowerPoint Presentation"; Flags: uninsdeletekey; Tasks: associate\pptx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Pptx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\pptx
Root: HKCU; Subkey: "Software\Classes\EleViewer.Pptx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\pptx

; ProgID: CSV Spreadsheet (.csv, .tsv)
Root: HKCU; Subkey: "Software\Classes\.csv\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Csv"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\csv
Root: HKCU; Subkey: "Software\Classes\.tsv\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Csv"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\csv
Root: HKCU; Subkey: "Software\Classes\EleViewer.Csv"; ValueType: string; ValueName: ""; ValueData: "CSV Spreadsheet"; Flags: uninsdeletekey; Tasks: associate\csv
Root: HKCU; Subkey: "Software\Classes\EleViewer.Csv"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer CSV Data Spreadsheet"; Flags: uninsdeletekey; Tasks: associate\csv
Root: HKCU; Subkey: "Software\Classes\EleViewer.Csv\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\csv
Root: HKCU; Subkey: "Software\Classes\EleViewer.Csv\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\csv

; ProgID: Plain Text (.txt)
Root: HKCU; Subkey: "Software\Classes\.txt\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Txt"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\txt
Root: HKCU; Subkey: "Software\Classes\EleViewer.Txt"; ValueType: string; ValueName: ""; ValueData: "Text Document"; Flags: uninsdeletekey; Tasks: associate\txt
Root: HKCU; Subkey: "Software\Classes\EleViewer.Txt"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer Plain Text File"; Flags: uninsdeletekey; Tasks: associate\txt
Root: HKCU; Subkey: "Software\Classes\EleViewer.Txt\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\txt
Root: HKCU; Subkey: "Software\Classes\EleViewer.Txt\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\txt

; ProgID: HTML Document (.html, .htm)
Root: HKCU; Subkey: "Software\Classes\.html\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Html"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\html
Root: HKCU; Subkey: "Software\Classes\.htm\OpenWithProgids"; ValueType: string; ValueName: "EleViewer.Html"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate\html
Root: HKCU; Subkey: "Software\Classes\EleViewer.Html"; ValueType: string; ValueName: ""; ValueData: "HTML Document"; Flags: uninsdeletekey; Tasks: associate\html
Root: HKCU; Subkey: "Software\Classes\EleViewer.Html"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "EleViewer Web Document"; Flags: uninsdeletekey; Tasks: associate\html
Root: HKCU; Subkey: "Software\Classes\EleViewer.Html\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\EleViewer.exe,0"; Tasks: associate\html
Root: HKCU; Subkey: "Software\Classes\EleViewer.Html\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\EleViewer.exe"" ""%1"""; Tasks: associate\html

[Run]
Filename: "{app}\EleViewer.exe"; Description: "Launch EleViewer"; Flags: nowait postinstall skipifsilent
Filename: "{app}\EleViewer.exe"; Parameters: ""; Flags: nowait; Check: IsSilentRelaunch

[Code]
function IsSilentRelaunch(): Boolean;
begin
  Result := CmdLineParamExists('/RESTARTAPP');
end;
