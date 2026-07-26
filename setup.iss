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
; Modern UI & Brand Styling
WizardStyle=modern
WizardResizable=no
; To apply our custom color code (#161616 dark panels and #6cb6ff electric blue accents)
; to the wizard sidebars and headers, place branded bitmaps in the icons/ folder:
; WizardImageFile=icons\wizard_banner.bmp
; WizardSmallImageFile=icons\wizard_logo.bmp

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
Name: "associate"; Description: "Open my study files (PDFs, Word docs, Excel, PowerPoint, Markdown, CSV, TXT, HTML) with EleViewer by default"; GroupDescription: "Default File Associations"
Name: "contextmenu"; Description: "Add 'Open with EleViewer' to my right-click menu in Windows Explorer"; GroupDescription: "Windows Explorer Integration"

[Files]
; The source is the single portable executable created by PyInstaller.
Source: "dist\EleViewer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "getting_started\*"; DestDir: "{app}\getting_started"; Flags: ignoreversion recursesubdirs createallsubdirs

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
