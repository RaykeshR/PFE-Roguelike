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
from items import Weapon, Potion


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
    def print_hud():
        print(f"PV: {player.get_hp()} | Arme: {player.get_equipped_weapon_name()} | Inventaire: {player.get_inventory_size()} (I pour ouvrir) | Aide: H")

    if msvcrt:
        # Boucle avec saisie continue (Windows)
        print("Contrôles: ZQSD, Inventaire=I, Aide=H, Quitter=X (maintenir possible)")
        while playing:
            game_map.draw((player.x, player.y))
            print_hud()
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
                elif key == "h":
                    print("Aide: ZQSD pour bouger, I inventaire (équip/usage), X quitter.")
                    time.sleep(0.6)
                elif key == "i":
                    _open_inventory_menu(player)
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
            print_hud()
            print("Déplacez-vous avec ZQSD | I=Inventaire | H=Aide | X=Quitter")
            game_map.tick((player.x, player.y))
            cmd = input("> ").lower()
            if cmd == "x":
                playing = False
                ep.end_episode("quit", {"tick": game_map.ticks})
            elif cmd == "h":
                print("Aide: ZQSD pour bouger, I inventaire (équip/usage), X quitter.")
            elif cmd == "i":
                _open_inventory_menu(player)
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



def _open_inventory_menu(player: PlayerController):
    while True:
        print("\n=== Inventaire ===")
        inv = player.list_inventory()
        if not inv:
            print("(Inventaire vide)")
        else:
            for i, it in enumerate(inv):
                name = getattr(it, "name", str(it))
                extra = []
                if isinstance(it, Weapon):
                    extra.append(f"DMG {getattr(it,'damage', '?')}")
                    extra.append(f"Dur {getattr(it,'durability','?')}")
                if isinstance(it, Potion):
                    extra.append(f"{getattr(it,'category','?')}")
                    extra.append(f"+{getattr(it,'potency','?')}")
                suffix = f" ({', '.join(extra)})" if extra else ""
                print(f"{i}: {name}{suffix}")

        print("\nCommandes: 'e <id>' pour équiper une arme | 'u <id>' pour utiliser une potion | 'b' pour revenir")
        choice = input("inv> ").strip().lower()
        if choice == "b" or choice == "":
            break
        if choice.startswith("e "):
            try:
                idx = int(choice.split()[1])
                if player.equip_weapon_by_index(idx):
                    print("Arme équipée.")
                else:
                    print("Échec: sélectionnez une arme valide.")
            except Exception:
                print("Format: e <id>")
        elif choice.startswith("u "):
            try:
                idx = int(choice.split()[1])
                if player.use_potion_by_index(idx):
                    print("Potion utilisée.")
                else:
                    print("Échec: sélectionnez une potion valide.")
            except Exception:
                print("Format: u <id>")
        else:
            print("Commande inconnue.")

