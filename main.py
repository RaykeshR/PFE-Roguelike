from engine.game import run_game
from system.logging_setup import setup_json_logging


def main():
    """ Lance le jeu """
    logger = setup_json_logging()
    logger.info("Application démarrée")
    print("Bienvenue dans le jeu Roguelike !")
    run_game()


if __name__ == "__main__":
    main()
    