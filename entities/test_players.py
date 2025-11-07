import os, sys, pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from entities.players import players
from entities.monster import Monster
from items import Weapon, Potion
from engine.map import Map
from items.category_weapon import CategoryWeapon
from engine.game import _player_attack


def test_joueur_attaque():
    # player = players(name="Testeur", weapon=Weapon("Épée", damage=10))
    # monster = Monster(name="Gobelin", hp=30)
    # player.joueur_attaque(monster)
    # assert monster.hp == 20
    ... # TODO 

@pytest.fixture
def player_fixture():
    game_map = Map(width=60, height=26)
    player = players(
        name="test_player",
        pv=100,
        inventory=[],
        equiped_item=None,
        is_human=True,
        x=0.0,
        y=0.0,
        game_map=game_map
    )
    return player, game_map

def test_player_move(player_fixture):
    player, game_map = player_fixture
    old_pos = (player.x, player.y)
    player.move("d")  # droite
    assert (player.x, player.y) != old_pos, "Le joueur doit se déplacer"
    player.move("z")  # haut
    assert 0 <= player.x < game_map.width and 0 <= player.y < game_map.height

def test_equip_weapon(player_fixture):
    player, _ = player_fixture
    sword = Weapon(
        name="Épée test",
        damage=5,
        durability=5,
        category=CategoryWeapon.MELEE,
        description="Une épée de test",
        rarity="common"
    )
    player.inventory.append(sword)
    result = player.equip_weapon_by_index(0)
    assert result is True
    assert player.get_equipped_weapon() == sword

# def test_use_potion(player_fixture):
#     player, _ = player_fixture
#     potion = Potion(
#         name="Potion PV",
#         category="Health",
#         potency=20,
#         description="Potion de soin",
#         rarity="common",
#         duration=1
#     )
#     player.inventory.append(potion)
#     old_pv = player.get_hp()
#     # player.use_potion_by_index(0)
#     result = player.use_potion_by_index(0)
#     assert result is True
#     assert player.get_hp() == old_pv + 20

def test_attack_monster(player_fixture):
    player, game_map = player_fixture
    monster = type("Monster", (), {})()  # Mock minimal monster
    monster.x = 1
    monster.y = 0
    monster.get_pv = lambda: 10
    monster.set_pv = lambda v: setattr(monster, "_pv", v)
    monster.get_is_alive = lambda: getattr(monster, "_pv", 10) > 0
    monster.die = lambda drop_rate=1.0: None
    monster._pv = 10

    game_map.enemies.append(monster)

    # Arme équipée
    sword = Weapon(
        name="Épée test",
        damage=5,
        durability=5,
        category=CategoryWeapon.MELEE,
        description="Une épée de test",
        rarity="common"
    )
    player.inventory.append(sword)
    player.equip_weapon_by_index(0)

    _player_attack(player, game_map)

    assert monster._pv <= 10
    if not monster.get_is_alive():
        assert monster not in game_map.enemies

def test_inventory_listing(player_fixture):
    player, _ = player_fixture
    sword = Weapon(
        name="Épée test",
        damage=5,
        durability=5,
        category=CategoryWeapon.MELEE,
        description="Une épée de test",
        rarity="common"
    )
    potion = Potion(
        name="Potion PV",
        category="Health",
        potency=20,
        description="Potion de soin",
        rarity="common",
        duration=1
    )
    player.inventory.extend([sword, potion])
    inv = player.list_inventory()
    assert sword in inv
    assert potion in inv
