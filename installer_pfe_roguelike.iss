; ---------------------------------------------------------
; Installeur PFE-Roguelike – Inno Setup 6.6.1
; ---------------------------------------------------------

; DÉFINITION DES CONSTANTES (Pour modifier facilement)
#define MyAppName "PFE-Roguelike"
#define MyAppVersion "2.6.0.80"
#define MyAppPublisher "Raykesh, Sabri, Maxence, Coumba, Chrisphen"
#define MyAppURL "https://github.com/RaykeshR/PFE-Roguelike"
#define MyAppExeName "PFE-Roguelike.exe"

[Setup]
AppId={{4F8525EE-084E-4213-9FFB-71FC3A0F9279}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription="Setup de {#MyAppName} - Un jeu roguelike développé dans le cadre d'un PFE."
VersionInfoCopyright="Copyright © 2024 {#MyAppPublisher}®. Tous droits réservés."
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; --- Droits ---
; Nécessaire pour écrire le .env dans Program Files
PrivilegesRequired=admin

OutputBaseFilename=Setup_PFE-Roguelike_v{#MyAppVersion}
SetupIconFile="images\Gemini_Generated_Image_9suv459suv459suv2.ico"
UninstallDisplayIcon="images\Gemini_Generated_Image_9suv459suv459suv.bmp"

WizardImageFile="images\Gemini_Generated_Image_9suv459suv459suv.bmp"
WizardSmallImageFile="images\Gemini_Generated_Image_9suv459suv459suv.bmp"
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern dark polar
UsePreviousLanguage=yes
WizardResizable=yes
; Permet de fermer l'appli si elle tourne déjà lors d'une mise à jour
CloseApplications=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
; 1. Le jeu principal
Source: "dist\PFE-Roguelike\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 2. L'icône (CRITIQUE : On l'ajoute explicitement pour qu'elle existe chez le client)
Source: "src\gameplay.ico"; DestDir: "{app}\src"; Flags: ignoreversion

[Icons]
; Raccourci dans le menu démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "images\Gemini_Generated_Image_9suv459suv459suv.bmp"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "images\Gemini_Generated_Image_9suv459suv459suv.bmp"

; Raccourci sur le bureau
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "images\Gemini_Generated_Image_9suv459suv459suv.bmp"

[Tasks]
; Option pouvant être décochée par l’utilisateur
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; Flags: unchecked

[Run]
; Lancer le jeu à la fin de l'installation
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\.env"


[Code]
var
  EnvPage: TWizardPage;
  StatusLabel: TLabel;
  SelectButton, EmailButton: TButton;

// --- Procédure de copie du fichier .env ---
procedure SelectEnvFile(Sender: TObject);
var
  SourcePath, DestPath: String;
begin
  // Utilisation de la fonction GetOpenFileName d'Inno Setup (Déjà corrigé)
  if GetOpenFileName(
        'Sélectionner le fichier .env', // Titre
        SourcePath,                    // Variable qui recevra le chemin
        '',                            // Dossier initial (vide = par défaut)
        'Fichiers de configuration (*.env)|*.env|Tous les fichiers (*.*)|*.*', // Filtre
        '.env'                         // Extension par défaut (facultatif)
      ) then
  begin
    DestPath := ExpandConstant('{app}\.env');
    
    // On tente la copie
    if FileCopy(SourcePath, DestPath, False) then
    begin
      StatusLabel.Caption := 'Succès : fichier .env installé !';
      StatusLabel.Font.Color := clGreen;
      WizardForm.NextButton.Enabled := True; // Débloque le bouton
    end
    else
      MsgBox('Erreur lors de la copie du fichier .env.'#13#10'Vérifiez vos droits administrateur.', mbError, MB_OK);
  end;
end;

// --- Procédure d'envoi d'email ---
procedure EmailAdmin(Sender: TObject);
var
  ErrorCode: Integer;
begin
  ShellExec(
    'open',
    'mailto:ton.email@etudiant.fr?subject=Demande du fichier .env - PFE Roguelike'
      + '&body=Bonjour,%0D%0AMerci de m''envoyer le fichier .env pour pouvoir lancer le jeu.',
    '',
    '',
    SW_SHOWNORMAL,
    ewNoWait,
    ErrorCode
  );
end;

// --- Initialisation de l'interface ---
procedure InitializeWizard;
var
  PageDescription: TLabel;
begin
  // Création de la page juste après l'installation des fichiers
  EnvPage := CreateCustomPage(wpInstalling, 'Configuration', 'Configuration du fichier .env');

  // Description
  PageDescription := TLabel.Create(EnvPage);
  PageDescription.Parent := EnvPage.Surface;
  PageDescription.Left := 0;
  PageDescription.Top := 0;
  PageDescription.Width := EnvPage.SurfaceWidth;
  PageDescription.Height := 50;
  PageDescription.WordWrap := True;
  PageDescription.Caption :=
    'Le jeu nécessite un fichier ".env" pour se connecter à la base de données.'#13#10+
    'Veuillez l''importer ou le demander à l''administrateur.';

  // Bouton Import
  SelectButton := TButton.Create(EnvPage);
  SelectButton.Parent := EnvPage.Surface;
  SelectButton.Left := 0;
  SelectButton.Top := PageDescription.Top + PageDescription.Height + 10;
  SelectButton.Width := 200;
  SelectButton.Caption := 'Importer mon fichier .env';
  SelectButton.OnClick := @SelectEnvFile;

  // Bouton Email
  EmailButton := TButton.Create(EnvPage);
  EmailButton.Parent := EnvPage.Surface;
  EmailButton.Left := 0; // Alignement propre à gauche
  EmailButton.Top := SelectButton.Top + SelectButton.Height + 10;
  EmailButton.Width := 200;
  EmailButton.Caption := 'Demander le fichier par Email';
  EmailButton.OnClick := @EmailAdmin;

  // Label Statut
  StatusLabel := TLabel.Create(EnvPage);
  StatusLabel.Parent := EnvPage.Surface;
  StatusLabel.Left := 0;
  StatusLabel.Top := EmailButton.Top + EmailButton.Height + 20;
  StatusLabel.Caption := 'Statut : en attente du fichier .env...';
  StatusLabel.Font.Color := clRed;
  StatusLabel.Font.Style := [fsBold];
end;

// --- Logique de passage de page ---
procedure CurPageChanged(CurPageID: Integer);
var
  EnvPath: String;
begin
  if CurPageID = EnvPage.ID then
  begin
    // Nouvelle tentative pour détecter le mode silencieux/non-interactif.
    // Cette méthode utilise la fonction intégrée IsTaskSelected, qui est toujours disponible.
    // Si l'assistant n'est pas affiché, l'installation est silencieuse/en arrière-plan.
    
    // **SOLUTION DE DERNIER RECOURS** :
    // On vérifie si l'installateur est en mode non-interactif (car pas de fenêtre d'assistant)
    if not Assigned(WizardForm) then 
    begin
      // Si WizardForm n'existe pas, nous sommes en mode /SILENT ou /VERYSILENT.
      WizardForm.NextButton.Enabled := True;
      Exit; 
    end;

    // --- Logique pour l'installation interactive (non-silencieuse) ---
    
    // Vérification de la présence du fichier
    EnvPath := ExpandConstant('{app}\.env');

    if FileExists(EnvPath) then
    begin
      StatusLabel.Caption := 'Fichier .env détecté.';
      StatusLabel.Font.Color := clGreen;
      WizardForm.NextButton.Enabled := True;
    end
    else
    begin
      StatusLabel.Caption := 'Fichier .env manquant.';
      StatusLabel.Font.Color := clRed;
      WizardForm.NextButton.Enabled := False; // Bloque le bouton Suivant
    end;
  end;
end;