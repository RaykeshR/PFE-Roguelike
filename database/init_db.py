from db import execute_query

def initialiser_base_de_donnees():
    """Crée les tables si elles n'existent pas."""
    schema = """
    CREATE TABLE IF NOT EXISTS joueurs (
        id SERIAL PRIMARY KEY,
        nom VARCHAR(50) NOT NULL UNIQUE,
        niveau INT DEFAULT 1,
        xp INT DEFAULT 0
    );

    """
    execute_query(schema)
    print(" Base de données initialisée.")

def ajouter_joueur(nom):
    """Ajoute un nouveau joueur et retourne son ID."""
    # Le %s est un placeholder. psycopg2 le remplace par la valeur dans `params`
    # C'est une protection contre les injections SQL.
    query = "INSERT INTO joueurs (nom) VALUES (%s) RETURNING id;"
    params = (nom,)
    result = execute_query(query, params, fetch="one")
    if result:
        print(f"Joueur '{nom}' ajouté avec l'ID {result[0]}.")
        return result[0]
    return None

def get_joueur_par_nom(nom):
    """Récupère les informations d'un joueur."""
    query = "SELECT id, nom, niveau, xp FROM joueurs WHERE nom = %s;"
    params = (nom,)
    return execute_query(query, params, fetch="one")


# --- DÉBUT DU JEU ---
if __name__ == "__main__":
    initialiser_base_de_donnees()
    
    # Test d'ajout et de récupération
    nom_joueur = "Gandalf"
    joueur_id = ajouter_joueur(nom_joueur)
    
    # Il est possible que le joueur existe déjà, on le récupère
    if not joueur_id:
        print(f"Le joueur '{nom_joueur}' existe déjà. On récupère ses infos.")
        joueur_data = get_joueur_par_nom(nom_joueur)
        if joueur_data:
            joueur_id = joueur_data[0]
            print(f"Infos récupérées pour {joueur_data[1]} (ID: {joueur_data[0]})")