import time
try:
    import msvcrt  # Windows input non bloquant
except ImportError:
    msvcrt = None

from engine.map import Map
from engine.player_controller import PlayerController


def run_game():
    """Lance la boucle de jeu (affichage + saisie)"""
    game_map = Map()
    player = PlayerController(game_map)

    playing = True
    if msvcrt:
        # Boucle avec saisie continue (Windows)
        print("Contrôles: ZQSD, Quitter=X (maintenir possible)")
        while playing:
            game_map.draw((player.x, player.y))
            time.sleep(0.08)
            # for i in game_map.get_matrix():print(i)
            # import sys
            # sys.exit(0)
            game_map.tick()
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()
                if key == "x":
                    playing = False
                elif key in ("z", "q", "s", "d"):
                    player.move(key)
    else:
        # Fallback: saisie par ligne
        while playing:
            game_map.draw((player.x, player.y))
            print("Déplacez-vous avec ZQSD (X pour quitter)")
            game_map.tick()
            cmd = input("> ").lower()
            if cmd == "x":
                playing = False
            elif cmd in ("z", "q", "s", "d"):
                player.move(cmd)


