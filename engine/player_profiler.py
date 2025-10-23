# PFE_Roguelike/engine/player_profiler.py

class PlayerProfiler:
    def __init__(self):
        self.recent_actions = []
        self.max_actions = 50  # Analyser les 50 dernières actions

    def log_action(self, action_type: str, distance_to_monster: float = -1.0):
        """Enregistre une action du joueur."""
        self.recent_actions.append({
            "type": action_type, # 'move', 'attack'
            "distance": distance_to_monster
        })
        if len(self.recent_actions) > self.max_actions:
            self.recent_actions.pop(0)

    def get_player_style(self) -> str:
        """Analyse les actions récentes pour déterminer un style de jeu."""
        if not self.recent_actions:
            return "standard"

        attacks = [a for a in self.recent_actions if a['type'] == 'attack' and a['distance'] != -1]
        moves = [a for a in self.recent_actions if a['type'] == 'move']

        if not attacks:
            return "passive"

        avg_distance = sum(a['distance'] for a in attacks) / len(attacks)
        move_ratio = len(moves) / len(self.recent_actions)

        if avg_distance > 3.5 and move_ratio > 0.6:
            return "kiter"
        elif avg_distance <= 2.0:
            return "brawler"
        else:
            return "standard"