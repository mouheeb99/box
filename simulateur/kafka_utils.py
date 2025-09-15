# kafka_utils.py - 
from kafka import KafkaProducer

# Configuration du producteur Kafka
def create_producer():
    """Crée et retourne un producteur Kafka"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: v.encode('utf-8')
        )
        print("✅ Connexion à Kafka établie (localhost:9092)")
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
        test_producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            request_timeout_ms=5000
        )
        test_producer.close()
        print("✅ Test connexion Kafka réussi")
        return True
    except Exception as e:
        print(f"❌ Test connexion Kafka échoué: {e}")
        return False