import logging
from typing import Optional, List
from items import Weapon, Potion
from items.category_potion import CategoryPotion
from entities.players import players as PlayerEntity


class PlayerController:
    def __init__(self, game_map):
        self.map = game_map
        self.x, self.y = self.map.start
        self.map.reveal_from((self.x, self.y))
        self._log = logging.getLogger("pfe_roguelike.engine.player")
        self._log.info("Joueur initialisé", extra={"extra": {"pos": (self.x, self.y)}})
        # Modèle de domaine joueur (entities.players)
        self.player = PlayerEntity(name="player", pv=100, inventory=[], equiped_item=[], is_human=True, x=self.x, y=self.y)

    # --- HUD helpers ---
    def get_hp(self) -> int:
        return int(self.player.get_pv())

    def get_equipped_weapon_name(self) -> str:
        w = None
        # entities.players stocke equiped_item (liste). On considère la première arme.
        for it in self.player.get_equiped_item() or []:
            if isinstance(it, Weapon):
                w = it
                break
        return w.name if w else "(aucune)"

    def get_equipped_weapon(self) -> Optional[Weapon]:
        for it in self.player.get_equiped_item() or []:
            if isinstance(it, Weapon):
                return it
        return None

    def get_inventory_size(self) -> int:
        inv = self.player.get_inventory() or []
        return len(inv)

    # --- Inventory actions ---
    def list_inventory(self):
        return list(self.player.get_inventory() or [])

    def equip_weapon_by_index(self, idx: int) -> bool:
        inv = self.player.get_inventory() or []
        if 0 <= idx < len(inv):
            item = inv[idx]
            if isinstance(item, Weapon):
                # remplace l'équipement actuel par cette arme (liste avec une arme)
                self.player.set_equiped_item([item])
                self._log.info("Arme équipée", extra={"extra": {"item": item.name}})
                return True
        return False

    def use_potion_by_index(self, idx: int) -> bool:
        inv = self.player.get_inventory() or []
        if 0 <= idx < len(inv):
            item = inv[idx]
            if isinstance(item, Potion):
                used = False
                if item.category == CategoryPotion.HEALTH:
                    before = int(self.player.get_pv())
                    self.player.set_pv(max(0, before + int(item.potency)))
                    used = True
                elif item.category == CategoryPotion.SPEED:
                    # Placeholder: on pourrait influencer la vitesse de déplacement
                    used = True
                if used:
                    inv.pop(idx)
                    self.player.set_inventory(inv)
                    self._log.info("Potion utilisée", extra={"extra": {"item": item.name}})
                    return True
        return False

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
        for pr in list(self.map.projectiles):
            px, py = pr[0], pr[1]
            owner = pr[4] if len(pr) >= 5 else "enemy"
            if owner != "enemy":
                continue
            if (px, py) == (self.x, self.y):
                print("\nVous avez été touché par un projectile !")
                self._log.warning("Joueur touché par projectile", extra={"extra": {"pos": (self.x, self.y)}})
                raise SystemExit(0)

        # Ramassage automatique des items présents sur la case
        items_here = self.map.get_items_at(self.x, self.y)
        if items_here:
            taken = self.map.pickup_all_items(self.x, self.y)
            inv = self.player.get_inventory() or []
            inv.extend(taken)
            self.player.set_inventory(inv)
            for it in taken:
                self._log.info("Ramassage item", extra={"extra": {"pos": (self.x, self.y), "item": getattr(it, "name", str(it))}})
            print(f"Vous avez ramassé {len(taken)} objet(s). Inventaire: {[getattr(i,'name',str(i)) for i in (self.player.get_inventory() or [])]}")

        # Vérifier porte finale
        if (self.x, self.y) == self.map.end:
            print("\nVous avez atteint la porte finale ! Nouvelle map générée...")
            self._log.info("Porte finale atteinte, regénération map")
            input("Appuyez sur Entrée pour continuer...")
            self.map.generate()
            self.x, self.y = self.map.start
            # synchroniser la position dans le modèle
            self.player.set_position(self.x, self.y)
