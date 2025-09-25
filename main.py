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
        print("Contrôles: ZQSD, Aide=H, Quitter=X (maintenir possible)")
        while playing:
            game_map.draw((player.x, player.y))
            time.sleep(0.05)
            game_map.tick()
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()
                if key == "x":
                    playing = False
                elif key == "h":
                    print("\nCommandes: ZQSD=Déplacement, X=Quitter, H=Aide")
                    time.sleep(0.7)
                elif key in ("z", "q", "s", "d"):
                    player.move(key)
    else:
        # Fallback: saisie par ligne
        while playing:
            game_map.draw((player.x, player.y))
            print("Déplacez-vous avec ZQSD (X pour quitter, H pour aide)")
            game_map.tick()
            move = input("> ").lower()
            if move == "x":
                playing = False
            elif move == "h":
                print("Commandes: ZQSD=Déplacement, X=Quitter, H=Aide")
                input("Entrée pour reprendre...")
            else:
                player.move(move)


if __name__ == "__main__":
    main()