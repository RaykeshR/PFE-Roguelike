; ---------------------------------------------------------
; Installeur PFE-Roguelike – Inno Setup 6.6.1
; ---------------------------------------------------------

[Setup]
AppName=PFE-Roguelike
AppVersion=2.6.0.3
DefaultDirName={pf}\PFE-Roguelike
DefaultGroupName=PFE-Roguelike
DisableProgramGroupPage=yes
OutputBaseFilename=Setup_PFE-Roguelike
SetupIconFile="src/gameplay.ico"
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

[Files]
Source: "dist\PFE-Roguelike\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Raccourci dans le menu démarrer
Name: "{group}\PFE-Roguelike"; Filename: "{app}\PFE-Roguelike.exe"

; Raccourci sur le bureau
Name: "{commondesktop}\PFE-Roguelike"; Filename: "{app}\PFE-Roguelike.exe"; Tasks: desktopicon

[Tasks]
; Option pouvant être décochée par l’utilisateur
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; Flags: unchecked

[Run]
; Lancer le jeu à la fin de l'installation
Filename: "{app}\PFE-Roguelike.exe"; Description: "Lancer PFE-Roguelike"; Flags: nowait postinstall skipifsilent
