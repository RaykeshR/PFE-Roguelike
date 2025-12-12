document.addEventListener('DOMContentLoaded', () => {
    const owner = 'RaykeshR';
    const repo = 'PFE-Roguelike';
    
    // Config
    const releasesApiUrl = `https://api.github.com/repos/${owner}/${repo}/releases`;
    const devBranchApiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/Output?ref=Dev-Raykesh`;

    const nightlySection = document.getElementById('nightly-installer-section');
    const devList = document.getElementById('dev-installers-list');

    // Messages de chargement
    if (nightlySection) nightlySection.innerHTML = '<p>Recherche de la dernière version...</p>';
    if (devList) devList.innerHTML = '<li>Chargement de l\'historique complet...</li>';

    Promise.all([
        fetch(releasesApiUrl).then(res => res.ok ? res.json() : []),
        fetch(devBranchApiUrl).then(res => res.ok ? res.json() : [])
    ]).then(([releases, devFiles]) => {
        
        let allInstallers = [];
        const seenNames = new Set();

        // 1. Ajouter TOUS les assets des RELEASES
        releases.forEach(r => {
            if (!r.draft) {
                // CORRECTION : On prend TOUS les exe, pas juste le premier (.find -> .filter)
                const exeAssets = r.assets.filter(a => a.name.endsWith('.exe'));
                
                exeAssets.forEach(asset => {
                    seenNames.add(asset.name);
                    allInstallers.push({
                        name: asset.name,
                        url: asset.browser_download_url,
                        source: r.prerelease ? 'Pré-release' : 'Release',
                        isRelease: true
                    });
                });
            }
        });

        // 2. Ajouter les FICHIERS DEV (si pas déjà présents)
        if (Array.isArray(devFiles)) {
            devFiles.forEach(f => {
                if (f.name.endsWith('.exe') && !seenNames.has(f.name)) {
                    allInstallers.push({
                        name: f.name,
                        url: f.download_url,
                        source: 'Branche Dev',
                        isRelease: false
                    });
                }
            });
        }

        // 3. TRIER (Le plus récent en premier par nom)
        // Cela va mettre v2.6.1.16 en premier, et v2.6.1.15 juste après
        allInstallers.sort((a, b) => b.name.localeCompare(a.name));

        // 4. AFFICHER NIGHTLY (Le Top 1 absolu)
        if (nightlySection) {
            nightlySection.innerHTML = '';
            if (allInstallers.length > 0) {
                const latest = allInstallers[0];
                const div = document.createElement('div');
                div.className = 'installer-version';
                div.setAttribute('data-status', 'nightly');
                div.innerHTML = `
                    <span>Dernière Version (${latest.name.replace('.exe', '')})</span>
                    <a href="${latest.url}" class="btn btn-primary" download>Télécharger</a>
                `;
                nightlySection.appendChild(div);
            } else {
                nightlySection.innerHTML = '<p>Aucune version disponible.</p>';
            }
        }

        // 5. AFFICHER LA LISTE COMPLÈTE
        if (devList) {
            devList.innerHTML = '';
            if (allInstallers.length > 0) {
                allInstallers.forEach(inst => {
                    const li = document.createElement('li');
                    const div = document.createElement('div');
                    div.className = 'installer-version';
                    div.setAttribute('data-status', inst.isRelease ? (inst.source === 'Release' ? 'stable' : 'prerelease') : 'unstable');
                    
                    div.innerHTML = `
                        <span>${inst.name} <small>(${inst.source})</small></span>
                        <a href="${inst.url}" class="btn btn-secondary" download>Télécharger</a>
                    `;
                    li.appendChild(div);
                    devList.appendChild(li);
                });
            } else {
                devList.innerHTML = '<li>Aucun installeur trouvé.</li>';
            }
        }

    }).catch(err => {
        console.error("Erreur lors de la récupération des installeurs:", err);
        if (nightlySection) nightlySection.innerHTML = '<p>Erreur de chargement.</p>';
        if (devList) devList.innerHTML = '<li>Erreur lors du chargement de l\'historique.</li>';
    });
});
