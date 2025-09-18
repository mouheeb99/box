# test_mongo.py
from pymongo import MongoClient
from datetime import datetime

print("🧪 Test connexion MongoDB...")

try:
    # Connexion
    client = MongoClient('mongodb://localhost:27017/')
    
    # Test connexion
    client.admin.command('ping')
    print("✅ Connexion MongoDB réussie!")
    
    # Accès à la database
    db = client.iot_project
    print(f"✅ Database 'iot_project' accessible")
    
    # Test insertion
    test_doc = {
        "test": True,
        "timestamp": datetime.now(),
        "message": "Test depuis Python"
    }
    
    result = db.test_collection.insert_one(test_doc)
    print(f"✅ Document inséré avec ID: {result.inserted_id}")
    
    # Vérifier dans Compass
    print("🔍 Vérifiez dans MongoDB Compass : database 'iot_project' → collection 'test_collection'")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Vérifiez que MongoDB service est démarré")