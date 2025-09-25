from engine.map import Map
from engine.player_controller import PlayerController
import os
import time
try:
    import msvcrt  # Windows input non bloquant
except ImportError:
    msvcrt = None


def main():
    """ Lance le jeu """
    print("Bienvenue dans le jeu Roguelike !")
    # Initialisation du jeu et boucle principale ici
    # print("Tout fonctionne !")

    game_map = Map()
    player = PlayerController(game_map)

    playing = True
    if msvcrt:
        # Boucle avec saisie continue (Windows)
        print("Contrôles: ZQSD, X pour quitter (maintenir possible)")
        while playing:
            game_map.draw((player.x, player.y))
            time.sleep(0.05)
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
            print("Déplacez-vous avec ZQSD (ou X pour quitter)")
            move = input("> ").lower()
            if move == "x":
                playing = False
            else:
                player.move(move)


if __name__ == "__main__":
    main()