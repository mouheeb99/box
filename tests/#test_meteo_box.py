# test_meteo_box.py
import sys
import os
import urllib.request
import urllib.parse
import json
import time

# Ajouter explicitement le dossier racine au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("🌍 Test de la BoxMeteoReelle...")

# Votre clé API
API_KEY = "f58ca4297930d81bf794cadf1b20c443"

try:
    # Test 1: Créer une box météo via API
    print("\n1️⃣ Création d'une box météo pour Paris:")
    
    box_data = {
        "id": "PARIS_METEO_001",
        "ville": "Paris", 
        "api_key": API_KEY
    }
    
    data = json.dumps(box_data).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/boxes/meteo",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ {result['message']}")
        print(f"📍 Ville: {result['ville']}")
        print(f"🆔 ID: {result['id']}")
    
    # Test 2: Vérifier que la box apparaît dans la liste
    print("\n2️⃣ Vérification de la box dans la liste:")
    with urllib.request.urlopen("http://127.0.0.1:5000/api/boxes") as response:
        boxes = json.loads(response.read().decode('utf-8'))
        if "PARIS_METEO_001" in boxes:
            print("✅ Box météo trouvée dans la liste")
            box_info = boxes["PARIS_METEO_001"]
            print(f"🌡️ Température: {box_info['capteurs']['HT']}°C")
            print(f"💧 Humidité: {box_info['capteurs']['HM']}%")
            print(f"🌬️ Vent: {box_info['capteurs']['VT']} km/h")
        else:
            print("❌ Box météo non trouvée")
    
    # Test 3: Démarrer la simulation météo
    print("\n3️⃣ Démarrage de la simulation météo (15 secondes):")
    
    sim_data = json.dumps({"intervalle": 10}).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/boxes/PARIS_METEO_001/simulation/start",
        data=sim_data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ {result['message']}")
    
    # Attendre et observer l'évolution
    print("⏳ Observation des données météo réelles...")
    for i in range(3):
        time.sleep(5)
        
        with urllib.request.urlopen("http://127.0.0.1:5000/api/boxes/PARIS_METEO_001") as response:
            box_status = json.loads(response.read().decode('utf-8'))
            capteurs = box_status['capteurs']
            relais = box_status['relais']
            compteurs = box_status['compteurs']
            
            print(f"📊 Mesure {i+1}:")
            print(f"   🌡️ Température: {capteurs['HT']}°C")
            print(f"   💧 Humidité: {capteurs['HM']}%") 
            print(f"   🌬️ Vent: {capteurs['VT']} km/h")
            print(f"   ⚡ Relais: {relais}")
            print(f"   📈 Compteurs: EC={compteurs['EC']} WC={compteurs['WC']} GC={compteurs['GC']}")
            
            if 'meteo' in box_status:
                meteo_info = box_status['meteo']
                print(f"   🌍 Source: {meteo_info['source']} - Dernière MAJ: {meteo_info['derniere_maj']}")
    
    # Test 4: Arrêter la simulation
    print("\n4️⃣ Arrêt de la simulation:")
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/boxes/PARIS_METEO_001/simulation/stop",
        data=b'{}',
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ {result['message']}")
    
    # Test 5: Envoyer une trame manuelle
    print("\n5️⃣ Envoi d'une trame 3F avec données météo:")
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/boxes/PARIS_METEO_001/trames/3F",
        data=b'{}',
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"📡 Trame envoyée: {result['trame']}")
    
    print("\n✅ Test de la box météo terminé avec succès!")
    
except Exception as e:
    print(f"❌ Erreur pendant le test: {e}")
    import traceback
    traceback.print_exc()