# create_10_boxes.py
import requests
import json

for i in range(1, 11):
    box_id = f"BOX_{i:03d}"
    data = {
        "id": box_id,
        "capteurs": ["HT", "HM", "LM"],
        "nb_relais": 2,
        "compteurs": {"EC": 1000 + i*100}
    }
    
    response = requests.post(
        "http://localhost:5000/api/boxes",
        json=data
    )
    print(f"✅ {box_id} créée: {response.status_code}")