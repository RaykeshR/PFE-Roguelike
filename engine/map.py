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

        self.generate()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate(self):
        """Génère plusieurs salles aléatoires avec portes et couloirs."""
        self.rooms = []
        self.connections = {}
        self.walkable = set()
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

        # Connecter les portes avec un graphe linéaire (chaîne) puis marquer les couloirs franchissables
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
                # Marquer walkable sur le couloir entre door1 et door2
                x1, y1 = door1
                x2, y2 = door2
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if 0 <= x < self.width and 0 <= y1 < self.height:
                        self.walkable.add((x, y1))
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 <= y < self.height and 0 <= x2 < self.width:
                        self.walkable.add((x2, y))

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

        # Renseigner les cases franchissables: sols et portes des salles
        for room in self.rooms:
            for j in range(1, room.height - 1):
                for i in range(1, room.width - 1):
                    self.walkable.add((room.x + i, room.y + j))
            for door in room.doors:
                self.walkable.add(door)

    def draw(self, player_pos):
        self.clear_screen()
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        # Calculer visibilité: salle courante + salles adjacentes via portes
        visible = set()
        current_room = self.get_room_containing(*player_pos)
        rooms_visible = set()
        if current_room:
            rooms_visible.add(current_room)
            # Ajouter toutes les tuiles de la salle courante
            for j in range(current_room.height):
                for i in range(current_room.width):
                    visible.add((current_room.x + i, current_room.y + j))
            # Salles adjacentes et couloirs
            for door, link in self.connections.items():
                if current_room.contains(*door):
                    target_room, target_door = link
                    rooms_visible.add(target_room)
                    # Ajouter portes et couloir entre les deux
                    x1, y1 = door
                    x2, y2 = target_door
                    visible.add((x1, y1))
                    visible.add((x2, y2))
                    for x in range(min(x1, x2), max(x1, x2) + 1):
                        visible.add((x, y1))
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        visible.add((x2, y))
            # Ajouter les tuiles des salles adjacentes
            for room in list(rooms_visible):
                for j in range(room.height):
                    for i in range(room.width):
                        visible.add((room.x + i, room.y + j))

        # Dessiner les salles (avec protections de bornes et visibilité)
        for room in self.rooms:
            room_str = room.draw().split("\n")
            for j, row in enumerate(room_str):
                for i, char in enumerate(row):
                    gx, gy = room.x + i, room.y + j
                    if 0 <= gy < self.height and 0 <= gx < self.width and ((gx, gy) in visible):
                        grid[gy][gx] = char

        # Dessiner les couloirs (seulement si visibles)
        for door, (target_room, target_door) in self.connections.items():
            x1, y1 = door
            x2, y2 = target_door
            # Si l'une des deux salles est visible, on dessine le couloir
            if (current_room and (current_room.contains(x1, y1) or current_room.contains(x2, y2))):
                self.create_corridor(door, target_door, grid)

        px, py = player_pos
        if 0 <= py < self.height and 0 <= px < self.width:
            grid[py][px] = "@"

        # Marquer départ et arrivée si visibles
        sx, sy = self.start
        ex, ey = self.end
        if 0 <= sy < self.height and 0 <= sx < self.width and ((sx, sy) in visible):
            grid[sy][sx] = "S"
        if 0 <= ey < self.height and 0 <= ex < self.width and ((ex, ey) in visible):
            grid[ey][ex] = "E"

        for row in grid:
            print("".join(row))
        print("\nLégende: @=Joueur, #=Mur, +=Porte, S=Départ, E=Arrivée")

    def create_corridor(self, start, end, grid):
        x1, y1 = start
        x2, y2 = end
        # Couloir horizontal
        yh = y1
        if 0 <= yh < self.height:
            for x in range(min(x1, x2), max(x1, x2)+1):
                if 0 <= x < self.width:
                    grid[yh][x] = "."
        # Couloir vertical
        xv = x2
        if 0 <= xv < self.width:
            for y in range(min(y1, y2), max(y1, y2)+1):
                if 0 <= y < self.height:
                    grid[y][xv] = "."

    def get_room_containing(self, x, y):
        for room in self.rooms:
            if room.contains(x, y):
                return room
        return None

    def get_connected_room(self, door_coord):
        return self.connections.get(door_coord, None)

    def is_walkable(self, x, y):
        return (x, y) in self.walkable
