from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import F
from .models import Project, UserBookmark
from .serializers import ProjectSerializer


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


# 북마크 관련 뷰
@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def bookmark_manage(request, project_id):
    """프로젝트 북마크 추가/삭제"""
    try:
        project = get_object_or_404(Project, id=project_id)

        if request.method == "POST":
            # 북마크 추가
            if UserBookmark.objects.filter(user=request.user, project=project).exists():
                return Response({"message": "북마크 등록 실패"}, status=status.HTTP_400_BAD_REQUEST)

            UserBookmark.objects.create(user=request.user, project=project)
            return Response({"message": "북마크 등록"}, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            # 북마크 삭제
            try:
                bookmark = UserBookmark.objects.get(user=request.user, project=project)
                bookmark.delete()
                return Response({"message": "북마크 등록 취소"}, status=status.HTTP_200_OK)
            except UserBookmark.DoesNotExist:
                return Response({"message": "북마크 등록 취소 실패"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        if request.method == "POST":
            return Response({"message": "북마크 등록 실패"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "북마크 등록 취소 실패"}, status=status.HTTP_400_BAD_REQUEST)
