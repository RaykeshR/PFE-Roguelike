import os
import random
import random as _r
import logging
from system.game_logging import get_episode_logger

from items import Weapon, Rarity
from entities.monster import Monster
from .room import Room


class Map:
    def __init__(self, width=60, height=26, room_count=5):
        self.width = width
        self.height = height
        self.room_count = room_count
        self.rooms = []
        self.start = (0, 0)
        self.end = None
        self.connections = {}  # {door_coord: (target_room, target_door)}
        self.walkable = set()
        self.tiles = [[" " for _ in range(self.width)] for _ in range(self.height)]
        self.discovered = set()
        self.enemies = []  # [{"x":int,"y":int,"dx":int,"dy":int}]
        self.projectiles = []  # [(x,y,dx,dy)]
        self.ticks = 0
        self._visible_cache_room = None
        self._visible_cache_set = set()
        # Couleurs: activées par défaut (désactiver avec USE_COLOR=0)
        self.use_color = os.environ.get("USE_COLOR", "1") != "0"
        self._color_map = None
        self._color_reset = ""
        if self.use_color:
            try:
                from colorama import Fore, Style, init as colorama_init
                try:
                    colorama_init()
                except Exception:
                    pass
                self._color_map = {
                    "#": Fore.WHITE,
                    ".": Fore.BLACK,
                    "+": Fore.CYAN,
                    "@": Fore.YELLOW,
                    "S": Fore.GREEN,
                    "E": Fore.MAGENTA,
                    "M": Fore.RED,
                    "*": Fore.RED,
                }
                self._color_reset = Style.RESET_ALL
            except Exception:
                # Fallback ANSI direct (sans colorama)
                ESC = "\x1b["
                self._color_map = {
                    "#": ESC + "37m",   # blanc
                    ".": ESC + "30m",   # noir (gris sombre)
                    "+": ESC + "36m",   # cyan
                    "@": ESC + "33m",   # jaune
                    "S": ESC + "32m",   # vert
                    "E": ESC + "35m",   # magenta
                    "M": ESC + "31m",   # rouge
                    "*": ESC + "31m",   # rouge
                }
                self._color_reset = "\x1b[0m"

        self.generate()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate(self):
        """Génère plusieurs salles aléatoires avec portes et couloirs."""
        log = logging.getLogger("pfe_roguelike.engine.map")
        self.rooms = []
        self.connections = {}
        self.walkable = set()
        self.tiles = [[" " for _ in range(self.width)] for _ in range(self.height)]
        self.discovered = set()
        self.enemies = []
        self.projectiles = []
        self.ticks = 0
        self._visible_cache_room = None
        self._visible_cache_set = set()
        attempts = 0

        while len(self.rooms) < self.room_count and attempts < 300:
            w = random.randint(8, 15)
            h = random.randint(5, 10)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            new_room = Room(x, y, w, h)

            # Vérifier chevauchement avec marge (buffer) pour éviter salles collées
            margin = 2
            overlap = any(
                (x - margin) < (r.x + r.width) and (x + w + margin) > r.x and
                (y - margin) < (r.y + r.height) and (y + h + margin) > r.y
                for r in self.rooms
            )
            if not overlap:
                # On n'ajoute pas de portes aléatoires ici; elles seront posées selon les connexions
                self.rooms.append(new_room)
            attempts += 1

        # Gérer cas limites
        if len(self.rooms) == 0:
            # Créer une salle par défaut au centre
            w, h = 10, 6
            x = max(1, self.width // 2 - w // 2)
            y = max(1, self.height // 2 - h // 2)
            default_room = Room(x, y, w, h)
            # au moins une porte
            default_room.doors.append((x + w // 2, y))
            self.rooms.append(default_room)

        # Connecter les salles en chaîne avec des portes orientées vers la salle voisine
        if len(self.rooms) >= 2:
            for i, room in enumerate(self.rooms[:-1]):
                room_next = self.rooms[i + 1]
                door1 = self._pick_unique_door(room, room_next)
                if door1 not in room.doors:
                    room.doors.append(door1)
                door2 = self._pick_unique_door(room_next, room)
                if door2 not in room_next.doors:
                    room_next.doors.append(door2)
                self.connections[door1] = (room_next, door2)
                self.connections[door2] = (room, door1)

        # Définir positions de départ/fin
        self.start = self.rooms[0].get_random_position()
        if len(self.rooms) >= 2:
            self.end = self.rooms[-1].get_random_position()
        else:
            # Même salle: position fin distincte
            end = self.start
            tries = 0
            while end == self.start and tries < 10:
                end = self.rooms[0].get_random_position()
                tries += 1
            self.end = end

        # Dessiner les salles dans tiles et renseigner walkable
        for room in self.rooms:
            for j in range(room.height):
                for i in range(room.width):
                    gx, gy = room.x + i, room.y + j
                    if 0 <= gx < self.width and 0 <= gy < self.height:
                        if i == 0 or i == room.width - 1 or j == 0 or j == room.height - 1:
                            self.tiles[gy][gx] = "#"
                        else:
                            self.tiles[gy][gx] = "."
                            self.walkable.add((gx, gy))
            # portes
            for door in room.doors:
                dx, dy = door
                if 0 <= dx < self.width and 0 <= dy < self.height:
                    self.tiles[dy][dx] = "+"
                    self.walkable.add((dx, dy))

        # Creuser les couloirs APRES avoir dessiné les salles pour éviter de traverser des murs futurs
        for door_start, (target_room, door_end) in self.connections.items():
            self.create_corridor(door_start, door_end)

        # Placer quelques ennemis immobiles
        self._place_enemies(count=min(3, max(1, len(self.rooms)//2)))
        log.info(
            "Carte générée",
            extra={
                "extra": {
                    "rooms": len(self.rooms),
                    "connections": len(self.connections),
                    "start": self.start,
                    "end": self.end,
                    "enemies": len(self.enemies),
                }
            },
        )

    def draw(self, player_pos):
        self.clear_screen()
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        # Calculer visibilité: salle courante + salles adjacentes via portes
        current_room = self.get_room_containing(*player_pos)
        if current_room is self._visible_cache_room and self._visible_cache_set:
            visible = self._visible_cache_set
        else:
            visible = self._compute_visible(current_room)
            self._visible_cache_room = current_room
            self._visible_cache_set = visible

        # Rendu masqué: on affiche tiles seulement si découvert/visible
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in visible or (x, y) in self.discovered:
                    grid[y][x] = self.tiles[y][x]

        # Les couloirs sont déjà peints dans tiles; rien à faire ici

        px, py = player_pos
        if 0 <= py < self.height and 0 <= px < self.width:
            grid[py][px] = "@"

        # Marquer départ et arrivée si visibles
        sx, sy = self.start
        ex, ey = self.end
        if 0 <= sy < self.height and 0 <= sx < self.width and ((sx, sy) in visible or (sx, sy) in self.discovered):
            grid[sy][sx] = "S"
        if 0 <= ey < self.height and 0 <= ex < self.width and ((ex, ey) in visible or (ex, ey) in self.discovered):
            grid[ey][ex] = "E"

        # Superposer ennemis et projectiles sur le rendu
        for enemy in self.enemies:
            ex, ey = enemy.x, enemy.y
            if 0 <= ey < self.height and 0 <= ex < self.width:
                if (ex, ey) in visible or (ex, ey) in self.discovered:
                    grid[ey][ex] = "M"
        for px2, py2, _, _ in self.projectiles:
            if 0 <= py2 < self.height and 0 <= px2 < self.width:
                if (px2, py2) in visible or (px2, py2) in self.discovered:
                    grid[py2][px2] = "*"

        # Couleurs ANSI (optionnelles)
        if self._color_map:
            for row in grid:
                out = []
                for c in row:
                    prefix = self._color_map.get(c)
                    if prefix:
                        out.append(prefix)
                        out.append(c)
                        out.append(self._color_reset)
                    else:
                        out.append(c)
                print("".join(out))
        else:
            for row in grid:
                print("".join(row))
        print("\nLégende: @=Joueur, #=Mur, +=Porte, S=Départ, E=Arrivée")

    def create_corridor(self, start, end, grid=None):
        x1, y1 = start
        x2, y2 = end

        # Déterminer les salles des portes (mur sur lequel se trouve la porte)
        room1 = self.get_room_containing(x1, y1)
        room2 = self.get_room_containing(x2, y2)

        def step_outside_from_door(dx, dy, rx, ry, rw, rh):
            # Porte sur le mur gauche
            if dx == rx:
                return (dx - 1, dy)
            # Porte sur le mur droit
            if dx == rx + rw - 1:
                return (dx + 1, dy)
            # Porte sur le mur haut
            if dy == ry:
                return (dx, dy - 1)
            # Porte sur le mur bas
            if dy == ry + rh - 1:
                return (dx, dy + 1)
            # Fallback (au cas où): ne bouge pas
            return (dx, dy)

        # Calculer les points juste à l'extérieur des deux portes
        if room1:
            sx, sy = step_outside_from_door(x1, y1, room1.x, room1.y, room1.width, room1.height)
        else:
            sx, sy = x1, y1
        if room2:
            ex, ey = step_outside_from_door(x2, y2, room2.x, room2.y, room2.width, room2.height)
        else:
            ex, ey = x2, y2

        # Clamp dans la carte
        sx = max(0, min(self.width - 1, sx))
        sy = max(0, min(self.height - 1, sy))
        ex = max(0, min(self.width - 1, ex))
        ey = max(0, min(self.height - 1, ey))

        # Chercher un chemin dans l'espace libre uniquement (' ') ou via des portes ('+') pour éviter de traverser les salles ('.')
        def neighbors(x, y):
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield nx, ny

        def passable(x, y):
            cell = self.tiles[y][x]
            return cell == ' ' or cell == '+'

        from collections import deque
        def bfs_path(start_xy, end_xy):
            sx0, sy0 = start_xy
            ex0, ey0 = end_xy
            queue = deque([(sx0, sy0)])
            came = { (sx0, sy0): None }
            while queue:
                cx, cy = queue.popleft()
                if (cx, cy) == (ex0, ey0):
                    # reconstruit
                    path = []
                    cur = (cx, cy)
                    while cur is not None:
                        path.append(cur)
                        cur = came[cur]
                    path.reverse()
                    return path
                for nx, ny in neighbors(cx, cy):
                    if (nx, ny) not in came and passable(nx, ny):
                        came[(nx, ny)] = (cx, cy)
                        queue.append((nx, ny))
            return None

        path = bfs_path((sx, sy), (ex, ey))

        def carve(x, y):
            # Creuser seulement dans l'espace vide; ne jamais remplacer un sol de salle '.'
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.tiles[y][x] == ' ':
                    self.tiles[y][x] = '.'
                    self.walkable.add((x, y))
                elif self.tiles[y][x] == '+':
                    self.walkable.add((x, y))

        if path:
            for (cx, cy) in path:
                if (cx, cy) not in (start, end):
                    carve(cx, cy)
        else:
            # Fallback: couloir en L mais en ne creusant que dans l'espace vide
            for x in range(min(sx, ex), max(sx, ex) + 1):
                if (x, sy) not in (start, end):
                    carve(x, sy)
            for y in range(min(sy, ey), max(sy, ey) + 1):
                if (ex, y) not in (start, end):
                    carve(ex, y)

    def get_room_containing(self, x, y):
        for room in self.rooms:
            if room.contains(x, y):
                return room
        return None

    def get_connected_room(self, door_coord):
        return self.connections.get(door_coord, None)

    def is_walkable(self, x, y):
        return (x, y) in self.walkable

    def get_matrix(self):
        """Retourne la matrice (liste de listes) représentant la carte.

        Chaque case correspond au caractère stocké dans `tiles`.
        """
        return self.tiles

    def reveal_from(self, player_pos):
        # Révéler salle courante, portes et couloirs adjacents, salles connectées
        room = self.get_room_containing(*player_pos)
        if room:
            for j in range(room.height):
                for i in range(room.width):
                    self.discovered.add((room.x + i, room.y + j))
        # Révéler couloirs et salles reliées accessibles directement
        for door, (target_room, target_door) in self.connections.items():
            if room and room.contains(*door):
                x1, y1 = door
                x2, y2 = target_door
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self.discovered.add((x, y1))
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self.discovered.add((x2, y))
                for j in range(target_room.height):
                    for i in range(target_room.width):
                        self.discovered.add((target_room.x + i, target_room.y + j))

    def _place_enemies(self, count=2):
        placed = 0
        tries = 0
        flat_walkable = list(self.walkable)
        while placed < count and tries < 200 and flat_walkable:
            x, y = _r.choice(flat_walkable)
            if (x, y) != self.start and (x, y) != self.end and self.tiles[y][x] == ".":
                dx, dy = _r.choice([(1,0),(-1,0),(0,1),(0,-1)])
                # arme optionnelle ; tu peux mettre None
                weapon = None
                m = Monster(weapon=weapon, pv=50, x=x, y=y, dx=dx, dy=dy, speed=0.33)
                self.enemies.append(m)
                placed += 1
            tries += 1

    def tick(self, player_pos=None):
        # if self.enemies:
        #     print("Type des ennemis :", type(self.enemies[0]))
        self.ticks += 1
        if self.ticks % 10 == 0:
            for e in self.enemies:
                self.projectiles.append((e.x, e.y, e.dx, e.dy))
        # log positions projectiles
        if self.projectiles:
            ep = get_episode_logger()
            ep.log_step({
                "tick": self.ticks,
                "projectiles": [ [px, py, dx, dy] for (px, py, dx, dy) in self.projectiles ]
            })

        new_projectiles = []
        for (px, py, dx, dy) in self.projectiles:
            nx, ny = px + dx, py + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.tiles[ny][nx] != "#":
                new_projectiles.append((nx, ny, dx, dy))
        self.projectiles = new_projectiles

        # -------- [RL] déplacement + update Q-learning ----------
        if player_pos is not None:
            for m in list(self.enemies):
                m._move_acc += m.speed
                while m._move_acc >= 1.0:
                    reached = m.rl_step(self, player_pos)
                    m._move_acc -= 1.0
                    if reached:
                        # TODO: gérer l'attaque/dégâts au joueur
                        break
        # -------------------------------------------------------


    def _compute_visible(self, current_room):
        visible = set()
        if not current_room:
            return visible
        rooms_visible = {current_room}
        for j in range(current_room.height):
            for i in range(current_room.width):
                visible.add((current_room.x + i, current_room.y + j))
        for door, link in self.connections.items():
            if current_room.contains(*door):
                target_room, target_door = link
                rooms_visible.add(target_room)
                x1, y1 = door
                x2, y2 = target_door
                visible.add((x1, y1))
                visible.add((x2, y2))
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    visible.add((x, y1))
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    visible.add((x2, y))
        for room in list(rooms_visible):
            for j in range(room.height):
                for i in range(room.width):
                    visible.add((room.x + i, room.y + j))
        return visible

    def _pick_door_towards(self, room_from, room_to):
        # Choisir un point sur le mur de room_from le plus proche du centre de room_to
        cx_to = room_to.x + room_to.width // 2
        cy_to = room_to.y + room_to.height // 2
        # Distances aux murs
        left = (room_from.x, min(max(cy_to, room_from.y + 1), room_from.y + room_from.height - 2))
        right = (room_from.x + room_from.width - 1, min(max(cy_to, room_from.y + 1), room_from.y + room_from.height - 2))
        top = (min(max(cx_to, room_from.x + 1), room_from.x + room_from.width - 2), room_from.y)
        bottom = (min(max(cx_to, room_from.x + 1), room_from.x + room_from.width - 2), room_from.y + room_from.height - 1)
        candidates = [left, right, top, bottom]
        # Choisir le plus proche du centre cible
        def dist2(p):
            return (p[0] - cx_to) * (p[0] - cx_to) + (p[1] - cy_to) * (p[1] - cy_to)
        candidates.sort(key=dist2)
        return candidates[0]

    def _pick_unique_door(self, room_from, room_to):
        """Comme _pick_door_towards mais évite de réutiliser une porte déjà posée sur room_from."""
        cx_to = room_to.x + room_to.width // 2
        cy_to = room_to.y + room_to.height // 2
        left = (room_from.x, min(max(cy_to, room_from.y + 1), room_from.y + room_from.height - 2))
        right = (room_from.x + room_from.width - 1, min(max(cy_to, room_from.y + 1), room_from.y + room_from.height - 2))
        top = (min(max(cx_to, room_from.x + 1), room_from.x + room_from.width - 2), room_from.y)
        bottom = (min(max(cx_to, room_from.x + 1), room_from.x + room_from.width - 2), room_from.y + room_from.height - 1)
        candidates = [left, right, top, bottom]
        def dist2(p):
            return (p[0] - cx_to) * (p[0] - cx_to) + (p[1] - cy_to) * (p[1] - cy_to)
        candidates.sort(key=dist2)
        for c in candidates:
            if c not in room_from.doors:
                return c
        # Si toutes prises, reprendre le meilleur (on n'ajoute pas de doublon plus tard)
        return candidates[0]