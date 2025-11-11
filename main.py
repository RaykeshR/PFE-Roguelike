from engine.game import menu_principal
from system.logging_setup import setup_json_logging


def main():
    """ Lance le jeu """
    logger = setup_json_logging()
    logger.info("Application démarrée")
    print("Bienvenue dans le jeu Roguelike !")
    menu_principal()
if __name__ == "__main__":
    main()
    