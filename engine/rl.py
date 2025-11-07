import random
from collections import defaultdict

class QLearningAgent:
    def __init__(self, actions=(0,1,2,3), alpha=0.2, gamma=0.95, epsilon=0.5,
                 min_epsilon=0.05, eps_decay=0.992):
        self.actions = tuple(actions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.eps_decay = eps_decay
        self.Q = defaultdict(lambda: defaultdict(float))

    def select(self, s):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        qs = self.Q[s]
        best_a, best_q = None, float("-inf")
        for a in self.actions:
            q = qs.get(a, 0.0)
            if q > best_q:
                best_q, best_a = q, a
        return best_a if best_a is not None else random.choice(self.actions)

    def update(self, s, a, r, s2, done):
        qsa = self.Q[s][a]
        target = r if done else r + self.gamma * max((self.Q[s2].get(a2, 0.0) for a2 in self.actions), default=0.0)
        self.Q[s][a] = qsa + self.alpha * (target - qsa)

    def decay(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.eps_decay)




import pickle
import os
from collections import defaultdict


def save_q_table(q_data, path):
    """Sauvegarde les données de la Q-table (un dictionnaire) dans un fichier pickle."""
    try:
        # S'assurer que le dossier existe
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Sauvegarder les données Q
        with open(path, 'wb') as f:
            pickle.dump(dict(q_data), f) # On sauvegarde un dict normal
        print(f"Q-Table sauvegardée à : {path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la Q-Table à {path}: {e}")

def load_q_table(path):
    """Charge une Q-table depuis un fichier pickle.
    Retourne un defaultdict vide si le fichier n'existe pas.
    """
    if not os.path.exists(path):
        print(f"Aucune Q-Table trouvée à {path}. Création d'une nouvelle table.")
        # Retourne une nouvelle Q-table vide
        return defaultdict(lambda: defaultdict(float))
        
    try:
        with open(path, 'rb') as f:
            q_data_dict = pickle.load(f)
            # Reconvertir en defaultdict pour l'agent
            q_data = defaultdict(lambda: defaultdict(float))
            q_data.update(q_data_dict)
            print(f"Q-Table chargée depuis : {path}")
            return q_data
    except Exception as e:
        print(f"Erreur lors du chargement de la Q-Table de {path}: {e}. Utilisation d'une table vide.")
        return defaultdict(lambda: defaultdict(float))