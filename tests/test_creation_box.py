# test_creation_box.py
import requests
import json

print("🧪 Test création de box...")

# Test 1: Créer une box simple
print("\n1️⃣ Création d'une box simple:")
nouvelle_box = {
    "id": "TEST_BOX",
    
        "capteurs": ["HT", "HM", "FM", "HT"],
        "nb_relais": 2,
        "compteurs": {
            "EC": 1200,    # Énergie: 1200 kWh
            "WC": 5000,    # Eau: 5000 L
            "GC": 300      # Gaz: 300 m³
        }
    }


try:
    response = requests.post(
        "http://127.0.0.1:5000/api/boxes",
        json=nouvelle_box
    )
    
    print(f"Status: {response.status_code}")
    print(f"Réponse: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Box créée avec succès!")
    else:
        print("❌ Erreur lors de la création")
        
except Exception as e:
    print(f"❌ Erreur: {e}")