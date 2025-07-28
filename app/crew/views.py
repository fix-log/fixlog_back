from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.crew.models import Project, Application
from app.crew.serializers import ProjectSerializer, ApplicationSerializer
from app.crew.models import Project, UserBookmark
from app.crew.serializers import ProjectSerializer


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all().prefetch_related(
            "projectposition_set__position", "projectlanguage_set__language", "projectskilltool_set__skill_tool",
            "projectdesign_set__design", "projectcooptool_set__coop_tool"
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

        # 디자인 필터링 (designs) - AND 조건
        designs = self.request.query_params.getlist("designs")
        if designs:
            for design in designs:
                queryset = queryset.filter(projectdesign__design__id=design)

        # 협업도구 필터링 (coop_tools) - AND 조건
        coop_tools = self.request.query_params.getlist("coop_tools")
        if coop_tools:
            for coop_tool in coop_tools:
                queryset = queryset.filter(projectcooptool__coop_tool__id=coop_tool)

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
        "projectposition_set__position", "projectlanguage_set__language", "projectskilltool_set__skill_tool",
        "projectdesign_set__design", "projectcooptool_set__coop_tool"
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


class ProjectApplyAPIView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        user = self.request.user

        try:
            return Application.objects.get(user=user, project=project)
        except Application.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        user = request.user

        # 자신의 프로젝트에는 지원할 수 없음
        if project.user == user:
            return Response({"message": "지원 실패"}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 지원한 프로젝트인지 확인
        if Application.objects.filter(user=user, project=project).exists():
            return Response({"message": "지원 실패"}, status=status.HTTP_400_BAD_REQUEST)

        # 지원 생성
        Application.objects.create(user=user, project=project)
        return Response({"message": "지원 성공"}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        user = request.user

        # 지원 내역 확인
        try:
            application = Application.objects.get(user=user, project=project)
            application.delete()
            return Response({"message": "지원 취소"}, status=status.HTTP_200_OK)
        except Application.DoesNotExist:
            return Response({"message": "지원 취소 성공"}, status=status.HTTP_400_BAD_REQUEST)


class ProjectApplicantsAPIView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)

        # 프로젝트 소유자만 지원자 목록을 볼 수 있음
        if project.user != self.request.user:
            raise PermissionDenied("프로젝트 소유자만 지원자 목록을 볼 수 있습니다.")

        return Application.objects.filter(project=project)


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
