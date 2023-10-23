import os
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from appmain.models import ImageFile, Clip
from .agentImg import RandomImageGenerator
from appmain.views import ProtectedView
from django.http import HttpResponse


def generateImage(request, name, generator):
    # Générez une image aléatoire avec des valeurs de pixel aléatoires
    generator.generate()

    # Créez le chemin où vous souhaitez sauvegarder l'image dans le répertoire de médias
    media_root = settings.MEDIA_ROOT
    img_name = f'{name}.png'
    random_image_path = os.path.join(media_root, "images", img_name)

    # Vérifiez si le fichier existe déjà
    counter = 0
    while os.path.exists(random_image_path):
        # Si le fichier existe, ajoutez un nombre aléatoire au nom du fichier
        counter += 1
        img_name = f'{name}_{counter}'
        random_image_path = os.path.join(media_root, "images", f'{img_name}.png')

    # Sauvegardez l'image à l'emplacement spécifié
    generator.save(random_image_path)

    # Créez une instance de ImageFile et enregistrez l'image téléchargée
    image_model = ImageFile(image=random_image_path, user=request.user, name=img_name, prompt=generator.prompt)
    image_model.save()

    # Récupérez l'ID de l'image enregistrée
    return image_model

def getImage(request, image_id):
    # Recherchez l'objet ImageFile correspondant à l'ID donné
    image_model = ImageFile.objects.get(id=image_id, user=request.user)

    # Récupérez le chemin du fichier de l'image
    image_path = image_model.image.path

    # Ouvrez le fichier et lisez son contenu en binaire
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    return image_data

class GenerateRandomImageView(ProtectedView):
    def __init__(self):
        # Instanciez RandomImageGenerator et générez une image
        self.generator = RandomImageGenerator(width=1280, height=720)

    def post(self, request):
        try:
            # Récupérez le paramètre 'name' de la requête POST
            name = request.data.get('name')  # Assurez-vous que 'name' est envoyé dans le corps de la requête


            if name is None:
                raise ValueError('Parameter "name" is required')

            image = generateImage(request, name, self.generator)

            # Renvoyez l'ID de l'image dans la réponse JSON
            return Response({'id': image.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while processing the request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetImageView(ProtectedView):
    def get(self, request, image_id):
        try:
            image_data = getImage(request, image_id)

            # Configurez le type de contenu de la réponse HTTP
            response = HttpResponse(image_data, content_type='image/png')  # Vous pouvez ajuster le type de contenu en fonction du format de l'image

            return response
        except ImageFile.DoesNotExist:
            return HttpResponse('Image not found', status=404)
        except Exception as e:
            return HttpResponse('An error occurred while fetching the image', status=500)
        
# Créer une vue qui génère une image qui l'assicie à un clip et qui renvoie l'image
class GenerateClipImageView(ProtectedView):
    def __init__(self):
        # Instanciez RandomImageGenerator et générez une image
        self.generator = RandomImageGenerator(width=1280, height=720)

    def get(self, request, clip_id):
        try:
            # Recherchez le clip par son ID
            clip = Clip.objects.get(id=clip_id)

            # Vérifiez si l'utilisateur a accès au clip
            if clip.project.user != request.user:
                raise ValueError('Error: Wrong user')

            # donner la prompt au générateur
            self.generator.prompt = clip.img_prompt

            # Générez une nouvelle image associée au clip
            image = generateImage(request=request, name=f"image_{clip_id}", generator=self.generator)

            # Associez l'ID de l'image au clip
            clip.image = image
            clip.save()

            # Récupérez les données de l'image générée
            image_data = getImage(request, image.id)

            # Configurez le type de contenu de la réponse HTTP
            return HttpResponse(image_data, content_type='image/png')

        except Clip.DoesNotExist:
            return HttpResponse('Clip not found', status=404)
        except ValueError as e:
            return HttpResponse(str(e), status=403)
        except Exception as e:
            print(e)
            return HttpResponse('An error occurred while processing the request.', status=500)
