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
        result = subprocess.run(
            ["gemini", "prompt", "Décris cette image", "--image", img_path],
            capture_output=True,
            text=True
        )
        description = result.stdout.strip()
        
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
