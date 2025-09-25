import os
import random
from engine.room import Room

class Map:
    ITEM_SYMBOLS = {
        "potion": "!",
        "weapon": "/"
    }

    def __init__(self, width=50, height=20, room_count=4):
        self.width = width
        self.height = height
        self.rooms = []
        self.player_x = 2
        self.player_y = 2
        self.start = (self.player_x, self.player_y)
        self.end = None
        self.room_count = room_count
        self.bots = []  # Pas encore implémenté

        self.generate()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate(self):
        """Génère la map avec plusieurs rooms et portes."""
        self.rooms = []
        for _ in range(self.room_count):
            w = random.randint(8, 15)
            h = random.randint(5, 10)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            # Porte(s) aléatoire(s)
            doors = []
            door_count = random.randint(1, 2)
            for _ in range(door_count):
                dx = random.randint(1, w - 2)
                dy = random.randint(1, h - 2)
                doors.append((x + dx, y + dy))

            # Items uniquement pour la légende, pas encore implémentés
            items = {}
            # Exemple : items[(x+2, y+2)] = self.ITEM_SYMBOLS["potion"]

            room = Room(x, y, w, h, doors=doors, items=items)
            self.rooms.append(room)

        # Définir départ et fin
        self.start = (self.rooms[0].x + 1, self.rooms[0].y + 1)
        self.player_x, self.player_y = self.start
        self.end_room = self.rooms[-1]
        self.end = self.end_room.doors[0] if self.end_room.doors else (self.end_room.x + 1, self.end_room.y + 1)

    def draw(self):
        """Affiche la map entière avec toutes les pièces et le joueur."""
        self.clear_screen()
        # Initialiser la grille complète
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        # Dessiner toutes les rooms
        for room in self.rooms:
            room_str = room.draw(player_pos=None).split("\n")
            for j, row in enumerate(room_str):
                for i, char in enumerate(row):
                    gx, gy = room.x + i, room.y + j
                    grid[gy][gx] = char

        # Placer le joueur
        grid[self.player_y][self.player_x] = "@"

        # Afficher la grille
        for row in grid:
            print("".join(row))

        # Légende
        print("\nLégende: @=Joueur, #=Mur, +=Porte, !=Potion (pas encore implémenté), /=Arme (pas encore implémenté)")

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        # Vérifier collisions avec murs (#)
        for room in self.rooms:
            if room.contains(new_x, new_y):
                # Vérifier si c'est un mur dans cette room
                rel_x = new_x - room.x
                rel_y = new_y - room.y
                if rel_x == 0 or rel_x == room.width - 1 or rel_y == 0 or rel_y == room.height - 1:
                    return  # Mur => pas bouger
                self.player_x, self.player_y = new_x, new_y
                # Si joueur atteint la porte finale, régénérer la map
                if (self.player_x, self.player_y) == self.end:
                    print("\nVous avez atteint la porte finale ! Nouvelle map...")
                    input("Appuyez sur Entrée...")
                    self.generate()
                return
