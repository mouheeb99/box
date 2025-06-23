# test_simulation.py
import urllib.request
import urllib.parse
import json
import time

print("🧪 Test simulation automatique...")

try:
    # Étape 1: Voir les box disponibles
    print("1️⃣ Box disponibles:")
    with urllib.request.urlopen("http://127.0.0.1:5000/api/boxes") as response:
        boxes = json.loads(response.read().decode('utf-8'))
        for box_id in boxes.keys():
            print(f"  - {box_id}")
    
    # Étape 2: Démarrer simulation pour box_001
    print("\n2️⃣ Démarrage simulation box_001 (intervalle 3 secondes)...")
    
    data = json.dumps({"intervalle": 5}).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/boxes/box_001/simulation/start",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ {result['message']}")
    
    
    time.sleep(100)
    
    print("\n3️⃣ Arrêt de la simulation...")
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/boxes/box_001/simulation/stop",
        data=b'{}',
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ {result['message']}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")