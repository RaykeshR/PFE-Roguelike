from db_sql import execute_query

def initialiser_base_de_donnees():
    """Crée les tables si elles n'existent pas."""
    schema = """

    -- Effacer les tables existantes dans le bon ordre (inverse de la création)
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS inventaires CASCADE;
DROP TABLE IF EXISTS parties CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS joueurs CASCADE;
DROP TABLE IF EXISTS monster_templates CASCADE;
DROP TABLE IF EXISTS utilisateurs CASCADE;
    
    -- Table des utilisateurs (les personnes qui jouent)
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    mdp VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table des modèles de monstres
CREATE TABLE monster_templates (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL,
    base_pv INT DEFAULT 50,
    base_speed FLOAT DEFAULT 0.33,
    ia_profile VARCHAR(50) -- ex: 'agressif'
);

-- Table des joueurs/personnages (liés à un utilisateur)
CREATE TABLE joueurs (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT REFERENCES utilisateurs(id) ON DELETE CASCADE,
    nom VARCHAR(50) NOT NULL,
    niveau INT DEFAULT 1,
    xp INT DEFAULT 0,
    pv INT DEFAULT 100, -- points de vie
    q_table_path VARCHAR(255) UNIQUE, 
    created_at TIMESTAMP DEFAULT NOW()
);

-- Catégories d’objets (weapon, potion, armor, etc.)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL
);

-- Items disponibles dans le jeu
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    rarity VARCHAR(50),      -- common, rare, epic, legendary
    item_type VARCHAR(50),   -- 'weapon' ou 'potion'
    
    -- Stats (la plupart peuvent être 0)
    damage INT DEFAULT 0,
    defense INT DEFAULT 0,
    range FLOAT DEFAULT 0.0,
    category VARCHAR(50),    -- 'melee', 'distance', 'health', 'speed', etc.
    durability INT DEFAULT 0,
    potency INT DEFAULT 0,
    duration INT DEFAULT 0
);

-- Inventaire des joueurs (relation N-N entre joueurs et items)
CREATE TABLE inventaires (
    id SERIAL PRIMARY KEY,
    joueur_id INT REFERENCES joueurs(id) ON DELETE CASCADE,
    item_id INT REFERENCES items(id) ON DELETE CASCADE,
    quantite INT DEFAULT 1
);

-- Parties lancées (pour suivre la progression et la map générée)
CREATE TABLE parties (
    id SERIAL PRIMARY KEY,
    joueur_id INT REFERENCES joueurs(id) ON DELETE CASCADE,
    seed_generation BIGINT, -- pour régénérer la map procédurale
    date_debut TIMESTAMP DEFAULT NOW(),
    score INT DEFAULT 0,
    en_cours BOOLEAN DEFAULT TRUE
);

-- Rooms générées dans une partie (si vous voulez stocker des infos)
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    partie_id INT REFERENCES parties(id) ON DELETE CASCADE,
    room_number INT,        
    ennemis INT DEFAULT 0,  
    butin TEXT              
);

    """
    execute_query(schema)
    print(" Base de données initialisée.")
if __name__ == "__main__":
    initialiser_base_de_donnees()

