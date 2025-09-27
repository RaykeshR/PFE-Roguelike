#######################################################################IMPORTS#######################################################################
import os
from PIL import Image
###################################################################################################################################################

class players:
    #constructeur
    def __init__(self, name="player", pv=100, inventory=[], equiped_item=[], is_human=True, x=0.0, y=0.0):
        self.pv=pv
        self.inventory=inventory
        self.equiped_item=equiped_item
        self.is_human=is_human
        self.name=name
        self.x=x
        self.y=y

###################################################################Méthodes##################################################################
    #### GETTERS AND SETTERS ####
    
    #Pour vérifier si le joueur est en vie
    def get_is_alive(self):
        """True si le joueur est en vie (pv > 0), sinon False."""
        if self.pv>0:
            return True
        else:
            return False

    #retourne les pv
    def get_pv(self):
        return self.pv

    #retourne l'inventory
    def get_inventory(self):
        return self.inventory

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
        return self.yz
    
    #returne les objets équipés
    def get_equiped_item(self):
        return self.equiped_item

    ### OTHERS METHODS ###

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
  
    def train_bot(self) :
        '''
        3 categoris de bot :
        Type      | Comportement                                                

        Agressif    | Attaque systématiquement les ennemis, fonce vers eux        
        Fuyard      | Évite le combat, fuit quand un ennemi approche              
        Aléatoire  | Choisit des actions au hasard (exploration, attaque, fuite) 
        '''
        pass





        


'''  def __init__(self, name, hp=100, position=(0, 0)):
        """
        Représente le joueur.

        :param name: Nom du joueur
        :param hp: Points de vie
        :param position: Position initiale (x, y)
        """
        self.name = name
        self.hp = hp
        self.position = position
        self.inventory = []       # Liste des objets collectés
        self.actions_log = []     # Historique des actions pour la BDD
        self.style = None         # Profil de jeu (agressif, sniper, tank…)

    # -------------------------
    # ⚔️ Combat
    # -------------------------
    def attack(self, enemy, damage=10):
        """
        Le joueur attaque un ennemi.
        """
        enemy.take_damage(damage)
        self.log_action("attack")

    def take_damage(self, amount):
        """
        Le joueur reçoit des dégâts.
        """
        self.hp -= amount
        print(f"{self.name} subit {amount} dégâts. HP restants: {self.hp}")
        if self.is_dead():
            self.log_action("death")

    def is_dead(self):
        """
        Vérifie si le joueur est mort.
        """
        return self.hp <= 0

    # -------------------------
    # 🚶 Déplacement
    # -------------------------
    def move(self, direction):
        """
        Déplace le joueur dans une direction (x, y).
        """
        x, y = self.position
        if direction == "up":
            self.position = (x, y + 1)
        elif direction == "down":
            self.position = (x, y - 1)
        elif direction == "left":
            self.position = (x - 1, y)
        elif direction == "right":
            self.position = (x + 1, y)

        print(f"{self.name} se déplace vers {self.position}")
        self.log_action(f"move_{direction}")

    # -------------------------
    # 🎒 inventory
    # ----------------
'''