from engine.map import Map
from engine.player_controller import PlayerController


def main():
    """ Lance le jeu """
    print("Bienvenue dans le jeu Roguelike !")
    # Initialisation du jeu et boucle principale ici
    # print("Tout fonctionne !")

    game_map = Map()
    player = PlayerController(game_map)

    playing = True
    while playing:
        game_map.draw((player.x, player.y))
        print("Déplacez-vous avec ZQSD (ou X pour quitter)")

        move = input("> ").lower()
        if move == "z":
            player.move(0, -1)
        elif move == "s":
            player.move(0, 1)
        elif move == "q":
            player.move(-1, 0)
        elif move == "d":
            player.move(1, 0)
        elif move == "x":
            playing = False


if __name__ == "__main__":
    main()