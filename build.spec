# -*- mode: python ; coding: utf-8 -*-

import sys

# Augmenter la limite de récursion pour certains projets complexes
sys.setrecursionlimit(5000)

# Définir le nom de l'exécutable
exe_name = 'PFE-Roguelike'

# --- Analyse du projet ---
# PyInstaller analyse tous les imports et dépendances à partir du script principal.
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    # --- Ajout des fichiers de données (assets) ---
    # C'est ici qu'on spécifie les fichiers et dossiers non-Python.
    # Le format est une liste de tuples : (source_sur_disque, destination_dans_le_bundle)
    datas=[
        # Inclure le dossier 'items' et son contenu (items.csv)
        # Le dossier 'items' sera créé à la racine du bundle.
        ('items', 'items'),
        
        # Inclure le dossier 'src' contenant les images (.gif, .ico, etc.)
        # Le dossier 'src' sera créé à la racine du bundle.
        ('src', 'src')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    # Ne pas inclure les assemblies privées de Windows
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)

# --- Création de l'exécutable ---
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Utiliser UPX pour compresser l'exécutable si disponible
    upx_exclude=[],
    runtime_tmpdir=None,
    # --- Console ---
    # True: ouvre une console au lancement (utile pour le débogage).
    # False: pas de console (pour une application purement graphique).
    # Gardons la console pour l'instant, car le jeu a un mode console.
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # --- Icône de l'exécutable ---
    # Spécifier une icône pour le fichier .exe
    # L'icône doit être au format .ico
    icon='src/gameplay.ico'
)

# --- Création du dossier de distribution (mode "one-folder") ---
# Le mode "one-folder" est plus facile à déboguer. Il crée un dossier
# contenant l'exécutable et toutes ses dépendances.
coll = COLLECT(
    exe,
    a.datas,
    a.binaries,
    a.zipfiles,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=exe_name
)
