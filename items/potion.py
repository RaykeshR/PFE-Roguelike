from item import Item
from rarity import Rarity
from category_potion import CategoryPotion

class Potion(Item):
    """
    A class representing a potion item.
    Potency indicates the strength of the potion's effect.
    """
    def __init__(self, name: str, description: str, rarity:Rarity, category: CategoryPotion, potency: int, duration: int):
        super().__init__(name, description, rarity)
        self.category = category
        self.potency = potency
        self.duration = duration
    
    # def use(self, target):
    #     """
    #     Apply the potion's effect to the target.
    #     The actual implementation would depend on the game's mechanics.
    #     """
    #     if self.category == CategoryPotion.HEALTH:
    #         target.heal(self.potency)
    #     elif self.category == CategoryPotion.STRENGTH:
    #         target.increase_strength(self.potency, self.duration)
    #     elif self.category == CategoryPotion.SPEED:
    #         target.increase_speed(self.potency, self.duration)
    #     else:
    #         raise ValueError("Unknown potion category")