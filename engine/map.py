import os

class Map:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.grid = [["." for _ in range(width)] for _ in range(height)]

        # On ajoute une bordure de murs
        for x in range(width):
            self.grid[0][x] = "#"
            self.grid[height - 1][x] = "#"
        for y in range(height):
            self.grid[y][0] = "#"
            self.grid[y][width - 1] = "#"

        # Position du joueur
        self.player_x = width // 2
        self.player_y = height // 2

    def clear_screen(self):
        """Nettoie le terminal (Windows/Linux/Mac)."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw(self):
        """Affiche la map en ASCII avec le joueur."""
        self.clear_screen()
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if x == self.player_x and y == self.player_y:
                    row += "@"
                else:
                    row += self.grid[y][x]
            print(row)

    def move_player(self, dx, dy):
        """Déplace le joueur si ce n'est pas un mur."""
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        if self.grid[new_y][new_x] != "#":
            self.player_x = new_x
            self.player_y = new_y
