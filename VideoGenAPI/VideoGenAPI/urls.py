"""VideoGenAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from appmain.views import RegistrationView, LoginView, ProjectView, ProjectClipView, UpdateClipsIndexView, ClipSwitchView, ClipView
from apptext.views import CompletionAgentView
from appimage.views import GenerateRandomImageView, GetImageView, GenerateClipImageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('projects/', ProjectView.as_view(), name='projects'), # URL pour créer un projet
    path('project/<int:project_id>/', ProjectView.as_view(), name='project'),
    path('project/clips/<int:project_id>/', ProjectClipView.as_view(), name='clips'),
    path('project/clips/update_index/', UpdateClipsIndexView.as_view(), name='update_clips_index'),
    path('project/clips/switch/<int:clip_id_1>/<int:clip_id_2>/', ClipSwitchView.as_view(), name='switch_clips_index'),
    path('clip/<int:clip_id>/', ClipView.as_view(), name='clip'),
    path('clip/generate/image/<int:clip_id>/', GenerateClipImageView.as_view(), name='generate_clip_image'),
    path('textgen/<int:project_id>/', CompletionAgentView.as_view(), name='textgen'),
    path('image/generate/', GenerateRandomImageView.as_view(), name='generate_image'),
    path('image/<int:image_id>/', GetImageView.as_view(), name='image'),
]
