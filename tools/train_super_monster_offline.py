import sys
import os
import json
import pickle
from collections import defaultdict

# Setup des chemins pour importer engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from engine.rl import QLearningAgent

# Chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs', 'episodes')
PRETRAINED_MODEL = os.path.join(BASE_DIR, 'models', 'base_q_table.pkl') # Créé par l'étape 1
FINAL_MODEL = os.path.join(BASE_DIR, 'models', 'global_q_table.pkl')

def train_super_monster_offline():
    print("--- 🧠 Entraînement du SUPER MONSTRE (Mode Hors Ligne) ---")
    
    agent = QLearningAgent()
    
    # 1. Charger le savoir du pré-entraînement (si disponible)
    if os.path.exists(PRETRAINED_MODEL):
        print(f"-> Chargement du pré-entraînement : {PRETRAINED_MODEL}")
        with open(PRETRAINED_MODEL, 'rb') as f:
            pretrained_data = pickle.load(f)
            agent.Q.update(pretrained_data)
        print(f"   Base de connaissances : {len(agent.Q)} états connus.")
    else:
        print("-> ⚠️ Aucun pré-entraînement trouvé. Le monstre part de zéro.")

    # 2. Apprendre depuis les logs de jeu locaux (.jsonl)
    print(f"-> Lecture des logs locaux dans : {LOGS_DIR}")
    transition_count = 0
    files_read = 0
    
    for root, dirs, files in os.walk(LOGS_DIR):
        for filename in files:
            if filename.endswith(".jsonl"):
                files_read += 1
                path = os.path.join(root, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                data = json.loads(line)
                                # On cherche les lignes qui sont des transitions RL
                                if 's' in data and 'a' in data and 'r' in data:
                                    # Conversion des listes en tuples pour les clés du dico
                                    s = tuple(data['s'])
                                    a = data['a']
                                    r = data['r']
                                    s2 = tuple(data['s2'])
                                    done = data.get('done', False)
                                    
                                    agent.update(s, a, r, s2, done)
                                    transition_count += 1
                            except:
                                continue
                except Exception as e:
                    print(f"Erreur sur {filename}: {e}")

    print(f"-> Fin de l'apprentissage sur {files_read} fichiers.")
    print(f"-> {transition_count} nouvelles expériences analysées.")

    # 3. Sauvegarder le modèle final
    os.makedirs(os.path.dirname(FINAL_MODEL), exist_ok=True)
    with open(FINAL_MODEL, 'wb') as f:
        pickle.dump(dict(agent.Q), f)

    print(f"✅ SUPER MONSTRE SAUVEGARDÉ : {FINAL_MODEL}")
    print(f"Total états dans le cerveau : {len(agent.Q)}")

if __name__ == "__main__":
    train_super_monster_offline()