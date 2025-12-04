// dashboard.js - Logique du dashboard principal

let refreshInterval = null;

// ==========================================
// INITIALISATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard chargé');
    loadDashboard();
    startAutoRefresh();
});

// ==========================================
// CHARGEMENT DU DASHBOARD
// ==========================================

async function loadDashboard() {
    try {
        showLoading();
        
        // Récupérer toutes les boxes
        const boxes = await API.getAllBoxes();
        
        // Mettre à jour les statistiques
        updateStats(boxes);
        
        // Mettre à jour le tableau
        updateBoxesTable(boxes);
        
        hideLoading();
    } catch (error) {
        console.error('Erreur chargement dashboard:', error);
        showError('Impossible de charger le dashboard');
        hideLoading();
    }
}

// ==========================================
// MISE À JOUR STATISTIQUES
// ==========================================

function updateStats(boxes) {
    const boxArray = Object.values(boxes);
    const total = boxArray.length;
    const active = boxArray.filter(box => box.simulation?.active === true).length;
    const stopped = total - active;
    
    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-active').textContent = active;
    document.getElementById('stat-stopped').textContent = stopped;
}

// ==========================================
// MISE À JOUR TABLEAU BOXES
// ==========================================

function updateBoxesTable(boxes) {
    const tbody = document.getElementById('boxes-tbody');
    const noBoxesAlert = document.getElementById('no-boxes-alert');
    const table = document.getElementById('boxes-table');
    
    const boxArray = Object.entries(boxes);
    
    if (boxArray.length === 0) {
        // Aucune box
        noBoxesAlert.style.display = 'block';
        table.style.display = 'none';
        return;
    }
    
    // Afficher le tableau
    noBoxesAlert.style.display = 'none';
    table.style.display = 'table';
    
    // Vider le tbody
    tbody.innerHTML = '';
    
    // Remplir le tableau
    boxArray.forEach(([boxId, box]) => {
        const row = createBoxRow(boxId, box);
        tbody.appendChild(row);
    });
}

// ==========================================
// CRÉATION LIGNE TABLEAU
// ==========================================

function createBoxRow(boxId, box) {
    const tr = document.createElement('tr');
    
    // ID
    const tdId = document.createElement('td');
    tdId.innerHTML = `<strong>${boxId}</strong>`;
    
    // Capteurs
    const tdCapteurs = document.createElement('td');
    const capteursKeys = Object.keys(box.capteurs || {});
    tdCapteurs.textContent = capteursKeys.length > 0 ? capteursKeys.join(', ') : '-';
    
    // Relais
    const tdRelais = document.createElement('td');
    const relaisCount = Object.keys(box.relais || {}).length;
    tdRelais.textContent = relaisCount;
    
    // Compteurs
    const tdCompteurs = document.createElement('td');
    const compteursKeys = Object.keys(box.compteurs || {});
    tdCompteurs.textContent = compteursKeys.length > 0 ? compteursKeys.join(', ') : '-';
    
    // Simulation
    const tdSimulation = document.createElement('td');
    const isActive = box.simulation?.active === true;
    tdSimulation.innerHTML = isActive 
        ? '<span class="badge status-active"><i class="bi bi-play-fill"></i> Active</span>'
        : '<span class="badge status-stopped"><i class="bi bi-stop-fill"></i> Arrêtée</span>';
    
    // Actions
    const tdActions = document.createElement('td');
    tdActions.innerHTML = `
        <a href="box-detail.html?id=${boxId}" class="btn btn-sm btn-primary">
            <i class="bi bi-eye"></i> Voir
        </a>
        <button class="btn btn-sm btn-danger" onclick="deleteBoxConfirm('${boxId}')">
            <i class="bi bi-trash"></i>
        </button>
    `;
    
    // Assembler la ligne
    tr.appendChild(tdId);
    tr.appendChild(tdCapteurs);
    tr.appendChild(tdRelais);
    tr.appendChild(tdCompteurs);
    tr.appendChild(tdSimulation);
    tr.appendChild(tdActions);
    
    return tr;
}

// ==========================================
// SUPPRESSION BOX
// ==========================================

async function deleteBoxConfirm(boxId) {
    if (!confirm(`Voulez-vous vraiment supprimer la box "${boxId}" ?`)) {
        return;
    }
    
    try {
        showLoading();
        await API.deleteBox(boxId);
        showSuccess(`Box "${boxId}" supprimée avec succès`);
        await loadDashboard();
    } catch (error) {
        console.error('Erreur suppression box:', error);
        showError(`Erreur lors de la suppression de "${boxId}"`);
        hideLoading();
    }
}

// ==========================================
// RAFRAÎCHISSEMENT AUTOMATIQUE
// ==========================================

function startAutoRefresh() {
    // Rafraîchir toutes les 3 secondes
    refreshInterval = setInterval(() => {
        loadDashboard();
    }, 3000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Arrêter le rafraîchissement quand on quitte la page
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});

// ==========================================
// UTILITAIRES UI
// ==========================================

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showSuccess(message) {
    // Créer une alerte Bootstrap
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="bi bi-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    // Auto-fermeture après 3 secondes
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

function showError(message) {
    // Créer une alerte Bootstrap
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="bi bi-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    // Auto-fermeture après 5 secondes
    setTimeout(() => {
        alert.remove();
    }, 5000);
}