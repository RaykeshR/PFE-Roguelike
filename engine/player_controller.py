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

        room = self.map.get_room_containing(new_x, new_y)
        if room is None:
            return  # bloque le joueur hors des salles

        rel_x = new_x - room.x
        rel_y = new_y - room.y

        # Déplacement vers une porte
        if (new_x, new_y) in room.doors:
            target_room = self.map.get_connected_room((new_x, new_y))
            if target_room:
                self.x, self.y = target_room.get_random_position()
            return

        # Déplacement normal
        self.x, self.y = new_x, new_y

        # Vérifier porte finale
        if (self.x, self.y) == self.map.end:
            print("\nVous avez atteint la porte finale ! Nouvelle map générée...")
            input("Appuyez sur Entrée pour continuer...")
            self.map.generate()
            self.x, self.y = self.map.start
