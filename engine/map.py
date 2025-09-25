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
        self.connections = {}  # { (room_id, door_coord): target_room }

        self.generate()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate(self):
        """Génère plusieurs rooms aléatoires sans chevauchement et les connecte."""
        self.rooms = []
        self.connections = {}
        attempts = 0
        while len(self.rooms) < self.room_count and attempts < 100:
            w = random.randint(8, 15)
            h = random.randint(5, 10)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            new_room = Room(x, y, w, h)

            # Vérifier chevauchement
            overlap = False
            for r in self.rooms:
                if (x < r.x + r.width and x + w > r.x and
                    y < r.y + r.height and y + h > r.y):
                    overlap = True
                    break
            if not overlap:
                # Ajouter portes aléatoires
                door_count = random.randint(1, 2)
                for _ in range(door_count):
                    dx = random.randint(1, w - 2)
                    dy = random.randint(1, h - 2)
                    new_room.doors.append((x + dx, y + dy))
                self.rooms.append(new_room)
            attempts += 1

        # Connecter les portes aléatoirement
        for i, room in enumerate(self.rooms[:-1]):
            # Choisir une porte de cette room et de la suivante
            door1 = random.choice(room.doors)
            door2 = random.choice(self.rooms[i+1].doors)
            self.connections[door1] = self.rooms[i+1]
            self.connections[door2] = room

        # Définir départ et arrivée
        self.start = self.rooms[0].get_random_position()
        self.end = self.rooms[-1].get_random_position()

    def draw(self, player_pos):
        self.clear_screen()
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for room in self.rooms:
            room_str = room.draw().split("\n")
            for j, row in enumerate(room_str):
                for i, char in enumerate(row):
                    gx, gy = room.x + i, room.y + j
                    grid[gy][gx] = char
        px, py = player_pos
        grid[py][px] = "@"
        for row in grid:
            print("".join(row))
        print("\nLégende: @=Joueur, #=Mur, +=Porte")

    def get_room_containing(self, x, y):
        for room in self.rooms:
            if room.contains(x, y):
                return room
        return None

    def get_connected_room(self, door_coord):
        """Retourne la room connectée à cette porte, s'il y en a."""
        return self.connections.get(door_coord, None)
