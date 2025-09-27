from items import Weapon

import random

class Monster():
    list_monster = []
    def __init__(self, weapon : Weapon, pv=100, x=0.0, y=0.0):
        self.pv=pv
        self.weapon=weapon
        self.x=x
        self.y=y
        Monster.list_monster.append(self)
    
    ###### getters and setters ######

    def get_is_alive(self):
        return self.pv>0
    
    def get_pv(self):
        return self.pv
    
    def heal(self,soin):
        self.pv+=soin

    def get_equiped_item(self):
        return self.equiped_item
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def get_position(self):
        return (self.x, self.y)

    def set_pv(self, pv):
        self.pv = pv

    def set_equiped_item(self, equiped_item):
        self.equiped_item = equiped_item
    
    def set_x(self, x):
        self.x = x
    
    def set_y(self, y):
        self.y = y
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    ###### other methods ######

    def die(self, drop_rate=0.5):
        """
        Handle the monster's death and item drop.
        drop_rate: Probability of dropping the equipped weapon (0.0 to 1.0).
        """
        if not self.get_is_alive():
            if self.weapon and (random.random() < drop_rate):
                print(f"Dropped item: {self.weapon.name}")
                return self.weapon
            print("Monster has died.")
        else :
            print("Monster's pv are still above 0.")
            return None
    
    def kill(self):
        """
        Instantly kill the monster by setting its health to 0.
        """
        self.pv = 0
        self.die(drop_rate=1.0)
    
    def kill_all_monsters():
        """
        Instantly kill all monsters in the list.
        """
        for monster in Monster.list_monster:
            monster.kill()


if __name__ == "__main__":
    # Example usage
    sword = Weapon(name="Sword", damage=15, category="melee", range=1.5, durability=10)
    goblin = Monster(weapon=sword, pv=50, x=5.0, y=10.0)
    
    print(f"Goblin's initial health: {goblin.get_pv()}")
    goblin.set_pv(0)  # Simulate the goblin taking damage
    dropped_item = goblin.die(drop_rate=0.7)
    if dropped_item:
        print(f"Goblin dropped: {dropped_item.name}")
    else:
        print("Goblin did not drop any item.")
    
