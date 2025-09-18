# mongo_utils.py - Module MongoDB pour le simulateur IoT
from pymongo import MongoClient
from datetime import datetime
import json

class MongoManager:
    def __init__(self, uri="mongodb://localhost:27017", db_name="iot_project"):
        """Initialise la connexion MongoDB"""
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            
            # Test de connexion
            self.client.admin.command('ping')
            print(f"✅ Connexion MongoDB réussie - Database: {db_name}")
            
            # Références aux collections
            self.boxes_collection = self.db.boxes
            self.sensor_data_collection = self.db.sensor_data
            self.logs_collection = self.db.logs
            
        except Exception as e:
            print(f"❌ Erreur connexion MongoDB: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self):
        """Vérifie si la connexion est active"""
        return self.client is not None and self.db is not None
    
    # ==========================================
    # GESTION DES BOX
    # ==========================================
    
    def save_box_metadata(self, box_id, config, status="created"):
        """Sauvegarde les métadonnées d'une box"""
        if not self.is_connected():
            return False
        
        try:
            box_doc = {
                "_id": box_id,
                "nom": f"Box {box_id}",
                "type": config.get("type", "standard"),
                "capteurs": config.get("capteurs", []),
                "nb_relais": config.get("nb_relais", 2),
                "compteurs": list(config.get("compteurs", {}).keys()),
                "created_at": datetime.now(),
                "status": status,
                "last_seen": datetime.now(),
                "config": config
            }
            
            # Upsert (insert ou update)
            self.boxes_collection.replace_one(
                {"_id": box_id}, 
                box_doc, 
                upsert=True
            )
            
            print(f"💾 Box {box_id} sauvegardée dans MongoDB")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde box {box_id}: {e}")
            return False
    
    def update_box_status(self, box_id, status, last_seen=None):
        """Met à jour le statut d'une box"""
        if not self.is_connected():
            return False
        
        try:
            update_doc = {
                "status": status,
                "last_seen": last_seen or datetime.now()
            }
            
            result = self.boxes_collection.update_one(
                {"_id": box_id},
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                print(f"📊 Box {box_id} statut mis à jour: {status}")
                return True
            else:
                print(f"⚠️ Box {box_id} non trouvée pour mise à jour")
                return False
                
        except Exception as e:
            print(f"❌ Erreur mise à jour box {box_id}: {e}")
            return False
    
    def delete_box(self, box_id):
        """Supprime une box de MongoDB"""
        if not self.is_connected():
            return False
        
        try:
            result = self.boxes_collection.delete_one({"_id": box_id})
            
            if result.deleted_count > 0:
                print(f"🗑️ Box {box_id} supprimée de MongoDB")
                return True
            else:
                print(f"⚠️ Box {box_id} non trouvée pour suppression")
                return False
                
        except Exception as e:
            print(f"❌ Erreur suppression box {box_id}: {e}")
            return False
    
    # ==========================================
    # DONNÉES CAPTEURS
    # ==========================================
    
    def save_sensor_data(self, trame_data):
        """Sauvegarde les données d'une trame 3F"""
        if not self.is_connected():
            return False
        
        try:
            # Extraire les informations de la trame
            box_id = trame_data.get("box_id")
            data = trame_data.get("data", {})
            
            sensor_doc = {
                "box_id": box_id,
                "timestamp": datetime.now(),
                "capteurs": data.get("capteurs", {}),
                "relais": data.get("relais", {}),
                "compteurs": data.get("compteurs", {}),
                "trame_brute": trame_data.get("trame_brute", "")
            }
            
            result = self.sensor_data_collection.insert_one(sensor_doc)
            
            # Mettre à jour last_seen de la box
            self.update_box_status(box_id, "active")
            
            print(f"📊 Données capteurs sauvegardées: {box_id} - ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde données capteurs: {e}")
            return False
    
    # ==========================================
    # LOGS SYSTÈME
    # ==========================================
    
    def log_event(self, level, source, message, box_id=None, action=None, extra_data=None):
        """Enregistre un événement dans les logs"""
        if not self.is_connected():
            return False
        
        try:
            log_doc = {
                "timestamp": datetime.now(),
                "level": level,  # INFO, WARNING, ERROR
                "source": source,  # api, consumer, box_manager
                "message": message,
                "box_id": box_id,
                "action": action,  # create_box, start_simulation, etc.
                "extra_data": extra_data or {}
            }
            
            result = self.logs_collection.insert_one(log_doc)
            print(f"📝 Log enregistré: {level} - {message}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur enregistrement log: {e}")
            return False
    
    # ==========================================
    # REQUÊTES DE LECTURE
    # ==========================================
    
    def get_box_info(self, box_id):
        """Récupère les informations d'une box"""
        if not self.is_connected():
            return None
        
        try:
            box_doc = self.boxes_collection.find_one({"_id": box_id})
            if box_doc:
                # Convertir ObjectId en string pour JSON
                box_doc["_id"] = str(box_doc["_id"])
                box_doc["created_at"] = box_doc["created_at"].isoformat()
                box_doc["last_seen"] = box_doc["last_seen"].isoformat()
            
            return box_doc
            
        except Exception as e:
            print(f"❌ Erreur récupération box {box_id}: {e}")
            return None
    
    def get_all_boxes(self):
        """Récupère toutes les box"""
        if not self.is_connected():
            return []
        
        try:
            boxes = list(self.boxes_collection.find())
            
            # Convertir pour JSON
            for box in boxes:
                box["_id"] = str(box["_id"])
                box["created_at"] = box["created_at"].isoformat()
                box["last_seen"] = box["last_seen"].isoformat()
            
            return boxes
            
        except Exception as e:
            print(f"❌ Erreur récupération toutes les box: {e}")
            return []
    
    def get_sensor_history(self, box_id, limit=100):
        """Récupère l'historique des capteurs d'une box"""
        if not self.is_connected():
            return []
        
        try:
            history = list(
                self.sensor_data_collection
                .find({"box_id": box_id})
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            # Convertir pour JSON
            for record in history:
                record["_id"] = str(record["_id"])
                record["timestamp"] = record["timestamp"].isoformat()
            
            return history
            
        except Exception as e:
            print(f"❌ Erreur récupération historique {box_id}: {e}")
            return []
    
    def close_connection(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Connexion MongoDB fermée")

# Instance globale
mongo_manager = MongoManager()