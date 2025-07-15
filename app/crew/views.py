from django.db.models import F
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.crew.models import Project
from app.crew.serializers import ProjectSerializer


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all().prefetch_related(
            "projectposition_set__position", "projectlanguage_set__language", "projectskilltool_set__skill_tool"
        )

        # 제목 검색 기능
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)

        # 모집구분 필터링 (status)
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        # 기술스택 필터링 (skill_tools) - AND 조건
        skill_tools = self.request.query_params.getlist("skill_tools")
        if skill_tools:
            for skill_tool in skill_tools:
                queryset = queryset.filter(projectskilltool__skill_tool__id=skill_tool)

        # 포지션 필터링 (positions) - AND 조건
        positions = self.request.query_params.getlist("positions")
        if positions:
            for position in positions:
                queryset = queryset.filter(projectposition__position__id=position)

        # 언어 필터링 (languages) - AND 조건
        languages = self.request.query_params.getlist("languages")
        if languages:
            for language in languages:
                queryset = queryset.filter(projectlanguage__language__id=language)

        # 정렬 (인기많은것부터 역순, 기본은 최신순)
        ordering = self.request.query_params.get("ordering", "-created_at")
        if ordering == "popular":
            queryset = queryset.order_by("-count", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset.distinct()  # 중복 제거

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailAPIView(generics.RetrieveAPIView):
    queryset = Project.objects.all().prefetch_related(
        "projectposition_set__position", "projectlanguage_set__language", "projectskilltool_set__skill_tool"
    )
    serializer_class = ProjectSerializer
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 조회수 자동 증가 (F() 사용으로 race condition 방지)
        Project.objects.filter(pk=instance.pk).update(count=F("count") + 1)

        # 증가된 조회수로 다시 조회
        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProjectUpdateAPIView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("본인이 생성한 프로젝트만 수정할 수 있습니다.")
        return obj


class ProjectDeleteAPIView(generics.DestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("본인이 생성한 프로젝트만 삭제할 수 있습니다.")
        return obj
