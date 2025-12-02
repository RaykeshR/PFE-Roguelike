document.addEventListener('DOMContentLoaded', () => {
    const owner = 'RaykeshR';
    const repo = 'PFE-Roguelike';
    const branch = 'Dev-Raykesh';
    const path = 'Output';
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${branch}`;
    const nightlyInstallerSection = document.getElementById('nightly-installer-section');

    const installersList = document.getElementById('dev-installers-list');
    if (!nightlyInstallerSection) {
        console.error("L'élément 'nightly-installer-section' est introuvable.");
        // Continue, as installersList might still be present
    }
    if (!installersList) {
        console.error("L'élément 'dev-installers-list' est introuvable.");
        return; // No need to continue if main list is missing
    }

    // Initial message for dev installers
    installersList.innerHTML = '<li>Chargement des versions de développement en cours...</li>';
    if (nightlyInstallerSection) {
        nightlyInstallerSection.innerHTML = '<p>Chargement de la version Nightly en cours...</p>';
    }

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
            installersList.innerHTML = ''; // Clear loading message for dev installers

            const installerFiles = data.filter(file =>
                file.name.startsWith('Setup_PFE-Roguelike_v') && file.name.endsWith('.exe')
            );

            if (installerFiles.length === 0) {
                installersList.innerHTML = '<li>Aucun installeur trouvé sur la branche de développement.</li>';
                if (nightlyInstallerSection) {
                    nightlyInstallerSection.innerHTML = '<p>Aucune version Nightly disponible.</p>';
                }
                return;
            }

            installerFiles.sort((a, b) => b.name.localeCompare(a.name)); // Sort descending for latest version first

            // Populate Nightly section
            if (nightlyInstallerSection && installerFiles.length > 0) {
                const latestFile = installerFiles[0];
                nightlyInstallerSection.innerHTML = ''; // Clear loading message

                const versionDiv = document.createElement('div');
                versionDiv.classList.add('installer-version');
                versionDiv.setAttribute('data-status', 'nightly');

                const span = document.createElement('span');
                span.textContent = `Nightly (${latestFile.name.replace('Setup_PFE-Roguelike_', '').replace('.exe', '')})`;

                const link = document.createElement('a');
                link.href = latestFile.download_url;
                link.textContent = 'Télécharger';
                link.classList.add('btn', 'btn-primary'); // Use primary for nightly too for prominence
                link.setAttribute('download', '');
                link.title = "Télécharger la dernière version de développement (Nightly)";

                versionDiv.appendChild(span);
                versionDiv.appendChild(link);
                nightlyInstallerSection.appendChild(versionDiv);
            } else if (nightlyInstallerSection) {
                nightlyInstallerSection.innerHTML = '<p>Aucune version Nightly disponible.</p>';
            }


            // Populate all dev installers list
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
            if (nightlyInstallerSection) {
                nightlyInstallerSection.innerHTML = '<p>Erreur lors du chargement de la version Nightly.</p>';
            }
        });
    });
