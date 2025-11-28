from .map import Map
from entities.monster import Monster
from .rl import QLearningAgent
from entities.players import players   # OK
import os

def train_monster_vs_bots(nb_episodes=200,
                          type_bot="Agressif",
                          max_steps=400):
    """
    Entraîne UN monstre (une seule Q-table) contre des bots existants.
    type_bot : 'Agressif', 'Fuyard' ou 'Aléatoire'
    """
    qtable_path = "qtable_monstre_vs_bots.json"

    if os.path.exists(qtable_path):
        print(f"Q-table trouvée, chargement depuis {qtable_path}...")
        shared_agent = QLearningAgent.load(qtable_path)
        # tu peux remonter un peu epsilon pour ré-explorer si tu veux
        shared_agent.epsilon = 0.4
    else:
        print("Pas de Q-table existante, création d’un nouvel agent.")
        shared_agent = QLearningAgent(epsilon=0.4, min_epsilon=0.05)

    for ep in range(nb_episodes):
        game_map = Map()

        # 3) Récupérer un seul monstre (ou en créer un si besoin)
        if game_map.enemies:
            monster = game_map.enemies[0]
        else:
            mx, my = game_map.start
            monster = Monster(weapon=None, pv=50, x=mx, y=my)
            game_map.enemies.append(monster)

        monster._ensure_rl()
        monster.rl_agent = shared_agent

        player = players(name="bot_rl",
                        is_human=False,
                        game_map=game_map
                        )


        for step in range(max_steps):
            if not player.get_is_alive():
                break

            player.train_bot(type_bot, monster)
            game_map.tick(player)

            if player.get_pv() <= 0:
                break

        print(f"Épisode {ep+1}/{nb_episodes} terminé.")

    shared_agent.save("qtable_monstre_vs_bots.json")
    print("Q-table sauvegardée dans qtable_monstre_vs_bots.json")


if __name__ == "__main__":
    train_monster_vs_bots(nb_episodes=30, type_bot="Agressif")
