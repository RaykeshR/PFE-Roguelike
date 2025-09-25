from engine.map import Map


def main():
    """ Lance le jeu """
    print("Bienvenue dans le jeu Roguelike !")
    # Initialisation du jeu et boucle principale ici
    # print("Tout fonctionne !")

    game_map = Map()
    playing = True

    while playing:
        game_map.draw()
        print("Déplacez-vous avec ZQSD (ou X pour quitter)")

        move = input("> ").lower()
        if move == "z":
            game_map.move_player(0, -1)
        elif move == "s":
            game_map.move_player(0, 1)
        elif move == "q":
            game_map.move_player(-1, 0)
        elif move == "d":
            game_map.move_player(1, 0)
        elif move == "x":
            playing = False


if __name__ == "__main__":
    main()