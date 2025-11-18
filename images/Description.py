import os
import subprocess

frames_folder = "Jeu"
descs_folder = "descriptions"
os.makedirs(descs_folder, exist_ok=True)

for img in sorted(os.listdir(frames_folder)):
    if img.endswith(".png"):
        img_path = os.path.join(frames_folder, img)
        txt_path = os.path.join(descs_folder, os.path.splitext(img)[0] + ".txt")
        
        result = subprocess.run(
            ["gemini", "prompt", "Décris cette image", "--image", img_path],
            capture_output=True, text=True
        )
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result.stdout.strip())
