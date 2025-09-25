class Room:
    def __init__(self, x, y, width, height, doors=None, items=None):
        """
        Représente une pièce dans la carte.
        :param x, y: position du coin supérieur gauche
        :param width, height: dimensions de la pièce
        :param doors: liste de coordonnées (x,y) des portes
        :param items: dictionnaire { (x,y): "symbol" } pour indiquer la présence d'un item
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.doors = doors if doors else []
        self.items = items if items else {}
        self.is_visible = True  # Toujours visible pour affichage complet

    def contains(self, px, py):
        """Retourne True si le joueur est dans la pièce."""
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height

    def draw(self, player_pos=None):
        """Retourne une représentation ASCII de la pièce."""
        output = []
        for j in range(self.height):
            row = ""
            for i in range(self.width):
                gx, gy = self.x + i, self.y + j

                if player_pos and (gx, gy) == player_pos:
                    row += "@"
                elif (gx, gy) in self.doors:
                    row += "+"
                elif (gx, gy) in self.items:
                    row += self.items[(gx, gy)]
                elif i == 0 or i == self.width - 1 or j == 0 or j == self.height - 1:
                    row += "#"
                else:
                    row += "."
            output.append(row)
        return "\n".join(output)
