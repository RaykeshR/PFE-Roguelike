from engine.room import Room
import random, os

class Map:
    ITEM_SYMBOLS = {"potion": "!", "weapon": "/"}

    def __init__(self, width=50, height=20, room_count=4):
        self.width = width
        self.height = height
        self.rooms = []
        self.room_count = room_count
        self.start = (0, 0)
        self.end = None
        self.bots = []  # pas encore implémenté

        self.generate()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate(self):
        """Génère plusieurs rooms aléatoires avec portes."""
        self.rooms = []
        for _ in range(self.room_count):
            w = random.randint(8, 15)
            h = random.randint(5, 10)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            doors = []
            for _ in range(random.randint(1, 2)):
                dx = random.randint(1, w - 2)
                dy = random.randint(1, h - 2)
                doors.append((x + dx, y + dy))

            room = Room(x, y, w, h, doors=doors)
            self.rooms.append(room)

        self.start = (self.rooms[0].x + 1, self.rooms[0].y + 1)
        self.end_room = self.rooms[-1]
        self.end = self.end_room.doors[0] if self.end_room.doors else (self.end_room.x + 1, self.end_room.y + 1)

    def draw(self, player_pos):
        """Dessine toutes les rooms et le joueur."""
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

    def find_room_by_door(self, x, y):
        """Retourne une room qui contient cette porte mais pas la room actuelle."""
        for room in self.rooms:
            if (x, y) in room.doors:
                return room
        return None
