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

        self.generate()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate(self):
        """Génère plusieurs rooms aléatoires sans chevauchement."""
        self.rooms = []
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

        # Définir départ et arrivée
        self.start = self.rooms[0].get_random_position()
        self.end = self.rooms[-1].doors[0] if self.rooms[-1].doors else self.rooms[-1].get_random_position()

    def draw(self, player_pos):
        """Affiche toutes les rooms et le joueur."""
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

    def get_connected_room(self, current_room, door_x, door_y):
        # Retourne une room différente qui contient cette porte
        for room in self.rooms:
            if room != current_room and (door_x, door_y) in room.doors:
                return room
        return None
