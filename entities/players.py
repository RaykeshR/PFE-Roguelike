#######################################################################IMPORTS#######################################################################
import os
import random
import logging
#from engine.map import Map
from random import randint
from PIL import Image
from .monster import Monster
from items import Weapon
from items import Potion
from items.category_potion import CategoryPotion

###################################################################################################################################################
#pv joueur =100
#pv monstre=50
#degats arme=10
#arme avec points de vie

class players:
    #constructeur
    def __init__(self, name="player", pv=100, inventory=None, equiped_item=None, is_human=True, x=0.0, y=0.0,game_map=None, niveau=1, xp=0):
        self.pv=pv
        self.inventory=inventory if inventory is not None else []
        self.equiped_item=equiped_item if equiped_item is not None else []
        self.is_human=is_human
        self.name=name
        self.map=game_map
        self.x,self.y=self.map.start
        self.niveau = int(niveau)
        self.xp = int(xp)
        self.map.reveal_from((self.x,self.y))
        self._log = logging.getLogger("pfe_roguelike.engine.player")
        self._log.info("Joueur initialisé", extra={"extra": {"pos": (self.x, self.y)}})

        

###################################################################Méthodes##################################################################
    #### GETTERS AND SETTERS ####
    
    #Pour vérifier si le joueur est en vie
    def get_is_alive(self):
        """True si le joueur est en vie (pv>0), sinon False."""
        if self.pv>0:
            return True
        else:
            return False

    #retourne les pv
    def get_pv(self):
        return self.pv
    def get_hp(self)->int:
        return int(self.get_pv())

    def get_xp(self):
        return self.xp
    
    def get_niveau(self):
        return self.niveau
        
    def set_xp(self, xp):
        self.xp = int(xp)
        
    def set_niveau(self, niveau):
        self.niveau = int(niveau)

    #retourne l'inventory
    def get_inventory(self):
        return self.inventory
    
    #retourne la taille de l'inventaire
    def get_inventory_size(self) -> int:
        inv = self.get_inventory() or []
        return len(inv)

    #retourne si le jourur est humain
    def get_is_human(self):
        """True si le joueur est humain, sinon False."""
        return self.is_human
    
    #retourne le nom du joueur
    def get_name(self):
        return self.name
    
    #retourne la position x
    def get_x(self):
        return self.x
    
    #retourne la position y
    def get_y(self):
        return self.y
    
    #returne les objets équipés
    def get_equiped_item(self):
        return self.equiped_item
    
    
    #retourne l'arme équipée
    def get_equipped_weapon(self) :
        for it in self.get_equiped_item() or []:
            if isinstance(it, Weapon):
                return it
        return None
    
     #retourne le nom de l'arme équipée
    def get_equipped_weapon_name(self) -> str:
        arme=None
        # entities.players stocke equiped_item (liste). On considère la première arme.
        for it in self.get_equiped_item() or []:
            if isinstance(it, Weapon):
                arme= it
                break
        return arme.name if arme else "(aucune)"
    
        return None
    def get_weapon_category(self):
        weapon=self.get_weapon()
        if weapon:
            return weapon.category
        return None
    
    #retourne les elements de l'inventaire
    def list_inventory(self):
        return list(self.get_inventory() or [])
    
    
    
    def set_pv(self, pv):
        self.pv=pv

    
    def set_inventory(self, inventory):
        self.inventory=inventory
    
    def set_is_human(self, is_human):
        self.is_human=is_human
    
    def set_name(self, name):
        self.name=name

    def set_x(self, x):
        self.x=x
    
    def set_y(self, y):
        self.y=y
    
    def set_position(self, x, y):
        self.x=x
        self.y=y

    def set_equiped_item(self, equiped_item):
        self.equiped_item=equiped_item


    ### OTHERS METHODS ###


    def ajouter_xp(self, montant):
        """Ajoute de l'XP au joueur et gère la montée de niveau."""
        if not self.get_is_alive():
            return
            
        self.xp += int(montant)
        print(f"Vous gagnez {montant} XP. (Total : {self.xp})")
        
        # Logique de montée de niveau (simple, à ajuster)
        xp_pour_niveau_sup = self.niveau * 100 # 100xp => niveau 2, 200xp => niveau 3, etc.
        
        while self.xp >= xp_pour_niveau_sup:
            self.niveau += 1
            self.xp -= xp_pour_niveau_sup
            
            # Amélioration des stats
            pv_gain = 10 # Par exemple
            self.pv += pv_gain
            
            print(f"🎉 LEVEL UP! Vous êtes niveau {self.niveau}. 🎉")
            print(f"Vous gagnez {pv_gain} PV max. (PV actuels : {self.pv})")
            
            self._log.info("Level Up!", extra={"extra": {"lvl": self.niveau, "xp": self.xp}})
            
            # Mettre à jour le seuil pour le prochain niveau
            xp_pour_niveau_sup = self.niveau * 100

    
    #pour retrouver des pv
    def heal(self,soin):
        """
        Soigne le joueur.
        soin: montant des points de vie à restaurer.
        """
        self.pv+=soin
    
    def die(self):
        """
        Gère la mort du joueur.
        Affiche "Game Over" si le joueur est humain, sinon indique le nom du mort.
        """
        if not self.get_is_alive():
            if self.get_is_human():
                print("Game Over")
            else:
                print(f"{self.name} est mort (non humain)")
    
    def kill(self):
        """
        Tue le joueur en mettant ses points de vie à 0 et en appelant la méthode die().
        """
        self.pv=0
        self.die()

    #équipe une arme par son index dans l'inventaire
    def equip_weapon_by_index(self, idx: int) -> bool:
        inv = self.get_inventory() or []
        if 0 <= idx < len(inv):
            item = inv[idx]
            if isinstance(item, Weapon):
                # remplace l'équipement actuel par cette arme (liste avec une arme)
                self.set_equiped_item([item])
                self._log.info("Arme équipée", extra={"extra": {"item": item.name}})
                return True
        return False
    
    #utilise une potion par son index dans l'inventaire
    def use_potion_by_index(self, idx: int) -> bool:
        inv = self.get_inventory() or []
        if 0 <= idx < len(inv):
            item = inv[idx]
            if isinstance(item, Potion):
                used = False
                if item.category == CategoryPotion.HEALTH:
                    before = int(self.get_pv())
                    self.set_pv(max(0, before + int(item.potency)))
                    used = True
                elif item.category == CategoryPotion.SPEED:
                    # Placeholder: on pourrait influencer la vitesse de déplacement
                    used = True
                if used:
                    inv.pop(idx)
                    self.set_inventory(inv)
                    self._log.info("Potion utilisée", extra={"extra": {"item": item.name}})
                    return True
        return False

    
    #pour afficher une image dans le dossier src
    def show_img_in_src(self, img_name):
        '''
        Affiche une image du repertoire src.
        img_name: nom du fichier image (ex: "player.gif").
        '''
        BASE_DIR=os.path.dirname(__file__)
        #Construire le chemin vers le GIF
        joueur_path=os.path.join(BASE_DIR, "..", "src", img_name)
        joueur_path = os.path.abspath(joueur_path)
        #Charger l'image et visualisation
        image=Image.open(joueur_path)
        image.show()

    #methode pour  calculer la distance euclidienne monstre-joueur
    def distance_euclidienne(self,monstre):
        return ((self.x-monstre.x)**2+(self.y-monstre.y)**2)**0.5
    
    ''' def move_towards(self,target_x,target_y,step_size=1.0):
        """
        Déplace le joueur vers une position cible (target_x, target_y) par une taille de pas spécifiée.
        step_size: distance maximale que le joueur peut se déplacer en une seule fois.
        """
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        distance = (direction_x**2 + direction_y**2)**0.5
        
        if distance == 0:
            return  #le joueur est déjà à la position cible
        
        #Normaliser la direction
        direction_x /= distance
        direction_y /= distance
        
        #Calculer le déplacement
        move_x = direction_x * min(step_size, distance)
        move_y = direction_y * min(step_size, distance)
        
        #Mettre à jour la position du joueur
        self.x += move_x
        self.y += move_y
        '''
    #déplace le joueur dans une direction donnée
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
        # mémoriser la dernière direction
        self._last_dir = (dx, dy)

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
                damage = pr[5] if len(pr) >= 6 else 10
                pv_avant = int(self.get_pv())
                self.set_pv(max(0, pv_avant - damage))
                pv_apres = int(self.get_pv())
                print(f"Vous perdez {damage} PV. PV restants: {pv_apres}/{pv_avant}")
                # Retirer le projectile pour éviter les dégâts multiples
                try:
                    self.map.projectiles.remove(pr)
                except ValueError:
                    pass
                if self.get_hp() <= 0:
                    print("Vous êtes mort ! Fin du jeu.")
                    self._log.error("Joueur est mort", extra={"extra": {"pos": (self.x, self.y)}})
                    raise SystemExit(0)

        # Ramassage automatique des items présents sur la case
        items_here = self.map.get_items_at(self.x, self.y)
        if items_here:
            taken = self.map.pickup_all_items(self.x, self.y)
            inv = self.get_inventory() or []
            inv.extend(taken)
            self.set_inventory(inv)
            for it in taken:
                self._log.info("Ramassage item", extra={"extra": {"pos": (self.x, self.y), "item": getattr(it, "name", str(it))}})
            print(f"Vous avez ramassé {len(taken)} objet(s). Inventaire: {[getattr(i,'name',str(i)) for i in (self.get_inventory() or [])]}")

        # Vérifier porte finale
        if (self.x, self.y) == self.map.end:
            print("\nVous avez atteint la porte finale ! Nouvelle map générée...")
            self._log.info("Porte finale atteinte, regénération map")
            input("Appuyez sur Entrée pour continuer...")
            self.map.generate()
            self.x, self.y = self.map.start
            # synchroniser la position dans le modèle
            self.set_position(self.x, self.y)


    def joueur_attaque(self, monstre):
        """
        Attaque un monstre en réduisant ses points de vie.
        degat: montant des points de vie à retirer au monstre.
        """
        arme=self.get_weapon()
        degats=arme.damage if arme else 5  #dégâts de base
        monstre.pv-=degats
        if monstre.pv<0:
            monstre.pv=0
        print(f"{self.name} attaque {monstre.name} avec {arme.name if arme else 'ses poings'} et inflige {degats} dégâts.")
        if not monstre.get_is_alive():
            print(f"{monstre.name} est vaincu!")

    # #type de bots qui vont prendre le role de joueur pour le pré-entrainement du model
    # def type_train_bot(self,type_bot):
    #     ''' 
    #     3 categoris de bot :
    #     Type      | Comportement                                                

    #     Agressif    | Attaque systématiquement les ennemis, fonce vers eux        
    #     Fuyard      | Évite le combat, fuit quand un ennemi approche              
    #     Aléatoire  | Choisit des actions au hasard (exploration, attaque, fuite) 
    #     '''

    #     type_bot=["Agressif","Fuyard","Aléatoire"]
        
  
    def train_bot(self,type_bot,monster) :
        monster_position=(monster.x, monster.y)
        bot_position=(self.x, self.y)
        """Initialise le bot avec un type de comportement"""
        
        if type_bot=="Agressif" :
            '''Se dirige toujours vers l'ennemi le plus proche et l'attaque'''
            if randint(0,1)==0 : #choisit aléatoirement de se déplacer en x ou y
                if bot_position[0]<monster_position[0] :
                    self.x+=1
                elif bot_position[0]>monster_position[0] :
                    self.x-=1
            else:
                if bot_position[1]<monster_position[1] :
                    self.y+=1
                elif bot_position[1]>monster_position[1] :
                    self.y-=1
            if self.distance_euclidienne(monster)<=0 :
                self.joueur_attaque(monster,10)

        elif type_bot=="Fuyard" :
            '''S'éloigne de l'ennemi le plus proche pour éviter le combat'''
            if randint(0,1)==0 :#choisit aléatoirement de se déplacer en x ou y
                self.x+=randint(-1,1)
            else :
                self.y+=randint(-1,1)
        elif type_bot=="Aléatoire" :
            '''Choisit aléatoirement entre attaquer, fuir ou explorer'''
            action=random.choice(["attaquer","fuir","explorer"])
            if action=="attaquer" :
                # action="Agressif"
                if randint(0,1)==0 : #choisit aléatoirement de se déplacer en x ou y
                    if bot_position[0]<monster_position[0] :
                        self.x+=1
                    elif bot_position[0]>monster_position[0] :
                        self.x-=1
                else:
                    if bot_position[1]<monster_position[1] :
                        self.y+=1
                    elif bot_position[1]>monster_position[1] :
                        self.y-=1
                if self.distance_euclidienne(monster)<=0 :
                    self.joueur_attaque(monster,10)
            elif action=="fuyard" :
                # action="Fuyard"
                if randint(0,1)==0 :#choisit aléatoirement de se déplacer en x ou y
                    self.x+=randint(-1,1)
                else :
                    self.y+=randint(-1,1)
        else :
            print("Type de bot inconnu. Choisissez parmi : Agressif, Fuyard, Aléatoire.")
    
    def combat(self, monster):
        """
        Gère un combat complet entre le joueur et un monstre.
        Utilise la méthode joueur_attaque pour infliger les dégâts.
        """
        print(f" Combat entre {self.name} et un monstre commence !")
        print(f"{self.name} : {self.pv} PV | Monstre : {monster.get_pv()} PV\n")

        #Boucle jusqu’à la mort d’un des deux
        while self.get_is_alive() and monster.get_is_alive():
            #Tour du joueur
            print(f"{self.name} attaque !")
            self.joueur_attaque(monster)

            #Vérifie si le monstre est mort
            if not monster.get_is_alive():
                print("Le monstre est mort !")
                dropped=monster.die()
                if dropped:
                    self.inventory.append(dropped)
                    print(f"{self.name} ramasse {dropped.name}.")
                break

            #Tour du monstre
            print("Le monstre riposte !")
            self.pv-=monster.weapon.get_damage()
            monster.weapon.use()

            if not self.get_is_alive():
                print(f"{self.name} est mort pendant le combat...")
                break

            #Affichage de l’état actuel
            print(f"\n➡️  {self.name} : {self.pv} PV , Monstre : {monster.get_pv()} PV\n")
        
        print("Combat terminé.")

    