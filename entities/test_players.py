import os, sys, pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from entities.players import players
from entities.monster import Monster
from items import Weapon

def test_joueur_attaque():
    # player = players(name="Testeur", weapon=Weapon("Épée", damage=10))
    # monster = Monster(name="Gobelin", hp=30)
    # player.joueur_attaque(monster)
    # assert monster.hp == 20
    ... # TODO 