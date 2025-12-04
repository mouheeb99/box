// history.js - Logique de la page historique

let boxId = null;
let currentData = [];

// ==========================================
// INITIALISATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Récupérer l'ID de la box depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    boxId = urlParams.get('id');
    
    if (!boxId) {
        showError('ID de box manquant dans l\'URL');
        return;
    }
    
    // Mettre à jour le titre
    document.getElementById('box-id-title').textContent = boxId;
    
    // Écouter les changements de limite
    document.querySelectorAll('input[name="limit"]').forEach(radio => {
        radio.addEventListener('change', loadHistory);
    });
    
    // Charger l'historique
    loadHistory();
});

// ==========================================
// CHARGEMENT DE L'HISTORIQUE
// ==========================================

async function loadHistory() {
    try {
        showLoading();
        
        const limit = parseInt(document.querySelector('input[name="limit"]:checked').value);
        
        console.log(`Chargement historique pour ${boxId}, limit=${limit}`);
        
        const history = await API.getHistory(boxId, limit);
        
        currentData = history;
        
        if (!history || history.length === 0) {
            showNoData();
            hideLoading();
            return;
        }
        
        // Masquer l'alerte "pas de données"
        document.getElementById('no-data-alert').style.display = 'none';
        
        // Mettre à jour le compteur
        document.getElementById('data-count').textContent = `${history.length} résultats`;
        
        // Construire le tableau
        buildTable(history);
        
        hideLoading();
        
    } catch (error) {
        console.error('Erreur chargement historique:', error);
        showError('Erreur lors du chargement de l\'historique');
        hideLoading();
    }
}

// ==========================================
// CONSTRUCTION DU TABLEAU
// ==========================================

function buildTable(data) {
    if (data.length === 0) {
        showNoData();
        return;
    }
    
    const thead = document.getElementById('table-header');
    const tbody = document.getElementById('history-tbody');
    
    // Vider le tableau
    thead.innerHTML = '<th>Timestamp</th>';
    tbody.innerHTML = '';
    
    // Récupérer les colonnes depuis le premier élément
    const firstRow = data[0];
    const columns = ['timestamp'];
    
    // Ajouter les colonnes capteurs
    if (firstRow.capteurs) {
        Object.keys(firstRow.capteurs).forEach(capteurId => {
            columns.push(`capteur_${capteurId}`);
            thead.innerHTML += `<th>${capteurId}</th>`;
        });
    }
    
    // Ajouter les colonnes relais
    if (firstRow.relais) {
        Object.keys(firstRow.relais).forEach(relaisId => {
            columns.push(`relais_${relaisId}`);
            thead.innerHTML += `<th>${relaisId}</th>`;
        });
    }
    
    // Ajouter les colonnes compteurs
    if (firstRow.compteurs) {
        Object.keys(firstRow.compteurs).forEach(compteurId => {
            columns.push(`compteur_${compteurId}`);
            thead.innerHTML += `<th>${compteurId}</th>`;
        });
    }
    
    // Remplir les lignes
    data.forEach(row => {
        const tr = document.createElement('tr');
        
        // Timestamp
        const tdTimestamp = document.createElement('td');
        const date = new Date(row.timestamp);
        tdTimestamp.textContent = formatDate(date);
        tr.appendChild(tdTimestamp);
        
        // Capteurs
        if (row.capteurs) {
            Object.values(row.capteurs).forEach(valeur => {
                const td = document.createElement('td');
                td.textContent = typeof valeur === 'number' ? valeur.toFixed(2) : valeur;
                tr.appendChild(td);
            });
        }
        
        // Relais
        if (row.relais) {
            Object.values(row.relais).forEach(etat => {
                const td = document.createElement('td');
                td.innerHTML = etat === 1 
                    ? '<span class="badge bg-success">ON</span>' 
                    : '<span class="badge bg-secondary">OFF</span>';
                tr.appendChild(td);
            });
        }
        
        // Compteurs
        if (row.compteurs) {
            Object.values(row.compteurs).forEach(valeur => {
                const td = document.createElement('td');
                td.textContent = typeof valeur === 'number' ? valeur.toFixed(3) : valeur;
                tr.appendChild(td);
            });
        }
        
        tbody.appendChild(tr);
    });
}

// ==========================================
// AFFICHER MESSAGE "PAS DE DONNÉES"
// ==========================================

function showNoData() {
    document.getElementById('no-data-alert').style.display = 'block';
    document.getElementById('data-count').textContent = '0 résultats';
    document.getElementById('history-tbody').innerHTML = '';
}

// ==========================================
// EXPORT CSV
// ==========================================

function exportCSV() {
    if (!currentData || currentData.length === 0) {
        showWarning('Aucune donnée à exporter');
        return;
    }
    
    try {
        // Construire le CSV
        let csv = '';
        
        // En-têtes
        const firstRow = currentData[0];
        const headers = ['timestamp'];
        
        if (firstRow.capteurs) {
            headers.push(...Object.keys(firstRow.capteurs));
        }
        if (firstRow.relais) {
            headers.push(...Object.keys(firstRow.relais));
        }
        if (firstRow.compteurs) {
            headers.push(...Object.keys(firstRow.compteurs));
        }
        
        csv += headers.join(',') + '\n';
        
        // Données
        currentData.forEach(row => {
            const values = [row.timestamp];
            
            if (row.capteurs) {
                values.push(...Object.values(row.capteurs));
            }
            if (row.relais) {
                values.push(...Object.values(row.relais));
            }
            if (row.compteurs) {
                values.push(...Object.values(row.compteurs));
            }
            
            csv += values.join(',') + '\n';
        });
        
        // Télécharger le fichier
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `historique_${boxId}_${Date.now()}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        showSuccess('CSV exporté avec succès !');
        
    } catch (error) {
        console.error('Erreur export CSV:', error);
        showError('Erreur lors de l\'export CSV');
    }
}

// ==========================================
// NAVIGATION
// ==========================================

function goBack() {
    if (boxId) {
        window.location.href = `box-detail.html?id=${boxId}`;
    } else {
        window.location.href = 'index.html';
    }
}

// ==========================================
// UTILITAIRES
// ==========================================

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

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
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="bi bi-${icon}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}