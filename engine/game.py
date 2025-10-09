import time
import logging
try:
    import msvcrt  # Windows input non bloquant
except ImportError:
    msvcrt = None

from engine.map import Map
from engine.player_controller import PlayerController


def run_game():
    """Lance la boucle de jeu (affichage + saisie)"""
    log = logging.getLogger("pfe_roguelike.engine")
    game_map = Map()
    player = PlayerController(game_map)
    log.info("Partie initialisée", extra={"extra": {"start": game_map.start, "rooms": len(game_map.rooms)}})

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
            game_map.tick((player.x, player.y))
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()
                if key == "x":
                    playing = False
                elif key in ("z", "q", "s", "d"):
                    old = (player.x, player.y)
                    player.move(key)
                    if (player.x, player.y) != old:
                        log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": key}})
    else:
        # Fallback: saisie par ligne
        while playing:
            game_map.draw((player.x, player.y))
            print("Déplacez-vous avec ZQSD (X pour quitter)")
            game_map.tick((player.x, player.y))
            cmd = input("> ").lower()
            if cmd == "x":
                playing = False
            elif cmd in ("z", "q", "s", "d"):
                old = (player.x, player.y)
                player.move(cmd)
                if (player.x, player.y) != old:
                    log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": cmd}})


