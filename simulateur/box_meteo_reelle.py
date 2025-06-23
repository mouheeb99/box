# box_meteo_reelle.py
import requests
import time
from datetime import datetime

# Import compatible
try:
    from .box import BoxSimulateur
except ImportError:
    from box import BoxSimulateur

class BoxMeteoReelle(BoxSimulateur):
    """Box qui récupère des données météo réelles depuis OpenWeatherMap"""
    
    def __init__(self, box_id, ville="Paris", api_key=None):
        # Configuration de base pour une box météo
        config = {
            "capteurs": ["HT", "HM", "VT"],  # Température, Humidité, Vent
            "valeurs": {"HT": 20.0, "HM": 50.0, "VT": 0.0},
            "nb_relais": 3,  # 3 relais comme box normale
            "etats_relais": {"1": 0, "2": 1, "3": 0},
            "compteurs": {"EC": 0.0, "WC": 0.0, "GC": 0.0}  # Électricité, Eau, Gaz
        }
        
        super().__init__(box_id, config)
        
        self.ville = ville
        self.api_key = api_key
        self.last_weather_update = 0
        self.weather_cache = None
        self.update_interval = 300  # 5 minutes entre les appels API
        
        # Ajouter le capteur VT manuellement s'il manque
        if "VT" not in self.capteurs:
            self.capteurs["VT"] = {"nom": "Vent", "unite": "km/h", "valeur": 0.0}
        
        print(f"🌍 Box météo créée pour {ville}")
    
    def get_weather_data(self):
        """Récupère les données météo depuis OpenWeatherMap"""
        
        # Vérifier le cache (éviter trop d'appels API)
        current_time = time.time()
        if (self.weather_cache and 
            current_time - self.last_weather_update < self.update_interval):
            return self.weather_cache
        
        if not self.api_key:
            print("❌ Pas de clé API météo - utilisation des valeurs par défaut")
            return None
        
        try:
            # URL API OpenWeatherMap
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": self.ville,
                "appid": self.api_key,
                "units": "metric",
                "lang": "fr"
            }
            
            print(f"🌐 Récupération météo pour {self.ville}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_data = {
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"].get("speed", 0) * 3.6,  # m/s -> km/h
                    "description": data["weather"][0]["description"],
                    "timestamp": current_time
                }
                
                # Mettre en cache
                self.weather_cache = weather_data
                self.last_weather_update = current_time
                
                print(f"✅ Météo récupérée: {weather_data['temperature']}°C, {weather_data['humidity']}%, {weather_data['wind_speed']} km/h")
                return weather_data
                
            else:
                print(f"❌ Erreur API météo: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération météo: {e}")
            return None
    
    def evoluer_valeurs(self):
        """Override: utilise les données météo réelles au lieu de la simulation"""
        
        # Récupérer les données météo
        weather_data = self.get_weather_data()
        
        if weather_data:
            # Mettre à jour les capteurs avec les vraies valeurs
            self.capteurs["HT"]["valeur"] = round(weather_data["temperature"], 1)
            self.capteurs["HM"]["valeur"] = weather_data["humidity"]
            self.capteurs["VT"]["valeur"] = round(weather_data["wind_speed"], 1)
        else:
            # Fallback: légère évolution des valeurs actuelles
            self.capteurs["HT"]["valeur"] += (self.random.random() - 0.5) * 0.2
            self.capteurs["HM"]["valeur"] += (self.random.random() - 0.5) * 2
            self.capteurs["VT"]["valeur"] += (self.random.random() - 0.5) * 1
        
        # Borner les valeurs
        self.capteurs["HT"]["valeur"] = max(-30, min(50, self.capteurs["HT"]["valeur"]))
        self.capteurs["HM"]["valeur"] = max(0, min(100, int(self.capteurs["HM"]["valeur"])))
        self.capteurs["VT"]["valeur"] = max(0, min(100, self.capteurs["VT"]["valeur"]))
        
        # Logique relais simple (comme box normale)
        self.gerer_relais_simple()
        
        # Mettre à jour les compteurs
        self.mettre_a_jour_compteurs()
    
    def gerer_relais_simple(self):
        """Évolution normale des relais (comme BoxSimulateur classique)"""
        # Les relais évoluent aléatoirement comme dans une box normale
        for relais_id in self.relais.keys():
            if self.random.random() < 0.1:  # 10% de chance de changer
                self.relais[relais_id] = 1 - self.relais[relais_id]
    
    def mettre_a_jour_compteurs(self):
        """Met à jour les compteurs comme une box normale"""
        # Compteur électrique évolue selon usage des relais
        nb_relais_actifs = sum(self.relais.values())
        if nb_relais_actifs > 0:
            self.compteurs["EC"] += nb_relais_actifs * 0.5 / 3600  # 0.5kW par relais actif
        
        # Ajouter d'autres compteurs si nécessaire
        if "WC" not in self.compteurs:
            self.compteurs["WC"] = 0.0
        if "GC" not in self.compteurs:
            self.compteurs["GC"] = 0.0
            
        # Évolution des autres compteurs
        self.compteurs["WC"] += self.random.uniform(0.1, 0.3) / 3600  # Eau
        self.compteurs["GC"] += self.random.uniform(0.05, 0.15) / 3600  # Gaz
        
        # Arrondir
        for compteur in self.compteurs:
            self.compteurs[compteur] = round(self.compteurs[compteur], 3)
    
    def get_status_details(self):
        """Informations détaillées de la box météo"""
        status = super().get_status_details()
        
        # Ajouter des infos spécifiques météo
        status["meteo"] = {
            "ville": self.ville,
            "derniere_maj": datetime.fromtimestamp(self.last_weather_update).strftime("%H:%M:%S") if self.last_weather_update > 0 else "Jamais",
            "source": "API_REELLE" if self.weather_cache else "SIMULATION"
        }
        
        return status