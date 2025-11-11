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


import getpass
from database.db_sql import (
    creer_utilisateur, 
    verifier_utilisateur, 
    get_joueurs_par_utilisateur_id, 
    ajouter_joueur,
    get_joueur_par_id,
    update_joueur_stats
)
from engine.rl import load_q_table, save_q_table

def menu_principal():
    """Gère le menu de connexion et de sélection de personnage."""
    print("=== 🛡️  Bienvenue dans PFE-Roguelike 🛡️  ===")
    
    utilisateur_connecte = None
    while not utilisateur_connecte:
        choix = input("1: Se connecter\n2: Créer un compte\nChoix: ").strip()
        
        if choix == "1":
            username = input("Nom d'utilisateur: ").strip()
            mdp = getpass.getpass("Mot de passe: ").strip()
            utilisateur_connecte = verifier_utilisateur(username, mdp)
        
        elif choix == "2":
            username = input("Nouveau nom d'utilisateur: ").strip()
            mdp = getpass.getpass("Nouveau mot de passe: ").strip()
            utilisateur_connecte = creer_utilisateur(username, mdp)
            if utilisateur_connecte:
                print(f"Compte '{username}' créé avec succès.")
                # 'creer_utilisateur' retourne (id, username)
                utilisateur_connecte = {'id': utilisateur_connecte[0], 'username': utilisateur_connecte[1]}

    # --- Étape 2: Sélection du Personnage ---
    
    print(f"\n👋 Bonjour, {utilisateur_connecte['username']}!")
    
    joueur_selectionne_id = None
    while not joueur_selectionne_id:
        joueurs_existants = get_joueurs_par_utilisateur_id(utilisateur_connecte['id'])
        
        print("\n--- Vos Personnages ---")
        if not joueurs_existants:
            print("(Aucun personnage trouvé)")
        else:
            for i, joueur in enumerate(joueurs_existants):
                # (id, nom, niveau, xp, pv, q_table_path)
                print(f"  {i+1}: {joueur[1]} (Niv. {joueur[2]}, {joueur[4]} PV)")
        
        print("\nN: Nouveau personnage")
        print("Q: Quitter")
        choix = input("Votre choix: ").strip().lower()

        if choix == "q":
            return # Quitte le programme
        
        if choix == "n":
            nom_perso = input("Nom du nouveau personnage: ").strip()
            if nom_perso:
                # 'ajouter_joueur' retourne le tuple du nouveau joueur
                nouveau_joueur = ajouter_joueur(nom_perso, utilisateur_connecte['id'])
                joueur_selectionne_id = nouveau_joueur[0] # L'ID est le premier élément
            else:
                print("Le nom ne peut pas être vide.")
        
        else:
            try:
                # Convertir le choix (ex: '1') en index de liste (ex: 0)
                index = int(choix) - 1
                if 0 <= index < len(joueurs_existants):
                    joueur_selectionne_id = joueurs_existants[index][0] # On prend l'ID
                else:
                    print("Choix invalide.")
            except ValueError:
                print("Choix invalide.")
                
    # --- Étape 3: Lancer le jeu ---
    print(f"Chargement du personnage ID: {joueur_selectionne_id}...")
    # On passe l'ID à la fonction run_game
    run_game(joueur_id_connecte=joueur_selectionne_id)




def run_game(joueur_id_connecte):
    """Lance la boucle de jeu (affichage + saisie)"""
    log = logging.getLogger("pfe_roguelike.engine")
    game_map = Map()
    player = PlayerController(name="player", pv=100, inventory=None, equiped_item=None, is_human=True, x=0.0, y=0.0,game_map=game_map) 
    log.info("Partie initialisée", extra={"extra": {"start": game_map.start, "rooms": len(game_map.rooms)}})
    


    # 1. Récupérer les données du joueur depuis la DB
    # (id, nom, niveau, xp, pv, q_table_path)
    joueur_data_tuple = get_joueur_par_id(joueur_id_connecte)
    
    if not joueur_data_tuple:
        log.error(f"Joueur {joueur_id_connecte} non trouvé ! Lancement impossible.")
        return

    # Pour que ce soit plus simple à lire, on peut en faire un dict
    joueur_data = {
        'id': joueur_data_tuple[0],
        'nom': joueur_data_tuple[1],
        'niveau': joueur_data_tuple[2],
        'xp': joueur_data_tuple[3],
        'pv': joueur_data_tuple[4],
        'q_table_path': joueur_data_tuple[5]
    }

    # 2. Charger la Q-Table *partagée* du joueur
    q_table_path = joueur_data['q_table_path']
    shared_player_q_data = load_q_table(q_table_path)
    
    # 3. Initialiser la Map EN LUI PASSANT la Q-Table partagée
    game_map = Map(shared_q_data=shared_player_q_data) 
    
    # 4. Initialiser le PlayerController avec les données de la DB
    player = PlayerController(
        name=joueur_data['nom'], 
        pv=joueur_data['pv'],
        niveau=joueur_data['niveau'],
        xp=joueur_data['xp'], 
        inventory=None, # (Tu devras aussi charger ça de la DB plus tard)
        equiped_item=None, # (Idem)
        is_human=True, 
        x=0.0, y=0.0,
        game_map=game_map
    ) 
    player.q_table_path = q_table_path 
    player.db_id = joueur_data['id'] # Garde l'ID pour la sauvegarde



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
                    #profiler.log_action('move')
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
    
    print(f"\nPartie terminée. Sauvegarde de la progression de {player.name}...")
    
    # 1. Sauvegarder la Q-Table
    save_q_table(shared_player_q_data, player.q_table_path)
    
    # 2. Sauvegarder l'état du joueur (PV, XP, etc.)
    update_joueur_stats(player.db_id, player.get_hp(), player.xp, player.niveau) 
    print("Sauvegarde terminée. Au revoir.")



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
            player.ajouter_xp(25)
        except ValueError:
            pass
