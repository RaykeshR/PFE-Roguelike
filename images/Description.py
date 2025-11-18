import os
import subprocess
from PIL import Image

frames_folder = "images/Jeu"
descs_folder = "images/descriptions"
os.makedirs(descs_folder, exist_ok=True)

for img in sorted(os.listdir(frames_folder)):
    if img.lower().endswith(".png"):
        img_path = os.path.join(frames_folder, img)
        txt_path = os.path.join(descs_folder, os.path.splitext(img)[0] + ".txt")
        
        # Vérifie si la description existe déjà
        if os.path.exists(txt_path):
            print(f"[INFO] La description pour {img} existe déjà, je passe...")
            continue
        
        # Récupère les dimensions de l'image
        with Image.open(img_path) as im:
            width, height = im.size
        
        # # Appel à Gemini CLI
        command = [r"C:\Users\...\AppData\Roaming\npm\gemini.cmd", "prompt", f"Décris cette image @{img_path}"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Vérifie s'il y a eu une erreur
        if result.returncode != 0:
            print(f"[ERREUR] Échec de la génération de la description pour {img}.")
            print(f"Commande : {' '.join(command)}")
            print(f"Code de retour : {result.returncode}")
            print(f"Stderr : {result.stderr.strip()}")
            continue # Passe à l'image suivante

        description = result.stdout.strip()

        # Vérifie si la description est vide
        if not description:
            print(f"[AVERTISSEMENT] La description générée pour {img} est vide.")
            print(f"Stderr : {result.stderr.strip()}")
        
        # Prépare le contenu final avec métadonnées
        content = f"--- MÉTADONNÉES ---\n"
        content += f"Fichier : {img}\n"
        content += f"Largeur : {width}px\n"
        content += f"Hauteur : {height}px\n"
        content += "\n--- DESCRIPTION ---\n"
        content += description
        
        # Écrit dans le fichier
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"[OK] Description générée pour {img}")
