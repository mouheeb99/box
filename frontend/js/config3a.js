// config3a.js - Logique du générateur de trames 3A

let capteurCounter = 0;
let relaisCounter = 0;
let compteurCounter = 0;

// ==========================================
// INITIALISATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Générateur 3A chargé');
    
    // Écouter les changements de type
    document.querySelectorAll('input[name="type"]').forEach(radio => {
        radio.addEventListener('change', changerType);
    });
    
    // Écouter les changements sur box-id
    document.getElementById('box-id').addEventListener('input', genererTrame);
    
    // Initialiser avec le type S
    changerType();
    
    // Ajouter un capteur par défaut
    ajouterCapteur();
});

// ==========================================
// CHANGEMENT DE TYPE
// ==========================================

function changerType() {
    const type = document.querySelector('input[name="type"]:checked').value;
    
    // Masquer toutes les sections
    document.getElementById('section-capteurs').style.display = 'none';
    document.getElementById('section-relais').style.display = 'none';
    document.getElementById('section-compteurs').style.display = 'none';
    
    // Afficher la section correspondante
    if (type === 'S') {
        document.getElementById('section-capteurs').style.display = 'block';
    } else if (type === 'O') {
        document.getElementById('section-relais').style.display = 'block';
    } else if (type === 'C') {
        document.getElementById('section-compteurs').style.display = 'block';
    }
    
    // Régénérer la trame
    genererTrame();
}

// ==========================================
// GESTION CAPTEURS (TYPE S)
// ==========================================

function ajouterCapteur() {
    capteurCounter++;
    const container = document.getElementById('capteurs-container');
    
    const capteurDiv = document.createElement('div');
    capteurDiv.className = 'capteur-form-group';
    capteurDiv.id = `capteur-${capteurCounter}`;
    
    capteurDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <strong>Capteur ${capteurCounter}</strong>
            <button type="button" class="btn btn-sm btn-danger" onclick="supprimerCapteur(${capteurCounter})">
                <i class="bi bi-x"></i>
            </button>
        </div>
        <div class="row">
            <div class="col-md-3">
                <label class="form-label">Type</label>
                <select class="form-select form-select-sm capteur-input" onchange="genererTrame()">
                    <option value="HT">HT - Température</option>
                    <option value="HM">HM - Humidité</option>
                    <option value="FM">FM - Fumée</option>
                    <option value="LM">LM - Luminosité</option>
                    <option value="PR">PR - Présence</option>
                    <option value="CT">CT - Contact</option>
                    <option value="SD">SD - Son</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Min</label>
                <input type="number" class="form-control form-control-sm capteur-input" value="0" onchange="genererTrame()">
            </div>
            <div class="col-md-3">
                <label class="form-label">Max</label>
                <input type="number" class="form-control form-control-sm capteur-input" value="100" onchange="genererTrame()">
            </div>
            <div class="col-md-3">
                <label class="form-label">Init</label>
                <input type="number" class="form-control form-control-sm capteur-input" value="50" onchange="genererTrame()">
            </div>
        </div>
    `;
    
    container.appendChild(capteurDiv);
    genererTrame();
}

function supprimerCapteur(id) {
    const capteurDiv = document.getElementById(`capteur-${id}`);
    if (capteurDiv) {
        capteurDiv.remove();
        genererTrame();
    }
}

// ==========================================
// GESTION RELAIS (TYPE O)
// ==========================================

function ajouterRelais() {
    relaisCounter++;
    const container = document.getElementById('relais-container');
    
    const relaisDiv = document.createElement('div');
    relaisDiv.className = 'capteur-form-group';
    relaisDiv.id = `relais-${relaisCounter}`;
    
    relaisDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <strong>Relais ${relaisCounter}</strong>
            <button type="button" class="btn btn-sm btn-danger" onclick="supprimerRelais(${relaisCounter})">
                <i class="bi bi-x"></i>
            </button>
        </div>
        <div class="row">
            <div class="col-md-6">
                <label class="form-label">Numéro</label>
                <input type="number" class="form-control form-control-sm relais-input" value="${relaisCounter}" min="1" onchange="genererTrame()">
            </div>
            <div class="col-md-6">
                <label class="form-label">État</label>
                <select class="form-select form-select-sm relais-input" onchange="genererTrame()">
                    <option value="0">0 - OFF</option>
                    <option value="1">1 - ON</option>
                </select>
            </div>
        </div>
    `;
    
    container.appendChild(relaisDiv);
    genererTrame();
}

function supprimerRelais(id) {
    const relaisDiv = document.getElementById(`relais-${id}`);
    if (relaisDiv) {
        relaisDiv.remove();
        genererTrame();
    }
}

// ==========================================
// GESTION COMPTEURS (TYPE C)
// ==========================================

function ajouterCompteur() {
    compteurCounter++;
    const container = document.getElementById('compteurs-container');
    
    const compteurDiv = document.createElement('div');
    compteurDiv.className = 'capteur-form-group';
    compteurDiv.id = `compteur-${compteurCounter}`;
    
    compteurDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <strong>Compteur ${compteurCounter}</strong>
            <button type="button" class="btn btn-sm btn-danger" onclick="supprimerCompteur(${compteurCounter})">
                <i class="bi bi-x"></i>
            </button>
        </div>
        <div class="row">
            <div class="col-md-6">
                <label class="form-label">Type</label>
                <select class="form-select form-select-sm compteur-input" onchange="genererTrame()">
                    <option value="EC">EC - Énergie (kWh)</option>
                    <option value="WC">WC - Eau (L)</option>
                    <option value="GC">GC - Gaz (m³)</option>
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label">Valeur</label>
                <input type="number" class="form-control form-control-sm compteur-input" value="0" onchange="genererTrame()">
            </div>
        </div>
    `;
    
    container.appendChild(compteurDiv);
    genererTrame();
}

function supprimerCompteur(id) {
    const compteurDiv = document.getElementById(`compteur-${id}`);
    if (compteurDiv) {
        compteurDiv.remove();
        genererTrame();
    }
}

// ==========================================
// GÉNÉRATION DE LA TRAME
// ==========================================

function genererTrame() {
    const boxId = document.getElementById('box-id').value.trim();
    const type = document.querySelector('input[name="type"]:checked').value;
    
    if (!boxId) {
        document.getElementById('trame-preview').innerHTML = '<span class="text-muted">Entrez un ID de box...</span>';
        return;
    }
    
    let trame = `3A;${boxId}`;
    
    if (type === 'S') {
        // Capteurs
        const capteurs = document.querySelectorAll('#capteurs-container .capteur-form-group');
        if (capteurs.length === 0) {
            document.getElementById('trame-preview').innerHTML = '<span class="text-warning">Ajoutez au moins un capteur</span>';
            return;
        }
        
        capteurs.forEach(capteurDiv => {
            const inputs = capteurDiv.querySelectorAll('.capteur-input');
            const typeCapteur = inputs[0].value;
            const min = inputs[1].value;
            const max = inputs[2].value;
            const init = inputs[3].value;
            trame += `;${typeCapteur};${min};${max};${init}`;
        });
        
        trame += `;S`;
        
    } else if (type === 'O') {
        // Relais
        const relais = document.querySelectorAll('#relais-container .capteur-form-group');
        if (relais.length === 0) {
            document.getElementById('trame-preview').innerHTML = '<span class="text-warning">Ajoutez au moins un relais</span>';
            return;
        }
        
        relais.forEach(relaisDiv => {
            const inputs = relaisDiv.querySelectorAll('.relais-input');
            const numero = inputs[0].value;
            const etat = inputs[1].value;
            trame += `;RL${numero};${etat}`;
        });
        
        trame += `;O`;
        
    } else if (type === 'C') {
        // Compteurs
        const compteurs = document.querySelectorAll('#compteurs-container .capteur-form-group');
        if (compteurs.length === 0) {
            document.getElementById('trame-preview').innerHTML = '<span class="text-warning">Ajoutez au moins un compteur</span>';
            return;
        }
        
        compteurs.forEach(compteurDiv => {
            const inputs = compteurDiv.querySelectorAll('.compteur-input');
            const typeCompteur = inputs[0].value;
            const valeur = inputs[1].value;
            trame += `;${typeCompteur};${valeur}`;
        });
        
        trame += `;C`;
    }
    
    document.getElementById('trame-preview').textContent = trame;
}

// ==========================================
// COPIER LA TRAME
// ==========================================

function copierTrame() {
    const trame = document.getElementById('trame-preview').textContent;
    
    if (!trame || trame.includes('...') || trame.includes('Entrez') || trame.includes('Ajoutez')) {
        showWarning('Aucune trame valide à copier');
        return;
    }
    
    navigator.clipboard.writeText(trame).then(() => {
        showSuccess('Trame copiée dans le presse-papier !');
    }).catch(err => {
        showError('Erreur lors de la copie');
        console.error(err);
    });
}

// ==========================================
// VALIDER LA TRAME
// ==========================================

async function validerTrame() {
    const trame = document.getElementById('trame-preview').textContent;
    
    if (!trame || trame.includes('...') || trame.includes('Entrez') || trame.includes('Ajoutez')) {
        showWarning('Veuillez générer une trame valide');
        return;
    }
    
    try {
        showLoading();
        
        const result = await API.validateTrame3A(trame);
        
        hideLoading();
        
        if (result.valid) {
            showSuccess('✅ Trame valide !');
            console.log('Configuration:', result.config);
        } else {
            showError('❌ Trame invalide : ' + result.error);
        }
        
    } catch (error) {
        hideLoading();
        showError('Erreur de validation : ' + error.message);
        console.error(error);
    }
}

// ==========================================
// ENVOYER LA TRAME
// ==========================================

async function envoyerTrame() {
    const trame = document.getElementById('trame-preview').textContent;
    
    if (!trame || trame.includes('...') || trame.includes('Entrez') || trame.includes('Ajoutez')) {
        showWarning('Veuillez générer une trame valide');
        return;
    }
    
    if (!confirm('Voulez-vous envoyer cette trame à l\'API ?')) {
        return;
    }
    
    try {
        showLoading();
        
        const result = await API.sendTrame3A(trame);
        
        hideLoading();
        
        if (result.success) {
            showSuccess(`✅ Configuration appliquée avec succès pour ${result.box_id} !`);
            console.log('Résultat:', result);
            
            // Proposer de voir la box
            setTimeout(() => {
                if (confirm('Voulez-vous voir la box créée/modifiée ?')) {
                    window.location.href = `box-detail.html?id=${result.box_id}`;
                }
            }, 1500);
        } else {
            showError('❌ Erreur : ' + result.error);
        }
        
    } catch (error) {
        hideLoading();
        showError('Erreur d\'envoi : ' + error.message);
        console.error(error);
    }
}

// ==========================================
// RÉINITIALISER
// ==========================================

function reinitialiser() {
    if (!confirm('Voulez-vous réinitialiser le formulaire ?')) {
        return;
    }
    
    // Vider box ID
    document.getElementById('box-id').value = '';
    
    // Réinitialiser type à S
    document.getElementById('type-s').checked = true;
    changerType();
    
    // Vider les conteneurs
    document.getElementById('capteurs-container').innerHTML = '';
    document.getElementById('relais-container').innerHTML = '';
    document.getElementById('compteurs-container').innerHTML = '';
    
    // Réinitialiser les compteurs
    capteurCounter = 0;
    relaisCounter = 0;
    compteurCounter = 0;
    
    // Ajouter un capteur par défaut
    ajouterCapteur();
    
    showSuccess('Formulaire réinitialisé');
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
    showAlert('success', message, 'check-circle');
}

function showError(message) {
    showAlert('danger', message, 'exclamation-triangle');
}

function showWarning(message) {
    showAlert('warning', message, 'exclamation-circle');
}

function showAlert(type, message, icon) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="bi bi-${icon}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.getElementById('alert-container');
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}