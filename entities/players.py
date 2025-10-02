#######################################################################IMPORTS#######################################################################
import os
from PIL import Image
###################################################################################################################################################

class players:
    #constructeur
    def __init__(self, name="player", pv=100, inventaire=[], equiped_item=[], is_human=True, x=0.0, y=0.0):
        self.pv=pv
        self.inventaire=inventaire
        self.equiped_item=equiped_item
        self.is_human=is_human
        self.name=name
        self.x=x
        self.y=y

###################################################################Méthodes##################################################################
    #Pour vérifier si le joueur est en vie
    def get_is_alive(self):
        if self.pv>0:
            return True
        else:
            return False

    #retourne les pv
    def get_pv(self):
        return self.pv
            
    #pour retrouver des pv
    def heal(self,soin):
        self.pv+=soin

    #retourne l'inventaire
    def get_inventaire(self):
        return self.inventaire

    #retourne si le jourur est humain
    def get_is_human(self):
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
    
    #pour afficher une image dans le dossier src
    def show_img_in_src(self, img_name):
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
  
    def train_bot(self,type_bot,) :
        

        if type_bot=="Agressif" :
            pass
        elif type_bot=="Fuyard" :
            pass
        elif type_bot=="Aléatoire" :
            pass
        else :
            print("Type de bot inconnu. Choisissez parmi : Agressif, Fuyard, Aléatoire.")





        


