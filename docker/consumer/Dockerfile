# Dockerfile pour le Consumer Kafka du projet BOX
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="box-project"
LABEL description="Consumer Kafka pour simulateur de box IoT"

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY simulateur/ ./simulateur/

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Commande de démarrage
CMD ["python", "simulateur/consumer.py"]