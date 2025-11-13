from engine.game import run_game
from system.logging_setup import setup_json_logging
from dotenv import load_dotenv
import os

def main():
    """ Lance le jeu """
    logger = setup_json_logging()
    logger.info("Application démarrée")
    print("Bienvenue dans le jeu Roguelike !")
    run_game()

if __name__ == "__main__": 
    dotenv_path = os.path.join(os.path.dirname(__file__), '.', 'database', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    main()
    