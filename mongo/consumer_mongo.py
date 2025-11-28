# consumer_mongo.py - VERSION DOCKER AVEC INDEXATION
import sys
import os
from kafka import KafkaConsumer
from datetime import datetime
import json

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import du module MongoDB
from mongo.mongo_utils import mongo_manager

# ✅ Lire la config depuis l'environnement Docker
KAFKA_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

def parser_trame_3F(trame):
    """Parse une trame 3F et retourne un objet structuré AVEC INDEX"""
    parts = trame.split(';')
    
    # Extraire box_id
    first_part = parts[0].strip()
    box_id = first_part[2:].strip()  # Enlever "3F"
    
    # Extraire les valeurs
    data = {"capteurs": {}, "relais": {}, "compteurs": {}}
    
    for part in parts[1:]:
        part = part.strip()
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # ✅ MODIFICATION : Supporter les capteurs indexés (HT1, HT2, etc.)
            # Extraire le type de capteur (lettres) et l'index (chiffres)
            capteur_type = ''.join([c for c in key if c.isalpha()])
            
            # Classifier selon le préfixe
            if capteur_type in ['HT', 'HM', 'LM', 'FM', 'PR', 'CT', 'SD']:
                # Capteurs - garder l'ID complet avec index (HT1, HT2, etc.)
                try:
                    data["capteurs"][key] = float(value)
                except ValueError:
                    data["capteurs"][key] = value
            elif capteur_type == 'RL':
                # Relais
                data["relais"][key] = int(value)
            elif capteur_type in ['EC', 'WC', 'GC']:
                # Compteurs
                data["compteurs"][key] = float(value)
    
    return {"box_id": box_id, "data": data}

def demarrer_consumer_mongo():
    """Démarre un consumer Kafka qui sauvegarde dans MongoDB (tourne indéfiniment)"""
    
    print("🔥 Consumer MongoDB - Simulateur box")
    print(f"📡 Connexion à {KAFKA_SERVERS}...")
    print("💾 Sauvegarde automatique dans MongoDB")
    print("-" * 60)
    print("⏳ En attente de trames...\n")
    
    # Vérifier la connexion MongoDB
    if not mongo_manager.is_connected():
        print("❌ MongoDB non connecté - Arrêt du consumer")
        return
    
    try:
        consumer = KafkaConsumer(
            'simulateur_topic',
            bootstrap_servers=[KAFKA_SERVERS],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='simulateur-mongo-group',
            value_deserializer=lambda x: x.decode('utf-8')
            # IMPORTANT: Pas de consumer_timeout_ms pour écouter indéfiniment
        )
        
        print("✅ Consumer MongoDB démarré avec succès!")
        print("🔍 Écoute permanente des messages Kafka...")
        print("=" * 60)
        
        # Compteurs
        count_total = 0
        count_saved = 0
        count_errors = 0
        
        # BOUCLE INFINIE - Ne s'arrête jamais
        for message in consumer:
            count_total += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            trame = message.value.strip()
            
            print(f"\n📨 MESSAGE #{count_total} reçu à {timestamp}")
            print(f"📝 Trame: {trame}")
            
            try:
                # Parser selon le type de trame
                if trame.startswith('3F'):
                    # Trame de données capteurs
                    trame_data = parser_trame_3F(trame)
                    trame_data["trame_brute"] = trame
                    
                    # Sauvegarder dans MongoDB
                    success = mongo_manager.save_sensor_data(trame_data)
                    
                    if success:
                        count_saved += 1
                        print(f"💾 ✅ Sauvegardé dans MongoDB")
                        print(f"📊 Box: {trame_data['box_id']}")
                        
                        # Afficher résumé des données
                        data = trame_data['data']
                        if data['capteurs']:
                            capteurs_str = ", ".join([f"{k}={v}" for k, v in data['capteurs'].items()])
                            print(f"🌡️ Capteurs: {capteurs_str}")
                        
                        if data['relais']:
                            relais_str = ", ".join([f"{k}={v}" for k, v in data['relais'].items()])
                            print(f"⚡ Relais: {relais_str}")
                            
                        if data['compteurs']:
                            compteurs_str = ", ".join([f"{k}={v}" for k, v in data['compteurs'].items()])
                            print(f"📈 Compteurs: {compteurs_str}")
                    else:
                        count_errors += 1
                        print(f"💾 ❌ Erreur sauvegarde")
                
                elif trame.startswith(('3E', '3D', '3B', '3C', '3A')):
                    # Autres types de trames - log seulement
                    mongo_manager.log_event(
                        level="INFO",
                        source="consumer",
                        message=f"Trame {trame[:2]} reçue",
                        extra_data={"trame": trame}
                    )
                    print(f"📝 ✅ Trame loggée")
                
                else:
                    # Trame inconnue
                    mongo_manager.log_event(
                        level="WARNING",
                        source="consumer", 
                        message="Trame inconnue reçue",
                        extra_data={"trame": trame}
                    )
                    print(f"⚠️ Trame inconnue loggée")
                
            except Exception as e:
                count_errors += 1
                print(f"❌ Erreur traitement: {e}")
                
                # Logger l'erreur
                mongo_manager.log_event(
                    level="ERROR",
                    source="consumer",
                    message=f"Erreur traitement trame: {str(e)}",
                    extra_data={"trame": trame, "error": str(e)}
                )
            
            # Afficher statistiques
            print(f"📊 Stats: {count_saved} sauvegardées / {count_total} total / {count_errors} erreurs")
            print("-" * 60)
    
    except KeyboardInterrupt:
        print(f"\n🛑 Consumer MongoDB arrêté par l'utilisateur")
        print(f"📊 Statistiques finales:")
        print(f"   - Total messages: {count_total}")
        print(f"   - Sauvegardés: {count_saved}")
        print(f"   - Erreurs: {count_errors}")
        print("👋 Au revoir!")
    
    except Exception as e:
        print(f"❌ Erreur consumer MongoDB: {e}")
        mongo_manager.log_event(
            level="ERROR",
            source="consumer",
            message=f"Erreur critique consumer: {str(e)}"
        )
    
    finally:
        # NE PAS fermer la connexion MongoDB car elle est partagée avec l'API
        pass

if __name__ == "__main__":
    # Ce fichier peut toujours être lancé séparément si besoin
    demarrer_consumer_mongo()