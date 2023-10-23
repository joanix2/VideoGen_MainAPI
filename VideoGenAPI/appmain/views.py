from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .serializers import UserSerializer, ProjectSerializer, ProjectDetailViewSerializer, ClipSerializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Project, Clip
from django.shortcuts import get_object_or_404

# Inscription
class RegistrationView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.perform_create(serializer)  # Utilisez la méthode perform_create
            if user:
                payload = api_settings.JWT_PAYLOAD_HANDLER(user)
                token = api_settings.JWT_ENCODE_HANDLER(payload)
                return Response({'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Récupérez le mot de passe à partir des données du sérialiseur
        password = serializer.validated_data.get('password')

        # Créez un nouvel utilisateur, en utilisant set_password pour hacher le mot de passe
        user = User(username=serializer.validated_data.get('username'))
        user.set_password(password)
        user.save()
        return user

    
# Création d'une vue protégée
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(username, password)

        user = authenticate(username=username, password=password)

        if user is not None:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({'token': token})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# Vérification du token
class ProtectedView(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = [IsAuthenticated]


class ProjectView(ProtectedView):
    # Création d'un projet
    def post(self, request):
        # Récupérez les données du projet à partir de la requête POST
        data = request.data

        # Créez un nouveau projet en utilisant les données de la requête
        project = Project(
            user=request.user,  # Associez le projet à l'utilisateur authentifié
            name=data.get('name')
        )
        project.save()

        return Response({'message': 'Le projet a été créé avec succès.'}, status=status.HTTP_201_CREATED)
        
    # Récupérer des informations sur les projets
    def get(self, request, project_id=None):
        if project_id is None:
            projects = Project.objects.filter(user=request.user)
            serializer = ProjectSerializer(projects, many=True)
        else:
            try:
                project = Project.objects.get(id=project_id, user=request.user)
                serializer = ProjectDetailViewSerializer(project)
            except Project.DoesNotExist:
                return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Modifier le titre ou la description d'un projet
    def put(self, request, project_id):
        try:
            # Récupérez le projet à modifier en fonction de son ID
            project = Project.objects.get(id=project_id, user=request.user)

            new_title = request.data.get('new_title')
            new_description = request.data.get('new_description')

            if new_title is not None:
                project.title = new_title

            if new_description is not None:
                project.description = new_description

            project.save()

            return Response({'message': 'Les modifications ont été enregistrées avec succès.'}, status=status.HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)
        
    # supprimer un projet
    def delete(self, request, project_id):
        try:
            # Récupérez le projet à supprimer en fonction de son ID
            project = Project.objects.get(id=project_id, user=request.user)

            # Supprimez le projet
            project.delete()
            return Response({'message': 'Le projet a été supprimé avec succès.'}, status=status.HTTP_204_NO_CONTENT)

        except Project.DoesNotExist:
            return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

# gestion des projets
class ProjectClipView(ProtectedView):
    # Création d'un clip et ajout au projet
    def post(self, request, project_id):
        try:
            # Récupérez les données du clip à partir de la requête POST
            clip_data = request.data
            text = clip_data.get('text')
            index = clip_data.get('index')

            # Récupérez le projet spécifique en fonction de son ID
            project = Project.objects.get(id=project_id, user=request.user)

            # Vérifiez si l'utilisateur actuellement authentifié est le propriétaire du projet
            if project.user != request.user:
                return Response({'message': 'Vous n\'êtes pas autorisé à ajouter un clip à ce projet.'}, status=status.HTTP_403_FORBIDDEN)

            # Créez un nouveau clip en utilisant les données de la requête
            clip = Clip.objects.create(
                index = index,
                project = project,
                text = text if text != None else ""
            )

            # Sauvegardez et le clip
            clip.save()

            return Response({'message': 'Le clip a été ajouté au projet avec succès.'}, status=status.HTTP_201_CREATED)

        except Project.DoesNotExist:
            return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, project_id):
        try:
            # Récupérez le projet spécifique en fonction de son ID
            project = Project.objects.get(id=project_id, user=request.user)

            # Vérifiez si l'utilisateur actuellement authentifié est le propriétaire du projet
            if project.user != request.user:
                return Response({'message': 'Vous n\'êtes pas autorisé à accéder à ces clips.'}, status=status.HTTP_403_FORBIDDEN)

            # Récupérer tous les clips d'un projet triés par ordre croissant de l'index
            clips = Clip.objects.filter(project=project).order_by('index')

            # Sérialisez les clips (vous devrez créer un sérialiseur pour les clips)
            serializer = ClipSerializer(clips, many=True)  # Supposons que vous ayez un sérialiseur nommé ClipSerializer

            print(serializer.data)
            return Response({'clips': serializer.data}, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)
        
    # Supprimer tous les clips associés à un projet
    def delete(self, request, project_id):
        try:
            # Récupérez le projet spécifique en fonction de son ID
            project = Project.objects.get(id=project_id, user=request.user)

            # Vérifiez si l'utilisateur actuellement authentifié est le propriétaire du projet
            if project.user != request.user:
                return Response({'message': 'Vous n\'êtes pas autorisé à supprimer les clips de ce projet.'}, status=status.HTTP_403_FORBIDDEN)

            # Supprimez tous les clips associés à ce projet
            Clip.objects.filter(project=project).delete()

            return Response({'message': 'Tous les clips du projet ont été supprimés avec succès.'}, status=status.HTTP_204_NO_CONTENT)

        except Project.DoesNotExist:
            return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)
        
class ClipView(ProtectedView):
    def put(self, request, clip_id):
        try:
            # Récupérez le clip spécifique en fonction de son ID
            clip = get_object_or_404(Clip, id=clip_id)

            # Vérifiez si l'utilisateur actuellement authentifié a le droit de modifier ce clip.
            if clip.project.user != request.user:
                return Response({'message': 'Vous n\'êtes pas autorisé à modifier ce clip.'}, status=status.HTTP_403_FORBIDDEN)

            # Récupérez les données du formulaire POST contenant le nouveau texte pour le clip.
            new_text = request.data.get('new_text')
            new_index = request.data.get('new_index')

            # Mettez à jour le texte du clip avec les nouvelles données.
            clip.text = new_text if new_text != None else clip.text
            clip.index = new_index if new_index != None else clip.index
            clip.save()

            # Sérialisez le clip mis à jour et renvoyez-le en réponse.
            serializer = ClipSerializer(clip)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Clip.DoesNotExist:
            return Response({'message': 'Le clip spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)
        
    # supprimer un clip
    def delete(self, request, clip_id):
        try:
            # Récupérez le clip à supprimer en fonction de son ID
            clip = Clip.objects.get(id=clip_id)

            # Vérifiez si l'utilisateur actuellement authentifié est le propriétaire du projet
            if clip.project.user == request.user:
                # Supprimez le projet
                clip.delete()
                return Response({'message': 'Le projet a été supprimé avec succès.'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'Vous n\'êtes pas autorisé à supprimer ce projet.'}, status=status.HTTP_403_FORBIDDEN)

        except Project.DoesNotExist:
            return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)
        

class UpdateClipsIndexView(ProtectedView):
    def post(post, request):
        try:
            # Récupérez les données du formulaire POST contenant le nouveau texte pour le clip.
            project_id = request.data.get('project_id')
            new_index = request.data.get('new_index')
            step = request.data.get('step')

            # Récupérez le projet spécifique en fonction de son ID
            project = Project.objects.get(id=project_id, user=request.user)

            # Vérifiez si l'utilisateur actuellement authentifié est le propriétaire du projet
            if project.user != request.user:
                return Response({'message': 'Vous n\'êtes pas autorisé à mettre à jour les index des clips de ce projet.'}, status=403)

            # Récupérez tous les clips associés à ce projet
            clips = Clip.objects.filter(project=project)

            # Mettez à jour l'index de tous les clips ayant un index supérieur ou égal
            for clip in clips:
                if clip.index >= new_index:
                    new_clip_index = clip.index + step
                    clip.index = new_clip_index
                    clip.save()

            return Response({'message': 'Les index des clips ont été mis à jour avec succès.'}, status=200)

        except Project.DoesNotExist:
            return Response({'message': 'Le projet spécifié n\'existe pas.'}, status=404)


class ClipSwitchView(ProtectedView):
    def post(self, request, clip_id_1, clip_id_2):
        try:
            # Récupérez le clip spécifique en fonction de son ID
            clip1 = Clip.objects.get(id=clip_id_1)
            clip2 = Clip.objects.get(id=clip_id_2)

            # Vérifiez si les clips appartient au projet de l'utilisateur actuellement authentifié
            if clip1.project.user != request.user or clip2.project.user != request.user:
                return Response({'message': 'Vous n\'êtes pas autorisé à effectuer cette opération sur ce clip.'}, status=403)

            # Échangez les index des clips
            clip1.index, clip2.index = clip2.index, clip1.index

            # Enregistrez les changements
            clip1.save()
            clip2.save()

            return Response({'message': 'La position du clip a été modifiée avec succès.'}, status=200)

        except Clip.DoesNotExist:
            return Response({'message': 'Le clip spécifié n\'existe pas.'}, status=404)