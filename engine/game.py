import time
import logging

try:
    import msvcrt  # Windows input non bloquant
except ImportError:
    msvcrt = None

from engine.map import Map
from entities.players import players as PlayerController
from system.game_logging import get_episode_logger
from items import Weapon, Potion
from items.category_weapon import CategoryWeapon



def run_game():
    """Lance la boucle de jeu (affichage + saisie)"""
    log = logging.getLogger("pfe_roguelike.engine")
    game_map = Map()
    player = PlayerController(name="player", pv=100, inventory=None, equiped_item=None, is_human=True, x=0.0, y=0.0,game_map=game_map) 
    log.info("Partie initialisée", extra={"extra": {"start": game_map.start, "rooms": len(game_map.rooms)}})
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
        w = player.get_equipped_weapon()
        w_stats = ""
        if w:
            w_stats = f" (DMG {getattr(w,'damage','?')}, Dur {getattr(w,'durability','?')}, Portée {getattr(w,'range','?')})"
        print(f"PV: {player.get_hp()} | Arme: {player.get_equipped_weapon_name()}{w_stats} | Inventaire: {player.get_inventory_size()} (I pour ouvrir) | Aide: H | Attaque: A")

    if msvcrt:
        # Boucle avec saisie continue (Windows)
        print("Contrôles: ZQSD, Attaque=A, Inventaire=I, Aide=H, Quitter=X (maintenir possible)")
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
                elif key == "a":
                    _player_attack(player, game_map)
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
            print("Déplacez-vous avec ZQSD | A=Attaque | I=Inventaire | H=Aide | X=Quitter")
            game_map.tick((player.x, player.y))
            cmd = input("> ").lower()
            if cmd == "x":
                playing = False
                ep.end_episode("quit", {"tick": game_map.ticks})
            elif cmd == "h":
                print("Aide: ZQSD pour bouger, I inventaire (équip/usage), X quitter.")
            elif cmd == "i":
                _open_inventory_menu(player)
            elif cmd == "a":
                _player_attack(player, game_map)
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
        # résumé d'état
        eq = player.get_equipped_weapon()
        eq_desc = "aucune"
        if eq:
            eq_desc = f"{eq.name} (DMG {getattr(eq,'damage','?')}, Dur {getattr(eq,'durability','?')})"
        print(f"Etat: PV={player.get_hp()} | Arme équipée={eq_desc}")
        inv = player.list_inventory()
        if not inv:
            print("(Inventaire vide)")
        else:
            for i, it in enumerate(inv):
                name = getattr(it, "name", str(it))
                extra = []
                if isinstance(it, Weapon):
                    dmg = getattr(it,'damage','?')
                    dur = getattr(it,'durability','?')
                    rng = getattr(it,'range','?')
                    extra.append(f"DMG {dmg}")
                    extra.append(f"Dur {dur}")
                    extra.append(f"Portée {rng}")
                    # delta si équipé
                    cur = player.get_equipped_weapon()
                    if cur and hasattr(cur,'damage') and hasattr(it,'damage'):
                        dd = it.damage - cur.damage
                        if dd != 0:
                            sign = "+" if dd>0 else ""
                            extra.append(f"ΔDMG {sign}{dd}")
                if isinstance(it, Potion):
                    cat = getattr(it,'category','?')
                    pot = getattr(it,'potency','?')
                    extra.append(f"{cat}")
                    # effet attendu sur PV si potion de soin
                    if str(cat).lower().endswith('health'):
                        extra.append(f"+PV {pot}")
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


def _player_attack(player: PlayerController, game_map: Map):
    w = player.get_equipped_weapon()
    if not w:
        print("Aucune arme équipée.")
        return
    rng = getattr(w, 'range', 1.0)
    dmg = getattr(w, 'damage', 5)
    px, py = player.x, player.y
    max_dist = int(round(float(rng)))
    # cible: monstre le plus proche dans la portée
    nearest = None
    nearest_d = 10**9
    for m in list(game_map.enemies):
        d = abs(m.x - px) + abs(m.y - py)
        if d <= max_dist and d < nearest_d:
            nearest = m
            nearest_d = d
    if nearest is None:
        # Pas de cible: si arme à distance, tirer dans la dernière direction connue
        is_ranged = getattr(w, 'category', None) == CategoryWeapon.DISTANCE
        if is_ranged:
            dx, dy = getattr(player, '_last_dir', (1, 0))
            if dx == 0 and dy == 0:
                dx, dy = (1, 0)
            sx, sy = player.x + dx, player.y + dy
            if 0 <= sx < game_map.width and 0 <= sy < game_map.height:
                game_map.projectiles.append((sx, sy, dx, dy, "player", None))
                print("Tir dans le vide pour tester l'arme.")
        else:
            print("Aucune cible à portée.")
        return
    # Animation/projectiles si arme à distance
    is_ranged = getattr(w, 'category', None) == CategoryWeapon.DISTANCE
    # projectile directionnel grossier vers la cible
    if is_ranged:
        dx = 0
        dy = 0
        if nearest.x != px:
            dx = 1 if nearest.x > px else -1
        elif nearest.y != py:
            dy = 1 if nearest.y > py else -1
        sx, sy = px + dx, py + dy
        if 0 <= sx < game_map.width and 0 <= sy < game_map.height:
            # projectiles du joueur, propriétaire "player"
            game_map.projectiles.append((sx, sy, dx, dy, "player", None))
    else:
        # flash mêlée sur la case de la cible
        try:
            game_map.add_attack_flash([(nearest.x, nearest.y)], duration_ticks=4)
        except Exception:
            pass

    # Appliquer dégâts à la cible
    try:
        before = int(nearest.get_pv())
        nearest.set_pv(max(0, before - max(1, int(dmg))))
        # flash hit sur la case de la cible
        try:
            game_map.add_hit_flash([(nearest.x, nearest.y)], duration_ticks=6)
        except Exception:
            pass
    except Exception:
        print("Erreur lors de l'application des dégâts.")
        return
    if hasattr(w, 'use'):
        try:
            w.use()
        except Exception:
            pass
    print(f"Vous frappez un monstre en ({nearest.x},{nearest.y}) pour {dmg} dégâts. PV restants: {nearest.get_pv()}")
    if not nearest.get_is_alive():
        dropped = None
        try:
            dropped = nearest.die(drop_rate=1.0)
        except Exception:
            dropped = None
        if dropped is not None:
            game_map.drop_item(nearest.x, nearest.y, dropped)
        try:
            game_map.enemies.remove(nearest)
            print(f"Monstre vaincu. Ennemis restants: {len(game_map.enemies)}")
        except ValueError:
            pass
