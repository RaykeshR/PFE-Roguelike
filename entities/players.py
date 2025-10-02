#######################################################################IMPORTS#######################################################################
import os
from PIL import Image
###################################################################################################################################################

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

    #type de bots qui vont prendre le role de joueur pour le pré-entrainement du model
    def type_train_bot(self,type_bot) :
        '''
        3 categoris de bot :
        Type      | Comportement                                                

        Agressif    | Attaque systématiquement les ennemis, fonce vers eux        
        Fuyard      | Évite le combat, fuit quand un ennemi approche              
        Aléatoire  | Choisit des actions au hasard (exploration, attaque, fuite) 
        '''
        type_bot=["Agressif","Fuyard","Aléatoire"]
        if type_bot in type_bot :
            return True
        else :
            return False
  
    def train_bot(self,type_bot) :
        

        if type_bot=="Agressif" :
            pass
        elif type_bot=="Fuyard" :
            pass
        elif type_bot=="Aléatoire" :
            pass
        else :
            print("Type de bot inconnu. Choisissez parmi : Agressif, Fuyard, Aléatoire.")





        


