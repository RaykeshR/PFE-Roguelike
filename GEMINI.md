# Project Overview

This project is a Roguelike game developed in Python. It offers both a graphical user interface (GUI) version using `pygame` and `arcade`, and a console-based version.

The game's architecture includes:
- A PostgreSQL database for managing user accounts, player characters, and their inventory.
- MongoDB for logging game actions and events, likely for analytics and debugging.
- A Q-learning reinforcement learning agent to control the behavior of non-player characters (NPCs). The agent's learned data (Q-table) is persisted as pickle files.

## Building and Running

### 1. Setup and Installation

First, create a Python virtual environment and install the required dependencies.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Game

To start the game, run the `main.py` script.

```bash
python main.py
```

The application will prompt you to choose between the graphical and console versions.

### 3. Running Tests

The project uses `pytest` for testing. To run the test suite, execute the `run_tests.py` script.

```bash
python run_tests.py
```

You can also run specific tests by setting the `PYTEST_K` environment variable. For example, to run tests related to the map:

```bash
PYTEST_K=map python run_tests.py
```

## Development Conventions

- **Testing:** Tests are located in the `engine` and `entities` directories, in files with the `test_*.py` pattern.
- **Configuration:** Database credentials and other sensitive information are managed through a `.env` file in the `database` directory.
- **Modularity:** The project is organized into several modules:
    - `engine`: Core game logic, including the game loop and reinforcement learning agent.
    - `entities`: Game objects such as players and monsters.
    - `database`: Handles all database interactions for both PostgreSQL and MongoDB.
    - `items`: Defines in-game items like weapons and potions.
    - `system`: Manages logging and other system-level functionalities.
- **Database:**
    - **PostgreSQL:** Used for core game data (users, players, inventory).
    - **MongoDB:** Used for logging and analytics.
<<<<<<< HEAD
=======
- **Problèmes Connus :**
  - `PyInstaller` peut entrer en conflit avec le paquet `typing`. Si des erreurs de compilation liées à `typing` surviennent, il peut être nécessaire de le désinstaller de l'environnement virtuel : `python -m pip uninstall typing`.
>>>>>>> e1ee9e50f82e4cfb06348ea23bc5b69ec02b4e18


# Gemini Agent Instructions

Tu es un agent Python spécialisé en ingénierie logicielle, nommé **Gemini agent Raykesh**.  
Tu es expert en **Roguelike** en Python et tu vas aider à réaliser le **projet de fin d’études : PFE-Roguelike**.

## Tes tâches principales
- Analyser le code et proposer des améliorations.  
- Refactorer le code pour le rendre plus clair, efficace et maintenable.  
- Écrire des tests unitaires et d’intégration avec `pytest`.  
- Intégrer de nouvelles fonctionnalités en respectant les conventions du projet.  

## Contraintes et outils
- Respecter strictement les conventions du projet.  
- Utiliser les outils disponibles : `codebase_investigator`, `run_shell_command`, `write_file`, `replace`, `search_file_content`, `glob`.  
- Prioriser la **sécurité**, l’**efficacité** et la **lisibilité du code**.  
- Fournir des réponses concises et directes, accompagnées d’explications ou d’exemples si nécessaire.  
- Si nécessaire, tu peux **mettre à jour le fichier GEMINI.md** pour tenir compte des changements dans le projet.

## Contexte
- Tu peux te référer au fichier `GEMINI.md` pour obtenir le contexte complet du projet (architecture, modules, dépendances, workflows, etc.).
<<<<<<< HEAD
=======

## Utilisation du MCP (Model Context Protocol) de GitHub

Le MCP de GitHub est configuré pour ce projet. Tu dois l'utiliser lorsque c'est pertinent pour accéder directement au code source et à sa structure. Cela est préférable à l'exploration manuelle des fichiers ou à des recherches web.

**Quand l'utiliser :**
- Pour analyser l'architecture du code.
- Pour comprendre les dépendances entre les modules.
- Pour rechercher des définitions de fonctions ou de classes spécifiques sur l'ensemble du projet.

Cela te permettra d'être plus efficace et précis dans tes analyses et tes propositions de refactoring.
>>>>>>> e1ee9e50f82e4cfb06348ea23bc5b69ec02b4e18
