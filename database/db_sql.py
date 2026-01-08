import os
import psycopg2
import bcrypt
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

# --- Configuration du "Connection Pool" ---
# Un pool est un ensemble de connexions prêtes à l'emploi.
# C'est plus efficace que de se connecter/déconnecter à chaque fois.
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10, # Pour un projet étudiant, c'est largement suffisant
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME")
    )
    print(" Connection pool créé avec succès.")
except Exception as e:
    print(f" Erreur lors de la création du connection pool : {e}")
    connection_pool = None

# --- Fonctions pour interagir avec la base de données ---

def execute_query(query, params=None, fetch=None):
    """
    Fonction unique pour exécuter des requêtes.
    - query: La requête SQL (string).
    - params: Les paramètres pour éviter l'injection SQL (tuple).
    - fetch: "one", "all" ou None.
    """
    if not connection_pool:
        print(" Le pool de connexion n'est pas disponible.")
        return None

    conn = None
    try:
        conn = connection_pool.getconn()
        with conn.cursor() as cur:
            cur.execute(query, params)
            
            result = None
            # 1. Récupérer les résultats s'il y en a
            if fetch == "all":
                result = cur.fetchall()
            elif fetch == "one":
                result = cur.fetchone()
            
            # 2. Valider (Commit) si ce n'est PAS une simple lecture
            # On vérifie si la requête commence par SELECT
            is_select_query = query.strip().upper().startswith("SELECT")
            
            if not is_select_query:
                conn.commit()
            
            # 3. Retourner le résultat (qui peut être None)
            return result

    except Exception as e:
        print(f" Erreur lors de l'exécution de la requête : {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            connection_pool.putconn(conn)

def creer_utilisateur(username, mdp_en_clair):
    """Crée un nouvel utilisateur avec un mot de passe haché."""
    try:
        # Hacher le mot de passe
        sel = bcrypt.gensalt()
        mdp_hache = bcrypt.hashpw(mdp_en_clair.encode('utf-8'), sel)
        
        query = "INSERT INTO utilisateurs (username, mdp) VALUES (%s, %s) RETURNING id, username;"
        # On stocke le haché en string
        result = execute_query(query, (username, mdp_hache.decode('utf-8')), fetch="one")
        return result
    except Exception as e:
        print(f"Erreur : L'utilisateur '{username}' existe peut-être déjà. {e}")
        return None

def verifier_utilisateur(username, mdp_en_clair_a_tester):
    """Vérifie le mot de passe d'un utilisateur."""
    # 1. Récupérer l'utilisateur et son VRAI mot de passe haché
    query = "SELECT id, username, mdp FROM utilisateurs WHERE username = %s;"
    user_data = execute_query(query, (username,), fetch="one")
    
    if not user_data:
        print("Utilisateur non trouvé.")
        return None
        
    user_id, db_username, db_mdp_hache = user_data
    
    # 2. Comparer le mot de passe fourni avec le haché de la DB
    if bcrypt.checkpw(mdp_en_clair_a_tester.encode('utf-8'), db_mdp_hache.encode('utf-8')):
        print(f"Connexion réussie pour {db_username} (ID: {user_id}).")
        # Retourne les infos de l'utilisateur (sauf le mdp)
        return {'id': user_id, 'username': db_username}
    else:
        print("Mot de passe incorrect.")
        return None

# --- Fonctions pour les Joueurs (Personnages) ---

def get_joueurs_par_utilisateur_id(utilisateur_id):
    """Récupère tous les personnages (joueurs) d'un utilisateur."""
    query = "SELECT id, nom, niveau, xp, pv, q_table_path FROM joueurs WHERE utilisateur_id = %s;"
    joueurs = execute_query(query, (utilisateur_id,), fetch="all")
    return joueurs if joueurs else []


def ajouter_joueur(nom, utilisateur_id):
    """
    Ajoute un nouveau joueur, crée son chemin de Q-Table et le stocke.
    Retourne les infos du nouveau joueur.
    """
    
    # 1. Insérer le joueur et récupérer son NOUVEL ID
    # (Note: 'RETURNING id' fonctionne sur Postgres)
    query_insert = """
    INSERT INTO joueurs (nom, utilisateur_id, q_table_path) 
    VALUES (%s, %s, %s) 
    RETURNING id;
    """
    
    # On met un chemin temporaire
    temp_path = f"temp_path_for_{nom}"
    new_id = execute_query(query_insert, (nom, utilisateur_id, temp_path), fetch="one")
    
    if not new_id:
        print("Erreur lors de la création du joueur.")
        return None
        
    joueur_id = new_id[0]
    
    # 2. Créer le chemin unique basé sur l'ID
    q_table_path = f"models/qtables/joueur_{joueur_id}.pkl"
    
    # 3. Mettre à jour le joueur avec le chemin final
    query_update = "UPDATE joueurs SET q_table_path = %s WHERE id = %s;"
    execute_query(query_update, (q_table_path, joueur_id))
    
    print(f"✅ Joueur '{nom}' (ID: {joueur_id}) ajouté.")
    print(f"   -> Fichier IA assigné : {q_table_path}")
    
    return get_joueur_par_id(joueur_id) # (Vous aurez besoin de créer cette fonction)

def creer_utilisateur(username, mdp_en_clair):
    """Crée un nouvel utilisateur avec un mot de passe haché."""
    try:
        # Hacher le mot de passe
        sel = bcrypt.gensalt()
        mdp_hache = bcrypt.hashpw(mdp_en_clair.encode('utf-8'), sel)
        
        query = "INSERT INTO utilisateurs (username, mdp) VALUES (%s, %s) RETURNING id, username;"
        # On stocke le haché en string
        result = execute_query(query, (username, mdp_hache.decode('utf-8')), fetch="one")
        return result
    except Exception as e:
        print(f"Erreur : L'utilisateur '{username}' existe peut-être déjà. {e}")
        return None

def get_joueur_par_id(joueur_id):
    """Récupère un joueur spécifique par son ID."""
    query = "SELECT id, nom, niveau, xp, pv, q_table_path FROM joueurs WHERE id = %s;"
    joueur = execute_query(query, (joueur_id,), fetch="one")
    return joueur # Retourne un tuple

def update_joueur_stats(joueur_id, pv, xp, niveau):
    """
    Met à jour les statistiques d'un joueur (PV, XP, Niveau) dans la base de données.
    """
    # On s'assure que les PV ne sont pas négatifs, 
    # mais on garde la valeur telle quelle si le joueur est mort (pv <= 0)
    # Si le joueur est vivant mais n'a plus tous ses PV, il reprendra avec ces PV.
    current_pv = max(0, pv) 
    
    # Si tu veux que le joueur recommence toujours avec 100 PV, 
    # décommente la ligne suivante :
    # current_pv = 100 # Le joueur est soigné à chaque sauvegarde

    query = """
    UPDATE joueurs 
    SET 
        pv = %s, 
        xp = %s, 
        niveau = %s
    WHERE 
        id = %s;
    """
    
    try:
        execute_query(query, (current_pv, xp, niveau, joueur_id))
        print(f"Statistiques du joueur {joueur_id} mises à jour (PV={current_pv}, XP={xp}).")
    except Exception as e:
        print(f"Erreur lors de la mise à jour des stats du joueur {joueur_id}: {e}")


try:
    from items import Weapon, Potion, Rarity
    from items.category_weapon import CategoryWeapon
    from items.category_potion import CategoryPotion
    print("Classes d'items importées pour le chargement.")
except ImportError as e:
    print(f"Attention: Erreur d'import des classes items. Le chargement échouera. {e}")
    Weapon = None
    Potion = None


def sauvegarder_inventaire(joueur_id, inventaire_objets):
    """
    Sauvegarde l'inventaire complet d'un joueur.
    Efface l'ancien inventaire et insère le nouveau basé sur la liste d'objets.
    """
    
    # 1. Effacer l'ancien inventaire pour ce joueur
    query_delete = "DELETE FROM inventaires WHERE joueur_id = %s;"
    execute_query(query_delete, (joueur_id,))
    
    # 2. Compter les objets pour obtenir la quantité
    #    (Ex: [<Dague>, <Potion>, <Dague>] -> {id_dague: 2, id_potion: 1})
    item_counts = {}
    
    for item in inventaire_objets:
        
        item_db_id = getattr(item, 'db_id', None) 
        
        if item_db_id is not None:
            item_counts[item_db_id] = item_counts.get(item_db_id, 0) + 1
        else:
            # Affiche un avertissement si l'objet n'a pas d'ID
            nom_item = getattr(item, 'name', 'Objet Inconnu')
            print(f"AVERTISSEMENT: L'objet '{nom_item}' n'a pas de 'db_id' et ne sera pas sauvegardé.")

    # 3. Insérer les nouveaux objets comptés
    if not item_counts:
        # print(f"Inventaire du joueur {joueur_id} vide. Aucune sauvegarde d'item.")
        return

    query_insert = "INSERT INTO inventaires (joueur_id, item_id, quantite) VALUES (%s, %s, %s);"
    
    try:
        for item_id, quantite in item_counts.items():
            execute_query(query_insert, (joueur_id, item_id, quantite))
        
        print(f"Inventaire du joueur {joueur_id} sauvegardé ({len(item_counts)} types d'objets).")
    
    except Exception as e:
        print(f"ERREUR lors de l'insertion de l'inventaire pour le joueur {joueur_id}: {e}")
        # L'inventaire est maintenant effacé mais pas rempli. 
        # C'est un risque de cette méthode simple.




def charger_inventaire(joueur_id):
    """
    Charge l'inventaire d'un joueur, crée les objets Python (Weapon, Potion)
    et retourne une liste d'objets.
    """
    if Weapon is None or Potion is None:
        print("Erreur: Classes Item non chargées. Impossible de créer l'inventaire.")
        return []

    inventaire_objets = []
    
    # 1. Récupérer les items du joueur (ID et quantité)
    query_inv = "SELECT item_id, quantite FROM inventaires WHERE joueur_id = %s;"
    items_bruts = execute_query(query_inv, (joueur_id,), fetch="all")
    
    if not items_bruts:
        return [] # Inventaire vide

    # 2. Pour chaque item, récupérer ses détails complets
    # (On pourrait optimiser avec un JOIN, mais c'est plus clair ainsi)
    query_details = "SELECT * FROM items WHERE id = %s;"
    
    for item_id, quantite in items_bruts:
        details = execute_query(query_details, (item_id,), fetch="one")
        
        if not details:
            print(f"Erreur: Item ID {item_id} trouvé dans l'inventaire mais n'existe pas dans la table 'items'.")
            continue
        
        # 3. Créer les objets Python
        
        # Convertir le tuple de la BDD en dictionnaire pour plus de lisibilité
        # (ATTENTION: l'ordre DOIT correspondre à ta nouvelle table 'items')
        try:
            item_data = {
                'id': details[0],
                'nom': details[1],
                'description': details[2],
                'rarity': Rarity(details[3]) if details[3] else Rarity.COMMON, # Suppose que tu as un Enum Rarity
                'item_type': details[4],
                'damage': details[5],
                'defense': details[6],
                'range': details[7],
                'category': details[8],
                'durability': details[9],
                'potency': details[10],
                'duration': details[11]
            }
            
            # --- Factory (création de l'objet) ---
            obj = None
            if item_data['item_type'] == 'weapon':
                obj = Weapon(
                    name=item_data['nom'],
                    description=item_data['description'],
                    rarity=item_data['rarity'],
                    damage=item_data['damage'],
                    category=item_data['category'], # (Tu devras peut-être convertir string en Enum)
                    range=item_data['range'],
                    durability=item_data['durability'],
                    db_id=item_data['id'] # On attache l'ID de la BDD
                )
            elif item_data['item_type'] == 'potion':
                obj = Potion(
                    name=item_data['nom'],
                    description=item_data['description'],
                    rarity=item_data['rarity'],
                    category=item_data['category'], # (Idem, convertir string en Enum)
                    potency=item_data['potency'],
                    duration=item_data['duration'],
                    db_id=item_data['id']
                )

            # 4. Ajouter l'objet à la liste (autant de fois que la quantité)
            if obj:
                for _ in range(quantite):
                    inventaire_objets.append(obj)
            else:
                print(f"Type d'item inconnu: {item_data['item_type']} pour l'item {item_data['nom']}")

        except Exception as e:
            print(f"Erreur lors de la reconstruction de l'item ID {item_id}: {e}")
            print(f"Données brutes: {details}")

    print(f"Inventaire du joueur {joueur_id} chargé : {len(inventaire_objets)} objet(s).")
<<<<<<< HEAD
    return inventaire_objets
=======
    return inventaire_objets


def recuperer_modeles_items():
    """
    Récupère la liste de tous les items définis dans la base de données SQL.
    Retourne une liste de dictionnaires utilisables par le jeu.
    """
    query = "SELECT * FROM items;"
    items_bruts = execute_query(query, fetch="all")
    
    if not items_bruts:
        print("Aucun item trouvé dans la base de données.")
        return []

    items_propres = []
    for row in items_bruts:
        # Mapping des colonnes (basé sur init_db_sql.py)
        # 0:id, 1:nom, 2:description, 3:rarity, 4:item_type, 
        # 5:damage, 6:defense, 7:range, 8:category, 
        # 9:durability, 10:potency, 11:duration
        item_data = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'rarity': row[3],
            'type': row[4],
            'damage': row[5],
            'defense': row[6],
            'range': row[7],
            'category': row[8],
            'durability': row[9],
            'potency': row[10],
            'duration': row[11]
        }
        items_propres.append(item_data)
        
    return items_propres
>>>>>>> e1ee9e50f82e4cfb06348ea23bc5b69ec02b4e18
