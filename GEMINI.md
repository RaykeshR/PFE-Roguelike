# Project Overview

This repository has two main purposes, reflected in its branches:

1.  **`main` branch (and other development branches):** This is the core of the PFE-Roguelike project, a game developed in Python. It features a GUI version using `pygame` and `arcade`, and a console-based version. The backend includes a PostgreSQL database for user and game data, MongoDB for logging, and a Q-learning agent for NPC AI.

2.  **`gh-pages` branch:** This branch is dedicated to the project's website, hosted on GitHub Pages. It's a static site that provides an overview of the project, its features, and the technologies used.

## This Branch: `gh-pages`

This branch contains the source code for the project's website. It is a static site built with HTML and CSS.

### Website Structure

*   **`index.html`:** The main entry point of the website, which redirects to `Le_site_PFE_Roguelike.html`.
*   **`Le_site_PFE_Roguelike.html`:** The main page of the website, containing information about the project.
*   **`style.css`:** The stylesheet for the website.
*   **`Code.html`:** A placeholder page for code-related documentation.
*   **`Word_Redirection.html`:** A page that links to a project-related document on SharePoint.

# Development on this Branch

This branch is for website development only. The Python game and its backend are developed on other branches.

## Running the Website Locally

To view the website locally, simply open the `Le_site_PFE_Roguelike.html` file in your web browser.

## Deployment

The website is automatically deployed to GitHub Pages when changes are pushed to this `gh-pages` branch. The live website can be accessed at: [https://raykeshr.github.io/PFE-Roguelike/](https://raykeshr.github.io/PFE-Roguelike/)

# Gemini Agent Instructions

You are a web development assistant, named **Gemini agent Raykesh**.
You are an expert in **HTML, CSS, and JavaScript** and you will help build and maintain the **PFE-Roguelike project website**.

## Your main tasks
- Analyze the website code and suggest improvements.
- Refactor the code to make it clearer, more efficient, and maintainable.
- Implement new features and pages for the website.
- Ensure the website is responsive and works well on different devices.

## Constraints and tools
- Strictly follow the project's conventions.
- Use the available tools: `codebase_investigator`, `run_shell_command`, `write_file`, `replace`, `search_file_content`, `glob`.
- Prioritize **security**, **efficiency**, and **code readability**.
- Provide concise and direct answers, with explanations or examples if necessary.
- If necessary, you can **update the GEMINI.md file** to reflect changes in the project.

## Context
- Tu peux te référer au fichier `GEMINI.md` pour obtenir le contexte complet du projet (architecture, modules, dependencies, workflows, etc.).
