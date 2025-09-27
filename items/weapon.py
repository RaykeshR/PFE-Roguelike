from item import Item
from category_weapon import CategoryWeapon
from rarity import Rarity

class Weapon(Item):
    """
    A class representing a weapon item.
    """
    def __init__(self, name: str, description: str, rarity:Rarity, damage: int, category: CategoryWeapon, range: float = 1.0, durability: int = 100):
        super().__init__(name, description, rarity)
        self.damage = damage
        self.category = category
        self.range = range
        self.durability = durability
    
    #### Getters and Setters ####
    
    def get_category(self) -> CategoryWeapon:
        return self.category

    def get_durability(self) -> int:
        return self.durability
    
    def get_damage(self) -> int:
        return self.damage
    
    def get_range(self) -> float:
        return self.range
    
    def set_category(self, category: CategoryWeapon):
        self.category = category

    def set_durability(self, durability: int):
        self.durability = durability

    def set_damage(self, damage: int):
        self.damage = damage

    def set_range(self, range: float):
        self.range = range
    

    #### Other Methods ####
    
    def get_is_broken(self) -> bool:
        """
        Check if the weapon is broken.
        Return True if durability is 0 or less, else False.
        """
        return self.durability <= 0
    
    def use(self):
        """
        Simulate using the weapon, reducing its durability.
        """
        if self.durability > 0:
            self.durability -= 1
            print(f"{self.name} used! Durability is now {self.durability}.")
        else:
            # if weapon is broken
            print(f"{self.name} is broken and cannot be used.")
    
    def repair(self, amount: int):
        """
        Repair the weapon, increasing its durability.
        """
        self.durability += amount
        print(f"{self.name} repaired! Durability is now {self.durability}.")


if __name__ == "__main__":
    sword = Weapon("Sword", "A sharp blade.", Rarity.LEGENDARY, 10, CategoryWeapon.MELEE)
    bow = Weapon("Bow", "A ranged weapon.",Rarity.LEGENDARY, 8, CategoryWeapon.DISTANCE, range=5.0)
    
    sword.use()
    bow.use()