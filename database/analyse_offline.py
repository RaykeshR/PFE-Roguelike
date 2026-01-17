import os
import json
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime
from collections import defaultdict

# --- Configuration ---

# Chemins relatifs basés sur la structure de votre projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs', 'episodes')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'global_q_table.pkl')
OUTPUT_DIR = os.path.join(BASE_DIR, 'analytics_charts')

# S'assurer que le dossier de sortie existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_data_from_local_logs(limit=0):
    """
    Parcourt les fichiers logs locaux (.jsonl) pour extraire les transitions et les durées.
    Remplace la connexion MongoDB.
    """
    print(f"Lecture des logs locaux depuis : {LOGS_DIR} ...")
    
    transitions_data = []
    durations_data = []
    
    file_count = 0
    
    # Parcourt récursivement le dossier logs/episodes
    for root, dirs, files in os.walk(LOGS_DIR):
        for filename in files:
            if filename.endswith(".jsonl"):
                file_path = os.path.join(root, filename)
                file_count += 1
                
                # Arrêt si limite atteinte (pour tester vite)
                if limit > 0 and len(transitions_data) > limit:
                    break

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        episode_events = []
                        for line in f:
                            try:
                                entry = json.loads(line)
                                episode_events.append(entry)
                                
                                # Si c'est une transition (pour l'analyse RL)
                                # On cherche les clés 'r' (reward) et 'a' (action)
                                if 'r' in entry and 'a' in entry:
                                    transitions_data.append({
                                        'r': entry['r'],
                                        'a': entry['a']
                                    })
                                    
                            except json.JSONDecodeError:
                                continue
                        
                        # Calcul durée épisode
                        if len(episode_events) > 1:
                            # On essaie de trouver les timestamps du début et de fin
                            # Format attendu: "timestamp": "2025-11-17T..." ou "ts" dans l'event
                            try:
                                t_start = None
                                t_end = None
                                
                                # Chercher le premier timestamp valide
                                for e in episode_events:
                                    if "ts" in e:
                                        t_start = datetime.datetime.fromisoformat(e["ts"].replace('Z', '+00:00'))
                                        break
                                    elif "timestamp" in e:
                                        t_start = datetime.datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00'))
                                        break
                                
                                # Chercher le dernier timestamp valide
                                for e in reversed(episode_events):
                                    if "ts" in e:
                                        t_end = datetime.datetime.fromisoformat(e["ts"].replace('Z', '+00:00'))
                                        break
                                    elif "timestamp" in e:
                                        t_end = datetime.datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00'))
                                        break
                                        
                                if t_start and t_end:
                                    duration = (t_end - t_start).total_seconds()
                                    if duration > 1: # Filtre les bugs
                                        durations_data.append(duration)
                            except Exception as e:
                                pass # Ignorer les erreurs de date ponctuelles

                except Exception as e:
                    print(f"Erreur lecture fichier {filename}: {e}")

    print(f" -> {file_count} fichiers analysés.")
    print(f" -> {len(transitions_data)} transitions trouvées.")
    print(f" -> {len(durations_data)} durées de parties calculées.\n")
    
    return pd.DataFrame(transitions_data), pd.DataFrame(durations_data, columns=['Durée (secondes)'])

def generate_rewards_histogram(df_transitions):
    if 'r' not in df_transitions.columns or df_transitions.empty:
        print("Pas de données de récompenses ('r'). Saut du graphique.")
        return

    print("Génération de l'histogramme des récompenses...")
    reward_counts = df_transitions['r'].value_counts().reset_index()
    reward_counts.columns = ['Récompense (r)', 'Nombre']
    reward_counts = reward_counts.sort_values(by='Récompense (r)')

    plt.figure(figsize=(10, 6))
    sns.barplot(data=reward_counts, x='Récompense (r)', y='Nombre', palette="viridis")
    plt.yscale('log')
    plt.title('Distribution des Récompenses (Axe Y Logarithmique) - OFFLINE')
    plt.xlabel('Valeur de la Récompense')
    plt.ylabel('Fréquence (Log)')
    
    filepath = os.path.join(OUTPUT_DIR, "1_histogramme_recompenses_offline.png")
    plt.savefig(filepath)
    print(f" -> Sauvegardé : {filepath}")
    plt.close()

def generate_actions_barchart(df_transitions):
    if 'a' not in df_transitions.columns or df_transitions.empty:
        print("Pas de données d'actions ('a'). Saut du graphique.")
        return

    print("Génération du diagramme des actions...")
    action_counts = df_transitions['a'].value_counts().sort_index()
    
    # Mappage des actions (0: Haut, 1: Bas, 2: Gauche, 3: Droite) - À adapter selon votre code
    action_map = {0: "Haut", 1: "Bas", 2: "Gauche", 3: "Droite"} 
    action_counts.index = action_counts.index.map(lambda x: action_map.get(x, f"Action {x}"))

    plt.figure(figsize=(10, 6))
    sns.barplot(x=action_counts.index, y=action_counts.values, palette="rocket")
    plt.title('Fréquence des Actions des Monstres - OFFLINE')
    plt.xlabel('Action')
    plt.ylabel('Nombre total')
    
    filepath = os.path.join(OUTPUT_DIR, "2_frequence_actions_offline.png")
    plt.savefig(filepath)
    print(f" -> Sauvegardé : {filepath}")
    plt.close()

import ast # N'oubliez pas d'ajouter ceci en haut si besoin, ou dans la fonction

def generate_q_table_heatmap():
    print(f"\nChargement du modèle Q-Table depuis {MODEL_PATH}...")
    try:
        with open(MODEL_PATH, 'rb') as f:
            q_table = pickle.load(f)
    except FileNotFoundError:
        print(f" -> ERREUR: Fichier '{MODEL_PATH}' introuvable. Avez-vous lancé l'entraînement ?")
        return

    print(f" -> Modèle chargé. {len(q_table)} états connus.")
    
    if len(q_table) == 0:
        print(" -> La Q-Table est vide. Rien à afficher.")
        return

    # Débogage : Afficher à quoi ressemble une clé
    first_key = next(iter(q_table))
    print(f" -> DEBUG : Type des clés = {type(first_key)}")
    print(f" -> DEBUG : Exemple de clé = {first_key}")

    # Préparation de la grille
    range_x = range(-10, 11)
    range_y = range(-10, 11)
    heatmap_data = pd.DataFrame(index=range_y, columns=range_x, dtype=float)
    
    points_plotted = 0

    # Au lieu de parcourir la grille, on parcourt LES DONNÉES du fichier
    for state, actions in q_table.items():
        dx, dy = None, None

        # 1. Cas idéal : C'est déjà un tuple ou une liste (ex: (-1, 0))
        if isinstance(state, (tuple, list)) and len(state) >= 2:
            dx, dy = state[0], state[1]
        
        # 2. Cas "String" : C'est devenu une chaine (ex: "[-1, 0]" ou "(-1, 0)")
        elif isinstance(state, str):
            try:
                # On essaie de convertir la chaine en structure Python
                parsed = ast.literal_eval(state)
                if isinstance(parsed, (list, tuple)) and len(parsed) >= 2:
                    dx, dy = parsed[0], parsed[1]
            except:
                pass # Échec du parsing

        # Si on a réussi à extraire des coordonnées
        if dx is not None and dy is not None:
            # On vérifie qu'on est dans les bornes du graphique (-10 à +10)
            if -10 <= dx <= 10 and -10 <= dy <= 10:
                # On prend la meilleure valeur Q pour cet état
                if actions: # Vérifie que le dico d'actions n'est pas vide
                    max_q = max(actions.values())
                    if max_q != 0: # On ignore les zéros pour la lisibilité
                        heatmap_data.loc[dy, dx] = max_q
                        points_plotted += 1

    print(f" -> {points_plotted} états affichés sur la heatmap.")

    plt.figure(figsize=(12, 10))
    sns.heatmap(heatmap_data, annot=False, cmap="viridis", cbar_kws={'label': 'Max Q-Value'})
    plt.title('Heatmap Q-Table (Offline & Robuste)')
    plt.xlabel('Distance X')
    plt.ylabel('Distance Y')
    plt.gca().invert_yaxis()
    
    filepath = os.path.join(OUTPUT_DIR, "3_heatmap_q_table_offline.png")
    plt.savefig(filepath)
    print(f" -> Sauvegardé : {filepath}")
    plt.close()

def generate_episode_duration_histogram(df_durations):
    if df_durations.empty:
        print("Pas de données de durée. Saut du graphique.")
        return

    print("Génération de l'histogramme des durées...")
    plt.figure(figsize=(10, 6))
    sns.histplot(df_durations, x="Durée (secondes)", bins=30, kde=True)
    plt.title('Distribution de la Durée des Parties - OFFLINE')
    plt.xlabel('Durée (secondes)')
    plt.ylabel('Nombre de parties')
    
    filepath = os.path.join(OUTPUT_DIR, "4_histogramme_duree_parties_offline.png")
    plt.savefig(filepath)
    print(f" -> Sauvegardé : {filepath}")
    plt.close()

def main():
    print("--- Démarrage de l'analyse en mode HORS LIGNE ---\n")
    
    # 1. Charger les données depuis les fichiers locaux
    df_transitions, df_durations = load_data_from_local_logs()

    # 2. Générer les graphiques basés sur les logs
    if not df_transitions.empty:
        generate_rewards_histogram(df_transitions)
        generate_actions_barchart(df_transitions)
    else:
        print("Aucune transition trouvée dans les logs locaux. Avez-vous joué des parties ?")

    if not df_durations.empty:
        generate_episode_duration_histogram(df_durations)

    # 3. Générer la heatmap (basée sur le fichier .pkl, donc toujours local)
    generate_q_table_heatmap()
    
    print("\n--- Analyse terminée ! ---")
    print(f"Graphiques disponibles dans : {OUTPUT_DIR}")

if __name__ == "__main__":
    main()