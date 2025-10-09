import os
import psycopg2
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