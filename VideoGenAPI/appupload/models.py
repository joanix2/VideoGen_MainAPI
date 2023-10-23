from django.db import models

# Create your models here.
class Channel(models.Model):
    name = models.CharField(max_length=255)  # Le nom de la chaîne
    api_key = models.CharField(max_length=100)  # Le code API de la chaîne YouTube
    
    # Ajoutez d'autres champs si nécessaire, comme une description, une date de création, etc.

    def __str__(self):
        return self.name