#!/usr/bin/env python3
"""
Script pour importer les items depuis un fichier CSV vers la base de données PostgreSQL.

Ce script est conçu pour être exécuté depuis le dossier 'tools'.
Il lit le fichier 'PFE-Roguelike/items/items.csv' et remplit la table 'items'
de la base de données.
"""
import sys
import os
import csv

# --- Configuration des imports ---
# 1. Obtenir le chemin du script actuel (tools/)
current_dir = os.path.dirname(__file__)
# 2. Remonter au dossier parent (PFE-Roguelike/)
project_root = os.path.abspath(os.path.join(current_dir, '..'))
# 3. Ajouter ce dossier parent au sys.path
sys.path.append(project_root)

# 4. Maintenant, on peut importer depuis 'database'
try:
    from database.db_sql import execute_query
except ImportError:
    print("Erreur: Impossible d'importer 'execute_query' depuis 'database.db_sql'.")
    print("Assurez-vous que le script est dans un dossier 'tools' et que 'database/db_sql.py' existe.")
    sys.exit(1)


# --- Fonctions utilitaires ---

def to_int(value, default=0):
    """Tente de convertir une chaîne en entier. Retourne 'default' en cas d'échec."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def to_float(value, default=0.0):
    """Tente de convertir une chaîne en float. Retourne 'default' en cas d'échec."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# --- Fonction principale ---

def importer_items():
    """
    Vide la table 'items' et la remplit depuis le fichier CSV.
    """
    print("Démarrage de l'importation des items...")
    
    # --- 1. Chemin vers le fichier CSV ---
    csv_path = os.path.join(project_root, 'items', 'items.csv')
    if not os.path.exists(csv_path):
        print(f"Erreur: Fichier CSV non trouvé à {csv_path}")
        return

    # --- 2. Vider la table (TRUNCATE) ---
    # RESTART IDENTITY remet l'auto-incrémentation de l'ID à 1.
    print("Nettoyage de la table 'items'...")
    try:
        execute_query("TRUNCATE TABLE items RESTART IDENTITY CASCADE;")
    except Exception as e:
        print(f"Erreur lors du nettoyage de la table 'items': {e}")
        return

    # --- 3. Définir la requête SQL ---
    # Doit correspondre à ta table 'items' (cf. init_db_sql.py)
    # Note: On n'insère pas 'id', car il est SERIAL (auto-généré).
    sql_insert = """
    INSERT INTO items (
        nom, description, rarity, item_type, 
        damage, defense, range, category, 
        durability, potency, duration
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    item_count = 0

    # --- 4. Lire le CSV et insérer ---
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            # DictReader utilise la première ligne comme en-têtes (keys)
            reader = csv.DictReader(f)
            
            for row in reader:
                # Préparer le tuple de paramètres dans le bon ordre
                params = (
                    row['name'],         # Correspond à 'nom' dans la BDD
                    row['description'],
                    row['rarity'],
                    row['type'],         # Correspond à 'item_type' dans la BDD
                    to_int(row['damage']),
                    to_int(row['defense']),
                    to_float(row['range']),
                    row['category'],
                    to_int(row['durability']),
                    to_int(row['potency']),
                    to_int(row['duration'])
                )
                
                # Exécuter la requête
                execute_query(sql_insert, params)
                item_count += 1

    except FileNotFoundError:
        print(f"Erreur: Fichier CSV non trouvé à {csv_path}")
        return
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV ou de l'insertion : {e}")
        print(f"Dernière ligne traitée (approximatif) : {row.get('name')}")
        return

    print(f"\n✅ Importation terminée.")
    print(f"{item_count} items ont été ajoutés à la base de données.")


if __name__ == "__main__":
    # Petit avertissement de sécurité
    print("ATTENTION : Ce script va vider (TRUNCATE) la table 'items'")
    print("avant de la re-remplir à partir de 'items.csv'.")
    
    # Convertir en minuscules et supprimer les espaces
    choice = input("Voulez-vous continuer ? (oui/non): ").strip().lower()
    
    if choice in ['o', 'oui', 'yes', 'y']:
        importer_items()
    else:
        print("Importation annulée.")