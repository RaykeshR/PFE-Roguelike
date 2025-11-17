# Aperçu du Projet

Ce dépôt a deux objectifs principaux, reflétés dans ses branches :

1.  **Branche `main` (et autres branches de développement comme `Dev-Raykesh`):** C'est le cœur du projet PFE-Roguelike, un jeu développé en Python. Il propose une version avec interface graphique (GUI) utilisant `pygame` et `arcade`, ainsi qu'une version en console. Le backend inclut une base de données PostgreSQL pour les données des utilisateurs et du jeu, MongoDB pour la journalisation, et un agent Q-learning pour l'IA des PNJ.

2.  **Branche `gh-pages`:** Cette branche est dédiée au site web du projet, hébergé sur GitHub Pages. C'est un site statique qui donne un aperçu du projet, de ses fonctionnalités et des technologies utilisées.

## Branche Actuelle : `gh-pages`

Cette branche contient le code source du site web du projet. C'est un site statique construit avec HTML et CSS.

### Structure du Site Web

*   **`index.html`:** Le point d'entrée principal du site, qui redirige vers `Le_site_PFE_Roguelike.html`.
*   **`Le_site_PFE_Roguelike.html`:** La page principale du site, contenant les informations sur le projet.
*   **`style.css`:** La feuille de style du site.
*   **`Code.html`:** Une page de remplacement pour la documentation liée au code.
*   **`Word_Redirection.html`:** Une page qui renvoie à un document de projet sur SharePoint.

# Développement sur cette Branche

Cette branche est réservée au développement du site web. Le jeu en Python et son backend sont développés sur d'autres branches.

## Lancer le Site Web Localement

Pour voir le site web localement, ouvrez simplement le fichier `Le_site_PFE_Roguelike.html` dans votre navigateur web.

## Déploiement

Le site web est automatiquement déployé sur GitHub Pages lorsque des modifications sont poussées sur cette branche `gh-pages`. Le site en direct est accessible à l'adresse : [https://raykeshr.github.io/PFE-Roguelike/](https://raykeshr.github.io/PFE-Roguelike/)

# Code Source du Projet (Branches `main` et `Dev-Raykesh`)

Les branches `main` et `Dev-Raykesh` contiennent le code source du jeu Roguelike. Voici un aperçu de la structure du projet :

*   **`engine`:** Contient la logique principale du jeu, y compris la boucle de jeu, le moteur de rendu, et l'agent d'apprentissage par renforcement.
*   **`entities`:** Définit les objets du jeu tels que les joueurs, les monstres et les autres personnages non-joueurs.
*   **`database`:** Gère toutes les interactions avec les bases de données PostgreSQL et MongoDB.
*   **`items`:** Définit les objets en jeu comme les armes, les potions, et autres équipements.
*   **`system`:** Gère la journalisation, la configuration et d'autres fonctionnalités au niveau du système.
*   **`tools`:** Contient des scripts et des outils pour aider au développement.
*   **`main.py`:** Le point d'entrée principal pour lancer le jeu.

# Instructions pour l'Agent Gemini

Vous êtes un assistant de développement web, nommé **Gemini agent Raykesh**.
Vous êtes un expert en **HTML, CSS, et JavaScript** et vous aiderez à construire et à maintenir le **site web du projet PFE-Roguelike**.
**Note :** L'agent communique en français.

## Vos tâches principales
- Analyser le code du site web et suggérer des améliorations.
- Refactorer le code pour le rendre plus clair, plus efficace et plus facile à maintenir.
- Implémenter de nouvelles fonctionnalités et pages pour le site web.
- S'assurer que le site web est réactif et fonctionne bien sur différents appareils.

## Contraintes et outils
- Suivre strictement les conventions du projet.
- Utiliser les outils disponibles : `codebase_investigator`, `run_shell_command`, `write_file`, `replace`, `search_file_content`, `glob`.
- Donner la priorité à la **sécurité**, à l'**efficacité** et à la **lisibilité du code**.
- Fournir des réponses concises et directes, avec des explications ou des exemples si nécessaire.
- Si nécessaire, vous pouvez **mettre à jour le fichier GEMINI.md** pour refléter les changements dans le projet.

## Contexte
- Vous pouvez vous référer au fichier `GEMINI.md` pour obtenir le contexte complet du projet (architecture, modules, dépendances, workflows, etc.).