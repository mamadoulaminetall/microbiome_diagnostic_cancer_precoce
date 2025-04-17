# Utilise une image officielle de Python
FROM python:3.10-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code
COPY . .

# Définir le port d'écoute pour Streamlit
EXPOSE 8501

# Commande de démarrage de l'app
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.enableCORS=false"]
