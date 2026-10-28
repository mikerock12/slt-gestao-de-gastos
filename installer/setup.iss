#define AppName "SLT - Gestao de Gastos"
#define AppVersion "1.1.0"
[Setup]
AppId={{BFC8B30A-E82D-452F-83B5-B98713BB5123}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Smells Like Tech
DefaultDirName={localappdata}\Programs\SLT Gestao de Gastos
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=SLT-Gestao-de-Gastos-Setup-1.1.0
SetupIconFile=..\recursos\slt.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\SLT - Gestão de Gastos.exe
[Files]
Source: "..\dist\SLT - Gestão de Gastos.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\SLT - Gestão de Gastos.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\SLT - Gestão de Gastos.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked
[Run]
Filename: "{app}\SLT - Gestão de Gastos.exe"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent
