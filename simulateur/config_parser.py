# config_parser.py - 


def parser_trame_3A(trame):
    """
    Parse une trame 3A et retourne la configuration.
    
    Args:
        trame (str): Trame complète, ex: "3A;BOX_001;HT;15;35;25;HM;30;80;50;S"
    
    Returns:
        dict: Configuration parsée
    """
    parts = [p.strip() for p in trame.split(';')]
    
    if not parts[0].startswith('3A'):
        raise ValueError("Ce n'est pas une trame 3A")
    
    if len(parts) < 3:
        raise ValueError("Trame 3A incomplète")
    
    # Extraire le type (dernier élément)
    config_type = parts[-1].upper()
    
    # Extraire box_id (après 3A)
    box_id = parts[1]
    
    # Extraire les données (entre box_id et type)
    data_parts = parts[2:-1]
    
    # Parser selon le type
    if config_type == 'S':
        return parser_sensors(box_id, data_parts)
    elif config_type == 'O':
        return parser_outputs(box_id, data_parts)
    elif config_type == 'C':
        return parser_counters(box_id, data_parts)
    elif config_type == 'A':
        return parser_all(box_id, data_parts)
    else:
        raise ValueError(f"Type de configuration inconnu: {config_type}")


def parser_sensors(box_id, data_parts):
    """Parse la configuration des capteurs"""
    if len(data_parts) % 4 != 0:
        raise ValueError("Format capteurs invalide (doit être TYPE;MIN;MAX;INIT)")
    
    capteurs = []
    valeurs = {}
    plages = {}
    capteur_counts = {}
    
    for i in range(0, len(data_parts), 4):
        capteur_type = data_parts[i]
        min_val = float(data_parts[i+1]) if data_parts[i+1] else None
        max_val = float(data_parts[i+2]) if data_parts[i+2] else None
        init_val = float(data_parts[i+3]) if data_parts[i+3] else None
        
        capteur_counts[capteur_type] = capteur_counts.get(capteur_type, 0) + 1
        index = capteur_counts[capteur_type]
        capteur_id = f"{capteur_type}{index}"
        
        capteurs.append(capteur_type)
        
        if init_val is not None:
            valeurs[capteur_id] = init_val
        
        if min_val is not None or max_val is not None:
            plages[capteur_id] = {}
            if min_val is not None:
                plages[capteur_id]["min"] = min_val
            if max_val is not None:
                plages[capteur_id]["max"] = max_val
    
    return {
        "box_id": box_id,
        "type": "sensors",
        "capteurs": capteurs,
        "valeurs": valeurs,
        "plages": plages
    }


def parser_outputs(box_id, data_parts):
    """Parse la configuration des relais"""
    if len(data_parts) % 2 != 0:
        raise ValueError("Format relais invalide (doit être RL;ÉTAT)")
    
    etats_relais = {}
    
    for i in range(0, len(data_parts), 2):
        relais_id = data_parts[i]
        etat = int(data_parts[i+1])
        
        if relais_id.startswith('RL'):
            numero = relais_id[2:]
            etats_relais[numero] = etat
    
    nb_relais = len(etats_relais)
    
    return {
        "box_id": box_id,
        "type": "outputs",
        "nb_relais": nb_relais,
        "etats_relais": etats_relais
    }


def parser_counters(box_id, data_parts):
    """Parse la configuration des compteurs"""
    if len(data_parts) % 2 != 0:
        raise ValueError("Format compteurs invalide (doit être TYPE;VALEUR)")
    
    compteurs = {}
    
    for i in range(0, len(data_parts), 2):
        compteur_type = data_parts[i]
        valeur = float(data_parts[i+1])
        compteurs[compteur_type] = valeur
    
    return {
        "box_id": box_id,
        "type": "counters",
        "compteurs": compteurs
    }


def parser_all(box_id, data_parts):
    """Parse une configuration complète"""
    return {
        "box_id": box_id,
        "type": "all",
        "data": data_parts
    }


def appliquer_configuration(config, box_manager):
    """
    Applique une configuration à une box via le box_manager.
    VERSION CORRIGÉE : Met à jour MongoDB pour tous les types
    
    Args:
        config (dict): Configuration parsée
        box_manager: Instance du BoxManager
    
    Returns:
        tuple: (success, message)
    """
    # Import MongoDB ici pour éviter les dépendances circulaires
    try:
        from mongo.mongo_utils import mongo_manager
    except ImportError:
        mongo_manager = None
    
    box_id = config["box_id"]
    config_type = config["type"]
    
    if config_type == "sensors":
        # Vérifier si la box existe déjà
        box = box_manager.get_box(box_id)
        if box:
            return False, f"Erreur: Les capteurs de {box_id} sont déjà définis. Impossible de modifier."
        
        # Créer la box avec les capteurs
        box_config = {
            "capteurs": config["capteurs"],
            "valeurs": config["valeurs"]
        }
        
        if "plages" in config and config["plages"]:
            box_config["plages"] = config["plages"]
        
        success, message = box_manager.create_box(box_id, box_config)
        return success, message
    
    elif config_type == "outputs":
        box = box_manager.get_box(box_id)
        
        if box:
            # ✅ Box existe : Mettre à jour les relais
            for relais_num, etat in config["etats_relais"].items():
                relais_id = f"RL{relais_num}"
                box.set_relais_etat(relais_id, etat)
            
            # ✅ CORRECTION : Mettre à jour MongoDB
            if mongo_manager and mongo_manager.is_connected():
                # Calculer le nombre total de relais
                total_relais = max(int(num) for num in config["etats_relais"].keys())
                
                # Mettre à jour nb_relais dans MongoDB
                mongo_manager.boxes_collection.update_one(
                    {"_id": box_id},
                    {"$set": {"nb_relais": total_relais}}
                )
                
                print(f"✅ MongoDB mis à jour: {box_id} - {total_relais} relais")
            
            return True, f"Relais de {box_id} mis à jour"
        else:
            # ✅ Box n'existe pas : La créer avec les relais
            box_config = {
                "nb_relais": config["nb_relais"],
                "etats_relais": config["etats_relais"]
            }
            return box_manager.create_box(box_id, box_config)
    
    elif config_type == "counters":
        box = box_manager.get_box(box_id)
        
        if box:
            # ✅ Box existe : Mettre à jour les compteurs
            for compteur_id, valeur in config["compteurs"].items():
                box.set_compteur_valeur(compteur_id, valeur)
            
            # ✅ CORRECTION : Mettre à jour MongoDB
            if mongo_manager and mongo_manager.is_connected():
                # Récupérer les compteurs actuels de la box
                box_doc = mongo_manager.boxes_collection.find_one({"_id": box_id})
                
                if box_doc:
                    # Fusionner avec les nouveaux compteurs
                    compteurs_existants = set(box_doc.get("compteurs", []))
                    nouveaux_compteurs = set(config["compteurs"].keys())
                    tous_compteurs = list(compteurs_existants | nouveaux_compteurs)
                    
                    # Mettre à jour dans MongoDB
                    mongo_manager.boxes_collection.update_one(
                        {"_id": box_id},
                        {"$set": {"compteurs": tous_compteurs}}
                    )
                    
                    print(f"✅ MongoDB mis à jour: {box_id} - Compteurs: {tous_compteurs}")
            
            return True, f"Compteurs de {box_id} mis à jour"
        else:
            # ✅ Box n'existe pas : La créer avec les compteurs
            box_config = {
                "compteurs": config["compteurs"]
            }
            return box_manager.create_box(box_id, box_config)
    
    else:
        return False, f"Type de configuration non supporté: {config_type}"


# ==========================================
# EXEMPLES D'UTILISATION
# ==========================================

if __name__ == "__main__":
    print("🧪 Tests du parser de trames 3A")
    print("=" * 60)
    
    # Test 1: Capteurs
    print("\n1️⃣ Test capteurs (S):")
    trame1 = "3A;BOX_001;HT;15;35;25;HM;30;80;50;S"
    print(f"Trame: {trame1}")
    config1 = parser_trame_3A(trame1)
    print(f"Config: {config1}")
    
    # Test 2: Capteurs multiples
    print("\n2️⃣ Test capteurs multiples (2x HT):")
    trame2 = "3A;BOX_002;HT;10;30;20;HT;18;28;22;HM;40;70;55;S"
    print(f"Trame: {trame2}")
    config2 = parser_trame_3A(trame2)
    print(f"Config: {config2}")
    
    # Test 3: Relais
    print("\n3️⃣ Test relais (O):")
    trame3 = "3A;BOX_003;RL1;0;RL2;1;RL3;0;O"
    print(f"Trame: {trame3}")
    config3 = parser_trame_3A(trame3)
    print(f"Config: {config3}")
    
    # Test 4: Compteurs
    print("\n4️⃣ Test compteurs (C):")
    trame4 = "3A;BOX_004;EC;1200;WC;5000;GC;300;C"
    print(f"Trame: {trame4}")
    config4 = parser_trame_3A(trame4)
    print(f"Config: {config4}")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés !")