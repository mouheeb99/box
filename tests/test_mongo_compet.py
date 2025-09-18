# test_mongo_complet.py
import sys
import os

# Ajouter le dossier parent au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from mongo.mongo_utils import mongo_manager

print("🧪 Test complet du module MongoDB...")

# Test 1: Sauvegarder une box
print("\n1️⃣ Test sauvegarde box:")
config_test = {
    "capteurs": ["HT", "HM", "FM"],
    "nb_relais": 2,
    "compteurs": {"EC": 1200},
    "type": "test"
}

success = mongo_manager.save_box_metadata("BOX_TEST_001", config_test)
print(f"✅ Box sauvegardée: {success}")

# Test 2: Sauvegarder des données capteurs
print("\n2️⃣ Test sauvegarde données capteurs:")
trame_data = {
    "box_id": "BOX_TEST_001",
    "trame_brute": "3F BOX_TEST_001 ; HT=23.5 ; HM=55.2 ; FM=0 ; RL1=1 ; RL2=0 ; EC=1200.5 ;",
    "data": {
        "capteurs": {
            "HT": 23.5,
            "HM": 55.2,
            "FM": 0
        },
        "relais": {
            "RL1": 1,
            "RL2": 0
        },
        "compteurs": {
            "EC": 1200.5
        }
    }
}

success = mongo_manager.save_sensor_data(trame_data)
print(f"✅ Données capteurs sauvegardées: {success}")

# Test 3: Enregistrer un log
print("\n3️⃣ Test enregistrement log:")
success = mongo_manager.log_event(
    level="INFO",
    source="test",
    message="Test complet MongoDB réussi",
    box_id="BOX_TEST_001",
    action="test_complet"
)
print(f"✅ Log enregistré: {success}")

# Test 4: Récupérer info box
print("\n4️⃣ Test récupération box:")
box_info = mongo_manager.get_box_info("BOX_TEST_001")
if box_info:
    print(f"✅ Box récupérée: {box_info['nom']} - Status: {box_info['status']}")
else:
    print("❌ Box non trouvée")

# Test 5: Récupérer historique capteurs
print("\n5️⃣ Test historique capteurs:")
history = mongo_manager.get_sensor_history("BOX_TEST_001", limit=5)
print(f"✅ Historique récupéré: {len(history)} enregistrements")

if history:
    derniere_mesure = history[0]
    print(f"🔍 Dernière mesure: HT={derniere_mesure['capteurs'].get('HT')}°C")

# Test 6: Lister toutes les box
print("\n6️⃣ Test liste toutes les box:")
all_boxes = mongo_manager.get_all_boxes()
print(f"✅ Total box dans MongoDB: {len(all_boxes)}")

for box in all_boxes:
    print(f"   📦 {box['_id']} - {box['status']} - {len(box['capteurs'])} capteurs")

print("\n🎉 Test complet terminé!")
print("🔍 Vérifiez dans MongoDB Compass:")
print("   - Database: iot_project")
print("   - Collections: boxes, sensor_data, logs")
print("   - Documents créés par ce test")