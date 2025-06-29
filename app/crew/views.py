from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Project
from .serializers import ProjectSerializer


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Project.objects.all()
        
        # 모집구분 필터링 (status)
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # 기술스택 필터링 (skills) - AND 조건
        skills = self.request.query_params.getlist('skills')
        if skills:
            for skill in skills:
                queryset = queryset.filter(skills__contains=skill)
        
        # 포지션 필터링 (position) - AND 조건
        positions = self.request.query_params.getlist('positions')
        if positions:
            for position in positions:
                queryset = queryset.filter(positions__contains=position)
        
        # 정렬 (인기많은것부터 역순, 기본은 최신순)
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'popular':
            queryset = queryset.order_by('-count', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailAPIView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'pk'


class ProjectUpdateAPIView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("본인이 생성한 프로젝트만 수정할 수 있습니다.")
        return obj


class ProjectDeleteAPIView(generics.DestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("본인이 생성한 프로젝트만 삭제할 수 있습니다.")
        return obj