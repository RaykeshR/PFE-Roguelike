class PlayerController:
    def __init__(self, game_map):
        self.map = game_map
        self.x, self.y = self.map.start

    def move(self, direction):
        dx, dy = 0, 0
        if direction == "z": dy = -1
        elif direction == "s": dy = 1
        elif direction == "q": dx = -1
        elif direction == "d": dx = 1
        else: return

        new_x = self.x + dx
        new_y = self.y + dy

        # Déplacement sur cases franchissables (sol, portes, couloirs)
        if not self.map.is_walkable(new_x, new_y):
            return

        # Téléportation si la case est une porte connectée
        target = self.map.get_connected_room((new_x, new_y))
        if target:
            target_room, target_door = target
            self.x, self.y = target_door
        else:
            self.x, self.y = new_x, new_y

        # Vérifier porte finale
        if (self.x, self.y) == self.map.end:
            print("\nVous avez atteint la porte finale ! Nouvelle map générée...")
            input("Appuyez sur Entrée pour continuer...")
            self.map.generate()
            self.x, self.y = self.map.start
