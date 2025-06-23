# test_simulation_multiple.py
import urllib.request
import json
import time

print("🧪 Test simulation multiple box...")

def start_simulation(box_id, intervalle):
    data = json.dumps({"intervalle": intervalle}).encode('utf-8')
    req = urllib.request.Request(
        f"http://127.0.0.1:5000/api/boxes/{box_id}/simulation/start",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ {box_id}: {result['message']}")

def stop_simulation(box_id):
    req = urllib.request.Request(
        f"http://127.0.0.1:5000/api/boxes/{box_id}/simulation/stop",
        data=b'{}',
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"🛑 {box_id}: {result['message']}")

try:
    print("🚀 Démarrage de 2 simulations simultanées...")
    start_simulation("box_001", 2)  # Toutes les 2 secondes
    start_simulation("box_002", 4)  # Toutes les 4 secondes
    
    print("\n⏱️  Les 2 box envoient maintenant des trames en parallèle!")
    print("📊 box_001: une trame toutes les 2 secondes")  
    print("📊 box_002: une trame toutes les 4 secondes")
    
    
    time.sleep(100)
    
    print("\n🛑 Arrêt des simulations...")
    stop_simulation("box_001")
    stop_simulation("box_002")
    
except Exception as e:
    print(f"❌ Erreur: {e}")