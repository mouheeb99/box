# test_box_manager.py

import sys
import os

# Ajouter explicitement le dossier racine au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from simulateur.box_manager import box_manager

print(" Test du BoxManager...")

# Test 1: Créer une box simple
print("\n1️⃣ Création d'une box simple:")
success, message = box_manager.create_box("BOX001")
print(f"Résultat: {message}")
# Test 2: Créer une box simple
print("\n1️⃣ Création d'une box AVEC CONFIG:")
config = {
    "capteurs": ["HT", "HM", "PR", "LM"],           # 4 capteurs
    "valeurs": {                                     # Valeurs initiales
        "HT": 23.5, 
        "HM": 45.0, 
        "PR": 1,
        "LM": 250
    },
    "nb_relais": 3,                                  # 3 relais
    "etats_relais": {"1": 1, "2": 0, "3": 1}       # États des relais
}
success, message1 = box_manager.create_box("BOX002",config)
print(f"Résultat: {message1}")


# Test 2: Voir les box créées
print("\n2️⃣ Liste des box:")
all_boxes = box_manager.get_all_status()
for box_id in all_boxes.keys():
    print(f"- {box_id}")

# Test 3: Envoyer une trame depuis cette box
print("\n3️⃣ Envoi d'une trame 3F:")
success, result = box_manager.send_specific_trame("BOX002", "3F")
if success:
    print(f"✅ Trame envoyée: {result['trame']}")
else:
    print(f"❌ Erreur: {result}")

print("\n✅ Test terminé")