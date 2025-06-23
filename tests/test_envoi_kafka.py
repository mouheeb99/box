
# test_envoi_kafka.py
import sys
import os

# Ajouter le dossier parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulateur.kafka_utils import envoyer_trame
print(" Test d'envoi d'une trame simple...")

# Envoyer une trame de test
trame = "3F TEST001 ; HT=22.5 ; HM=55.0 ; RL1=1 ; RL2=0 ; EC=100 ;"
print(f"Envoi de: {trame}")
success = envoyer_trame(trame)
    

if success:
    print("Trame envoyée avec succès")
else:
    print(" Erreur lors de l'envoi")