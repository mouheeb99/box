# api.py - VERSION DOCKER
from flask import Flask, request, jsonify, send_from_directory  
import threading
import sys
import os
from config_parser import parser_trame_3A, appliquer_configuration

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

# ==========================================
# ENDPOINTS CONFIGURATION 3A
# ==========================================

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
# ENDPOINT HISTORIQUE (NOUVEAU)
# ==========================================

@app.route('/api/boxes/<box_id>/history', methods=['GET'])
def get_box_history(box_id):
    """
    Récupère l'historique des données d'une box
    Query params:
        - limit: nombre de résultats (default: 50, max: 200)
    """
    limit = request.args.get('limit', 50, type=int)
    
    if limit > 200:
        limit = 200
    
    if mongo_manager.is_connected():
        try:
            history = list(mongo_manager.box_data_collection
                .find({"box_id": box_id})
                .sort("timestamp", -1)
                .limit(limit))
            
            for item in history:
                item['_id'] = str(item['_id'])
            
            return jsonify(history)
        
        except Exception as e:
            print(f"❌ Erreur récupération historique: {e}")
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "MongoDB non connecté"}), 500

@app.route('/api/boxes/<box_id>/relais/<relais_id>', methods=['PUT'])
def set_relais_etat(box_id, relais_id):
    data = request.json
    etat = data.get('etat')

# ==========================================
# SERVIR LE FRONTEND (NOUVEAU)
# ==========================================

@app.route('/')
def serve_frontend():
    """Page d'accueil - Dashboard"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Servir les fichiers statiques (CSS, JS, images)"""
    try:
        return send_from_directory('../frontend', path)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# ==========================================
# DÉMARRAGE
# ==========================================

if __name__ == '__main__':
    print("🚀 Démarrage du serveur API (Docker)...")
    
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    
    print(f"✅ Configuration:")
    print(f"   - Kafka: {kafka_servers}")
    print(f"   - MongoDB: {mongo_uri}")
    
    box_manager.create_box("box_001", {
        "capteurs": ["HT", "HM", "FM", "HT"],
        "nb_relais": 2,
        "compteurs": {
            "EC": 1200,
            "WC": 5000,
            "GC": 300
        }
    })
    
    print("📍 API disponible sur le port 5000")
    print("💾 Consumer MongoDB actif - Sauvegarde automatique activée")
    print("🎨 Frontend disponible sur http://localhost:5000")
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)