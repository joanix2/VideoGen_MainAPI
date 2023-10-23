from django.conf import settings
from .GPTagent import ChatCompletionAgent
from appmain.views import ProtectedView
from rest_framework import status
from rest_framework.response import Response
from .models import CompletionAgentModel
from appmain.models import Project




class CompletionAgentView(ProtectedView):
    def getAgent(self, request, project_id):
        # Recherchez un projet existant par son ID
        project = Project.objects.get(id=project_id)

        # Vérifiez s'il existe déjà un CompletionAgentModel associé à ce projet
        agent, created = CompletionAgentModel.objects.get_or_create(project=project)

        # Récupérez les données de la requête PUT
        if created :
            api_token = request.data.get('api_token',settings.OPENAI_API_KEY)
            model = request.data.get('model', "gpt-3.5-turbo")
            temperature = request.data.get('temperature', 0.7)
            max_tokens = request.data.get('max_tokens', 100)
            n = request.data.get('n', 1)
            stop = request.data.get('stop', None)
            presence_penalty = request.data.get('presence_penalty', 0)
            frequency_penalty = request.data.get('frequency_penalty', 0)
            behavior = request.data.get('behavior', "You are a helpful assistant.")
            messages = request.data.get('messages', list())
        else :
            api_token = request.data.get('api_token',agent.api_token)
            model = request.data.get('model', agent.model)
            temperature = request.data.get('temperature', agent.temperature)
            max_tokens = request.data.get('max_tokens', agent.max_tokens)
            n = request.data.get('n', agent.n)
            stop = request.data.get('stop', agent.stop)
            presence_penalty = request.data.get('presence_penalty', agent.presence_penalty)
            frequency_penalty = request.data.get('frequency_penalty', agent.frequency_penalty)
            behavior = request.data.get('behavior', agent.behavior)
            messages = request.data.get('messages', agent.messages)

        # Saugarder les données dans CompletionAgentModel
        agent.api_token = api_token
        agent.model = model
        agent.temperature = temperature
        agent.max_tokens = max_tokens
        agent.n = n
        agent.stop = stop
        agent.presence_penalty = presence_penalty
        agent.frequency_penalty = frequency_penalty
        agent.behavior = behavior
        agent.messages = messages

        # Enregistrez les modifications dans la base de données
        agent.save()

        # Créez un objet ChatCompletionAgent
        chat_agent = ChatCompletionAgent(
            api_token=api_token,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            behavior=behavior,
            messages=messages
        )

        return chat_agent, agent

    def post(self, request, project_id):
        try:
            # Créez un objet ChatCompletionAgent
            chat_agent, agent = self.getAgent(request, project_id)
            # Faites une prédiction du texte avec le prompt
            prompt = request.data.get('prompt')
            if prompt != None:
                print(prompt)
                generated_text = chat_agent.get_text(prompt)

                # Mettez à jour les messages de CompletionAgentModel
                agent.messages = chat_agent.messages
                agent.save()

                # Retournez le texte généré
                return Response({'generated_text': generated_text}, status=200)
            return Response({'error': "no prompt"}, status=400)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    # Changement des paramètres
    def put(self, request, project_id):
        try:
            chat_agent, agent = self.getAgent(request, project_id)
            return Response({
                'message': 'Paramètres de l\'agent mis à jour avec succès.',
                'agent_params': {
                    "api_token": agent.api_token,
                    "model": agent.model,
                    "temperature": agent.temperature,
                    "max_tokens": agent.max_tokens,
                    "n": agent.n,
                    "stop": agent.stop,
                    "presence_penalty": agent.presence_penalty,
                    "frequency_penalty": agent.frequency_penalty,
                    "best_of": agent.best_of,
                    "behavior": agent.behavior,
                    "messages": agent.messages
                }
            }, status=200)

        except Project.DoesNotExist:
            return Response({'error': 'Le projet spécifié n\'existe pas.'}, status=404)

        except Exception as e:
            return Response({'error': str(e)}, status=400)


    # Supression des messages
    def delete(self, request, project_id):
        try:
            chat_agent, agent = self.getAgent(request, project_id)
            agent.messages = list()
            agent.save()
            return Response({'message': 'Les messages ont été supprimé avec succès.'}, status=200)

        except Project.DoesNotExist:
            return Response({'error': 'Le projet spécifié n\'existe pas.'}, status=404)

        except Exception as e:
            return Response({'error': str(e)}, status=400)
