from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer


class ProjectCreateAPIView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)