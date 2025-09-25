import os
import random
from engine.room import Room

class Map:
    def __init__(self, width=50, height=20, room_count=4):
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

        while len(self.rooms) < self.room_count and attempts < 100:
            w = random.randint(8, 15)
            h = random.randint(5, 10)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            new_room = Room(x, y, w, h)

            # Vérifier chevauchement
            overlap = any(
                x < r.x + r.width and x + w > r.x and
                y < r.y + r.height and y + h > r.y
                for r in self.rooms
            )
            if not overlap:
                # Ajouter portes sur les murs (1 à 2 portes)
                door_count = random.randint(1, 2)
                added = set()
                for _ in range(door_count):
                    # Choisir un mur: 0=haut,1=bas,2=gauche,3=droite
                    side = random.randint(0, 3)
                    if side == 0:  # haut
                        dx = random.randint(1, w - 2)
                        dy = 0
                    elif side == 1:  # bas
                        dx = random.randint(1, w - 2)
                        dy = h - 1
                    elif side == 2:  # gauche
                        dx = 0
                        dy = random.randint(1, h - 2)
                    else:  # droite
                        dx = w - 1
                        dy = random.randint(1, h - 2)

                    door = (x + dx, y + dy)
                    if door not in added:
                        new_room.doors.append(door)
                        added.add(door)
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

        # Connecter les portes avec un graphe linéaire (chaîne) puis peindre les couloirs dans tiles
        if len(self.rooms) >= 2:
            for i, room in enumerate(self.rooms[:-1]):
                room_next = self.rooms[i + 1]
                if not room.doors:
                    room.doors.append(room.get_random_position())
                if not room_next.doors:
                    room_next.doors.append(room_next.get_random_position())
                door1 = random.choice(room.doors)
                door2 = random.choice(room_next.doors)
                self.connections[door1] = (room_next, door2)
                self.connections[door2] = (room, door1)
                # Peindre couloir dans tiles (préserve '+') et marquer walkable
                self.create_corridor(door1, door2)

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

        # Placer quelques ennemis immobiles
        self._place_enemies(count=min(3, max(1, len(self.rooms)//2)))

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
            ex, ey = enemy["x"], enemy["y"]
            if 0 <= ey < self.height and 0 <= ex < self.width:
                if (ex, ey) in visible or (ex, ey) in self.discovered:
                    grid[ey][ex] = "M"  # Monstre immobile
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
        # Couloir horizontal (exclure la porte de départ)
        for x in range(min(x1, x2), max(x1, x2)+1):
            if (x, y1) == (x1, y1) or (x, y1) == (x2, y2):
                continue
            if 0 <= x < self.width and 0 <= y1 < self.height:
                if self.tiles[y1][x] != "+":
                    self.tiles[y1][x] = "."
                self.walkable.add((x, y1))
        # Couloir vertical (exclure la porte d'arrivée)
        for y in range(min(y1, y2), max(y1, y2)+1):
            if (x2, y) == (x1, y1) or (x2, y) == (x2, y2):
                continue
            if 0 <= x2 < self.width and 0 <= y < self.height:
                if self.tiles[y][x2] != "+":
                    self.tiles[y][x2] = "."
                self.walkable.add((x2, y))

    def get_room_containing(self, x, y):
        for room in self.rooms:
            if room.contains(x, y):
                return room
        return None

    def get_connected_room(self, door_coord):
        return self.connections.get(door_coord, None)

    def is_walkable(self, x, y):
        return (x, y) in self.walkable

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
        import random as _r
        placed = 0
        tries = 0
        flat_walkable = list(self.walkable)
        while placed < count and tries < 200 and flat_walkable:
            x, y = _r.choice(flat_walkable)
            # éviter start/end
            if (x, y) != self.start and (x, y) != self.end and self.tiles[y][x] == ".":
                # choisir une direction de tir (haut/bas/gauche/droite)
                dx, dy = _r.choice([(1,0),(-1,0),(0,1),(0,-1)])
                self.enemies.append({"x": x, "y": y, "dx": dx, "dy": dy})
                placed += 1
            tries += 1

    def tick(self):
        # Avancer les projectiles et tirer périodiquement
        self.ticks += 1
        # Tir ennemi moins fréquent pour performance
        if self.ticks % 10 == 0:
            for e in self.enemies:
                self.projectiles.append((e["x"], e["y"], e["dx"], e["dy"]))
        # Bouger projectiles
        new_projectiles = []
        for (px, py, dx, dy) in self.projectiles:
            nx, ny = px + dx, py + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.tiles[ny][nx] != "#":
                new_projectiles.append((nx, ny, dx, dy))
        self.projectiles = new_projectiles

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
