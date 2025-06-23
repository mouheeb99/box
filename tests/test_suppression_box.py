# test_suppression_box.py
import urllib.request
import urllib.parse
import json

print("🧪 Test suppression de box...")

try:
    # Étape 1: Vérifier que la box existe avant suppression
    print("1️⃣ Vérification que TEST_BOX existe...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:5000/api/boxes/TEST_BOX") as response:
            if response.getcode() == 200:
                print("✅ TEST_BOX existe")
            else:
                print("❌ TEST_BOX n'existe pas")
                exit()
    except:
        print("❌ TEST_BOX n'existe pas")
        exit()
    
    # Étape 2: Supprimer la box
    print("\n2️⃣ Suppression de TEST_BOX...")
    
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/boxes/TEST_BOX",
        method='DELETE'
    )
    
    with urllib.request.urlopen(req) as response:
        status = response.getcode()
        result = response.read().decode('utf-8')
        
        print(f"Status: {status}")
        print(f"Réponse: {result}")
        
        if status == 200:
            print("✅ Box supprimée avec succès!")
        else:
            print("❌ Erreur lors de la suppression")
    
    # Étape 3: Vérifier que la box n'existe plus
    print("\n3️⃣ Vérification que la box n'existe plus...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:5000/api/boxes/TEST_BOX") as response:
            print("❌ La box existe encore!")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("✅ Box correctement supprimée (404 Not Found)")
        else:
            print(f"❌ Erreur inattendue: {e.code}")
    
    # Étape 4: Lister toutes les box pour confirmation
    print("\n4️⃣ Liste des box restantes...")
    with urllib.request.urlopen("http://127.0.0.1:5000/api/boxes") as response:
        result = response.read().decode('utf-8')
        boxes = json.loads(result)
        print(f"Box restantes: {list(boxes.keys())}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")