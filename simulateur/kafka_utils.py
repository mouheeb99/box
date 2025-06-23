# kafka_utils.py - VERSION DOCKER COMPATIBLE
from kafka import KafkaProducer
import os
import time

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

# Configuration du producteur Kafka
def create_producer():
    """Crée et retourne un producteur Kafka avec configuration adaptative"""
    bootstrap_servers = get_kafka_servers()
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=[bootstrap_servers],
            value_serializer=lambda v: v.encode('utf-8'),
            # Ajout de retry et timeout pour Docker
            retries=5,
            request_timeout_ms=30000,
            retry_backoff_ms=1000
        )
        print(f"✅ Connexion à Kafka établie ({bootstrap_servers})")
        return producer
    except Exception as e:
        print(f"❌ Impossible de se connecter à Kafka: {e}")
        return None

# Création du producteur global
try:
    producer = create_producer()
except Exception as e:
    print(f"❌ Erreur lors de l'initialisation du producteur Kafka: {e}")
    producer = None

def envoyer_trame(trame, topic="simulateur_topic"):
    """Envoie une trame vers le topic Kafka spécifié"""
    global producer
    
    # Recréer le producteur si nécessaire
    if producer is None:
        print("🔄 Tentative de reconnexion à Kafka...")
        producer = create_producer()
        
    if producer is None:
        print(f"❌ Échec d'envoi: producteur Kafka non disponible")
        return False
    
    try:
        producer.send(topic, trame)
        producer.flush()  # Assurer l'envoi immédiat
        print(f"📡 Trame envoyée : {trame}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")
        # Réinitialiser le producteur en cas d'erreur
        producer = None
        return False

def fermer_producer():
    """Ferme proprement le producteur Kafka"""
    global producer
    if producer:
        try:
            producer.close()
            producer = None
            print("✅ Producteur Kafka fermé")
        except Exception as e:
            print(f"❌ Erreur lors de la fermeture: {e}")

def tester_connexion():
    """Test la connexion Kafka"""
    try:
        servers = get_kafka_servers()
        test_producer = KafkaProducer(
            bootstrap_servers=[servers],
            request_timeout_ms=5000
        )
        test_producer.close()
        print("✅ Test connexion Kafka réussi")
        return True
    except Exception as e:
        print(f"❌ Test connexion Kafka échoué: {e}")
        return False