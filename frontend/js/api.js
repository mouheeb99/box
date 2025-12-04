// api.js - Module centralisé pour les appels API
const API_BASE = 'http://localhost:5000/api';

const API = {
    // ==========================================
    // BOXES
    // ==========================================
    
    /**
     * Récupère toutes les boxes
     */
    getAllBoxes: async () => {
        try {
            const response = await fetch(`${API_BASE}/boxes`);
            if (!response.ok) throw new Error('Erreur réseau');
            return await response.json();
        } catch (error) {
            console.error('Erreur getAllBoxes:', error);
            throw error;
        }
    },

    /**
     * Récupère une box spécifique
     */
    getBox: async (boxId) => {
        try {
            const response = await fetch(`${API_BASE}/boxes/${boxId}`);
            if (!response.ok) throw new Error('Box non trouvée');
            return await response.json();
        } catch (error) {
            console.error('Erreur getBox:', error);
            throw error;
        }
    },

    /**
     * Crée une nouvelle box
     */
    createBox: async (boxData) => {
        try {
            const response = await fetch(`${API_BASE}/boxes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(boxData)
            });
            if (!response.ok) throw new Error('Erreur création box');
            return await response.json();
        } catch (error) {
            console.error('Erreur createBox:', error);
            throw error;
        }
    },

    /**
     * Supprime une box
     */
    deleteBox: async (boxId) => {
        try {
            const response = await fetch(`${API_BASE}/boxes/${boxId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Erreur suppression box');
            return await response.json();
        } catch (error) {
            console.error('Erreur deleteBox:', error);
            throw error;
        }
    },

    // ==========================================
    // SIMULATION
    // ==========================================
    
    /**
     * Démarre la simulation pour une box
     */
    startSimulation: async (boxId, intervalle = 5) => {
        try {
            const response = await fetch(`${API_BASE}/boxes/${boxId}/simulation/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ intervalle })
            });
            if (!response.ok) throw new Error('Erreur démarrage simulation');
            return await response.json();
        } catch (error) {
            console.error('Erreur startSimulation:', error);
            throw error;
        }
    },

    /**
     * Arrête la simulation pour une box
     */
    stopSimulation: async (boxId) => {
        try {
            const response = await fetch(`${API_BASE}/boxes/${boxId}/simulation/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if (!response.ok) throw new Error('Erreur arrêt simulation');
            return await response.json();
        } catch (error) {
            console.error('Erreur stopSimulation:', error);
            throw error;
        }
    },

    // ==========================================
    // CONFIGURATION 3A
    // ==========================================
    
    /**
     * Envoie une trame 3A
     */
    sendTrame3A: async (trame) => {
        try {
            const response = await fetch(`${API_BASE}/config/3A`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ trame })
            });
            if (!response.ok) throw new Error('Erreur envoi trame 3A');
            return await response.json();
        } catch (error) {
            console.error('Erreur sendTrame3A:', error);
            throw error;
        }
    },

    /**
     * Valide une trame 3A sans l'envoyer
     */
    validateTrame3A: async (trame) => {
        try {
            const response = await fetch(`${API_BASE}/config/3A/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ trame })
            });
            if (!response.ok) throw new Error('Trame invalide');
            return await response.json();
        } catch (error) {
            console.error('Erreur validateTrame3A:', error);
            throw error;
        }
    },

    // ==========================================
    // HISTORIQUE
    // ==========================================
    
    /**
     * Récupère l'historique d'une box
     */
    getHistory: async (boxId, limit = 50) => {
        try {
            const response = await fetch(`${API_BASE}/boxes/${boxId}/history?limit=${limit}`);
            if (!response.ok) throw new Error('Erreur récupération historique');
            return await response.json();
        } catch (error) {
            console.error('Erreur getHistory:', error);
            throw error;
        }
    },

    // ==========================================
    // STATUS SYSTÈME
    // ==========================================
    
    /**
     * Récupère le statut global du système
     */
    getStatus: async () => {
        try {
            const response = await fetch(`${API_BASE}/status`);
            if (!response.ok) throw new Error('Erreur statut système');
            return await response.json();
        } catch (error) {
            console.error('Erreur getStatus:', error);
            throw error;
        }
    },

    // ==========================================
    // CAPTEURS & COMPTEURS DISPONIBLES
    // ==========================================
    
    /**
     * Liste des capteurs disponibles
     */
    getAvailableCapteurs: async () => {
        try {
            const response = await fetch(`${API_BASE}/capteurs/available`);
            if (!response.ok) throw new Error('Erreur récupération capteurs');
            return await response.json();
        } catch (error) {
            console.error('Erreur getAvailableCapteurs:', error);
            throw error;
        }
    },

    /**
     * Liste des compteurs disponibles
     */
    getAvailableCompteurs: async () => {
        try {
            const response = await fetch(`${API_BASE}/compteurs/available`);
            if (!response.ok) throw new Error('Erreur récupération compteurs');
            return await response.json();
        } catch (error) {
            console.error('Erreur getAvailableCompteurs:', error);
            throw error;
        }
    }
};

// Export pour utilisation dans d'autres fichiers
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}