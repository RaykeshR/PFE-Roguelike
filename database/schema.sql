-- Création de la table des clients
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

-- Création de la table des commandes
CREATE TABLE commandes (
    id SERIAL PRIMARY KEY,
    produit VARCHAR(100) NOT NULL,
    client_id INT REFERENCES clients(id)
);
