from django.db import models
from appmain.models import Project
    
    
class CompletionAgentModel(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    api_token = models.CharField(max_length=64)
    model = models.CharField(max_length=20, default="gpt-3.5-turbo")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=1024)
    n = models.IntegerField(default=1)
    stop = models.TextField(blank=True, null=True)
    presence_penalty = models.FloatField(default=0)
    frequency_penalty = models.FloatField(default=0)
    behavior = models.TextField(blank=True, default="You are a helpful assistant.")
    messages = models.JSONField(blank=True, default=list)

    def __str__(self):
        return f"CompletionAgent for Project {self.project_id}"
