import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from dotenv import load_dotenv
from collections import defaultdict
import numpy as np
import datetime

# --- Configuration ---

# Charge les variables d'environnement (ex: MONGO_URL)
# depuis le fichier database/.env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'database', '.env')
load_dotenv(dotenv_path=dotenv_path)

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = "RoguelikePFE_Analytics"

# Chemin vers le modèle sauvegardé
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'global_q_table.pkl')

# Dossier où sauvegarder les graphiques
OUTPUT_DIR = "analytics_charts"

# S'assurer que le dossier de sortie existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"Connexion à MongoDB (URL: {MONGO_URL[:20]}...)\n")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]


def fetch_data_from_mongo(collection_name, projection, limit=0):
    """
    Récupère les données de MongoDB et les convertit en DataFrame pandas.
    """
    print(f"Chargement des données depuis la collection [{collection_name}]...")
    collection = db[collection_name]
    
    # .find() retourne un curseur
    cursor = collection.find({}, projection)
    
    if limit > 0:
        cursor = cursor.limit(limit)

    data = list(cursor)
    
    if not data:
        print(f"  -> Aucune donnée trouvée dans '{collection_name}'.")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    print(f"  -> {len(df)} documents chargés.\n")
    return df


def generate_rewards_histogram(df_transitions):
    """
    Génère un histogramme des récompenses ('r')
    """
    if 'r' not in df_transitions.columns:
        print("Colonne 'r' (récompense) non trouvée. Saut de l'histogramme des récompenses.")
        return

    print("Génération de l'histogramme des récompenses...")
    
    # Compte la fréquence de chaque récompense
    reward_counts = df_transitions['r'].value_counts().reset_index()
    reward_counts.columns = ['Récompense (r)', 'Nombre']
    
    # On trie par la récompense pour que le graphique soit lisible
    reward_counts = reward_counts.sort_values(by='Récompense (r)')

    plt.figure(figsize=(10, 6))
    sns.barplot(data=reward_counts, x='Récompense (r)', y='Nombre', palette="viridis")
    
    # On met l'axe Y en log pour mieux voir les faibles valeurs
    plt.yscale('log')
    
    plt.title('Distribution des Récompenses (Axe Y Logarithmique)')
    plt.xlabel('Valeur de la Récompense')
    plt.ylabel('Fréquence (Log)')
    
    filepath = os.path.join(OUTPUT_DIR, "1_histogramme_recompenses.png")
    plt.savefig(filepath)
    print(f"  -> Graphique sauvegardé : {filepath}\n")
    plt.close()


def generate_actions_barchart(df_transitions):
    """
    Génère un diagramme en barres de la fréquence des actions ('a')
    """
    if 'a' not in df_transitions.columns:
        print("Colonne 'a' (action) non trouvée. Saut du diagramme des actions.")
        return

    print("Génération du diagramme des actions...")
    
    action_counts = df_transitions['a'].value_counts().sort_index()
    
    # Mappage des actions (optionnel, à adapter)
    # 0: Up, 1: Down, 2: Left, 3: Right
    action_map = {0: "Haut", 1: "Bas", 2: "Gauche", 3: "Droite"} 
    action_counts.index = action_counts.index.map(lambda x: action_map.get(x, f"Action {x}"))

    plt.figure(figsize=(10, 6))
    sns.barplot(x=action_counts.index, y=action_counts.values, palette="rocket")
    
    plt.title('Fréquence des Actions des Monstres')
    plt.xlabel('Action')
    plt.ylabel('Nombre total d\'utilisations')
    
    filepath = os.path.join(OUTPUT_DIR, "2_frequence_actions.png")
    plt.savefig(filepath)
    print(f"  -> Graphique sauvegardé : {filepath}\n")
    plt.close()


def generate_q_table_heatmap():
    """
    Charge la Q-Table depuis le fichier .pkl et génère une heatmap.
    """
    print(f"Chargement du modèle Q-Table depuis {MODEL_PATH}...")
    try:
        with open(MODEL_PATH, 'rb') as f:
            q_table = pickle.load(f)
    except FileNotFoundError:
        print(f"  -> ERREUR: Fichier modèle '{MODEL_PATH}' non trouvé. Saut de la heatmap.\n")
        return
    except Exception as e:
        print(f"  -> ERREUR: Impossible de charger le fichier pickle : {e}\n")
        return

    if not isinstance(q_table, (dict, defaultdict)):
        print(f"  -> ERREUR: La Q-Table n'est pas un dictionnaire. Type trouvé: {type(q_table)}. Saut de la heatmap.\n")
        return
        
    print("Génération de la heatmap de la Q-Table...")

    # Définit la grille de l'état (distance au joueur)
    # A adapter selon ton état ! J'assume ici que l'état est un tuple (dx, dy)
    range_x = range(-10, 11)
    range_y = range(-10, 11)
    
    # Crée une matrice vide pour stocker la *meilleure valeur* de chaque état
    # np.nan est utilisé pour les états non visités
    heatmap_data = pd.DataFrame(index=range_y, columns=range_x, dtype=float)
    
    for x in range_x:
        for y in range_y:
            state = (x, y) # L'état est (dx, dy)
            
            # Récupère les valeurs Q pour cet état
            # Si l'état n'a jamais été vu, q_values sera None ou un tableau de zéros
            q_values = q_table.get(state)
            
            if q_values is not None and np.any(q_values != 0):
                # On prend la *valeur maximale* (la meilleure action possible)
                heatmap_data.loc[y, x] = np.max(q_values)
            else:
                heatmap_data.loc[y, x] = np.nan # État non exploré

    plt.figure(figsize=(12, 10))
    sns.heatmap(heatmap_data, annot=False, cmap="viridis", cbar_kws={'label': 'Valeur Q Maximale'})
    
    plt.title('Heatmap de la Q-Table (Valeur maximale par état)')
    plt.xlabel('Distance X au Joueur (dx)')
    plt.ylabel('Distance Y au Joueur (dy)')
    plt.gca().invert_yaxis() # Met le (0,0) en haut à gauche
    
    # Ajoute un point pour le joueur au centre
    plt.scatter([10.5], [10.5], c='red', marker='X', s=100, label='Joueur (0, 0)')
    plt.legend()
    
    filepath = os.path.join(OUTPUT_DIR, "3_heatmap_q_table.png")
    plt.savefig(filepath)
    print(f"  -> Graphique sauvegardé : {filepath}\n")
    plt.close()


def generate_episode_duration_histogram():
    """
    Calcule la durée des épisodes et génère un histogramme.
    """
    print("Chargement des données depuis [game_episodes] pour la durée...")
    collection = db["game_episodes"]
    cursor = collection.find({}, {"events.ts": 1}) # On ne prend que les timestamps

    durations = []
    
    for i, episode in enumerate(cursor):
        if "events" in episode and len(episode["events"]) > 1:
            try:
                # Timestamps sont au format ISO (string)
                start_time = datetime.datetime.fromisoformat(episode["events"][0]["ts"].replace('Z', '+00:00'))
                end_time = datetime.datetime.fromisoformat(episode["events"][-1]["ts"].replace('Z', '+00:00'))
                
                duration_sec = (end_time - start_time).total_seconds()
                
                # On ignore les parties trop courtes (ex: moins d'1 seconde)
                if duration_sec > 1:
                    durations.append(duration_sec)
            except Exception as e:
                print(f"Erreur de parsing date pour épisode: {e}")

    if not durations:
        print("  -> Aucune donnée de durée d'épisode trouvée. Saut du graphique.\n")
        return

    print(f"  -> {len(durations)} durées d'épisodes calculées.")
    df_durations = pd.DataFrame(durations, columns=["Durée (secondes)"])

    plt.figure(figsize=(10, 6))
    sns.histplot(df_durations, x="Durée (secondes)", bins=30, kde=True)
    
    plt.title('Distribution de la Durée des Parties')
    plt.xlabel('Durée (secondes)')
    plt.ylabel('Nombre de parties')
    
    filepath = os.path.join(OUTPUT_DIR, "4_histogramme_duree_parties.png")
    plt.savefig(filepath)
    print(f"  -> Graphique sauvegardé : {filepath}\n")
    plt.close()


def main():
    # --- Analyse 1 & 2 : Transitions (Récompenses et Actions) ---
    # On limite à 500 000 pour l'analyse rapide. Enlève le 'limit' pour tout analyser.
    df_transitions = fetch_data_from_mongo(
        collection_name="rl_transitions", 
        projection={"r": 1, "a": 1, "_id": 0},
        limit=500000 
    )

    if not df_transitions.empty:
        generate_rewards_histogram(df_transitions)
        generate_actions_barchart(df_transitions)
    else:
        print("Collection [rl_transitions] vide. Analyses 1 et 2 sautées.\n")

    # --- Analyse 3 : Heatmap du Modèle ---
    generate_q_table_heatmap()
    
    # --- Analyse 4 : Durée des Épisodes ---
    generate_episode_duration_histogram()
    
    print("--- Analyse terminée ! ---")
    print(f"Tous les graphiques sont dans le dossier : {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    # Assure-toi d'avoir ces librairies installées !
    # pip install pandas matplotlib seaborn pymongo python-dotenv
    main()