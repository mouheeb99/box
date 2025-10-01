# start_10_simulations.py
import requests
import json

for i in range(1, 11):
    box_id = f"BOX_{i:03d}"
    interval = 2 + (i % 5)  # Intervalles variés: 2-6 secondes
    
    data = {"intervalle": interval}
    
    response = requests.post(
        f"http://localhost:5000/api/boxes/{box_id}/simulation/start",
        json=data
    )
    print(f"🚀 {box_id} démarrée (intervalle: {interval}s)")