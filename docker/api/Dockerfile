# Dockerfile pour l'API Flask du projet BOX
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="box-project"
LABEL description="API Flask pour simulateur de box IoT"

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY simulateur/ ./simulateur/

# Exposer le port Flask
EXPOSE 5000

# Variables d'environnement
ENV FLASK_APP=simulateur/api.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Commande de démarrage
CMD ["python", "simulateur/api.py"]