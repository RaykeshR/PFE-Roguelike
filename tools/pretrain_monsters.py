import sys
import os
import random
import pickle
from collections import defaultdict

# Ajout du chemin racine pour importer les modules du moteur
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.map import Map
from entities.players import players
from entities.monster import Monster
from items import Weapon
from items.category_weapon import CategoryWeapon
from items.rarity import Rarity

def preentrainer_monstres(nb_episodes=1000):
    print(f"--- 🤖 Démarrage du pré-entraînement ({nb_episodes} combats) ---")
    
    # 1. Créer une Q-Table vide qui sera partagée par tous les monstres d'entraînement
    # On utilise un defaultdict pour gérer les nouveaux états automatiquement
    base_q_table = defaultdict(lambda: defaultdict(float))
    
    # Statistiques pour suivre les progrès
    victoires_monstre = 0
    
    for i in range(nb_episodes):
        # --- A. Mise en place de l'arène ---
        # Petite map pour forcer la rencontre
        game_map = Map(width=15, height=15, room_count=1, shared_q_data=base_q_table)
        
        # Le Bot (Joueur)
        # On lui donne beaucoup de PV pour que le combat dure un peu
        bot = players(name="TrainingBot", pv=100, game_map=game_map)
        bot.set_position(2, 2)
        # Arme du bot
        bot_weapon = Weapon("Épée d'entraînement", "...", Rarity.COMMON, damage=5, category=CategoryWeapon.MELEE)
        bot.inventory.append(bot_weapon)
        bot.equip_weapon_by_index(0)
        
        # Le Monstre (Apprenti)
        # IMPORTANT : On lui passe la base_q_table
        monster_weapon = Weapon("Griffes", "...", Rarity.COMMON, damage=5, category=CategoryWeapon.MELEE)
        monster = Monster(weapon=monster_weapon, pv=50, x=8, y=8, shared_q_data=base_q_table)
        game_map.enemies.append(monster)
        
        # --- B. La Boucle de Combat ---
        steps = 0
        max_steps = 100 # Limite pour éviter les boucles infinies
        
        while monster.get_is_alive() and bot.get_is_alive() and steps < max_steps:
            # 1. Le Bot joue (Simule un comportement varié)
            # On alterne les stratégies pour que le monstre apprenne à réagir à tout
            strat = random.choice(["Agressif", "Fuyard", "Aléatoire"])
            bot.train_bot(strat, monster)
            
            # 2. Le Monstre apprend (C'est ici que la Q-Table se remplit)
            # Il observe le bot, choisit une action, voit la récompense et met à jour la table
            monster.rl_step(game_map, (bot.x, bot.y))
            
            # (Optionnel) Si le bot attaque, le monstre perd des PV (géré dans train_bot)
            # (Optionnel) Si le monstre est sur le bot, il attaque (géré via rl_step/rewards ou logique jeu)
            
            steps += 1
            
        if not bot.get_is_alive():
            victoires_monstre += 1
            
        if (i+1) % 100 == 0:
            print(f"Épisode {i+1}/{nb_episodes} terminé. Taille Q-Table: {len(base_q_table)} états. Victoires Monstre: {victoires_monstre}")
            victoires_monstre = 0 # Reset compteur

    # --- C. Sauvegarde du Cerveau ---
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "base_q_table.pkl")
    
    # On convertit le defaultdict en dict normal pour le pickle
    with open(output_path, "wb") as f:
        pickle.dump(dict(base_q_table), f)
        
    print(f"✅ Pré-entraînement terminé. Modèle de base sauvegardé sous : {output_path}")

if __name__ == "__main__":
    preentrainer_monstres()