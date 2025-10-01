#simulateur de boitiers intelligent

Architecture:
Le projet implémente une architecture distribuée basée sur :
- python : Logique métier et algorithmes de simulation
- Flask  : API REST pour le contrôle des simulations
- Apache Kafka : Communication asynchrone et messagerie
- Mongodb : Persistance des données et logs centralisés
![collection sensorDATA](img/orga.png)

Collections mongo:
Le système utilise 3 collections dans la base iot_project :

boxes : Métadonnées des boîtiers (configuration, statut, timestamps)
sensor_data : Mesures en temps réel (capteurs, relais, compteurs)
logs :sauvegarde des événements système (créations, erreurs, démarrages,deconnesion reseau)

Endpoint API:
- Gestion des boîtiers

GET /api/boxes - Liste tous les boîtiers
POST /api/boxes - Créer un nouveau boîtier
GET /api/boxes/{id} - Détails d'un boîtier
DELETE /api/boxes/{id} - Supprimer un boîtier

- Contrôle des simulations

POST /api/boxes/{id}/simulation/start - Démarrer une simulation
POST /api/boxes/{id}/simulation/stop - Arrêter une simulation

- Informations système

GET /api/status - Statut global du système
GET /api/capteurs/available - Types de capteurs disponibles
GET /api/compteurs/available - Types de compteurs disponibles
![demarrage kafka](img/apii.png)

- exemple dutulisation
démarrer kafka 
![demarrage kafka](img/image.png)

lancer api
![demarrage kafka](img/api.png)
L'API sera accessible sur : "http://localhost:5000"
demarrer le consumemongodb
Crer un boitier virtuel
![test_creation_postman](img/POST.png)
une fois requete est validé le système sauvegarde automatiquement les métadonnées du boîtier dans la collection MongoDB boxes
![collection boxes](img/vuecollectionboxes.png)
Parallèlement, le système enregistre l'événement de création dans la collection logs pour assurer la traçabilité des opérations.
![collections logs](img/vuecollectionlogs.png)
demarrage de simulation:
 le lancement d’une simulation via une requête POST adressée à l’endpoint
/api/boxes/BOX_002/simulation/start avec un intervalle configuré
![demarrage simulation](img/sim1.png)
Simultanément au démarrage de la simulation, l’événement correspondant est enregistré dans la collection log   afin d’assurer la traçabilité de cette opération.
![sauvegarde de debut de simulation ](img/SIM2.png)
Une fois la simulation active, le consommateur MongoDB traite en temps réel les trames reçues depuis Kafka. Il analyse automatiquement les données, et les sauvegarde dans la collection sensor_data
![collection sensorDATA](img/sim3.png)


- exemple de detection de deconenexion kafka:
 Le système fonctionne normalement avec envoi et réception des messages. Ensuite nousprocédons à l’arrêt du service Kafka en utilisant:
![collection sensorDATA](img/arretkafka.png)
le système de logs  enregistre l’évènement de panne dans la collection logs.
![collection sensorDATA](img/arretkafka.png)


