import logging


class PlayerController:
    def __init__(self, game_map):
        self.map = game_map
        self.x, self.y = self.map.start
        self.map.reveal_from((self.x, self.y))
        self._log = logging.getLogger("pfe_roguelike.engine.player")
        self._log.info("Joueur initialisé", extra={"extra": {"pos": (self.x, self.y)}})

    def move(self, direction):
        dx, dy = 0, 0
        haut = ["z", "w", "up"]
        bas = ["s", "down"]
        gauche = ["q", "a", "left"]
        droite = ["d", "right"]
        if direction in haut: dy = -1
        elif direction in bas: dy = 1
        elif direction in gauche: dx = -1
        elif direction in droite: dx = 1
        else: return

        new_x = self.x + dx
        new_y = self.y + dy

        # Déplacement sur cases franchissables (sol, portes, couloirs)
        if not self.map.is_walkable(new_x, new_y):
            self._log.debug("Blocage déplacement: mur", extra={"extra": {"from": (self.x, self.y), "to": (new_x, new_y)}})
            return

        # Téléportation si la case est une porte connectée
        target = self.map.get_connected_room((new_x, new_y))
        if target:
            target_room, target_door = target
            # Placer le joueur juste à l'intérieur de la salle cible
            tx, ty = target_door
            # Déterminer une case adjacente walkable côté intérieur
            candidates = [(tx+1, ty), (tx-1, ty), (tx, ty+1), (tx, ty-1)]
            placed = False
            for cx, cy in candidates:
                if self.map.is_walkable(cx, cy):
                    # s'assurer qu'on est bien dans la salle cible
                    if self.map.get_room_containing(cx, cy) == target_room:
                        self.x, self.y = cx, cy
                        placed = True
                        break
            if not placed:
                # fallback: rester sur la porte si aucune case intérieure trouvée
                self.x, self.y = target_door
        else:
            self.x, self.y = new_x, new_y

        # Mise à jour de la visibilité persistante
        self.map.reveal_from((self.x, self.y))
        self._log.info("Position joueur mise à jour", extra={"extra": {"pos": (self.x, self.y)}})

        # Check collision projectile (simple): mort => message et quitter
        for (px, py, _, _) in list(self.map.projectiles):
            if (px, py) == (self.x, self.y):
                print("\nVous avez été touché par un projectile !")
                self._log.warning("Joueur touché par projectile", extra={"extra": {"pos": (self.x, self.y)}})
                raise SystemExit(0)

        # Vérifier porte finale
        if (self.x, self.y) == self.map.end:
            print("\nVous avez atteint la porte finale ! Nouvelle map générée...")
            self._log.info("Porte finale atteinte, regénération map")
            input("Appuyez sur Entrée pour continuer...")
            self.map.generate()
            self.x, self.y = self.map.start
