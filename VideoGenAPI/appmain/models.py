from django.db import models
from django.contrib.auth.models import User  # Importez le modèle User de Django

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Clé étrangère vers le modèle User
    name = models.CharField(max_length=100)  # Nom du projet
    title = models.CharField(max_length=100, blank=True)  # Titre de la vidéo
    description = models.TextField(max_length=5000, blank=True)  # Description du projet
    render = models.FileField(upload_to='final_videos/', blank=True)  # Vidéo de rendu final (stockée sur le disque)
    sent = models.BooleanField(default=False)  # Booléen indiquant si la vidéo a été envoyée
    
    # Ajoutez d'autres champs si nécessaire, comme une date de création, etc.

    def __str__(self):
        return self.name
    
class AudioFile(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    text = models.CharField(max_length=255)
    audio = models.FileField(upload_to='audio/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Clé étrangère vers le modèle User

    def __str__(self):
        if self.name == None:
            return f"Audio {self.id}"
        else:
            return self.name
    
class ImageFile(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    # Ajoutez d'autres champs si nécessaire
    prompt = models.CharField(max_length=255, blank=True)
    # Champ pour stocker l'image
    image = models.ImageField(upload_to='images/')  # 'images/' est le répertoire où seront stockées les images
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Clé étrangère vers le modèle User

    def __str__(self):
        if self.name == None:
            return f"Image {self.id}"
        else:
            return self.name
    
class VideoClipFile(models.Model):
    audio = models.FileField(upload_to='audio/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Clé étrangère vers le modèle User

    def __str__(self):
        return f"Video Clip {self.id}"

# Create your models here.
class Clip(models.Model):
    # Champ pour l'index
    index = models.IntegerField()

    # Champ pour le projet
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Champ pour le texte
    text = models.TextField()

    # Champ pour la description de l'image
    img_prompt = models.TextField(default="")
    
    # Champ pour l'audio
    audio = models.ForeignKey(AudioFile, blank=True, null=True, on_delete=models.SET_NULL)
    
    # Champ pour l'image
    image = models.ForeignKey(ImageFile, blank=True, null=True, on_delete=models.SET_NULL)
    
    # Champ pour la vidéo
    video = models.ForeignKey(VideoClipFile, blank=True, null=True, on_delete=models.SET_NULL)
    
    # Ajoutez d'autres champs si nécessaire, comme un titre, une date de création, etc.

    def __str__(self):
        return f"Clip {self.id}"
    
