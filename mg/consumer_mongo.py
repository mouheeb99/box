# consumer_mongo.py
from kafka import KafkaConsumer
import json
from pymongo import MongoClient
from datetime import datetime

class MongoConsumer:
    def __init__(self):
        # Connexion MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.iot_project
        self.collection = self.db.trames
        
        # Consumer Kafka
        self.consumer = KafkaConsumer(
            'simulateur_topic',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        print("🚀 Consumer MongoDB démarré...")
       
    
    def start_consuming(self):
        """Consommer et sauvegarder les trames"""
        try:
            for message in self.consumer:
                trame_data = message.value
                
                # Ajouter timestamp et métadonnées
                document = {
                    'timestamp': datetime.now(),
                    'box_id': trame_data.get('box_id'),
                    'type_trame': trame_data.get('type_trame'),
                    'trame_brute': trame_data.get('trame'),
                    'donnees': trame_data.get('donnees', {}),
                    'kafka_offset': message.offset,
                    'kafka_topic': message.topic
                }
                
                # Sauvegarder dans MongoDB
                result = self.collection.insert_one(document)
                
                print(f"💾 Trame sauvegardée: {trame_data.get('box_id')} - {trame_data.get('type_trame')} - ID: {result.inserted_id}")
                
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du consumer MongoDB")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        finally:
            self.consumer.close()
            self.client.close()

if __name__ == "__main__":
    consumer = MongoConsumer()
    consumer.start_consuming()