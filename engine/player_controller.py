class PlayerController:
    def __init__(self, game_map):
        self.map = game_map
        self.x, self.y = self.map.start

    def move(self, direction):
        """Déplace le joueur selon la direction."""
        dx, dy = 0, 0
        if direction == "z":
            dy = -1
        elif direction == "s":
            dy = 1
        elif direction == "q":
            dx = -1
        elif direction == "d":
            dx = 1
        else:
            return

        new_x = self.x + dx
        new_y = self.y + dy

        # Vérifier collisions avec murs
        room = self.map.get_room_containing(new_x, new_y)
        if room is None:
            return  # hors map

        rel_x = new_x - room.x
        rel_y = new_y - room.y

        # Si mur et pas une porte => bloqué
        if (rel_x == 0 or rel_x == room.width - 1 or
            rel_y == 0 or rel_y == room.height - 1):
            if (new_x, new_y) in room.doors:
                # Passage par la porte
                target_room = self.map.get_connected_room(room, new_x, new_y)
                if target_room:
                    self.x, self.y = target_room.get_random_position()
            return

        # Déplacement valide
        self.x, self.y = new_x, new_y

        # Vérifier porte finale
        if (self.x, self.y) == self.map.end:
            print("\nVous avez atteint la porte finale ! Nouvelle map...")
            input("Appuyez sur Entrée...")
            self.map.generate()
            self.x, self.y = self.map.start
