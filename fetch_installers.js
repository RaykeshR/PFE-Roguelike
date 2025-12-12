document.addEventListener('DOMContentLoaded', () => {
    const owner = 'RaykeshR';
    const repo = 'PFE-Roguelike';
    const deduplicateInstallers = true;

    // --- URLs de l'API GitHub ---
    const releasesApiUrl = `https://api.github.com/repos/${owner}/${repo}/releases`;
    const devBranchApiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/Output?ref=Dev-Raykesh`;

    // --- Sections HTML ---
    const nightlyInstallerSection = document.getElementById('nightly-installer-section');
    const devInstallersList = document.getElementById('dev-installers-list');

    // --- Messages de chargement initiaux ---
    if (devInstallersList) {
        devInstallersList.innerHTML = '<li>Chargement des versions de développement en cours...</li>';
    }
    if (nightlyInstallerSection) {
        nightlyInstallerSection.innerHTML = '<p>Chargement de la version Nightly en cours...</p>';
    }

    // --- Fonctions de fetch ---
    const fetchReleases = fetch(releasesApiUrl).then(response => {
        if (response.status === 404) return [];
        if (!response.ok) throw new Error(`Erreur de récupération des releases : ${response.statusText}`);
        return response.json();
    });

    const fetchDevFiles = fetch(devBranchApiUrl).then(response => {
        if (response.status === 404) return [];
        if (!response.ok) throw new Error(`Erreur de récupération des fichiers de dev : ${response.statusText}`);
        return response.json();
    });

    // --- Exécution des fetchs en parallèle ---
    Promise.all([fetchReleases, fetchDevFiles])
        .then(([releases, devFiles]) => {
            const releaseInstallerNames = new Set();
            let allInstallers = [];

            // 1. Traiter les releases pour les ajouter à la liste principale
            const releaseInstallers = releases
                .filter(r => !r.draft && r.assets.some(a => a.name.endsWith('.exe')))
                .map(release => {
                    const asset = release.assets.find(a => a.name.endsWith('.exe'));
                    if (!asset) return null;
                    
                    releaseInstallerNames.add(asset.name); // Pour la déduplication
                    
                    return {
                        name: asset.name,
                        url: asset.browser_download_url,
                        source: release.prerelease ? 'Pré-release' : 'Release',
                        tag: release.tag_name,
                        date: new Date(release.published_at),
                        isRelease: true
                    };
                })
                .filter(Boolean); // Nettoyer les releases sans asset .exe

            // 2. Traiter les fichiers de Dev-Raykesh
            let devInstallerFiles = Array.isArray(devFiles) ? devFiles.filter(file => file.name.endsWith('.exe')) : [];

            // 3. Gérer la version Nightly
            if (nightlyInstallerSection) {
                nightlyInstallerSection.innerHTML = ''; // Nettoyer le message de chargement
                
                // Trier pour trouver le plus récent
                devInstallerFiles.sort((a, b) => b.name.localeCompare(a.name)); 
                
                // La version Nightly est le dernier build de dev qui n'est PAS une release
                const latestNightly = devInstallerFiles.find(file => !releaseInstallerNames.has(file.name));

                if (latestNightly) {
                    const versionDiv = document.createElement('div');
                    versionDiv.classList.add('installer-version');
                    versionDiv.setAttribute('data-status', 'nightly');
                    
                    versionDiv.innerHTML = `
                        <span>Nightly (${latestNightly.name.replace(/Setup_PFE-Roguelike_|Setup_Roguia_|\.exe/g, '')})</span>
                        <a href="${latestNightly.download_url}" class="btn btn-primary" download title="Télécharger la dernière version de développement (Nightly)">Télécharger</a>
                    `;
                    nightlyInstallerSection.appendChild(versionDiv);
                } else {
                    nightlyInstallerSection.innerHTML = '<p>Aucune nouvelle version Nightly disponible (la dernière est une release).</p>';
                }
            }

            // 4. Mapper les fichiers de dev, en excluant les doublons si nécessaire
            const devBranchInstallers = (deduplicateInstallers ? devInstallerFiles.filter(file => !releaseInstallerNames.has(file.name)) : devInstallerFiles)
                .map(file => ({
                    name: file.name,
                    url: file.download_url,
                    source: 'Dev',
                    date: null, // Pas de date de publication pour les fichiers de dev
                    isRelease: false
                }));

            // 5. Fusionner, trier et afficher la liste de développement
            allInstallers = [...releaseInstallers, ...devBranchInstallers];
            
            // Trier par nom de fichier (qui contient la version), du plus récent au plus ancien
            allInstallers.sort((a, b) => b.name.localeCompare(a.name));

            if (devInstallersList) {
                devInstallersList.innerHTML = ''; // Nettoyer le message de chargement

                if (allInstallers.length === 0) {
                    devInstallersList.innerHTML = '<li>Aucun installeur de développement trouvé.</li>';
                } else {
                    allInstallers.forEach(installer => {
                        const listItem = document.createElement('li');
                        const versionDiv = document.createElement('div');
                        versionDiv.classList.add('installer-version');
                        
                        const status = installer.isRelease ? (installer.source === 'Release' ? 'stable' : 'prerelease') : 'unstable';
                        versionDiv.setAttribute('data-status', status);
                        
                        const span = document.createElement('span');
                        span.textContent = `${installer.name} (${installer.source})`;
                        
                        const link = document.createElement('a');
                        link.href = installer.url;
                        link.textContent = 'Télécharger';
                        link.classList.add('btn', installer.isRelease && status !== 'prerelease' ? 'btn-primary' : 'btn-secondary');
                        link.setAttribute('download', '');

                        versionDiv.appendChild(span);
                        versionDiv.appendChild(link);
                        listItem.appendChild(versionDiv);
                        devInstallersList.appendChild(listItem);
                    });
                }
            }
        })
        .catch(error => {
            console.error("Erreur lors de la récupération des installeurs :", error);
            if (devInstallersList) devInstallersList.innerHTML = '<li>Erreur lors du chargement des versions de développement.</li>';
            if (nightlyInstallerSection) nightlyInstallerSection.innerHTML = '<p>Erreur lors du chargement de la version Nightly.</p>';
        });
});
