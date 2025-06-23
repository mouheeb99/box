# box.py 
import random
import time
import math

class BoxSimulateur:
    def __init__(self, box_id, config=None):
        self.box_id = box_id
        self.creation_time = time.time()
        
        # Configuration par défaut
        self.capteurs = {}
        self.relais = {}
        self.compteurs = {}
        
        # Informations de base de la box
        self.code_unique = f"IMEI{random.randint(1000000000, 9999999999)}"
        self.mode_comm = "GPRS"
        self.version = "V1.0_2025-03-14"
        self.service1 = "IMON"
        self.service2 = "IGM"
        self.signal = 75
        self.ip = f"192.168.1.{random.randint(100, 200)}"
        self.operateur = "orange.tn"
        self.etat_reseau = "CONNECTED"
        
        # === NOUVEAU: Système d'évolution des valeurs ===
        self.valeurs_base = {}  # Valeurs de référence pour l'évolution
        self.tendances = {}     # Tendances actuelles des capteurs
        self.derniere_evolution = time.time()
        self.cycle_offset = random.uniform(0, 2 * math.pi)  # Pour varier les cycles
        
        # Initialiser avec la configuration
        self.init_capteurs(config)
        self.init_relais(config)
        self.init_compteurs(config)
        
        # === NOUVEAU: Initialiser le système d'évolution ===
        self.init_evolution()
    
    def init_capteurs(self, config=None):
        """Initialise les capteurs selon la configuration"""
        capteurs_disponibles = {
            "HT": {"nom": "Température", "valeur": 25.0, "unite": "°C"},
            "HM": {"nom": "Humidité", "valeur": 50.0, "unite": "%"},
            "FM": {"nom": "Fumée", "valeur": 0, "unite": "bool"},
            "PR": {"nom": "Présence", "valeur": 0, "unite": "bool"},
            "LM": {"nom": "Luminosité", "valeur": 60, "unite": "%"},
            "CT": {"nom": "Contact", "valeur": 0, "unite": "bool"},
            "SD": {"nom": "Son", "valeur": 45, "unite": "dB"}
        }
        
        # Si aucune config, utiliser température et humidité par défaut
        if not config or "capteurs" not in config:
            self.capteurs["HT"] = capteurs_disponibles["HT"].copy()
            self.capteurs["HM"] = capteurs_disponibles["HM"].copy()
            return
        
        # Ajouter les capteurs spécifiés
        for capteur_id in config["capteurs"]:
            if capteur_id in capteurs_disponibles:
                self.capteurs[capteur_id] = capteurs_disponibles[capteur_id].copy()
                
                # Appliquer valeurs personnalisées si spécifiées
                if "valeurs" in config and capteur_id in config["valeurs"]:
                    self.capteurs[capteur_id]["valeur"] = config["valeurs"][capteur_id]
    
    def init_relais(self, config=None):
        """Initialise les relais selon la configuration"""
        # Par défaut: 2 relais
        if not config or "nb_relais" not in config:
            self.relais["RL1"] = {"etat": 0, "mode": "auto"}
            self.relais["RL2"] = {"etat": 0, "mode": "auto"}
            return
        
        # Créer le nombre de relais spécifié
        nb_relais = min(int(config["nb_relais"]), 8)  # Max 8 relais
        for i in range(1, nb_relais + 1):
            relais_id = f"RL{i}"
            self.relais[relais_id] = {"etat": 0, "mode": "auto"}
            
            # Appliquer états initiaux si spécifiés
            if "etats_relais" in config and str(i) in config["etats_relais"]:
                self.relais[relais_id]["etat"] = config["etats_relais"][str(i)]
    
    def init_compteurs(self, config=None):
        """Initialise les compteurs selon la configuration"""
        # Par défaut: compteur énergie
        self.compteurs["EC"] = {"nom": "Énergie", "valeur": 1200, "unite": "kWh"}
        
        # Ajouter compteurs supplémentaires si spécifiés
        if config and "compteurs" in config:
            for compteur_id, valeur in config["compteurs"].items():
                if compteur_id == "EC":
                    self.compteurs["EC"]["valeur"] = valeur
                elif compteur_id == "WC":
                    self.compteurs["WC"] = {"nom": "Eau", "valeur": valeur, "unite": "L"}
                elif compteur_id == "GC":
                    self.compteurs["GC"] = {"nom": "Gaz", "valeur": valeur, "unite": "m³"}
    
    # === NOUVEAU: Système d'évolution des valeurs ===
    def init_evolution(self):
        """Initialise le système d'évolution des valeurs"""
        # Sauvegarder les valeurs de base pour l'évolution
        for capteur_id, capteur in self.capteurs.items():
            self.valeurs_base[capteur_id] = capteur["valeur"]
            self.tendances[capteur_id] = 0  # 0 = stable, -1 = baisse, 1 = hausse
    
    def evoluer_valeurs(self):
        """Fait évoluer les valeurs des capteurs de manière réaliste"""
        maintenant = time.time()
        dt = maintenant - self.derniere_evolution
        self.derniere_evolution = maintenant
        
        # Évolution pour chaque capteur
        for capteur_id, capteur in self.capteurs.items():
            if capteur["unite"] == "bool":
                # Capteurs booléens: changement occasionnel
                self._evoluer_capteur_booleen(capteur_id, capteur)
            else:
                # Capteurs analogiques: évolution continue
                self._evoluer_capteur_analogique(capteur_id, capteur, dt)
        
        # Appliquer les corrélations réalistes
        self._appliquer_correlations()
        
        # Évolution des compteurs (incrémentale)
        self._evoluer_compteurs(dt)
    
    def _evoluer_capteur_analogique(self, capteur_id, capteur, dt):
        """Évolution des capteurs analogiques (température, humidité, etc.)"""
        valeur_base = self.valeurs_base[capteur_id]
        valeur_actuelle = capteur["valeur"]
        
        # Paramètres selon le type de capteur
        if capteur_id == "HT":  # Température
            amplitude = 3.0  # ±3°C
            vitesse = 0.1    # Changement lent
            bruit = 0.2      # Petit bruit
        elif capteur_id == "HM":  # Humidité
            amplitude = 10.0  # ±10%
            vitesse = 0.15    # Un peu plus rapide
            bruit = 0.5       # Plus de variation
        elif capteur_id == "LM":  # Luminosité
            amplitude = 20.0  # ±20%
            vitesse = 0.2     # Changement plus rapide
            bruit = 2.0       # Beaucoup de variation
        elif capteur_id == "SD":  # Son
            amplitude = 15.0  # ±15dB
            vitesse = 0.3     # Changement rapide
            bruit = 3.0       # Très variable
        else:
            amplitude = 5.0
            vitesse = 0.1
            bruit = 0.5
        
        # Cycle journalier (température suit l'heure)
        heure_actuelle = time.localtime().tm_hour
        cycle_journalier = math.sin((heure_actuelle / 24) * 2 * math.pi + self.cycle_offset)
        variation_cyclique = cycle_journalier * amplitude * 0.3
        
        # Changement de tendance occasionnel
        if random.random() < 0.05:  # 5% de chance
            self.tendances[capteur_id] = random.choice([-1, 0, 1])
        
        # Valeur cible basée sur base + cycle + tendance
        valeur_cible = valeur_base + variation_cyclique + (self.tendances[capteur_id] * amplitude * 0.5)
        
        # Mouvement vers la cible avec inertie
        difference = valeur_cible - valeur_actuelle
        mouvement = difference * vitesse * dt
        
        # Ajout du bruit
        bruit_aleatoire = random.uniform(-bruit, bruit)
        
        # Nouvelle valeur
        nouvelle_valeur = valeur_actuelle + mouvement + bruit_aleatoire
        
        # Limites réalistes
        if capteur_id == "HT":
            nouvelle_valeur = max(10, min(40, nouvelle_valeur))
        elif capteur_id == "HM":
            nouvelle_valeur = max(20, min(90, nouvelle_valeur))
        elif capteur_id == "LM":
            nouvelle_valeur = max(0, min(100, nouvelle_valeur))
        elif capteur_id == "SD":
            nouvelle_valeur = max(30, min(80, nouvelle_valeur))
        
        # Mettre à jour la valeur
        if capteur["unite"] == "°C" or capteur["unite"] == "%" or capteur["unite"] == "dB":
            capteur["valeur"] = round(nouvelle_valeur, 1)
        else:
            capteur["valeur"] = round(nouvelle_valeur, 2)
    
    def _evoluer_capteur_booleen(self, capteur_id, capteur):
        """Évolution des capteurs booléens"""
        # Probabilités de changement selon le type
        if capteur_id == "FM":  # Fumée - rare
            prob_changement = 0.01
        elif capteur_id == "PR":  # Présence - occasionnel
            prob_changement = 0.03
        elif capteur_id == "CT":  # Contact - rare
            prob_changement = 0.02
        else:
            prob_changement = 0.02
        
        # Changement d'état
        if random.random() < prob_changement:
            capteur["valeur"] = 1 - capteur["valeur"]  # Basculer 0->1 ou 1->0
    
    def _appliquer_correlations(self):
        """Applique les corrélations réalistes entre capteurs"""
        # Corrélation température <-> humidité
        if "HT" in self.capteurs and "HM" in self.capteurs:
            temp = self.capteurs["HT"]["valeur"]
            humidite_actuelle = self.capteurs["HM"]["valeur"]
            
            # Ajustement: quand il fait chaud, humidité tend à baisser
            if temp > 28:
                correction = -2
            elif temp < 18:
                correction = +3
            else:
                correction = 0
            
            nouvelle_humidite = humidite_actuelle + correction * 0.1
            self.capteurs["HM"]["valeur"] = max(20, min(90, nouvelle_humidite))
        
        # Impact des relais sur l'environnement
        self._appliquer_impact_relais()
    
    def _appliquer_impact_relais(self):
        """Simule l'impact des relais sur l'environnement"""
        for relais_id, relais in self.relais.items():
            if relais["etat"] == 1:  # Relais activé
                # Simulation d'impact selon le type de relais
                if relais_id == "RL1" and "HT" in self.capteurs:  # Chauffage
                    self.capteurs["HT"]["valeur"] += 0.1
                elif relais_id == "RL2" and "LM" in self.capteurs:  # Éclairage
                    self.capteurs["LM"]["valeur"] = min(95, self.capteurs["LM"]["valeur"] + 5)
    
    def _evoluer_compteurs(self, dt):
        """Évolution des compteurs (incrémentale)"""
        # Les compteurs augmentent lentement
        for compteur_id, compteur in self.compteurs.items():
            if compteur_id == "EC":  # Énergie
                increment = random.uniform(0.001, 0.003) * dt  # kWh par seconde
                compteur["valeur"] += increment
            elif compteur_id == "WC":  # Eau
                increment = random.uniform(0.01, 0.05) * dt  # L par seconde
                compteur["valeur"] += increment
            elif compteur_id == "GC":  # Gaz
                increment = random.uniform(0.0001, 0.0005) * dt  # m³ par seconde
                compteur["valeur"] += increment
            
            # Arrondir les valeurs
            compteur["valeur"] = round(compteur["valeur"], 3)
    
    # === Méthodes existantes (inchangées) ===
    def set_capteur_valeur(self, capteur_id, valeur):
        """Modifie manuellement la valeur d'un capteur"""
        if capteur_id in self.capteurs:
            self.capteurs[capteur_id]["valeur"] = valeur
            # Mettre à jour la valeur de base pour l'évolution
            self.valeurs_base[capteur_id] = valeur
            return True
        return False
    
    def set_relais_etat(self, relais_id, etat):
        """Modifie manuellement l'état d'un relais"""
        if relais_id in self.relais:
            self.relais[relais_id]["etat"] = int(etat)
            return True
        return False
    
    def set_compteur_valeur(self, compteur_id, valeur):
        """Modifie manuellement la valeur d'un compteur"""
        if compteur_id in self.compteurs:
            self.compteurs[compteur_id]["valeur"] = valeur
            return True
        return False
    
    def get_status(self):
        """Retourne l'état actuel de la box"""
        status = {
            "id": self.box_id,
            "capteurs": {},
            "relais": {},
            "compteurs": {},
            "info": {
                "code_unique": self.code_unique,
                "mode_comm": self.mode_comm,
                "version": self.version,
                "signal": self.signal,
                "ip": self.ip,
                "operateur": self.operateur,
                "etat_reseau": self.etat_reseau,
                "uptime": round(time.time() - self.creation_time)
            }
        }
        
        # Copier les données des capteurs
        for capteur_id, capteur in self.capteurs.items():
            status["capteurs"][capteur_id] = {
                "nom": capteur["nom"],
                "valeur": capteur["valeur"],
                "unite": capteur["unite"]
            }
        
        # Copier les données des relais
        for relais_id, relais in self.relais.items():
            status["relais"][relais_id] = {
                "etat": relais["etat"],
                "mode": relais["mode"]
            }
        
        # Copier les données des compteurs
        for compteur_id, compteur in self.compteurs.items():
            status["compteurs"][compteur_id] = {
                "nom": compteur["nom"],
                "valeur": compteur["valeur"],
                "unite": compteur["unite"]
            }
        
        return status
    
    # === GÉNÉRATION DE TRAMES (inchangée) ===
    
    def generer_trame_3F(self):
        """Génère une trame 3F (VALUES_SET)"""
        valeurs = []
        
        # Ajouter capteurs
        for capteur_id, capteur in self.capteurs.items():
            valeurs.append(f"{capteur_id}={capteur['valeur']}")
        
        # Ajouter relais
        for relais_id, relais in self.relais.items():
            valeurs.append(f"{relais_id}={relais['etat']}")
        
        # Ajouter compteurs
        for compteur_id, compteur in self.compteurs.items():
            valeurs.append(f"{compteur_id}={compteur['valeur']}")
        
        return f"3F {self.box_id} ; " + " ; ".join(valeurs) + " ;"
    
    def generer_trame_3E(self):
        """Génère une trame 3E (MODEL_INFO)"""
        return f"3E{self.box_id};{self.code_unique};{self.mode_comm};{self.version};{self.service1};{self.service2}"
    
    def generer_trame_3D(self):
        """Génère une trame 3D (NETWORK_INFO)"""
        return f"3D{self.box_id};{self.signal};{self.ip};{self.operateur};{self.etat_reseau}"
    
    def generer_trame_3B(self):
        """Génère une trame 3B (COMMAND_GET)"""
        return f"3B{self.box_id};REQ;"
    
    def generer_trame_3C(self, commande_id, resultat="OK"):
        """Génère une trame 3C (COMMAND_SET)"""
        return f"3C{self.box_id};{commande_id};{resultat};"
    
    def generer_trame_3A(self, type_config):
        """Génère une trame 3A (CONFIG_GET)"""
        return f"3A{self.box_id};{self.code_unique};{type_config}"