import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# Connexion à MongoDB
client = MongoClient(os.getenv("MONGO_URL"))
db = client["RoguelikePFE"]   # nom de la base Mongo

# Exemple : fonction pour logguer une action
def log_action(joueur_id, partie_id, action, details=None):
    log = {
        "joueur_id": joueur_id,
        "partie_id": partie_id,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    db.logs_actions.insert_one(log)
    print(f" Log inséré : {log}")
