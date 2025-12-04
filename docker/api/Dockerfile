FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers du simulateur directement dans /app
COPY simulateur/__init__.py ./
COPY simulateur/api.py ./
COPY simulateur/box.py ./
COPY simulateur/config_parser.py ./       
COPY simulateur/box_manager.py ./
COPY simulateur/kafka_utils.py ./

# Créer le dossier mongo et copier les fichiers
RUN mkdir -p mongo
COPY mongo/__init__.py ./mongo/
COPY mongo/consumer_mongo.py ./mongo/
COPY mongo/mongo_utils.py ./mongo/

# Copier tous les fichiers de test
COPY tests/ ./tests

COPY frontend/ ../frontend/


# Variable d'environnement pour Python
ENV PYTHONUNBUFFERED=1

# Exposer le port de l'API
EXPOSE 5000

# Commande de démarrage
CMD ["python", "api.py"]