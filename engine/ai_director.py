# PFE_Roguelike/engine/ai_director.py

class AIDirector:
    def decide_monster_strategy(self, player_style: str) -> str:
        """Choisit une stratégie pour les monstres."""
        if player_style == "kiter":
            print("[AI Director] Style 'Kiter' détecté. Stratégie -> RUSHDOWN")
            return "rushdown"
        elif player_style == "brawler":
            print("[AI Director] Style 'Brawler' détecté. Stratégie -> CAUTIOUS")
            return "cautious"
        else:
            print("[AI Director] Style standard. Stratégie -> STANDARD")
            return "standard"