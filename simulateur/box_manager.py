# box_manager.py - 

import time
import threading
try:
    from .box import BoxSimulateur
    from .kafka_utils import envoyer_trame
except ImportError:
    from box import BoxSimulateur
    from kafka_utils import envoyer_trame

class BoxManager:
    def __init__(self):
        self.boxes = {}  # Dictionnaire des box
        self.simulation_threads = {}  # Threads de simulation
        self.running = {}  # État des simulations
        self.simulation_intervals = {}  # Intervalles de simulation
    
    def create_box(self, box_id, config=None):
        """Crée une nouvelle box"""
        if box_id in self.boxes:
            return False, "Une box avec cet ID existe déjà"
        
        try:
            box = BoxSimulateur(box_id, config)
            self.boxes[box_id] = box
            self.running[box_id] = False
            self.simulation_intervals[box_id] = 5  # 5 secondes par défaut
            
            return True, f"Box {box_id} créée avec succès"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def delete_box(self, box_id):
        """Supprime une box"""
        if box_id not in self.boxes:
            return False, "Box non trouvée"
        
        # Arrêter la simulation si active
        self.stop_simulation(box_id)
        
        # Supprimer la box
        del self.boxes[box_id]
        del self.running[box_id]
        if box_id in self.simulation_intervals:
            del self.simulation_intervals[box_id]
        
        return True, f"Box {box_id} supprimée"
    
    def get_box(self, box_id):
        """Récupère une box par son ID"""
        return self.boxes.get(box_id)
    
    def get_all_boxes(self):
        """Récupère toutes les box"""
        return self.boxes
    
    def get_box_status(self, box_id):
        """Récupère le statut d'une box"""
        box = self.get_box(box_id)
        if not box:
            return None
        
        status = box.get_status()
        status["simulation"] = {
            "active": self.running.get(box_id, False),
            "intervalle": self.simulation_intervals.get(box_id, 5)
        }
        
        return status
    
    def get_all_status(self):
        """Récupère le statut de toutes les box"""
        result = {}
        for box_id in self.boxes:
            result[box_id] = self.get_box_status(box_id)
        return result
    
    def start_simulation(self, box_id, intervalle=None, evolution=True):
        """Démarre la simulation pour une box"""
        box = self.get_box(box_id)
        if not box:
            return False, "Box non trouvée"
        
        if self.running.get(box_id, False):
            return False, "Simulation déjà en cours"
        
        # Mettre à jour l'intervalle si spécifié
        if intervalle is not None:
            try:
                intervalle = float(intervalle)
                if intervalle < 0.1:
                    return False, "Intervalle minimum: 0.1 seconde"
                self.simulation_intervals[box_id] = intervalle
            except ValueError:
                return False, "Intervalle invalide"
        
        intervalle = self.simulation_intervals.get(box_id, 5)
        self.running[box_id] = True
        
        # Thread de simulation avec évolution
        def simulation_task():
            while self.running.get(box_id, False):
                try:
                    # Faire évoluer les valeurs si demandé
                    if evolution:
                        box.evoluer_valeurs()
                    
                    # Générer et envoyer trame 3F (avec valeurs évoluées)
                    trame = box.generer_trame_3F()
                    envoyer_trame(trame)
                    
                    # Attendre l'intervalle
                    time.sleep(intervalle)
                    
                except Exception as e:
                    print(f"Erreur simulation {box_id}: {e}")
                    self.running[box_id] = False
                    break
        
        thread = threading.Thread(target=simulation_task)
        thread.daemon = True
        thread.start()
        self.simulation_threads[box_id] = thread
        
        evolution_msg = " (avec évolution)" if evolution else " (valeurs fixes)"
        return True, f"Simulation démarrée (intervalle: {intervalle}s){evolution_msg}"
    
    def stop_simulation(self, box_id):
        """Arrête la simulation pour une box"""
        if box_id not in self.boxes:
            return False, "Box non trouvée"
        
        if not self.running.get(box_id, False):
            return False, "Aucune simulation en cours"
        
        self.running[box_id] = False
        
        if box_id in self.simulation_threads:
            try:
                self.simulation_threads[box_id].join(timeout=2)
                del self.simulation_threads[box_id]
            except Exception as e:
                print(f"Erreur arrêt thread: {e}")
        
        return True, f"Simulation arrêtée"
    
    def send_specific_trame(self, box_id, trame_type, evolution_avant=False, **kwargs):
        """Envoie une trame spécifique"""
        box = self.get_box(box_id)
        if not box:
            return False, "Box non trouvée"
        
        try:
            # Option d'évolution avant envoi
            if evolution_avant:
                box.evoluer_valeurs()
            
            if trame_type == "3F":
                trame = box.generer_trame_3F()
            elif trame_type == "3E":
                trame = box.generer_trame_3E()
            elif trame_type == "3D":
                trame = box.generer_trame_3D()
            elif trame_type == "3B":
                trame = box.generer_trame_3B()
            elif trame_type == "3C":
                commande_id = kwargs.get("commande_id", "CMD001")
                resultat = kwargs.get("resultat", "OK")
                trame = box.generer_trame_3C(commande_id, resultat)
            elif trame_type == "3A":
                type_config = kwargs.get("type_config", "C")
                trame = box.generer_trame_3A(type_config)
            else:
                return False, f"Type de trame {trame_type} non supporté"
            
            success = envoyer_trame(trame)
            if not success:
                return False, "Erreur lors de l'envoi"
            
            evolution_info = " (après évolution)" if evolution_avant else ""
            return True, {"message": f"Trame {trame_type} envoyée{evolution_info}", "trame": trame}
        
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def get_available_capteurs(self):
        """Liste des capteurs disponibles"""
        return {
            "HT": "Température (°C)",
            "HM": "Humidité (%)",
            "FM": "Fumée (0/1)",
            "PR": "Présence (0/1)",
            "LM": "Luminosité (%)",
            "CT": "Contact (0/1)",
            "SD": "Son (dB)"
        }
    
    def get_available_compteurs(self):
        """Liste des compteurs disponibles"""
        return {
            "EC": "Énergie (kWh)",
            "WC": "Eau (L)",
            "GC": "Gaz (m³)"
        }

# Instance singleton du manager
box_manager = BoxManager()