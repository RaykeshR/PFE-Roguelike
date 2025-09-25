class PlayerController:
    def __init__(self, game_map):
        self.map = game_map
        self.x, self.y = self.map.start

    def move(self, dx, dy):
        """Déplace le joueur selon dx/dy."""
        new_x = self.x + dx
        new_y = self.y + dy

        # Vérifier collisions et portes
        for room in self.map.rooms:
            if room.contains(new_x, new_y):
                rel_x = new_x - room.x
                rel_y = new_y - room.y

                # Si mur => pas bouger
                if rel_x == 0 or rel_x == room.width - 1 or rel_y == 0 or rel_y == room.height - 1:
                    # Vérifier si c'est une porte
                    if (new_x, new_y) in room.doors:
                        # Déplacer joueur dans la pièce connectée aléatoirement
                        target_room = self.map.find_room_by_door(new_x, new_y)
                        if target_room:
                            # Placer le joueur à l'entrée correspondante
                            self.x, self.y = target_room.get_random_position()
                        return
                    return  # mur
                # Sinon bouger normalement
                self.x, self.y = new_x, new_y
                return
