document.addEventListener('DOMContentLoaded', () => {
    const owner = 'RaykeshR';
    const repo = 'PFE-Roguelike';
    
    // Config URLs
    const releasesApiUrl = `https://api.github.com/repos/${owner}/${repo}/releases`;
    const devBranchApiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/Output?ref=Dev-Raykesh`;

    const nightlySection = document.getElementById('nightly-installer-section');
    const devList = document.getElementById('dev-installers-list');

    // Messages de chargement
    if (nightlySection) nightlySection.innerHTML = '<p>Recherche de la dernière version...</p>';
    if (devList) devList.innerHTML = '<li>Chargement de l\'historique complet...</li>';

    // Fonction utilitaire : Formatage Taille
    function formatBytes(bytes, decimals = 2) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'Ko', 'Mo', 'Go'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
    }

    Promise.all([
        fetch(releasesApiUrl).then(res => res.ok ? res.json() : []),
        fetch(devBranchApiUrl).then(res => res.ok ? res.json() : [])
    ]).then(([releases, devFiles]) => {
        
        let allInstallers = [];
        const seenNames = new Set();

        // 1. TRAITEMENT DES RELEASES (GitHub)
        releases.forEach(r => {
            if (!r.draft) {
                // CORRECTION : On prend TOUS les exe, pas juste le premier (.find -> .filter)
                const exeAssets = r.assets.filter(a => a.name.endsWith('.exe') && (a.name.startsWith('Setup_PFE-Roguelike_v') || a.name.startsWith('Setup_Roguia_v')));
                
                exeAssets.forEach(asset => {
                    seenNames.add(asset.name);
                    allInstallers.push({
                        name: asset.name,
                        url: asset.browser_download_url,
                        source: r.prerelease ? 'Pré-release' : 'Release',
                        tag: r.tag_name, // Le tag (ex: v2.6.1)
                        title: r.name || r.tag_name, // Le titre de la release
                        size: asset.size,
                        downloads: asset.download_count,
                        // On préfère la date de mise à jour du fichier, sinon la date de publi de la release
                        date: new Date(asset.updated_at || r.published_at), 
                        uploader: asset.uploader ? asset.uploader.login : 'Inconnu',
                        isRelease: true,
                        isPre: r.prerelease // IMPORTANT : On stocke si c'est une pré-release
                    });
                });
            }
        });

        // 2. TRAITEMENT DES FICHIERS DEV (Dossier Output)
        if (Array.isArray(devFiles)) {
            devFiles.forEach(f => {
                if (f.name.endsWith('.exe') && (f.name.startsWith('Setup_PFE-Roguelike_v') || f.name.startsWith('Setup_Roguia_v')) && !seenNames.has(f.name)) {
                    allInstallers.push({
                        name: f.name,
                        url: f.download_url,
                        source: 'Branche Dev',
                        tag: 'Dev',
                        title: 'Build de développement',
                        size: f.size,
                        downloads: null,
                        date: new Date(), 
                        uploader: 'RaykeshR', // Par défaut pour la branche dev
                        isRelease: false,
                        isPre: true // Les fichiers dev sont considérés comme instables

                    });
                }
            });
        }

        // 3. TRI (Plus récent en haut)
        allInstallers.sort((a, b) => b.name.localeCompare(a.name));

        // --- FONCTION DE CRÉATION HTML (MODIFIÉE) ---
        // isTopBox = Vrai seulement pour la grosse case du haut
        // isLatest = Vrai si c'est le tout premier élément de la liste (le plus récent)
        const createInstallerHTML = (inst, isTopBox = false, isLatest = false) => {
            const sizeStr = formatBytes(inst.size);
            const dlStr = inst.downloads !== null ? ` • ⬇️ ${inst.downloads}` : '';
            const dateStr = inst.date.toLocaleDateString('fr-FR');
            
            // Tooltips
            const mainTooltip = `Titre : ${inst.title}\nDate MAJ : ${dateStr}\nUploader : ${inst.uploader}`;
            const btnTooltip = `Date : ${dateStr}\nTaille : ${sizeStr}`;

            // LOGIQUE DE COULEUR :
            // Si c'est la TopBox OU si c'est le dernier fichier (isLatest) -> Violet (Nightly)
            let statusAttr = 'unstable'; 

            if (isTopBox || isLatest) {
                statusAttr = 'nightly'; // Violet
            } else if (inst.isRelease && !inst.isPre) {
                statusAttr = 'stable';  // Vert (Uniquement pour les releases officielles non-pre)
            } else if (inst.isRelease && inst.isPre) {
                statusAttr = 'prerelease'; // Cyan (Pré-release GitHub)
            } 
            // Sinon reste 'unstable' (Cyan) pour les fichiers dev

            const div = document.createElement('div');
            div.className = 'installer-version';
            div.setAttribute('data-status', statusAttr);
            div.title = mainTooltip;

            div.innerHTML = `
                <div style="display:flex; flex-direction:column;">
                    <span style="font-weight:${isTopBox ? 'bold' : 'normal'};">
                        ${isTopBox ? `Dernière Version (${inst.name.replace('.exe', '')})` : inst.name} 
                        ${!isTopBox ? `<small>(${inst.source})</small>` : ''}
                    </span>
                    <span style="font-size:0.85em; opacity:0.8; margin-top:2px;">
                        ${sizeStr}${dlStr}
                    </span>
                </div>
                <a href="${inst.url}" class="btn ${isTopBox ? 'btn-primary' : 'btn-secondary'}" download title="${btnTooltip}">Télécharger</a>
            `;
            return div;
        };

        // 4. AFFICHER NIGHTLY (Top Box)
        if (nightlySection) {
            nightlySection.innerHTML = '';
            if (allInstallers.length > 0) {
                // On passe true pour isTopBox
                nightlySection.appendChild(createInstallerHTML(allInstallers[0], true, true));
            } else {
                nightlySection.innerHTML = '<p>Aucune version disponible.</p>';
            }
        }

        // 5. AFFICHER LISTE COMPLÈTE
        if (devList) {
            devList.innerHTML = '';
            if (allInstallers.length > 0) {
                allInstallers.forEach((inst, index) => {
                    const li = document.createElement('li');
                    // Si index == 0, c'est le dernier fichier (donc isLatest = true) -> Violet
                    const isLatest = (index === 0);
                    li.appendChild(createInstallerHTML(inst, false, isLatest));
                    devList.appendChild(li);
                });
            } else {
                devList.innerHTML = '<li>Aucun installeur trouvé.</li>';
            }
        }

    }).catch(err => {
        console.error("Erreur Fetch:", err);
        if (devList) devList.innerHTML = '<li>Erreur lors du chargement des données.</li>';
    });
});