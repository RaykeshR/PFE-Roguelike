from rarity import Rarity

class Item:
    def __init__(self, name: str, description: str, rarity: Rarity):
        self.name = name
        self.description = description
        self.rarity = rarity