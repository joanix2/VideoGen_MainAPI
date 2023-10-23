from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Project, Clip

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')  # Ajoutez les champs que vous souhaitez inclure dans l'inscription
        extra_kwargs = {'password': {'write_only': True}}  # Pour que le mot de passe ne soit pas renvoyé en réponse

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'title', 'sent']

class ProjectDetailViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = '__all__'