from engine.game import menu_principal
from engine.graphical_game import graphical_menu_principal
from system.logging_setup import setup_json_logging
from dotenv import load_dotenv
import os

def main():
    """ Lance le jeu """
    logger = setup_json_logging()
    logger.info("Application démarrée")
    print("Bienvenue dans le jeu Roguelike !")
    try:
        if int(input("voulez vous "+"\x1b["+"31m"+"la version graphique ?"+"\x1b[90m"+" (1: oui / 0: non) : "))==0:
            print("\x1b[0m");menu_principal()
        else:
            print("\x1b[0m");graphical_menu_principal()
    except Exception as e:
        logger.error(f"Commande illégale : {e}")
        print("\x1b[0m");menu_principal()
if __name__ == "__main__": 
    dotenv_path = os.path.join(os.path.dirname(__file__), '.', 'database', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    main()
    