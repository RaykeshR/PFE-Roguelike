import random
from collections import defaultdict
import json
from pathlib import Path
import tempfile
import os

class QLearningAgent:
    def __init__(self, actions=(0,1,2,3), alpha=0.2, gamma=0.95, epsilon=0.5,
                 min_epsilon=0.05, eps_decay=0.992) :
        self.actions = tuple(actions)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.eps_decay = eps_decay
        self.Q = defaultdict(lambda: defaultdict(float))

    def select(self, s) -> int: 
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        qs = self.Q[s]
        best_a, best_q = None, float("-inf")
        for a in self.actions:
            q = qs.get(a, 0.0)
            if q > best_q:
                best_q, best_a = q, a
        return best_a if best_a is not None else random.choice(self.actions)

    def update(self, s, a, r, s2, done) -> None:
        qsa = self.Q[s][a]
        target = r if done else r + self.gamma * max((self.Q[s2].get(a2, 0.0) for a2 in self.actions),
                                                      default=0.0)
        self.Q[s][a] = qsa + self.alpha * (target - qsa)

    def decay(self) -> None:
        self.epsilon = max(self.min_epsilon, self.epsilon * self.eps_decay)
    
    ########### ENREGISTREMENT / CHARGEMENT ###########

    def _ensure_json_target(self, target) -> Path:
        """
        Assure que le chemin cible pour le fichier JSON existe.
        Crée les répertoires parents si nécessaire.  
        Retourne un objet Path.
        """
        p = Path(target)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.touch()
        return p

    def _state_key(self, s) -> str:
        """
        Convertit un état en une clé de chaîne pour le stockage.
        """
        if isinstance(s, tuple):
            return ",".join(str(x) for x in s)
        return str(s)

    def save(self, filepath: str) -> None:
        """
        Sauvegarder la Q-table dans un fichier JSON dans .
        """
        target = self._ensure_json_target(filepath)
        data = {}
        for s, actions_dict in self.Q.items():
            sk = self._state_key(s)
            # actions_dict est un dict {action: qvalue}
            data[sk] = dict(actions_dict)
        payload = {
            "actions": list(self.actions),
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "min_epsilon": self.min_epsilon,
            "eps_decay": self.eps_decay,
            "Q": data,
        }
        #enregistrer atomiquement
        with tempfile.NamedTemporaryFile("w", delete=False, dir=target.parent, encoding="utf-8") as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_name = tmp.name

        os.replace(tmp_name, target)

    @classmethod
    def load(cls, filepath: str) -> "QLearningAgent":
        """
        Recharge un agent depuis un fichier JSON.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)

        agent = cls(
            actions=tuple(payload["actions"]),
            alpha=payload["alpha"],
            gamma=payload["gamma"],
            epsilon=payload["epsilon"],
            min_epsilon=payload["min_epsilon"],
            eps_decay=payload["eps_decay"],
        )

        # reconstruire le defaultdict
        for sk, actions_dict in payload["Q"].items():
            # re-transformer "dx,dy" → (dx, dy)
            if "," in sk:
                s = tuple(int(x) for x in sk.split(","))
            else:
                s = sk
            for a, qv in actions_dict.items():
                agent.Q[s][int(a)] = float(qv)

        return agent

