import random

class Room:
    def __init__(self, x, y, width, height, doors=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.doors = doors if doors else []

    def contains(self, px, py):
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height

    def draw(self):
        output = []
        for j in range(self.height):
            row = ""
            for i in range(self.width):
                gx, gy = self.x + i, self.y + j
                # Les portes doivent être visibles même si elles sont sur les murs
                if (gx, gy) in self.doors:
                    row += "+"
                elif i == 0 or i == self.width-1 or j == 0 or j == self.height-1:
                    row += "#"
                else:
                    row += "."
            output.append(row)
        return "\n".join(output)

    def get_random_position(self):
        x = random.randint(self.x + 1, self.x + self.width - 2)
        y = random.randint(self.y + 1, self.y + self.height - 2)
        return (x, y)
