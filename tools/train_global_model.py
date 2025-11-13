from engine.rl import QLearningAgent #
from pymongo import MongoClient
import pickle # Pour sauvegarder le modèle
import os

# 1. Initialiser un NOUVEL agent (le futur "Super Monstre")
agent = QLearningAgent()

# 2. Se connecter à la base de données des logs
client = MongoClient(os.getenv("MONGO_URL"))
db = client["RoguelikePFE_Analytics"]
collection_transitions = db["rl_transitions"]

# 3. Récupérer TOUTES les transitions (des millions !)
print("Chargement des transitions depuis MongoDB...")
# .find() crée un curseur, c'est efficace
transitions = list(collection_transitions.find()) 
print(f"{len(transitions)} transitions chargées.")

# 4. Définir le nombre "d'époques" (Epochs)
# Une époque = passer en revue tout le jeu de données
NB_EPOCHS = 5 

# 5. La boucle d'entraînement
for epoch in range(NB_EPOCHS):
    print(f"--- Époque {epoch + 1}/{NB_EPOCHS} ---")

    # Optionnel mais recommandé : mélanger les données
    #random.shuffle(transitions) 

    for transition in transitions:
        # Récupérer les 5 ÉLÉMENTS INDISPENSABLES
        s = transition['s']
        a = transition['a']
        r = transition['r']
        s2 = transition['s2']
        done = transition['done']

        # C'EST LA LIGNE MAGIQUE :
        # On applique la mise à jour Q-Learning, exactement
        # comme en jeu, mais sur les données historiques.
        agent.update(s, a, r, s2, done) #

print("Entraînement terminé !")

# 6. Sauvegarder la Q-Table résultante
# C'est cette Q-Table (agent.Q) qui est le "Super Monstre"
with open("models/global_q_table.pkl", "wb") as f:
    pickle.dump(dict(agent.Q), f)

print("Modèle global sauvegardé dans 'models/global_q_table.pkl'")