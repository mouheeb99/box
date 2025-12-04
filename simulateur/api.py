from flask import Flask, request, jsonify
import threading
import sys
import os
from config_parser import parser_trame_3A, appliquer_configuration

# ✅ Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports
from box_manager import box_manager
from mongo.consumer_mongo import demarrer_consumer_mongo
from mongo.mongo_utils import mongo_manager  

app = Flask(__name__)

# ==========================================
# DÉMARRAGE AUTOMATIQUE DU CONSUMER MONGODB
# ==========================================

def demarrer_consumer_en_arriere_plan():
    """Démarre le consumer MongoDB dans un thread séparé"""
    print("🔄 Démarrage du consumer MongoDB en arrière-plan...")
    consumer_thread = threading.Thread(target=demarrer_consumer_mongo, daemon=True)
    consumer_thread.start()
    print("✅ Consumer MongoDB démarré en arrière-plan")

# Démarrer le consumer au lancement de l'API
demarrer_consumer_en_arriere_plan()

# ==========================================
# ENDPOINTS POUR LA GESTION DES BOX
# ==========================================

@app.route('/api/boxes', methods=['GET'])
def get_all_boxes():
    """Récupère toutes les box"""
    return jsonify(box_manager.get_all_status())

@app.route('/api/boxes/<box_id>', methods=['GET'])
def get_box(box_id):
    """Récupère une box spécifique"""
    status = box_manager.get_box_status(box_id)
    if status:
        return jsonify(status)
    else:
        return jsonify({"error": "Box non trouvée"}), 404

@app.route('/api/boxes', methods=['POST'])
def create_box():
    """Crée une nouvelle box"""
    data = request.json
    box_id = data.get('id')
    
    if not box_id:
        return jsonify({"error": "ID de box requis"}), 400
    
    # Configuration de la box
    config = {
        "capteurs": data.get('capteurs', []),
        "valeurs": data.get('valeurs', {}),
        "nb_relais": data.get('nb_relais', 2),
        "etats_relais": data.get('etats_relais', {}),
        "compteurs": data.get('compteurs', {})
    }
    
    success, message = box_manager.create_box(box_id, config)
    
    if success:
        return jsonify({"message": message, "id": box_id}), 201
    else:
        return jsonify({"error": message}), 400

@app.route('/api/boxes/<box_id>', methods=['DELETE'])
def delete_box(box_id):
    """Supprime une box"""
    success, message = box_manager.delete_box(box_id)
    
    if success:
        return jsonify({"message": message})
    else:
        return jsonify({"error": message}), 404

# ==========================================
# ENDPOINTS POUR LA SIMULATION
# ==========================================

@app.route('/api/boxes/<box_id>/simulation/start', methods=['POST'])
def start_simulation(box_id):
    """Démarre la simulation pour une box"""
    data = request.json or {}
    intervalle = data.get('intervalle')
    
    success, message = box_manager.start_simulation(box_id, intervalle)
    
    if success:
        return jsonify({"message": message})
    else:
        return jsonify({"error": message}), 400

@app.route('/api/boxes/<box_id>/simulation/stop', methods=['POST'])
def stop_simulation(box_id):
    """Arrête la simulation pour une box"""
    success, message = box_manager.stop_simulation(box_id)
    
    if success:
        return jsonify({"message": message})
    else:
        return jsonify({"error": message}), 400

# ==========================================
# ENDPOINTS POUR LES TRAMES
# ==========================================

@app.route('/api/boxes/<box_id>/trames/<trame_type>', methods=['POST'])
def send_specific_trame(box_id, trame_type):
    """Envoie une trame spécifique"""
    data = request.json or {}
    
    success, result = box_manager.send_specific_trame(box_id, trame_type, **data)
    
    if success:
        return jsonify(result)
    else:
        return jsonify({"error": result}), 400

# ==========================================
# ENDPOINTS D'INFORMATION
# ==========================================

@app.route('/api/capteurs/available', methods=['GET'])
def get_available_capteurs():
    """Liste des capteurs disponibles"""
    return jsonify(box_manager.get_available_capteurs())

@app.route('/api/compteurs/available', methods=['GET'])
def get_available_compteurs():
    """Liste des compteurs disponibles"""
    return jsonify(box_manager.get_available_compteurs())

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Statut général du système"""
    boxes = box_manager.get_all_status()
    total = len(boxes)
    running = sum(1 for box in boxes.values() if box.get('simulation', {}).get('active', False))
    
    return jsonify({
        "total_boxes": total,
        "running_simulations": running,
        "stopped_simulations": total - running,
        "boxes": list(boxes.keys())
    })
@app.route('/api/config/3A', methods=['POST'])
def recevoir_trame_3A():
    """Reçoit et applique une trame 3A"""
    try:
        if request.is_json:
            data = request.json
            trame = data.get('trame')
        else:
            trame = request.data.decode('utf-8').strip()
        
        if not trame:
            return jsonify({"error": "Trame manquante"}), 400
        
        config = parser_trame_3A(trame)
        
        # Vérification spéciale pour les capteurs (type S)
        if config['type'] == 'sensors':
            box = box_manager.get_box(config['box_id'])
            if box:
                return jsonify({
                    "success": False,
                    "error": f"Les capteurs de {config['box_id']} sont déjà définis. Impossible de modifier."
                }), 400
        
        success, message = appliquer_configuration(config, box_manager)
        
        if success:
            if mongo_manager.is_connected():
                mongo_manager.log_event(
                    level="INFO",
                    source="api",
                    message=f"Configuration 3A appliquée: {message}",
                    box_id=config['box_id'],
                    action="config_3A",
                    extra_data={"trame": trame, "config": config}
                )
            
            return jsonify({
                "success": True,
                "message": message,
                "box_id": config['box_id'],
                "type": config['type'],
                "config": config
            }), 200
        else:
            return jsonify({"success": False, "error": message}), 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/config/3A/validate', methods=['POST'])
def valider_trame_3A():
    """Valide une trame 3A sans l'appliquer"""
    try:
        if request.is_json:
            trame = request.json.get('trame')
        else:
            trame = request.data.decode('utf-8').strip()
        
        if not trame:
            return jsonify({"error": "Trame manquante"}), 400
        
        config = parser_trame_3A(trame)
        return jsonify({"valid": True, "config": config}), 200
    
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 400

# ==========================================
# PAGE D'ACCUEIL
# ==========================================

@app.route('/')
def index():
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    return f"""
    <html>
        <head><title>Simulateur IoT - Docker</title></head>
        <body>
            <h1>🏭 Simulateur de Box IoT (Docker)</h1>
            
            <p>Les trames sont automatiquement sauvegardées dans MongoDB</p>
            
            <h3>📊 Configuration:</h3>
            <ul>
                <li>Kafka: {kafka_servers}</li>
                <li>MongoDB: {mongo_uri}</li>
            </ul>
            
            <h2>API Endpoints:</h2>
            <ul>
                <li><code>GET /api/boxes</code> - Liste toutes les box</li>
                <li><code>POST /api/boxes</code> - Crée une nouvelle box</li>
                <li><code>GET /api/boxes/{{id}}</code> - Détails d'une box</li>
                <li><code>DELETE /api/boxes/{{id}}</code> - Supprime une box</li>
                <li><code>POST /api/boxes/{{id}}/simulation/start</code> - Démarre simulation</li>
                <li><code>POST /api/boxes/{{id}}/simulation/stop</code> - Arrête simulation</li>
                <li><code>POST /api/boxes/{{id}}/trames/{{type}}</code> - Envoie trame manuelle</li>
                <li><code>GET /api/capteurs/available</code> - Types de capteurs disponibles</li>
                <li><code>GET /api/compteurs/available</code> - Types de compteurs disponibles</li>
                <li><code>GET /api/status</code> - Statut global du système</li>
            </ul>
        </body>
    </html>
    """

# ==========================================
# DÉMARRAGE
# ==========================================

if __name__ == '__main__':
    print("🚀 Démarrage du serveur API (Docker)...")
    
    # Afficher la configuration
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    print(f"✅ Configuration:")
    print(f"   - Kafka: {kafka_servers}")
    print(f"   - MongoDB: {mongo_uri}")
    
    # Créer quelques box par défaut pour les tests AVEC COMPTEURS
    box_manager.create_box("box_001", {
        "capteurs": ["HT", "HM", "FM", "HT"],
        "nb_relais": 2,
        "compteurs": {
            "EC": 1200,    # Énergie: 1200 kWh
            "WC": 5000,    # Eau: 5000 L
            "GC": 300      # Gaz: 300 m³
        }
    })
    
    print("📍 API disponible sur le port 5000")
    print("💾 Consumer MongoDB actif - Sauvegarde automatique activée")
    
    # ✅ Configuration pour Docker
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)