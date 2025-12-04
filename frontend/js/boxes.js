// boxes.js - Logique de création de box

// ==========================================
// INITIALISATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Page création de box chargée');
    
    // Écouter la soumission du formulaire
    document.getElementById('create-box-form').addEventListener('submit', creerBox);
    
    // Écouter les changements sur les checkboxes des compteurs
    document.getElementById('compteur-ec').addEventListener('change', toggleCompteurInput);
    document.getElementById('compteur-wc').addEventListener('change', toggleCompteurInput);
    document.getElementById('compteur-gc').addEventListener('change', toggleCompteurInput);
});

// ==========================================
// TOGGLE INPUT COMPTEURS
// ==========================================

function toggleCompteurInput(event) {
    const checkbox = event.target;
    const compteurId = checkbox.value;
    const input = document.getElementById(`compteur-${compteurId.toLowerCase()}-value`);
    
    if (checkbox.checked) {
        input.disabled = false;
    } else {
        input.disabled = true;
    }
}

// ==========================================
// CRÉATION DE LA BOX
// ==========================================

async function creerBox(event) {
    event.preventDefault();
    
    try {
        showLoading();
        
        // Récupérer l'ID
        const boxId = document.getElementById('box-id').value.trim();
        
        if (!boxId) {
            showError('Veuillez entrer un ID de box');
            hideLoading();
            return;
        }
        
        // Récupérer les capteurs sélectionnés
        const capteurs = [];
        document.querySelectorAll('input[type="checkbox"][id^="capteur-"]:checked').forEach(checkbox => {
            capteurs.push(checkbox.value);
        });
        
        // Récupérer le nombre de relais
        const nbRelais = parseInt(document.getElementById('nb-relais').value);
        
        // Récupérer les compteurs
        const compteurs = {};
        if (document.getElementById('compteur-ec').checked) {
            compteurs.EC = parseFloat(document.getElementById('compteur-ec-value').value) || 1200;
        }
        if (document.getElementById('compteur-wc').checked) {
            compteurs.WC = parseFloat(document.getElementById('compteur-wc-value').value) || 5000;
        }
        if (document.getElementById('compteur-gc').checked) {
            compteurs.GC = parseFloat(document.getElementById('compteur-gc-value').value) || 300;
        }
        
        // Construire les états initiaux des relais (tous à OFF)
        const etatsRelais = {};
        for (let i = 1; i <= nbRelais; i++) {
            etatsRelais[i] = 0;
        }
        
        // Construire l'objet de configuration
        const boxData = {
            id: boxId,
            capteurs: capteurs,
            nb_relais: nbRelais,
            etats_relais: etatsRelais,
            compteurs: compteurs
        };
        
        console.log('Création de la box:', boxData);
        
        // Envoyer à l'API
        const result = await API.createBox(boxData);
        
        hideLoading();
        
        showSuccess(`✅ Box "${boxId}" créée avec succès !`);
        
        // Rediriger vers la page de détails après 1.5 secondes
        setTimeout(() => {
            window.location.href = `box-detail.html?id=${boxId}`;
        }, 1500);
        
    } catch (error) {
        hideLoading();
        console.error('Erreur création box:', error);
        
        // Vérifier si c'est une erreur de box déjà existante
        if (error.message && error.message.includes('existe')) {
            showError('Cette box existe déjà. Choisissez un autre ID.');
        } else {
            showError('Erreur lors de la création de la box');
        }
    }
}

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