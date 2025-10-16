import time
import logging
from engine.player_profiler import PlayerProfiler
from engine.ai_director import AIDirector
try:
    import msvcrt  # Windows input non bloquant
except ImportError:
    msvcrt = None

from engine.map import Map
from engine.player_controller import PlayerController
from system.game_logging import get_episode_logger


def run_game():
    """Lance la boucle de jeu (affichage + saisie)"""
    log = logging.getLogger("pfe_roguelike.engine")
    game_map = Map()
    player = PlayerController(game_map)
    log.info("Partie initialisée", extra={"extra": {"start": game_map.start, "rooms": len(game_map.rooms)}})
    profiler = PlayerProfiler()
    director = AIDirector()
    current_monster_strategy = "standard"

    # Episode logger
    ep = get_episode_logger()
    ep.start_episode({
        "seed": None,  # pourra être rempli si on introduit un seed global
        "map_size": [game_map.width, game_map.height],
        "rooms": len(game_map.rooms),
        "start": game_map.start,
        "end": game_map.end,
    })

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
                    ep.end_episode("quit", {"tick": game_map.ticks})
                elif key in ("z", "q", "s", "d"):
                    profiler.log_action('move')
                    old = (player.x, player.y)
                    player.move(key)
                    if (player.x, player.y) != old:
                        log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": key}})
                        ep.log_step({
                            "tick": game_map.ticks,
                            "player": {"from": list(old), "to": [player.x, player.y]},
                            "action_player": key,
                        })
    else:
        # Fallback: saisie par ligne
        while playing:
            game_map.draw((player.x, player.y))
            print("Déplacez-vous avec ZQSD (X pour quitter)")
            game_map.tick((player.x, player.y))
            cmd = input("> ").lower()
            if cmd == "x":
                playing = False
                ep.end_episode("quit", {"tick": game_map.ticks})
            elif cmd in ("z", "q", "s", "d"):
                old = (player.x, player.y)
                player.move(cmd)
                if (player.x, player.y) != old:
                    log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": cmd}})
                    ep.log_step({
                        "tick": game_map.ticks,
                        "player": {"from": list(old), "to": [player.x, player.y]},
                        "action_player": cmd,
                    })


