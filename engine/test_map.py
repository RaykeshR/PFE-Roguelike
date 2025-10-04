import os, sys, pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.map import Map


def test_rooms_have_margins_and_walls_intact():
    game_map = Map(width=60, height=26, room_count=6)
    # Tous les murs de salle doivent rester '#', pas remplacés arbitrairement par '.'
    for room in game_map.rooms:
        for j in range(room.height):
            for i in range(room.width):
                gx, gy = room.x + i, room.y + j
                if i == 0 or i == room.width - 1 or j == 0 or j == room.height - 1:
                    # On tolère les portes '+' sur les murs
                    assert game_map.tiles[gy][gx] in ('#', '+')


def test_corridors_connect_doors():
    game_map = Map(width=60, height=26, room_count=5)
    # Pour chaque connexion, s'assurer qu'il existe un chemin via '.' ou '+' entre les deux portes
    from collections import deque

    def neighbors(x, y):
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_map.width and 0 <= ny < game_map.height:
                yield nx, ny

    def passable(x, y):
        return game_map.tiles[y][x] in ('.', '+')

    for door_start, (_, door_end) in game_map.connections.items():
        sx, sy = door_start
        ex, ey = door_end
        q = deque([(sx, sy)])
        seen = { (sx, sy) }
        found = False
        while q:
            cx, cy = q.popleft()
            if (cx, cy) == (ex, ey):
                found = True
                break
            for nx, ny in neighbors(cx, cy):
                if (nx, ny) not in seen and passable(nx, ny):
                    seen.add((nx, ny))
                    q.append((nx, ny))
        assert found, f"Pas de chemin entre {door_start} et {door_end}"


def test_walkability_rules():
    game_map = Map(width=60, height=26, room_count=5)
    # On ne doit pas pouvoir marcher sur un mur '#'
    for y in range(game_map.height):
        for x in range(game_map.width):
            if game_map.tiles[y][x] == '#':
                assert not game_map.is_walkable(x, y)