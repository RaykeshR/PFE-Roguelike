; ---------------------------------------------------------
; Installeur PFE-Roguelike – Inno Setup 6.6.1
; ---------------------------------------------------------

; DÉFINITION DES CONSTANTES (Pour modifier facilement)
#define MyAppURL "https://github.com/RaykeshR/PFE-Roguelike"

[Setup]
AppName=PFE-Roguelike
AppVersion=2.6.0.4
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={pf}\PFE-Roguelike
DefaultGroupName=PFE-Roguelike
DisableProgramGroupPage=yes

OutputBaseFilename=Setup_PFE-Roguelike
SetupIconFile="src/gameplay.ico"
WizardImageFile="images\Gemini_Generated_Image_9suv459suv459suv.bmp"
WizardSmallImageFile="images\Gemini_Generated_Image_9suv459suv459suv.bmp"
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
; Permet de fermer l'appli si elle tourne déjà lors d'une mise à jour
CloseApplications=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

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
