# Utilisez une image de base qui inclut Python
FROM python:3.7-slim

# Copiez les fichiers de votre application dans le conteneur
COPY . .

# Installez les dépendances de votre application
RUN pip install -r requirements.txt

# Exposez le port sur lequel votre application Django écoute
EXPOSE 8080

# Commande pour démarrer votre application Django
CMD ["python", "VideoGenAPI/manage.py", "runserver", "0.0.0.0:8080"]

