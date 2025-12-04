# test_config_3A.py - Tests des trames 3A
import requests
import json

API_URL = "http://localhost:5000"

print("🧪 TESTS TRAMES 3A - CONFIGURATION DYNAMIQUE")
print("=" * 70)

# Test 1: Configuration capteurs simples
print("\n1️⃣ Test: Configuration capteurs simples")
trame1 = "3A;Vbox;HT;15;35;25;HM;30;80;50;S"
print(f"Trame: {trame1}")

response = requests.post(
    f"{API_URL}/api/config/3A",
    json={"trame": trame1}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Succès: {result['message']}")
    print(f"   Box: {result['box_id']}")
    print(f"   Type: {result['type']}")
else:
    print(f"❌ Erreur: {response.json()}")


# Test 2: Configuration capteurs multiples (2x température)
print("\n2️⃣ Test: Capteurs multiples (2x HT)")
trame2 = "3A;TEST_MULTI;HT;10;30;20;HT;18;28;22;HM;40;70;55;S"
print(f"Trame: {trame2}")

response = requests.post(
    f"{API_URL}/api/config/3A",
    json={"trame": trame2}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Succès: {result['message']}")
    print(f"   Capteurs configurés:")
    for capteur_id, valeur in result['config'].get('valeurs', {}).items():
        plage = result['config'].get('plages', {}).get(capteur_id, {})
        print(f"      • {capteur_id}: {valeur} (min={plage.get('min')}, max={plage.get('max')})")
else:
    print(f"❌ Erreur: {response.json()}") 

# Test 3: Configuration relais
print("\n3️⃣ Test: Configuration relais")
trame3 = "3A;Vbox;RL1;0;RL2;1;O"
print(f"Trame: {trame3}")

response = requests.post(
    f"{API_URL}/api/config/3A",
    json={"trame": trame3}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Succès: {result['message']}")
    print(f"   Relais configurés: {result['config']['nb_relais']}")
    for num, etat in result['config']['etats_relais'].items():
        etat_str = "✅ Activé" if etat == 1 else "⚪ Désactivé"
        print(f"      • RL{num}: {etat_str}")
else:
    print(f"❌ Erreur: {response.json()}") 

# Test 4: Configuration compteurs
print("\n4️⃣ Test: Configuration compteurs")
trame4 = "3A;Vbox;EC;1200;WC;5000;C"
print(f"Trame: {trame4}")

response = requests.post(
    f"{API_URL}/api/config/3A",
    json={"trame": trame4}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Succès: {result['message']}")
    print(f"   Compteurs configurés:")
    for compteur, valeur in result['config']['compteurs'].items():
        print(f"      • {compteur}: {valeur}")
else:
    print(f"❌ Erreur: {response.json()}")

# Test 5: Validation sans application
print("\n5️⃣ Test: Validation (sans appliquer)")
trame5 = "3A;TEST_VALIDATION;HT;0;50;25;LM;0;100;60;S"
print(f"Trame: {trame5}")

response = requests.post(
    f"{API_URL}/api/config/3A/validate",
    json={"trame": trame5}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Trame valide")
    print(f"   Preview:")
    print(f"   {result['preview']['details']}")
else:
    print(f"❌ Erreur: {response.json()}")



# Test 7: Vérifier les boxes créées
print("\n7️⃣ Test: Vérification des boxes créées")
response = requests.get(f"{API_URL}/api/boxes")
boxes = response.json()

print(f"📦 Boxes créées via trames 3A:")
for box_id in boxes.keys():
    if box_id.startswith("TEST_"):
        box_data = requests.get(f"{API_URL}/api/boxes/{box_id}").json()
        print(f"   • {box_id}:")
        print(f"      Capteurs: {list(box_data['capteurs'].keys())}")
        print(f"      Relais: {list(box_data['relais'].keys())}")
        print(f"      Compteurs: {list(box_data['compteurs'].keys())}")

print("\n" + "=" * 70)
print("✅ TESTS TERMINÉS !")
print("\n💡 Pour tester en PowerShell:")
print('$body = @{ trame = "3A;MA_BOX;HT;10;40;25;S" } | ConvertTo-Json')
print('Invoke-RestMethod -Uri "http://localhost:5000/api/config/3A" -Method Post -Body $body -ContentType "application/json"')