// box-detail.js - Logique de la page détails box

let boxId = null;
let refreshInterval = null;

// ==========================================
// INITIALISATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Récupérer l'ID de la box depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    boxId = urlParams.get('id');
    
    if (!boxId) {
        showError('ID de box manquant dans l\'URL');
        document.getElementById('box-not-found').style.display = 'block';
        return;
    }
    
    // Charger les données
    loadBoxDetails();
    
    // Démarrer le rafraîchissement automatique
    startAutoRefresh();
});

// ==========================================
// CHARGEMENT DES DÉTAILS
// ==========================================

async function loadBoxDetails() {
    try {
        const box = await API.getBox(boxId);
        
        // Afficher le contenu
        document.getElementById('box-content').style.display = 'block';
        document.getElementById('box-not-found').style.display = 'none';
        
        // Mettre à jour le titre
        document.getElementById('box-id-title').textContent = boxId;
        
        // Mettre à jour les sections
        updateCapteurs(box.capteurs);
        updateRelais(box.relais);
        updateCompteurs(box.compteurs);
        updateSimulationStatus(box.simulation);
        
    } catch (error) {
        console.error('Erreur chargement box:', error);
        document.getElementById('box-not-found').style.display = 'block';
        document.getElementById('box-content').style.display = 'none';
    }
}

// ==========================================
// MISE À JOUR CAPTEURS
// ==========================================

function updateCapteurs(capteurs) {
    const container = document.getElementById('capteurs-container');
    
    if (!capteurs || Object.keys(capteurs).length === 0) {
        container.innerHTML = '<p class="text-muted">Aucun capteur configuré</p>';
        return;
    }
    
    container.innerHTML = '';
    
    Object.entries(capteurs).forEach(([capteurId, capteur]) => {
        const capteurDiv = document.createElement('div');
        capteurDiv.className = 'capteur-item';
        
        // Valeur actuelle
        const valeur = capteur.valeur;
        const unite = capteur.unite;
        const nom = capteur.nom;
        
        // Calculer le pourcentage pour la barre de progression
        let percentage = 50; // Par défaut
        let min = 0;
        let max = 100;
        
        // Si on a des plages définies
        if (capteur.plage) {
            min = capteur.plage.min;
            max = capteur.plage.max;
            percentage = ((valeur - min) / (max - min)) * 100;
        }
        
        // Déterminer la couleur de la barre
        let barColor = 'bg-primary';
        if (percentage > 80) {
            barColor = 'bg-danger';
        } else if (percentage > 60) {
            barColor = 'bg-warning';
        } else if (percentage < 20) {
            barColor = 'bg-info';
        }
        
        capteurDiv.innerHTML = `
            <div class="capteur-label">
                <span><strong>${capteurId}</strong> - ${nom}</span>
                <span class="capteur-value">${valeur.toFixed(1)} ${unite}</span>
            </div>
            <div class="progress">
                <div class="progress-bar ${barColor}" role="progressbar" 
                     style="width: ${percentage}%" 
                     aria-valuenow="${valeur}" 
                     aria-valuemin="${min}" 
                     aria-valuemax="${max}">
                    ${percentage.toFixed(0)}%
                </div>
            </div>
        `;
        
        container.appendChild(capteurDiv);
    });
}

// ==========================================
// MISE À JOUR RELAIS
// ==========================================

function updateRelais(relais) {
    const container = document.getElementById('relais-container');
    
    if (!relais || Object.keys(relais).length === 0) {
        container.innerHTML = '<p class="text-muted">Aucun relais configuré</p>';
        return;
    }
    
    container.innerHTML = '';
    
    Object.entries(relais).forEach(([relaisId, relaisData]) => {
        const etat = relaisData.etat;
        const isOn = etat === 1;
        
        const relaisDiv = document.createElement('div');
        relaisDiv.className = 'relais-item';
        
        relaisDiv.innerHTML = `
            <div>
                <span class="relais-label">${relaisId}</span>
                <span class="relais-status ${isOn ? 'on' : 'off'}">
                    ${isOn ? '✅ ON' : '⚪ OFF'}
                </span>
            </div>
            <button class="btn btn-sm ${isOn ? 'btn-warning' : 'btn-success'}" 
                    onclick="toggleRelais('${relaisId}', ${isOn ? 0 : 1})">
                <i class="bi bi-${isOn ? 'toggle-off' : 'toggle-on'}"></i>
                ${isOn ? 'Désactiver' : 'Activer'}
            </button>
        `;
        
        container.appendChild(relaisDiv);
    });
}

// ==========================================
// BASCULER RELAIS
// ==========================================

async function toggleRelais(relaisId, nouvelEtat) {
    try {
        showLoading();
        
        // Pour le moment, on ne peut pas changer directement via l'API
        // On pourrait ajouter un endpoint pour ça
        showInfo('Fonctionnalité de contrôle des relais à venir');
        
        hideLoading();
    } catch (error) {
        console.error('Erreur toggle relais:', error);
        showError('Erreur lors du changement d\'état du relais');
        hideLoading();
    }
}

// ==========================================
// MISE À JOUR COMPTEURS
// ==========================================

function updateCompteurs(compteurs) {
    const container = document.getElementById('compteurs-container');
    
    if (!compteurs || Object.keys(compteurs).length === 0) {
        container.innerHTML = '<p class="text-muted">Aucun compteur configuré</p>';
        return;
    }
    
    container.innerHTML = '';
    
    Object.entries(compteurs).forEach(([compteurId, compteurData]) => {
        const compteurDiv = document.createElement('div');
        compteurDiv.className = 'compteur-item';
        
        const valeur = compteurData.valeur;
        const unite = compteurData.unite;
        const nom = compteurData.nom;
        
        compteurDiv.innerHTML = `
            <div>
                <span class="compteur-label">${compteurId} - ${nom}</span>
            </div>
            <div>
                <span class="compteur-value">${valeur.toFixed(3)} ${unite}</span>
            </div>
        `;
        
        container.appendChild(compteurDiv);
    });
}

// ==========================================
// MISE À JOUR STATUT SIMULATION
// ==========================================

function updateSimulationStatus(simulation) {
    const statusBadge = document.getElementById('simulation-status');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const intervalleInput = document.getElementById('intervalle-input');
    
    const isActive = simulation && simulation.active === true;
    
    if (isActive) {
        statusBadge.textContent = 'Active';
        statusBadge.className = 'badge bg-success';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'block';
        intervalleInput.disabled = true;
        
        if (simulation.intervalle) {
            intervalleInput.value = simulation.intervalle;
        }
    } else {
        statusBadge.textContent = 'Arrêtée';
        statusBadge.className = 'badge bg-secondary';
        startBtn.style.display = 'block';
        stopBtn.style.display = 'none';
        intervalleInput.disabled = false;
    }
}

// ==========================================
// CONTRÔLE SIMULATION
// ==========================================

async function startSimulation() {
    try {
        showLoading();
        
        const intervalle = parseInt(document.getElementById('intervalle-input').value);
        
        if (intervalle < 1 || intervalle > 60) {
            showError('L\'intervalle doit être entre 1 et 60 secondes');
            hideLoading();
            return;
        }
        
        await API.startSimulation(boxId, intervalle);
        showSuccess('Simulation démarrée avec succès');
        
        // Recharger immédiatement
        await loadBoxDetails();
        
        hideLoading();
    } catch (error) {
        console.error('Erreur démarrage simulation:', error);
        showError('Erreur lors du démarrage de la simulation');
        hideLoading();
    }
}

async function stopSimulation() {
    try {
        showLoading();
        
        await API.stopSimulation(boxId);
        showSuccess('Simulation arrêtée avec succès');
        
        // Recharger immédiatement
        await loadBoxDetails();
        
        hideLoading();
    } catch (error) {
        console.error('Erreur arrêt simulation:', error);
        showError('Erreur lors de l\'arrêt de la simulation');
        hideLoading();
    }
}

// ==========================================
// SUPPRESSION BOX
// ==========================================

async function deleteBox() {
    if (!confirm(`Voulez-vous vraiment supprimer la box "${boxId}" ?`)) {
        return;
    }
    
    try {
        showLoading();
        await API.deleteBox(boxId);
        showSuccess(`Box "${boxId}" supprimée avec succès`);
        
        // Rediriger vers le dashboard après 1 seconde
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
        
    } catch (error) {
        console.error('Erreur suppression box:', error);
        showError(`Erreur lors de la suppression de "${boxId}"`);
        hideLoading();
    }
}

// ==========================================
// NAVIGATION HISTORIQUE
// ==========================================

function goToHistory() {
    window.location.href = `history.html?id=${boxId}`;
}

// ==========================================
// RAFRAÎCHISSEMENT AUTOMATIQUE
// ==========================================

function startAutoRefresh() {
    // Rafraîchir toutes les 3 secondes
    refreshInterval = setInterval(() => {
        loadBoxDetails();
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
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="bi bi-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="bi bi-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function showInfo(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="bi bi-info-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}