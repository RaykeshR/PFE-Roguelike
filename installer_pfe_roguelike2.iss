; ---------------------------------------------------------
; Installeur PFE-Roguelike – Inno Setup 6.6.1
; ---------------------------------------------------------

; DÉFINITION DES CONSTANTES (Pour modifier facilement)
#define MyAppURL "https://github.com/RaykeshR/PFE-Roguelike"
#define MyAppPublisher "Raykesh"

[Setup]
AppName=PFE-Roguelike
AppVersion=2.6.0.4
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={pf}\PFE-Roguelike
DefaultGroupName=PFE-Roguelike
DisableProgramGroupPage=yes

OutputBaseFilename=Setup_PFE-Roguelike
SetupIconFile="src/gameplay.ico"
UninstallDisplayIcon="images\Gemini_Generated_Image_9suv459suv459suv.bmp"

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
Name: "{group}\Désinstaller PFE-Roguelike"; Filename: "{uninstallexe}"; IconFilename: "images\Gemini_Generated_Image_9suv459suv459suv.bmp"

; Raccourci sur le bureau
Name: "{commondesktop}\PFE-Roguelike"; Filename: "{app}\PFE-Roguelike.exe"; Tasks: desktopicon

[Tasks]
; Option pouvant être décochée par l’utilisateur
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; Flags: unchecked

[Run]
; Lancer le jeu à la fin de l'installation
Filename: "{app}\PFE-Roguelike.exe"; Description: "Lancer PFE-Roguelike"; Flags: nowait postinstall skipifsilent

[Code]
var
  FinishedPage: TWizardPage;
  StatusLabel: TLabel;
  AdminEmail: String;

// Fired when the "Browse for .env file" button is clicked
procedure SelectEnvFile;
var
  OpenDialog: TOpenDialog;
  SourcePath, DestPath: String;
begin
  OpenDialog := TOpenDialog.Create(FinishedPage);
  try
    OpenDialog.Title := 'Sélectionner le fichier .env';
    OpenDialog.Filter := '.env files|*.env|All files|*.*';
    if OpenDialog.Execute then
    begin
      SourcePath := OpenDialog.FileName;
      DestPath := ExpandConstant('{app}\.env');
      if FileCopy(SourcePath, DestPath, False) then
      begin
        StatusLabel.Caption := 'Fichier .env importé avec succès dans ' + DestPath;
        WizardForm.NextButton.Enabled := True;
      end
      else
      begin
        MsgBox('Échec de la copie du fichier .env. Veuillez réessayer en tant qu''administrateur.', mbError, MB_OK);
      end;
    end;
  finally
    OpenDialog.Free;
  end;
end;

// Fired when the "Email Admin" button is clicked
procedure EmailAdmin;
var
  ErrorCode: Integer;
begin
  // IMPORTANT: Replace with the actual admin email address
  AdminEmail := 'admin@example.com';
  ShellExec('open', 'mailto:' + AdminEmail + '?subject=Demande de fichier .env pour PFE-Roguelike&body=Bonjour,%0D%0A%0D%0AVeuillez m''envoyer le fichier de configuration .env pour l''application PFE-Roguelike.%0D%0A%0D%0AMerci.', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

procedure InitializeWizard;
var
  PageDescription: TLabel;
  SelectButton, EmailButton: TButton;
begin
  // Create the custom final page
  FinishedPage := CreateCustomPage(wpFinished, 'Configuration Requise', 'Le fichier .env est nécessaire pour continuer.');

  // Add descriptive label
  PageDescription := TLabel.Create(FinishedPage);
  PageDescription.Parent := FinishedPage.Surface;
  PageDescription.Left := 0;
  PageDescription.Top := 0;
  PageDescription.Width := FinishedPage.SurfaceWidth;
  PageDescription.Height := 80;
  PageDescription.Autosize := False;
  PageDescription.WordWrap := True;
  PageDescription.Caption := 'L''application PFE-Roguelike a besoin du fichier de configuration ".env" pour se connecter à la base de données.' + #13#10#13#10 +
                           'Vous pouvez soit chercher le fichier sur votre ordinateur, soit envoyer une demande par e-mail à l''administrateur pour l''obtenir.';

  // Add the "Browse" button
  SelectButton := TButton.Create(FinishedPage);
  SelectButton.Parent := FinishedPage.Surface;
  SelectButton.Top := PageDescription.Top + PageDescription.Height;
  SelectButton.Width := 200;
  SelectButton.Caption := '1. Chercher le fichier .env...';
  SelectButton.OnClick := @SelectEnvFile;

  // Add the "Email" button
  EmailButton := TButton.Create(FinishedPage);
  EmailButton.Parent := FinishedPage.Surface;
  EmailButton.Top := SelectButton.Top + SelectButton.Height + 10;
  EmailButton.Width := 200;
  EmailButton.Caption := '2. Envoyer un e-mail à l''admin';
  EmailButton.OnClick := @EmailAdmin;

  // Add a status label to give feedback to the user
  StatusLabel := TLabel.Create(FinishedPage);
  StatusLabel.Parent := FinishedPage.Surface;
  StatusLabel.Top := EmailButton.Top + EmailButton.Height + 20;
  StatusLabel.Left := 0;
  StatusLabel.Width := FinishedPage.SurfaceWidth;
  StatusLabel.Caption := 'Statut : Le fichier .env est manquant.';
end;

// This function is called when the wizard is leaving a page.
function NextButtonClick(CurPageID: Integer): Boolean;
var
  EnvPath: String;
begin
  Result := True;
  // If we are on the page before our custom page
  if CurPageID = wpReady then
  begin
    // Check if .env file already exists from a previous installation
    EnvPath := ExpandConstant('{app}\.env');
    if FileExists(EnvPath) then
    begin
        // If it exists, we don't need to show the custom page
        WizardForm.FinishedPage := wpFinished;
        WizardForm.NextButton.Enabled := True;
    end
    else
    begin
        // If not, show the custom page and disable "Finish" button until the file is provided
        WizardForm.FinishedPage := FinishedPage;
        WizardForm.NextButton.Enabled := False;
    end;
  end;
end;

// Override the default finished page
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = FinishedPage.ID then
  begin
    // This is our custom page
    // The "Finish" button is initially disabled
    WizardForm.NextButton.Caption := 'Terminer';
  end
  else if CurPageID = wpFinished then
  begin
    // This is the default finished page, in case our custom page was skipped
    WizardForm.NextButton.Caption := 'Terminer';
  end;
end;
