# consumer.py - VERSION DOCKER COMPATIBLE
from kafka import KafkaConsumer
from datetime import datetime
import json
import os

def get_kafka_servers():
    """Retourne la configuration Kafka selon l'environnement"""
    # Si on est dans Docker (variable d'environnement définie)
    if os.getenv('KAFKA_BOOTSTRAP_SERVERS'):
        servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        print(f"🐳 Mode Docker détecté - Kafka: {servers}")
        return servers
    else:
        # Mode local
        servers = 'localhost:9092'
        print(f"💻 Mode local détecté - Kafka: {servers}")
        return servers

def parser_trame_3F(trame):
    """Parse une trame 3F et retourne un objet structuré"""
    # Format: 3F box_id ; capteur1=valeur1 ; capteur2=valeur2 ; ...
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
            
            # Classifier selon le préfixe (ajout VT pour météo)
            if key.startswith(('HT', 'HM', 'LM', 'FM', 'PR', 'CT', 'SD', 'VT')):
                try:
                    data["capteurs"][key] = float(value)
                except ValueError:
                    data["capteurs"][key] = value
            elif key.startswith('RL'):
                data["relais"][key] = int(value)
            elif key.startswith(('EC', 'WC', 'GC')):
                data["compteurs"][key] = float(value)
    
    return {"box_id": box_id, "data": data}

def parser_trame_3E(trame):
    """Parse une trame 3E"""
    parts = trame.split(';')
    box_id = parts[0][2:]  # Enlever "3E"
    
    return {
        "box_id": box_id,
        "code_unique": parts[1] if len(parts) > 1 else "N/A",
        "mode_comm": parts[2] if len(parts) > 2 else "N/A",
        "version": parts[3] if len(parts) > 3 else "N/A",
        "service1": parts[4] if len(parts) > 4 else "N/A",
        "service2": parts[5] if len(parts) > 5 else "N/A"
    }

def parser_trame_3D(trame):
    """Parse une trame 3D"""
    parts = trame.split(';')
    box_id = parts[0][2:]  # Enlever "3D"
    
    return {
        "box_id": box_id,
        "signal": parts[1] if len(parts) > 1 else "N/A",
        "ip": parts[2] if len(parts) > 2 else "N/A",
        "operateur": parts[3] if len(parts) > 3 else "N/A",
        "etat_reseau": parts[4] if len(parts) > 4 else "N/A"
    }

def demarrer_consumer():
    """Démarre un consumer Kafka simple pour afficher les trames en JSON"""
    
    print("🔥 Consumer Kafka - Simulateur box")
    servers = get_kafka_servers()
    print(f"📡 Connexion à {servers}...")
    print("📋 Topic: simulateur_topic")
    print("-" * 60)
    print("⏳ En attente de trames... (Ctrl+C pour arrêter)\n")
    
    try:
        # CONFIGURATION ADAPTATIVE
        consumer = KafkaConsumer(
            'simulateur_topic',
            bootstrap_servers=[servers],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='simulateur-group',
            value_deserializer=lambda x: x.decode('utf-8'),
            consumer_timeout_ms=1000,
            # Ajout de paramètres pour Docker
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
            request_timeout_ms=40000
        )
        
        print("✅ Consumer démarré avec succès!")
        print("🔍 Recherche de messages...")
        
        # Compteur de trames
        count = 0
        
        # ✅ MÉTHODE SIMPLIFIÉE - Plus fiable
        for message in consumer:
            count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            trame = message.value.strip()
            
            print(f"\n🆕 MESSAGE #{count} reçu à {timestamp}")
            
            # Créer l'objet de base
            result = {
                "timestamp": timestamp,
                "numero": count,
                "trame_brute": trame,
                "type": "INCONNU",
                "donnees": {}
            }
            
            # Parser selon le type de trame
            try:
                if trame.startswith('3F'):
                    result["type"] = "VALUES_SET"
                    result["donnees"] = parser_trame_3F(trame)
                    
                elif trame.startswith('3E'):
                    result["type"] = "MODEL_INFO"
                    result["donnees"] = parser_trame_3E(trame)
                    
                elif trame.startswith('3D'):
                    result["type"] = "NETWORK_INFO"
                    result["donnees"] = parser_trame_3D(trame)
                    
                elif trame.startswith('3B'):
                    result["type"] = "COMMAND_GET"
                    parts = trame.split(';')
                    result["donnees"] = {
                        "box_id": parts[0][2:],
                        "commande": parts[1] if len(parts) > 1 else "N/A"
                    }
                    
                elif trame.startswith('3C'):
                    result["type"] = "COMMAND_SET"
                    parts = trame.split(';')
                    result["donnees"] = {
                        "box_id": parts[0][2:],
                        "commande_id": parts[1] if len(parts) > 1 else "N/A",
                        "resultat": parts[2] if len(parts) > 2 else "N/A"
                    }
                    
                elif trame.startswith('3A'):
                    result["type"] = "CONFIG_GET"
                    parts = trame.split(';')
                    result["donnees"] = {
                        "box_id": parts[0][2:],
                        "code_unique": parts[1] if len(parts) > 1 else "N/A",
                        "type_config": parts[2] if len(parts) > 2 else "N/A"
                    }
                    
            except Exception as e:
                result["erreur_parsing"] = str(e)
            
            # Afficher en JSON formaté
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 60)
    
    except KeyboardInterrupt:
        print(f"\n🛑 Consumer arrêté. Total: {count} trames reçues")
        print("👋 Au revoir!")
    
    except Exception as e:
        print(f"❌ Erreur consumer: {e}")
        print("🔧 Vérifiez que Kafka est démarré")
        print("📋 Vérifiez que le topic 'simulateur_topic' existe")

def tester_connexion():
    """Test simple de connexion Kafka"""
    try:
        servers = get_kafka_servers()
        consumer = KafkaConsumer(
            bootstrap_servers=[servers],
            consumer_timeout_ms=5000
        )
        print("✅ Connexion Kafka OK!")
        consumer.close()
        return True
    except Exception as e:
        print(f"❌ Connexion Kafka échouée: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de connexion Kafka...")
    if tester_connexion():
        print("🚀 Démarrage du consumer...")
        demarrer_consumer()
    else:
        print("💡 Solutions possibles:")
        print("   1. Vérifiez que Kafka tourne sur localhost:9092")
        print("   2. Redémarrez Kafka et Zookeeper")
        print("   3. Vérifiez les logs Kafka")