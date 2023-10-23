from django.contrib import admin
from .models import Project, Clip, AudioFile, ImageFile

# Register your models here.
admin.site.register(Project)
admin.site.register(Clip)
admin.site.register(AudioFile)
admin.site.register(ImageFile)