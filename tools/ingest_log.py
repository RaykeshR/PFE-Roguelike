# PFE_Roguelike/tools/ingest_logs.py
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

def run_etl():
    # Charger les variables d'environnement
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'database', '.env')
    load_dotenv(dotenv_path=dotenv_path)

    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url or '<db_password>' in mongo_url:
        print("Erreur: L'URL de MongoDB n'est pas configurée dans database/.env")
        return

    client = MongoClient(mongo_url)
    db = client["RoguelikePFE_Analytics"]
    collection = db["game_episodes"]
    print(" Connecté à MongoDB.")

    # Chemin vers les logs
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'episodes')
    
    processed_files = set() # Pour éviter de traiter les mêmes fichiers plusieurs fois

    for day_folder in os.listdir(logs_dir):
        day_path = os.path.join(logs_dir, day_folder)
        if not os.path.isdir(day_path):
            continue
            
        for filename in os.listdir(day_path):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(day_path, filename)
                
                # Extrait l'ID de l'épisode du nom de fichier
                episode_id = filename.replace('episode_', '').replace('.jsonl', '')

                # Vérifie si cet épisode est déjà dans la base
                if collection.find_one({"episode_id": episode_id}):
                    continue

                print(f" Traitement du fichier : {filename}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    episode_data = [json.loads(line) for line in f]
                
                if episode_data:
                    # Insère l'ensemble de l'épisode comme un seul document
                    collection.insert_one({
                        "episode_id": episode_id, 
                        "events": episode_data
                    })
                    print(f"  -> Episode {episode_id} inséré.")

if __name__ == "__main__":
    run_etl()