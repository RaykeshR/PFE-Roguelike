#######################################################################IMPORTS#######################################################################
import os
from PIL import Image
import random
from random import randint

from monster import Monster
from items import weapon

###################################################################################################################################################
#pv joueur =100
#pv monstre=50
#degats arme=10
#arme avec points de vie

class players:
    #constructeur
    def __init__(self, name="player", pv=100, inventory=None, equiped_item=None, is_human=True, x=0.0, y=0.0):
        self.pv=pv
        self.inventory=inventory if inventory is not None else []
        self.equiped_item=equiped_item if equiped_item is not None else []
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
        return self.y
    
    #returne les objets équipés
    def get_equiped_item(self):
        return self.equiped_item
    
    def get_weapon(self):
        for item in self.equiped_item:
            if isinstance(item, weapon):
                return item
        return None
    def get_weapon_category(self):
        weapon=self.get_weapon()
        if weapon:
            return weapon.category
        return None
    
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
    
    def move_towards(self,target_x,target_y,step_size=1.0):
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

    