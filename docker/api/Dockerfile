FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système si nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source
COPY simulateur/ ./simulateur/
COPY mongo/ ./mongo/

# Variable d'environnement pour Python
ENV PYTHONUNBUFFERED=1

# Exposer le port de l'API
EXPOSE 5000

# Commande de démarrage
CMD ["python", "simulateur/api.py"]