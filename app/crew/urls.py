from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.ProjectCreateAPIView.as_view(), name='project-create'),
]