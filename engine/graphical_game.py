import time, os, logging, sys
import pickle
from collections import defaultdict

try:
    import msvcrt
except ImportError:
    msvcrt = None

if __name__ != "__main__":
    import pygame, getpass
    from engine.map import Map
    from entities.players import players as PlayerController
    from system.game_logging import get_episode_logger
    from items import Weapon, Potion
    from items.category_weapon import CategoryWeapon
    from engine.rl import load_q_table, save_q_table
    from pygame.locals import *
    from engine.GUI.gui import GameGUI, Button, Panel, InputBox, ScrollableList, Label
else:
    # Redirect to main.py if run directly
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")])
    exit(0)

from database.db_sql import (
    creer_utilisateur, 
    verifier_utilisateur, 
    get_joueurs_par_utilisateur_id, 
    ajouter_joueur,
    get_joueur_par_id,
    update_joueur_stats,
    sauvegarder_inventaire,
    charger_inventaire
)


def graphical_menu_principal():
    """Menu graphique principal du jeu avec connexion et sélection de personnage."""
    gui = GameGUI(
        width=1000,
        height=600,
        bg_color=(40, 40, 50),
        title="PFE-Roguelike"
    )
    
    # Variables pour stocker l'état de connexion
    gui.user_data = {
        'utilisateur_connecte': None,
        'joueur_selectionne_id': None,
        'joueurs_liste': [],
        'character_list_ref': None  # Référence à la liste scrollable pour mise à jour
    }
    
    # ========== CALLBACKS ==========
    
    def aller_connexion():
        gui.change_state("connexion")
    
    def aller_inscription():
        gui.change_state("inscription")
    
    def quitter_jeu():
        gui.quit()
    
    def tenter_connexion(username_input, password_input):
        username = username_input.get_text().strip()
        password = password_input.get_text().strip()
        
        if not username or not password:
            update_login_message("Veuillez remplir tous les champs", (255, 100, 100))
            return
        
        utilisateur = verifier_utilisateur(username, password)
        
        if utilisateur:
            # verifier_utilisateur retourne un dict {'id': ..., 'username': ...}
            gui.user_data['utilisateur_connecte'] = utilisateur
            update_login_message(f"Bienvenue, {username}!", (100, 255, 100))
            # Ne pas utiliser time.sleep dans la boucle Pygame, utiliser un timer
            charger_liste_personnages()
            gui.change_state("selection_personnage")
        else:
            update_login_message("Identifiants incorrects", (255, 100, 100))
    
    def tenter_inscription(username_input, password_input, password_confirm_input):
        username = username_input.get_text().strip()
        password = password_input.get_text().strip()
        password_confirm = password_confirm_input.get_text().strip()
        
        if not username or not password:
            update_register_message("Veuillez remplir tous les champs", (255, 100, 100))
            return
        
        if password != password_confirm:
            update_register_message("Les mots de passe ne correspondent pas", (255, 100, 100))
            return
        
        if len(password) < 4:
            update_register_message("Mot de passe trop court (min 4 caractères)", (255, 100, 100))
            return
        
        utilisateur = creer_utilisateur(username, password)
        
        if utilisateur:
            # creer_utilisateur retourne un tuple (id, username)
            gui.user_data['utilisateur_connecte'] = {
                'id': utilisateur[0],
                'username': utilisateur[1]
            }
            update_register_message(f"Compte créé! Bienvenue, {username}!", (100, 255, 100))
            # Ne pas utiliser time.sleep dans la boucle Pygame
            charger_liste_personnages()
            gui.change_state("selection_personnage")
        else:
            update_register_message("Ce nom d'utilisateur existe déjà", (255, 100, 100))
    
    def charger_liste_personnages():
        """Charge la liste des personnages de l'utilisateur connecté."""
        utilisateur = gui.user_data['utilisateur_connecte']
        if not utilisateur:
            return
        
        # Mettre à jour le label avec le nom d'utilisateur
        username_label = gui.user_data.get('username_label_ref')
        if username_label:
            username_label.set_text(f"👋 Bonjour, {utilisateur['username']} !")
        
        joueurs = get_joueurs_par_utilisateur_id(utilisateur['id'])
        gui.user_data['joueurs_liste'] = joueurs
        
        # Met à jour la liste scrollable via la référence stockée
        character_list = gui.user_data.get('character_list_ref')
        if character_list:
            if joueurs:
                items = [f"{j[1]} (Niv. {j[2]}, {j[4]} PV)" for j in joueurs]
            else:
                items = ["Aucun personnage"]
            character_list.set_items(items)
    
    def selectionner_personnage(index, item_text):
        """Callback quand un personnage est sélectionné dans la liste."""
        joueurs = gui.user_data['joueurs_liste']
        if joueurs and 0 <= index < len(joueurs):
            gui.user_data['joueur_selectionne_id'] = joueurs[index][0]
            update_character_message(f"Sélectionné: {item_text}", (100, 255, 100))
    
    def lancer_jeu():
        """Lance le jeu avec le personnage sélectionné."""
        joueur_id = gui.user_data.get('joueur_selectionne_id')
        if not joueur_id:
            update_character_message("Veuillez sélectionner un personnage", (255, 100, 100))
            return
        
        # Ferme la GUI mais garde Pygame actif
        gui.running = False
        # Stocker l'ID du joueur pour le lancer après la fermeture de la GUI
        gui.user_data['_joueur_a_lancer'] = joueur_id
    
    def creer_nouveau_personnage(name_input):
        """Crée un nouveau personnage."""
        nom_perso = name_input.get_text().strip()
        
        if not nom_perso:
            update_character_message("Le nom ne peut pas être vide", (255, 100, 100))
            return
        
        utilisateur = gui.user_data['utilisateur_connecte']
        if utilisateur:
            nouveau_joueur = ajouter_joueur(nom_perso, utilisateur['id'])
            if nouveau_joueur:
                update_character_message(f"Personnage '{nom_perso}' créé!", (100, 255, 100))
                name_input.set_text("")
                charger_liste_personnages()
            else:
                update_character_message("Erreur lors de la création", (255, 100, 100))
    
    def deconnexion():
        """Retour à l'écran d'accueil."""
        gui.user_data['utilisateur_connecte'] = None
        gui.user_data['joueur_selectionne_id'] = None
        gui.user_data['joueurs_liste'] = []
        gui.change_state("main", save_history=False)
    
    # Fonctions pour mettre à jour les messages
    def update_login_message(text, color):
        for element in gui.elements.get("connexion", []):
            if isinstance(element, Label) and hasattr(element, '_is_message'):
                element.set_text(text)
                element.color = color
    
    def update_register_message(text, color):
        for element in gui.elements.get("inscription", []):
            if isinstance(element, Label) and hasattr(element, '_is_message'):
                element.set_text(text)
                element.color = color
    
    def update_character_message(text, color):
        for element in gui.elements.get("selection_personnage", []):
            if isinstance(element, Label) and hasattr(element, '_is_message'):
                element.set_text(text)
                element.color = color
    
    # ========== CONSTRUCTION DES MENUS ==========
    
    # --- Menu Principal ---
    title_font = pygame.font.Font(None, 72)
    gui.add_element("main", Label(500, 150, "🛡️ PFE-ROGUELIKE 🛡️", title_font, (255, 255, 255), "center"))
    
    gui.add_button("main", Button(350, 280, 300, 60, "Se connecter", gui.font, 
                                  bg_color=(70, 130, 180), text_color=(255, 255, 255), 
                                  hover_color=(100, 160, 210), callback=aller_connexion))
    
    gui.add_button("main", Button(350, 360, 300, 60, "Créer un compte", gui.font,
                                  bg_color=(100, 180, 100), text_color=(255, 255, 255),
                                  hover_color=(130, 210, 130), callback=aller_inscription))
    
    gui.add_button("main", Button(350, 440, 300, 60, "Quitter", gui.font,
                                  bg_color=(180, 70, 70), text_color=(255, 255, 255),
                                  hover_color=(210, 100, 100), callback=quitter_jeu))
    
    # --- Menu Connexion ---
    panel_login = Panel(250, 120, 500, 400, bg_color=(60, 60, 70), border_color=(100, 100, 120))
    
    panel_login.add_element(Label(500, 160, "CONNEXION", gui.font, (255, 255, 255), "center"))
    
    username_input_login = InputBox(300, 220, 400, 50, gui.font, placeholder="Nom d'utilisateur")
    panel_login.add_element(username_input_login)
    
    password_input_login = InputBox(300, 290, 400, 50, gui.font, placeholder="Mot de passe", password=True)
    panel_login.add_element(password_input_login)
    
    login_message = Label(500, 360, "", pygame.font.Font(None, 24), (255, 100, 100), "center")
    login_message._is_message = True
    panel_login.add_element(login_message)
    
    gui.add_element("connexion", panel_login)
    
    gui.add_button("connexion", Button(300, 460, 180, 50, "Connexion", gui.font,
                                       bg_color=(70, 130, 180), text_color=(255, 255, 255),
                                       callback=lambda: tenter_connexion(username_input_login, password_input_login)))
    
    gui.add_button("connexion", Button(520, 460, 180, 50, "Retour", gui.font,
                                       bg_color=(120, 120, 120), text_color=(255, 255, 255),
                                       callback=gui.go_back))
    
    # --- Menu Inscription ---
    panel_register = Panel(250, 100, 500, 450, bg_color=(60, 60, 70), border_color=(100, 100, 120))
    
    panel_register.add_element(Label(500, 140, "CRÉER UN COMPTE", gui.font, (255, 255, 255), "center"))
    
    username_input_register = InputBox(300, 200, 400, 50, gui.font, placeholder="Nom d'utilisateur")
    panel_register.add_element(username_input_register)
    
    password_input_register = InputBox(300, 270, 400, 50, gui.font, placeholder="Mot de passe", password=True)
    panel_register.add_element(password_input_register)
    
    password_confirm_input = InputBox(300, 340, 400, 50, gui.font, placeholder="Confirmer mot de passe", password=True)
    panel_register.add_element(password_confirm_input)
    
    register_message = Label(500, 410, "", pygame.font.Font(None, 24), (255, 100, 100), "center")
    register_message._is_message = True
    panel_register.add_element(register_message)
    
    gui.add_element("inscription", panel_register)
    
    gui.add_button("inscription", Button(300, 500, 180, 50, "Créer", gui.font,
                                         bg_color=(100, 180, 100), text_color=(255, 255, 255),
                                         callback=lambda: tenter_inscription(username_input_register, 
                                                                            password_input_register,
                                                                            password_confirm_input)))
    
    gui.add_button("inscription", Button(520, 500, 180, 50, "Retour", gui.font,
                                         bg_color=(120, 120, 120), text_color=(255, 255, 255),
                                         callback=gui.go_back))
    
    # --- Menu Sélection Personnage ---
    panel_character = Panel(200, 80, 600, 460, bg_color=(60, 60, 70), border_color=(100, 100, 120))
    
    utilisateur_label = Label(500, 120, "Sélectionnez un personnage", gui.font, (255, 255, 255), "center")
    utilisateur_label._is_username_label = True  # Marquer pour pouvoir le mettre à jour
    panel_character.add_element(utilisateur_label)
    gui.user_data['username_label_ref'] = utilisateur_label  # Stocker la référence
    
    # Liste scrollable des personnages
    character_list = ScrollableList(240, 160, 520, 180, font=pygame.font.Font(None, 28))
    character_list.callback = selectionner_personnage
    panel_character.add_element(character_list)
    # Stocker la référence pour pouvoir la mettre à jour
    gui.user_data['character_list_ref'] = character_list
    
    panel_character.add_element(Label(500, 360, "Créer un nouveau personnage:", pygame.font.Font(None, 28), (200, 200, 200), "center"))
    
    new_character_input = InputBox(280, 390, 440, 45, gui.font, placeholder="Nom du personnage")
    panel_character.add_element(new_character_input)
    
    character_message = Label(500, 455, "", pygame.font.Font(None, 24), (255, 100, 100), "center")
    character_message._is_message = True
    panel_character.add_element(character_message)
    
    gui.add_element("selection_personnage", panel_character)
    
    gui.add_button("selection_personnage", Button(250, 500, 150, 50, "Créer", gui.font,
                                                   bg_color=(100, 180, 100), text_color=(255, 255, 255),
                                                   callback=lambda: creer_nouveau_personnage(new_character_input)))
    
    gui.add_button("selection_personnage", Button(425, 500, 150, 50, "Jouer", gui.font,
                                                   bg_color=(70, 130, 180), text_color=(255, 255, 255),
                                                   callback=lancer_jeu))
    
    gui.add_button("selection_personnage", Button(600, 500, 150, 50, "Déconnexion", gui.font,
                                                   bg_color=(180, 70, 70), text_color=(255, 255, 255),
                                                   callback=deconnexion))
    
    # ========== LANCEMENT ==========
    gui.run_menu()
    
    # Si un joueur doit être lancé, lancer le jeu après la fermeture de la GUI
    joueur_a_lancer = gui.user_data.get('_joueur_a_lancer')
    if joueur_a_lancer:
        # Ne pas quitter Pygame, on en a besoin pour le jeu
        # La fenêtre GUI sera fermée mais Pygame reste actif
        run_game(joueur_id_connecte=joueur_a_lancer)
    else:
        gui.quit()


def menu_principal():
    """Fonction wrapper pour compatibilité - utilise le menu graphique."""
    graphical_menu_principal()


def run_game(joueur_id_connecte):
    """Lance la boucle de jeu graphique avec Pygame"""
    log = logging.getLogger("pfe_roguelike.engine")
    
    # 1. Récupérer les données du joueur depuis la DB
    joueur_data_tuple = get_joueur_par_id(joueur_id_connecte)
    
    if not joueur_data_tuple:
        log.error(f"Joueur {joueur_id_connecte} non trouvé ! Lancement impossible.")
        return

    joueur_data = {
        'id': joueur_data_tuple[0],
        'nom': joueur_data_tuple[1],
        'niveau': joueur_data_tuple[2],
        'xp': joueur_data_tuple[3],
        'pv': joueur_data_tuple[4],
        'q_table_path': joueur_data_tuple[5]
    }

    # 2. Charger la Q-Table partagée du joueur
    q_table_path = joueur_data['q_table_path']
    shared_player_q_data = load_q_table(q_table_path)
    
    # --- AJOUT: Chargement du Super Cerveau ---
    global_model_path = "models/global_q_table.pkl"
    super_monster_brain = None
    
    if os.path.exists(global_model_path):
        try:
            with open(global_model_path, "rb") as f:
                global_data = pickle.load(f)
                super_monster_brain = defaultdict(lambda: defaultdict(float))
                super_monster_brain.update(global_data)
                print("[GUI] Super Monstre Brain chargé.")
        except Exception as e:
            print(f"[GUI] Erreur chargement Super Monstre: {e}")
    else:
        # Fallback vide si nécessaire
        super_monster_brain = defaultdict(lambda: defaultdict(float))

    inventaire_charge = charger_inventaire(joueur_id_connecte)

    # 3. Initialiser la Map
    game_map = Map(shared_q_data=shared_player_q_data, super_brain=super_monster_brain)  
    # [FIX] Initialize cache variables to prevent AttributeError in draw_map_pygame
    game_map._visible_cache_room = None
    game_map._visible_cache_set = None
    # [FIX] Ensure hit_flash dict exists
    if not hasattr(game_map, 'hit_flash'):
        game_map.hit_flash = {}
    
    # 4. Initialiser le PlayerController avec les données de la DB
    player = PlayerController(
        name=joueur_data['nom'], 
        pv=joueur_data['pv'],
        niveau=joueur_data['niveau'],
        xp=joueur_data['xp'], 
        inventory=inventaire_charge,
        equiped_item=None,
        is_human=True, 
        x=0.0, y=0.0,
        game_map=game_map
    ) 
    player.q_table_path = q_table_path 
    player.db_id = joueur_data['id']
    # [FIX] Initialize direction for projectiles
    player._last_dir = (1, 0)

    # Episode logger
    ep = get_episode_logger()
    ep.start_episode({
        "seed": None,
        "map_size": [game_map.width, game_map.height],
        "rooms": len(game_map.rooms),
        "start": game_map.start,
        "end": game_map.end,
    })

    # Initialiser Pygame pour le jeu
    # Si Pygame n'est pas initialisé, l'initialiser
    if not pygame.get_init():
        pygame.init()
    
    # Configuration de l'écran
    TILE_SIZE = 20
    MAP_WIDTH = game_map.width * TILE_SIZE
    MAP_HEIGHT = game_map.height * TILE_SIZE
    HUD_HEIGHT = 100
    SCREEN_WIDTH = MAP_WIDTH
    SCREEN_HEIGHT = MAP_HEIGHT + HUD_HEIGHT
    
    # Créer une nouvelle fenêtre pour le jeu (ferme l'ancienne si elle existe)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PFE-Roguelike - Jeu")
    print(f"[DEBUG] Fenêtre Pygame créée: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    hud_font = pygame.font.Font(None, 20)
    
    # Couleurs
    COLOR_WALL = (50, 50, 50)
    COLOR_FLOOR = (200, 200, 200)
    COLOR_PLAYER = (0, 255, 0)
    COLOR_ENEMY = (255, 0, 0)
    COLOR_ITEM = (255, 255, 0)
    COLOR_DOOR = (139, 69, 19)
    COLOR_START = (0, 255, 255)
    COLOR_END = (0, 100, 255) # Bleu pour l'arrivée
    COLOR_PROJECTILE_PLAYER = (0, 200, 255)
    COLOR_PROJECTILE_ENEMY = (255, 100, 0)
    COLOR_HIT = (255, 0, 0)
    COLOR_UNDISCOVERED = (30, 30, 30)
    
    # Système de messages
    game_messages = []  # Liste de messages à afficher: [(text, color, expire_tick), ...]
    message_font = pygame.font.Font(None, 18)
    
    playing = True
    
    def draw_map_pygame():
        """Dessine la carte avec Pygame"""
        # Calculer visibilité
        current_room = game_map.get_room_containing(player.x, player.y)
        if current_room is game_map._visible_cache_room and game_map._visible_cache_set:
            visible = game_map._visible_cache_set
        else:
            visible = game_map._compute_visible(current_room)
            game_map._visible_cache_room = current_room
            game_map._visible_cache_set = visible
        
        # Dessiner la carte
        for y in range(game_map.height):
            for x in range(game_map.width):
                screen_x = x * TILE_SIZE
                screen_y = y * TILE_SIZE
                
                if (x, y) in visible or (x, y) in game_map.discovered:
                    tile = game_map.tiles[y][x]
                    if tile == "#":
                        pygame.draw.rect(screen, COLOR_WALL, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif tile == "+":
                        pygame.draw.rect(screen, COLOR_DOOR, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    else:
                        pygame.draw.rect(screen, COLOR_FLOOR, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    
                    # Départ et arrivée
                    if (x, y) == game_map.start:
                        pygame.draw.rect(screen, COLOR_START, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif (x, y) == game_map.end:
                        pygame.draw.rect(screen, COLOR_END, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(screen, COLOR_UNDISCOVERED, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
        
        # Dessiner les items
        for obj in game_map.items:
            ix, iy = obj["x"], obj["y"]
            if 0 <= iy < game_map.height and 0 <= ix < game_map.width:
                if (ix, iy) in visible or (ix, iy) in game_map.discovered:
                    pygame.draw.circle(screen, COLOR_ITEM, 
                                     (ix * TILE_SIZE + TILE_SIZE // 2, iy * TILE_SIZE + TILE_SIZE // 2),
                                     TILE_SIZE // 3)
        
        # Dessiner les ennemis avec effet de brillance (shader)
        for enemy in game_map.enemies:
            ex, ey = enemy.x, enemy.y
            if 0 <= ey < game_map.height and 0 <= ex < game_map.width:
                if (ex, ey) in visible or (ex, ey) in game_map.discovered:
                    enemy_screen_x = ex * TILE_SIZE + TILE_SIZE // 2
                    enemy_screen_y = ey * TILE_SIZE + TILE_SIZE // 2
                    
                    # --- AJOUT: Vérifier si c'est un Super Monstre ---
                    is_super = getattr(enemy, 'is_super', False)
                    current_color = (255, 0, 255) if is_super else COLOR_ENEMY # Magenta pour Super, Rouge pour normal
                    radius_bonus = 4 if is_super else 0 # Plus gros

                    # Effet de brillance
                    glow_radius = TILE_SIZE // 2 + radius_bonus + int(1.5 * (game_map.ticks % 40) / 40)
                    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    # Adapter la couleur du glow
                    glow_rgb = current_color
                    glow_color = (*glow_rgb, 80) if len(glow_rgb) == 3 else glow_rgb
                    
                    pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surface, (enemy_screen_x - glow_radius, enemy_screen_y - glow_radius))
                    
                    # Dessiner le corps de l'ennemi avec la bonne couleur
                    pygame.draw.circle(screen, current_color,
                                     (enemy_screen_x, enemy_screen_y),
                                     TILE_SIZE // 2 - 2 + radius_bonus)
                    
                    # Indicateur d'arme (petit point jaune si équipé)
                    if enemy.weapon:
                        pygame.draw.circle(screen, (255, 255, 0),
                                         (enemy_screen_x + 4, enemy_screen_y - 4), 2)
        
        # Dessiner les projectiles
        for pr in game_map.projectiles:
            if len(pr) >= 4:
                px2, py2 = pr[0], pr[1]
                owner = pr[4] if len(pr) >= 5 else "enemy"
                if 0 <= py2 < game_map.height and 0 <= px2 < game_map.width:
                    if (px2, py2) in visible or (px2, py2) in game_map.discovered:
                        color = COLOR_PROJECTILE_PLAYER if owner == "player" else COLOR_PROJECTILE_ENEMY
                        pygame.draw.circle(screen, color,
                                         (px2 * TILE_SIZE + TILE_SIZE // 2, py2 * TILE_SIZE + TILE_SIZE // 2),
                                         TILE_SIZE // 4)
        
        # Effet de hit
        if getattr(game_map, 'hit_flash', None):
            for (hx, hy), expire in list(game_map.hit_flash.items()):
                if 0 <= hy < game_map.height and 0 <= hx < game_map.width:
                    if (hx, hy) in visible or (hx, hy) in game_map.discovered:
                        pygame.draw.line(screen, COLOR_HIT,
                                       (hx * TILE_SIZE, hy * TILE_SIZE),
                                       ((hx + 1) * TILE_SIZE, (hy + 1) * TILE_SIZE), 3)
                        pygame.draw.line(screen, COLOR_HIT,
                                       ((hx + 1) * TILE_SIZE, hy * TILE_SIZE),
                                       (hx * TILE_SIZE, (hy + 1) * TILE_SIZE), 3)
        
        # Dessiner le joueur avec effet de brillance (shader)
        player_x = int(player.x) * TILE_SIZE + TILE_SIZE // 2
        player_y = int(player.y) * TILE_SIZE + TILE_SIZE // 2
        # Effet de brillance animé
        glow_radius = TILE_SIZE // 2 + int(2 * (game_map.ticks % 30) / 30)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (*COLOR_PLAYER, 100) if len(COLOR_PLAYER) == 3 else COLOR_PLAYER
        pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (player_x - glow_radius, player_y - glow_radius))
        pygame.draw.circle(screen, COLOR_PLAYER, (player_x, player_y), TILE_SIZE // 2 - 1)
        # Highlight blanc pour effet de brillance
        pygame.draw.circle(screen, (255, 255, 255), (player_x - 2, player_y - 2), 3)
    
    def add_message(text, color=(255, 255, 255), duration_ticks=180):
        """Ajoute un message à afficher dans le HUD."""
        expire = game_map.ticks + duration_ticks
        game_messages.append((text, color, expire))
        # Garder seulement les 5 derniers messages
        if len(game_messages) > 5:
            game_messages.pop(0)
    
    # Stocker la fonction add_message dans le joueur pour qu'il puisse l'utiliser
    # (après la définition de add_message)
    player._add_message_callback = add_message
    
    def draw_hud():
        """Dessine le HUD avec Pygame"""
        hud_y = MAP_HEIGHT
        pygame.draw.rect(screen, (40, 40, 50), (0, hud_y, SCREEN_WIDTH, HUD_HEIGHT))
        
        w = player.get_equipped_weapon()
        w_name = player.get_equipped_weapon_name()
        w_stats = ""
        if w:
            w_stats = f"DMG:{getattr(w,'damage','?')} Dur:{getattr(w,'durability','?')} Portée:{getattr(w,'range','?')}"
        
        texts = [
            f"PV: {player.get_hp()}",
            f"Niv: {player.get_niveau()}",
            f"XP: {player.get_xp()}",
            f"Arme: {w_name}",
            w_stats if w_stats else "",
            f"Inventaire: {player.get_inventory_size()}",
            "ZQSD: Déplacer | A: Attaquer | I: Inventaire | H: Aide | X: Quitter"
        ]
        
        y_offset = hud_y + 10
        for i, text in enumerate(texts):
            if text:
                text_surf = hud_font.render(text, True, (255, 255, 255))
                screen.blit(text_surf, (10, y_offset + i * 20))
        
        # Afficher les messages (dans la partie droite du HUD)
        # Nettoyer les messages expirés
        current_tick = game_map.ticks
        game_messages[:] = [msg for msg in game_messages if msg[2] > current_tick]
        
        # Afficher les messages
        msg_x = SCREEN_WIDTH - 400
        msg_y = hud_y + 10
        for text, color, _ in game_messages[-3:]:  # Afficher les 3 derniers messages
            msg_surf = message_font.render(text, True, color)
            screen.blit(msg_surf, (msg_x, msg_y))
            msg_y += 22
    
    # Boucle principale du jeu
# <<<<<<< HEAD
#     while playing:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 playing = False
#                 ep.end_episode("quit", {"tick": game_map.ticks})
#             elif event.type == pygame.KEYDOWN:
#                 key = event.unicode.lower() if event.unicode else ""
#                 # Gérer les touches spéciales
#                 if event.key == pygame.K_x:
#                     playing = False
#                     ep.end_episode("quit", {"tick": game_map.ticks})
#                 elif event.key == pygame.K_h:
#                     _show_help_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, hud_font)
#                 elif event.key == pygame.K_i:
#                     _open_inventory_menu_pygame(screen, player, SCREEN_WIDTH, SCREEN_HEIGHT, font, hud_font)
#                 elif event.key == pygame.K_a:
#                     messages = _player_attack(player, game_map, add_message_callback=add_message)
#                     if messages:
#                         for i, msg in enumerate(messages):
#                             color = (100, 255, 100) if "vaincu" in msg or "XP" in msg else (255, 200, 100)
#                             add_message(msg, color)
#                 elif event.key == pygame.K_UP or event.key == pygame.K_w or key == "z":
#                     old = (player.x, player.y)
#                     player.move("z")
#                     if (player.x, player.y) != old:
#                         log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "z"}})
#                         ep.log_step({
#                             "tick": game_map.ticks,
#                             "player": {"from": list(old), "to": [player.x, player.y]},
#                             "action_player": "z",
#                         })
#                 elif event.key == pygame.K_LEFT or key == "q":
#                     old = (player.x, player.y)
#                     player.move("q")
#                     if (player.x, player.y) != old:
#                         log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "q"}})
#                         ep.log_step({
#                             "tick": game_map.ticks,
#                             "player": {"from": list(old), "to": [player.x, player.y]},
#                             "action_player": "q",
#                         })
#                 elif event.key == pygame.K_DOWN or event.key == pygame.K_s or key == "s":
#                     old = (player.x, player.y)
#                     player.move("s")
#                     if (player.x, player.y) != old:
#                         log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "s"}})
#                         ep.log_step({
#                             "tick": game_map.ticks,
#                             "player": {"from": list(old), "to": [player.x, player.y]},
#                             "action_player": "s",
#                         })
#                 elif event.key == pygame.K_RIGHT or event.key == pygame.K_d or key == "d":
#                     old = (player.x, player.y)
#                     player.move("d")
#                     if (player.x, player.y) != old:
#                         log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "d"}})
#                         ep.log_step({
#                             "tick": game_map.ticks,
#                             "player": {"from": list(old), "to": [player.x, player.y]},
#                             "action_player": "d",
#                         })
        
#         # Rendu
#         screen.fill((0, 0, 0))
#         draw_map_pygame()
#         draw_hud()
#         pygame.display.flip()
        
#         # Tick logique
#         game_map.tick((player.x, player.y))
        
#         clock.tick(30)  # 30 FPS
    
#     # Sauvegarde
#     print(f"\nPartie terminée. Sauvegarde de la progression de {player.name}...")
#     save_q_table(shared_player_q_data, player.q_table_path)
#     update_joueur_stats(player.db_id, player.get_hp(), player.xp, player.niveau) 
#     sauvegarder_inventaire(player.db_id, player.get_inventory())
#     print("Sauvegarde terminée. Au revoir.")
    
#     pygame.quit()
# =======
    try:
        while playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                    ep.end_episode("quit", {"tick": game_map.ticks})
                elif event.type == pygame.KEYDOWN:
                    key = event.unicode.lower() if event.unicode else ""
                    # Gérer les touches spéciales
                    if event.key == pygame.K_x:
                        playing = False
                        ep.end_episode("quit", {"tick": game_map.ticks})
                    elif event.key == pygame.K_h:
                        _show_help_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, hud_font)
                    elif event.key == pygame.K_i:
                        _open_inventory_menu_pygame(screen, player, SCREEN_WIDTH, SCREEN_HEIGHT, font, hud_font)
                    elif event.key == pygame.K_a:
                        messages = _player_attack(player, game_map, add_message_callback=add_message)
                        if messages:
                            for i, msg in enumerate(messages):
                                color = (100, 255, 100) if "vaincu" in msg or "XP" in msg else (255, 200, 100)
                                add_message(msg, color)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w or key == "z":
                        player._last_dir = (0, -1)  # [FIX] Update direction for projectile
                        old = (player.x, player.y)
                        player.move("z")
                        if (player.x, player.y) != old:
                            log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "z"}})
                            ep.log_step({
                                "tick": game_map.ticks,
                                "player": {"from": list(old), "to": [player.x, player.y]},
                                "action_player": "z",
                            })
                    elif event.key == pygame.K_LEFT or key == "q":
                        player._last_dir = (-1, 0) # [FIX] Update direction
                        old = (player.x, player.y)
                        player.move("q")
                        if (player.x, player.y) != old:
                            log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "q"}})
                            ep.log_step({
                                "tick": game_map.ticks,
                                "player": {"from": list(old), "to": [player.x, player.y]},
                                "action_player": "q",
                            })
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s or key == "s":
                        player._last_dir = (0, 1) # [FIX] Update direction
                        old = (player.x, player.y)
                        player.move("s")
                        if (player.x, player.y) != old:
                            log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "s"}})
                            ep.log_step({
                                "tick": game_map.ticks,
                                "player": {"from": list(old), "to": [player.x, player.y]},
                                "action_player": "s",
                            })
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d or key == "d":
                        player._last_dir = (1, 0) # [FIX] Update direction
                        old = (player.x, player.y)
                        player.move("d")
                        if (player.x, player.y) != old:
                            log.info("Déplacement joueur", extra={"extra": {"from": old, "to": (player.x, player.y), "input": "d"}})
                            ep.log_step({
                                "tick": game_map.ticks,
                                "player": {"from": list(old), "to": [player.x, player.y]},
                                "action_player": "d",
                            })
            
            # Rendu
            screen.fill((0, 0, 0))
            draw_map_pygame()
            draw_hud()
            pygame.display.flip()
            
            # Tick logique
            game_map.tick((player.x, player.y))
            
            clock.tick(30)  # 30 FPS
            
    finally:
        # [FIX] Always save progress, even if an error occurs
        print(f"\nSauvegarde de la progression de {player.name}...")
        save_q_table(shared_player_q_data, player.q_table_path)
        update_joueur_stats(player.db_id, player.get_hp(), player.xp, player.niveau) 
        sauvegarder_inventaire(player.db_id, player.get_inventory())
        print("Sauvegarde terminée. Au revoir.")
        pygame.quit()


def _show_help_menu(screen, screen_width, screen_height, font):
    """Affiche un menu d'aide modal."""
    # Fond semi-transparent
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Panel d'aide
    panel_width = 600
    panel_height = 400
    panel_x = (screen_width - panel_width) // 2
    panel_y = (screen_height - panel_height) // 2
    
    pygame.draw.rect(screen, (60, 60, 70), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
    pygame.draw.rect(screen, (100, 100, 120), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)
    
    # Titre
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("AIDE", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(screen_width // 2, panel_y + 40))
    screen.blit(title_text, title_rect)
    
    # Contenu
    help_texts = [
        "ZQSD ou Flèches : Déplacer",
        "A : Attaquer",
        "I : Ouvrir l'inventaire",
        "H : Afficher l'aide",
        "X : Quitter le jeu",
        "",
        "Appuyez sur une touche pour fermer"
    ]
    
    y_offset = panel_y + 100
    for text in help_texts:
        if text:
            text_surf = font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(screen_width // 2, y_offset))
            screen.blit(text_surf, text_rect)
        y_offset += 35
    
    pygame.display.flip()
    
    # Attendre qu'une touche soit pressée
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                break
            elif event.type == pygame.QUIT:
                waiting = False
                break

# <<<<<<< HEAD

# def _open_inventory_menu_pygame(screen, player: PlayerController, screen_width, screen_height, font, hud_font):
#     """Affiche le menu d'inventaire dans une fenêtre Pygame."""
#     # Fond semi-transparent
#     overlay = pygame.Surface((screen_width, screen_height))
#     overlay.set_alpha(200)
#     overlay.fill((0, 0, 0))
#     screen.blit(overlay, (0, 0))
    
#     # Panel d'inventaire
# =======
def _open_inventory_menu_pygame(screen, player: PlayerController, screen_width, screen_height, font, hud_font):
    """Affiche le menu d'inventaire dans une fenêtre Pygame avec défilement."""
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))

    panel_width = 700
    panel_height = 500
    panel_x = (screen_width - panel_width) // 2
    panel_y = (screen_height - panel_height) // 2
    
# <<<<<<< HEAD
#     pygame.draw.rect(screen, (60, 60, 70), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
#     pygame.draw.rect(screen, (100, 100, 120), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)
    
#     # Titre
#     title_font = pygame.font.Font(None, 48)
#     title_text = title_font.render("INVENTAIRE", True, (255, 255, 255))
#     title_rect = title_text.get_rect(center=(screen_width // 2, panel_y + 30))
#     screen.blit(title_text, title_rect)
    
#     # État du joueur
#     eq = player.get_equipped_weapon()
#     eq_desc = "aucune"
#     if eq:
#         eq_desc = f"{eq.name} (DMG {getattr(eq,'damage','?')}, Dur {getattr(eq,'durability','?')})"
    
#     state_text = font.render(f"PV: {player.get_hp()} | Arme équipée: {eq_desc}", True, (200, 200, 200))
#     screen.blit(state_text, (panel_x + 20, panel_y + 70))
    
#     # Liste des items
#     inv = player.list_inventory()
#     y_start = panel_y + 110
#     item_height = 30
#     max_items_visible = 10
    
#     if not inv:
#         empty_text = font.render("(Inventaire vide)", True, (150, 150, 150))
#         screen.blit(empty_text, (panel_x + 20, y_start))
#     else:
#         # Afficher les items avec scroll si nécessaire
#         start_idx = 0
#         items_to_show = inv[start_idx:start_idx + max_items_visible]
        
#         for i, it in enumerate(items_to_show):
#             y_pos = y_start + i * item_height
#             name = getattr(it, "name", str(it))
#             extra = []
            
#             if isinstance(it, Weapon):
#                 dmg = getattr(it,'damage','?')
#                 dur = getattr(it,'durability','?')
#                 rng = getattr(it,'range','?')
#                 extra.append(f"DMG {dmg}")
#                 extra.append(f"Dur {dur}")
#                 extra.append(f"Portée {rng}")
#                 cur = player.get_equipped_weapon()
#                 if cur and hasattr(cur,'damage') and hasattr(it,'damage'):
#                     dd = it.damage - cur.damage
#                     if dd != 0:
#                         sign = "+" if dd>0 else ""
#                         extra.append(f"ΔDMG {sign}{dd}")
#             elif isinstance(it, Potion):
#                 cat = getattr(it,'category','?')
#                 pot = getattr(it,'potency','?')
#                 extra.append(f"{cat}")
#                 if str(cat).lower().endswith('health'):
#                     extra.append(f"+PV {pot}")
            
#             suffix = f" ({', '.join(extra)})" if extra else ""
#             item_text = f"{i}: {name}{suffix}"
            
#             # Highlight si équipé
#             if isinstance(it, Weapon) and eq == it:
#                 highlight_rect = pygame.Rect(panel_x + 15, y_pos - 2, panel_width - 30, item_height)
#                 pygame.draw.rect(screen, (100, 150, 200), highlight_rect, border_radius=3)
            
#             text_surf = hud_font.render(item_text, True, (255, 255, 255))
#             screen.blit(text_surf, (panel_x + 20, y_pos))
    
#     # Instructions
#     instructions = [
#         "E + numéro : Équiper une arme",
#         "U + numéro : Utiliser une potion",
#         "B ou ESC : Fermer"
#     ]
    
#     y_instructions = panel_y + panel_height - 80
#     for instruction in instructions:
#         inst_text = hud_font.render(instruction, True, (180, 180, 180))
#         screen.blit(inst_text, (panel_x + 20, y_instructions))
#         y_instructions += 20
    
#     pygame.display.flip()
    
#     # Boucle d'interaction
#     waiting = True
#     input_mode = False
#     input_text = ""
#     input_type = None  # 'equip' ou 'use'
    
#     while waiting:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 waiting = False
#                 break
#             elif event.type == pygame.KEYDOWN:
#                 if input_mode:
#                     if event.key == pygame.K_RETURN:
#                         # Exécuter l'action
#                         try:
#                             idx = int(input_text)
#                             if input_type == 'equip':
#                                 if player.equip_weapon_by_index(idx):
#                                     message = "Arme équipée."
#                                 else:
#                                     message = "Échec: sélectionnez une arme valide."
#                             elif input_type == 'use':
#                                 if player.use_potion_by_index(idx):
#                                     message = "Potion utilisée."
#                                 else:
#                                     message = "Échec: sélectionnez une potion valide."
#                             else:
#                                 message = "Action inconnue."
                            
#                             # Afficher le message et fermer
#                             _show_message(screen, screen_width, screen_height, message, font)
#                             waiting = False
#                         except ValueError:
#                             _show_message(screen, screen_width, screen_height, "Format invalide", font)
#                             waiting = False
#                         input_mode = False
# =======
    # [FIX] Define y_start here so it is available in the loop below
    y_start = panel_y + 110
    
    inv = player.list_inventory()
    scroll_offset = 0
    max_items_visible = 10
    item_height = 30

    input_mode = False
    input_text = ""
    input_type = None

    def draw_inventory_panel():
        """Dessine l'ensemble du panneau d'inventaire."""
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (60, 60, 70), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)
        
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("INVENTAIRE", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width // 2, panel_y + 30))
        screen.blit(title_text, title_rect)
        
        eq = player.get_equipped_weapon()
        eq_desc = "aucune"
        if eq:
            eq_desc = f"{eq.name} (DMG {getattr(eq,'damage','?')}, Dur {getattr(eq,'durability','?')})"
        
        state_text = font.render(f"PV: {player.get_hp()} | Arme équipée: {eq_desc}", True, (200, 200, 200))
        screen.blit(state_text, (panel_x + 20, panel_y + 70))
        
        # y_start is now accessed from the parent scope
        
        if not inv:
            empty_text = font.render("(Inventaire vide)", True, (150, 150, 150))
            screen.blit(empty_text, (panel_x + 20, y_start))
        else:
            if scroll_offset > 0:
                pygame.draw.polygon(screen, (200, 200, 200), [(panel_x + panel_width - 30, y_start - 5), (panel_x + panel_width - 20, y_start - 15), (panel_x + panel_width - 40, y_start - 15)])
            
            if scroll_offset < len(inv) - max_items_visible:
                y_end = y_start + max_items_visible * item_height
                pygame.draw.polygon(screen, (200, 200, 200), [(panel_x + panel_width - 30, y_end + 5), (panel_x + panel_width - 20, y_end - 5), (panel_x + panel_width - 40, y_end - 5)])

            items_to_show = inv[scroll_offset : scroll_offset + max_items_visible]
            
            for i, it in enumerate(items_to_show):
                actual_index = scroll_offset + i
                y_pos = y_start + i * item_height
                name = getattr(it, "name", str(it))
                extra = []
                
                if isinstance(it, Weapon):
                    extra.extend([f"DMG {getattr(it, 'damage', '?')}", f"Dur {getattr(it, 'durability', '?')}", f"Portée {getattr(it, 'range', '?')}"])
                    if eq and hasattr(eq, 'damage') and hasattr(it, 'damage'):
                        dd = it.damage - eq.damage
                        if dd != 0: extra.append(f"ΔDMG {'+' if dd > 0 else ''}{dd}")
                elif isinstance(it, Potion):
                    extra.append(f"{getattr(it, 'category', '?')}")
                    if str(getattr(it, 'category', '')).lower().endswith('health'): extra.append(f"+PV {getattr(it, 'potency', '?')}")
                
                suffix = f" ({', '.join(extra)})" if extra else ""
                item_text = f"{actual_index}: {name}{suffix}"
                
                if isinstance(it, Weapon) and eq == it:
                    highlight_rect = pygame.Rect(panel_x + 15, y_pos - 2, panel_width - 30, item_height)
                    pygame.draw.rect(screen, (80, 110, 140), highlight_rect, border_radius=3)
                
                text_surf = hud_font.render(item_text, True, (255, 255, 255))
                screen.blit(text_surf, (panel_x + 20, y_pos))
        
        instructions = ["E+num: Équiper", "U+num: Utiliser", "B/ESC: Fermer", "↑/↓/Molette: Défiler"]
        y_instructions = panel_y + panel_height - 100
        for i, instruction in enumerate(instructions):
            inst_text = hud_font.render(instruction, True, (180, 180, 180))
            screen.blit(inst_text, (panel_x + 20 + (i % 2) * 250, y_instructions + (i // 2) * 25))

    waiting = True
    while waiting:
        draw_inventory_panel()

        if input_mode:
            prompt = f"{'Équiper' if input_type == 'equip' else 'Utiliser'} (numéro): {input_text}_"
            prompt_surf = font.render(prompt, True, (255, 255, 0))
            # [FIX] y_start is now defined in this scope, so this won't crash
            prompt_rect_bg = pygame.Rect(panel_x + 20, y_start + max_items_visible * item_height + 10, panel_width - 40, 40)
            pygame.draw.rect(screen, (40, 40, 50), prompt_rect_bg, border_radius=5)
            screen.blit(prompt_surf, (prompt_rect_bg.x + 10, prompt_rect_bg.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            
            elif event.type == pygame.MOUSEWHEEL:
                if len(inv) > max_items_visible:
                    if event.y > 0: scroll_offset = max(0, scroll_offset - 1)
                    elif event.y < 0: scroll_offset = min(len(inv) - max_items_visible, scroll_offset + 1)

            elif event.type == pygame.KEYDOWN:
                if input_mode:
                    if event.key == pygame.K_RETURN:
                        try:
                            # [FIX] Handle empty string
                            if not input_text.strip():
                                raise ValueError("Empty")
                            idx = int(input_text)
                            if 0 <= idx < len(inv):
                                if input_type == 'equip':
                                    if player.equip_weapon_by_index(idx): _show_message(screen, screen_width, screen_height, "Arme équipée.", font)
                                    else: _show_message(screen, screen_width, screen_height, "Échec : ce n'est pas une arme.", font)
                                elif input_type == 'use':
                                    if player.use_potion_by_index(idx): _show_message(screen, screen_width, screen_height, "Potion utilisée.", font)
                                    else: _show_message(screen, screen_width, screen_height, "Échec : ce n'est pas une potion.", font)
                                waiting = False
                            else:
                                _show_message(screen, screen_width, screen_height, "Numéro d'objet invalide.", font)
                                input_mode = False
                        except ValueError:
                            _show_message(screen, screen_width, screen_height, "Entrée invalide.", font)
                            input_mode = False
                        input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        input_mode = False
                        input_text = ""
                    elif event.unicode.isdigit():
                        input_text += event.unicode
                else:
# <<<<<<< HEAD
#                     if event.key == pygame.K_e:
#                         input_mode = True
#                         input_type = 'equip'
#                         input_text = ""
#                     elif event.key == pygame.K_u:
#                         input_mode = True
#                         input_type = 'use'
#                         input_text = ""
#                     elif event.key == pygame.K_b or event.key == pygame.K_ESCAPE:
#                         waiting = False
#                         break
        
#         # Redessiner si en mode input
#         if input_mode:
#             # Redessiner complètement l'inventaire
#             overlay = pygame.Surface((screen_width, screen_height))
#             overlay.set_alpha(200)
#             overlay.fill((0, 0, 0))
#             screen.blit(overlay, (0, 0))
            
#             pygame.draw.rect(screen, (60, 60, 70), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
#             pygame.draw.rect(screen, (100, 100, 120), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)
            
#             title_text = title_font.render("INVENTAIRE", True, (255, 255, 255))
#             title_rect = title_text.get_rect(center=(screen_width // 2, panel_y + 30))
#             screen.blit(title_text, title_rect)
            
#             state_text = font.render(f"PV: {player.get_hp()} | Arme équipée: {eq_desc}", True, (200, 200, 200))
#             screen.blit(state_text, (panel_x + 20, panel_y + 70))
            
#             # Redessiner les items
#             if inv:
#                 for i, it in enumerate(items_to_show):
#                     y_pos = y_start + i * item_height
#                     name = getattr(it, "name", str(it))
#                     extra = []
                    
#                     if isinstance(it, Weapon):
#                         dmg = getattr(it,'damage','?')
#                         dur = getattr(it,'durability','?')
#                         rng = getattr(it,'range','?')
#                         extra.append(f"DMG {dmg}")
#                         extra.append(f"Dur {dur}")
#                         extra.append(f"Portée {rng}")
#                         cur = player.get_equipped_weapon()
#                         if cur and hasattr(cur,'damage') and hasattr(it,'damage'):
#                             dd = it.damage - cur.damage
#                             if dd != 0:
#                                 sign = "+" if dd>0 else ""
#                                 extra.append(f"ΔDMG {sign}{dd}")
#                     elif isinstance(it, Potion):
#                         cat = getattr(it,'category','?')
#                         pot = getattr(it,'potency','?')
#                         extra.append(f"{cat}")
#                         if str(cat).lower().endswith('health'):
#                             extra.append(f"+PV {pot}")
                    
#                     suffix = f" ({', '.join(extra)})" if extra else ""
#                     item_text = f"{i}: {name}{suffix}"
                    
#                     if isinstance(it, Weapon) and eq == it:
#                         highlight_rect = pygame.Rect(panel_x + 15, y_pos - 2, panel_width - 30, item_height)
#                         pygame.draw.rect(screen, (100, 150, 200), highlight_rect, border_radius=3)
                    
#                     text_surf = hud_font.render(item_text, True, (255, 255, 255))
#                     screen.blit(text_surf, (panel_x + 20, y_pos))
            
#             # Afficher le prompt d'input
#             prompt = f"{'Équiper' if input_type == 'equip' else 'Utiliser'} (entrez le numéro): {input_text}_"
#             prompt_text = font.render(prompt, True, (255, 255, 0))
#             prompt_rect = pygame.Rect(panel_x + 20, panel_y + panel_height - 100, panel_width - 40, 40)
#             pygame.draw.rect(screen, (40, 40, 50), prompt_rect, border_radius=5)
#             screen.blit(prompt_text, (panel_x + 20, panel_y + panel_height - 100))
            
#             pygame.display.flip()
    
#     # Redessiner le jeu après fermeture
# =======
                    if event.key == pygame.K_UP:
                        if len(inv) > max_items_visible: scroll_offset = max(0, scroll_offset - 1)
                    elif event.key == pygame.K_DOWN:
                        if len(inv) > max_items_visible: scroll_offset = min(len(inv) - max_items_visible, scroll_offset + 1)
                    elif event.key == pygame.K_e:
                        input_mode, input_type, input_text = True, 'equip', ""
                    elif event.key == pygame.K_u:
                        input_mode, input_type, input_text = True, 'use', ""
                    elif event.key == pygame.K_b or event.key == pygame.K_ESCAPE:
                        waiting = False

    screen.fill((0, 0, 0))


def _show_message(screen, screen_width, screen_height, message, font):
    """Affiche un message temporaire."""
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    msg_text = font.render(message, True, (255, 255, 255))
    msg_rect = msg_text.get_rect(center=(screen_width // 2, screen_height // 2))
    
    bg_rect = pygame.Rect(msg_rect.x - 20, msg_rect.y - 10, msg_rect.width + 40, msg_rect.height + 20)
    pygame.draw.rect(screen, (60, 60, 70), bg_rect, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 120), bg_rect, 2, border_radius=5)
    
    screen.blit(msg_text, msg_rect)
    pygame.display.flip()
    
    # Attendre un peu
    pygame.time.wait(1000)


def _open_inventory_menu(player: PlayerController):
    while True:
        print("\n=== Inventaire ===")
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
                    if str(cat).lower().endswith('health'):
                        extra.append(f"+PV {pot}")
                suffix = f" ({', '.join(extra)})" if extra else ""
                print(f"{i}: {name}{suffix}")

        print("\nCommandes: 'e <id>' pour équiper | 'u <id>' pour utiliser | 'b' pour revenir")
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


def _player_attack(player: PlayerController, game_map: Map, add_message_callback=None):
    """Attaque un monstre. Retourne un message à afficher ou None."""
    def _is_weapon_ranged(w) -> bool:
        cat = getattr(w, 'category', None)
        if isinstance(cat, CategoryWeapon):
            return cat == CategoryWeapon.DISTANCE
        if isinstance(cat, str):
            c = cat.strip().lower()
            return c in ("distance", "ranged", "range", "bow", "arc")
        return False
    
    w = player.get_equipped_weapon()
    if not w:
        if add_message_callback:
            add_message_callback("Aucune arme équipée.", (255, 100, 100))
        return None
    
    rng = getattr(w, 'range', 1.0)
    dmg = getattr(w, 'damage', 5)
    px, py = player.x, player.y
    max_dist = int(round(float(rng)))
    
    nearest = None
    nearest_d = 10**9
    for m in list(game_map.enemies):
        d = abs(m.x - px) + abs(m.y - py)
        if d <= max_dist and d < nearest_d:
            nearest = m
            nearest_d = d
    
    if nearest is None:
        is_ranged = _is_weapon_ranged(w)
        if is_ranged:
            # [FIX] Ensure direction is not zero
            dx, dy = getattr(player, '_last_dir', (1, 0))
            if dx == 0 and dy == 0:
                dx, dy = (1, 0)
            sx, sy = player.x + dx, player.y + dy
            if 0 <= sx < game_map.width and 0 <= sy < game_map.height:
                if os.environ.get("PFE_DEBUG_PROJECTILES") == "1":
                    print(f"[DBG] Emit projectile(no target) from {(player.x, player.y)} dir={(dx,dy)} start={(sx,sy)} max_steps={max_dist}")
                game_map.projectiles.append((sx, sy, dx, dy, "player", None, 0, max_dist))
                if add_message_callback:
                    add_message_callback("Tir dans le vide.", (200, 200, 200))
        else:
            if add_message_callback:
                add_message_callback("Aucune cible à portée.", (255, 200, 100))
        return None
    
    is_ranged = _is_weapon_ranged(w)
    if is_ranged:
        dx = 0
        dy = 0
        if nearest.x != px:
            dx = 1 if nearest.x > px else -1
        elif nearest.y != py:
            dy = 1 if nearest.y > py else -1
        sx, sy = px + dx, py + dy
        if 0 <= sx < game_map.width and 0 <= sy < game_map.height:
            if os.environ.get("PFE_DEBUG_PROJECTILES") == "1":
                print(f"[DBG] Emit projectile(to target) from {(px,py)} dir={(dx,dy)} start={(sx,sy)} max_steps={max_dist}")
            game_map.projectiles.append((sx, sy, dx, dy, "player", None, 0, max_dist))
    else:
        try:
            game_map.add_attack_flash([(nearest.x, nearest.y)], duration_ticks=4)
        except Exception:
            pass

    try:
        before = int(nearest.get_pv())
        nearest.set_pv(max(0, before - max(1, int(dmg))))
        try:
            game_map.add_hit_flash([(nearest.x, nearest.y)], duration_ticks=6)
        except Exception:
            pass
    except Exception:
        if add_message_callback:
            add_message_callback("Erreur lors de l'application des dégâts.", (255, 100, 100))
        return None
    
    if hasattr(w, 'use'):
        try:
            w.use()
        except Exception:
            pass
    
    # Message d'attaque
    attack_msg = f"Attaque: {dmg} dégâts. PV monstre: {nearest.get_pv()}"
    messages = [attack_msg]
    
    if not nearest.get_is_alive():
        dropped = None
        try:
            # Probabilité de drop d'arme : 60% si le monstre a une arme
            drop_rate = 0.6 if nearest.weapon else 0.0
            dropped = nearest.die(drop_rate=drop_rate)
        except Exception:
            dropped = None
        if dropped is not None:
            game_map.drop_item(nearest.x, nearest.y, dropped)
        try:
            game_map.enemies.remove(nearest)
            player.ajouter_xp(25)
            messages.append(f"Monstre vaincu! +25 XP. Ennemis: {len(game_map.enemies)}")
        except ValueError:
            pass
    
    # Retourner les messages pour affichage
    return messages