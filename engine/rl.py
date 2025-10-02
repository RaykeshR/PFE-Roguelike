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
