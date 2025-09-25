import os
from engine.room import Room

class Map:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.rooms = []
        self.player_x = 2
        self.player_y = 2
        self.start = (self.player_x, self.player_y)
        self.end = None  # pourra pointer vers une sortie
        self.bots = []   # pas encore implémenté

        # Génération procédurale basique
        self.generate()

    def generate(self):
        """Crée une map simple avec 2 pièces connectées."""
        room1 = Room(1, 1, 15, 10, doors=[(15, 5)], items={(5, 5): "!"})
        room2 = Room(16, 3, 15, 8, doors=[(16, 5)], items={(20, 6): "/"})
        self.rooms = [room1, room2]
        self.end = (25, 7)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw(self):
        """Affiche seulement la pièce où se trouve le joueur."""
        self.clear_screen()
        for room in self.rooms:
            if room.contains(self.player_x, self.player_y):
                room.is_visible = True
                print(room.draw((self.player_x, self.player_y)))
                break

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        # Autoriser mouvement uniquement si dans une pièce visible
        for room in self.rooms:
            if room.contains(new_x, new_y):
                self.player_x, self.player_y = new_x, new_y
                return
