# start_10_simulations.py
import requests
import json
import time
import urllib.parse
import urllib.request

for i in range(1, 11):
    box_id = f"BOO_{i:03d}"
    interval = 2 + (i % 5)  # Intervalles variés: 2-6 secondes
    
    data = {"intervalle": interval}
    
    response = requests.post(
        f"http://localhost:5000/api/boxes/{box_id}/simulation/start",
        json=data
    )
    print(f"🚀 {box_id} démarrée (intervalle: {interval}s)")

time.sleep(200)

for i in range(1, 11):
        box_id = f"BOO_{i:03d}"
        print("\n3️⃣ Arrêt de la simulation...")
        req = urllib.request.Request(
        f"http://127.0.0.1:5000/api/boxes/{box_id}/simulation/stop",
        data=b'{}',
        headers={'Content-Type': 'application/json'}
    )    