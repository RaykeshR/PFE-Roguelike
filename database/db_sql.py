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
    - fetch: "one", "all" ou None. Si None, c'est une requête d'écriture (INSERT, UPDATE, CREATE).
    """
    if not connection_pool:
        print(" Le pool de connexion n'est pas disponible.")
        return None

    conn = None
    try:
        # Récupère une connexion depuis le pool
        conn = connection_pool.getconn()
        # 'with' s'assure que le curseur est bien fermé après usage
        with conn.cursor() as cur:
            cur.execute(query, params)
            
            # Si c'est une requête de LECTURE
            if fetch == "all":
                return cur.fetchall()
            if fetch == "one":
                return cur.fetchone()
            
            # Si c'est une requête d'ÉCRITURE, on valide la transaction
            conn.commit()

    except Exception as e:
        print(f" Erreur lors de l'exécution de la requête : {e}")
        # Si une erreur survient, annule la transaction
        if conn:
            conn.rollback()
        return None
    finally:
        # Redonne la connexion au pool pour qu'elle soit réutilisée
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