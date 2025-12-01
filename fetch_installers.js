document.addEventListener('DOMContentLoaded', () => {
    const owner = 'RaykeshR';
    const repo = 'PFE-Roguelike';
    const branch = 'Dev-Raykesh';
    const path = 'Output';
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`;

    const installersList = document.getElementById('dev-installers-list');
    if (!installersList) {
        console.error("L'élément 'dev-installers-list' est introuvable.");
        return;
    }

    installersList.innerHTML = '<li>Chargement des versions de développement en cours...</li>';

    fetch(apiUrl)
        .then(response => {
            if (response.status === 404) {
                return []; // Le dossier n'existe pas ou est vide, traiter comme une liste vide
            }
            if (!response.ok) {
                throw new Error(`Erreur réseau : ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            installersList.innerHTML = ''; // Nettoyer le message de chargement

            const installerFiles = data.filter(file => 
                file.name.startsWith('Setup_PFE-Roguelike_v') && file.name.endsWith('.exe')
            );

            if (installerFiles.length === 0) {
                installersList.innerHTML = '<li>Aucun installeur trouvé sur la branche de développement.</li>';
                return;
            }

            // Trier les fichiers par nom pour avoir la dernière version en premier
            installerFiles.sort((a, b) => b.name.localeCompare(a.name));

            installerFiles.forEach(file => {
                const listItem = document.createElement('li');
                
                const versionDiv = document.createElement('div');
                versionDiv.classList.add('installer-version');
                versionDiv.setAttribute('data-status', 'unstable');
                
                const span = document.createElement('span');
                span.textContent = `${file.name} (Dev)`;
                
                const link = document.createElement('a');
                link.href = file.download_url;
                link.textContent = 'Télécharger';
                link.classList.add('btn', 'btn-secondary');
                link.setAttribute('download', '');

                versionDiv.appendChild(span);
                versionDiv.appendChild(link);
                listItem.appendChild(versionDiv);
                installersList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error("Erreur lors de la récupération des installeurs :", error);
            if (installersList) {
                installersList.innerHTML = "<li>Erreur lors du chargement des versions de développement.</li>";
            }
        });
});
