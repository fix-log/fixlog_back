from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.accounts.models import User
from app.crew.models import Project
from app.fixred.models import Fixred
from app.workroom.models import Workroom

from .models import SearchHistory
from .serializers import SearchHistorySerializer


@extend_schema(
    summary="검색 기능",
    description="크루, 워크룸, 픽레드, 유저를 통합 검색합니다.",
    parameters=[
        OpenApiParameter(name="q", description="검색어", required=True, type=str),
        OpenApiParameter(name="sort", description="픽레드 정렬 기준: latest | popular", required=False, type=str),
        OpenApiParameter(
            name="category",
            description="검색 카테고리: all | crew | workroom | fixred | user",
            required=False,
            type=str,
        ),
    ],
    responses={
        200: OpenApiResponse(description="검색 결과 반환"),
        400: OpenApiResponse(description="검색어 누락"),
    },
)
# 검색 기능
class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        category = request.query_params.get("category", "all")  # 검색 카테고리 (all, crew, workroom, fixred, user)
        sort = request.query_params.get("sort")  # 픽레드 정렬 기준

        user = request.user

        if not query:
            return Response({"error": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 검색어 저장 on일때만
        if user.search_history:
            SearchHistory.objects.get_or_create(user=user, keyword=query)

        results = {}

        if category in ("crew", "all"):
            crew_results = Project.objects.filter(title__icontains=query)
            results["크루"] = [{"id": c.id, "title": c.title} for c in crew_results]

        if category in ("workroom", "all"):
            workroom_results = Workroom.objects.filter(title__icontains=query)
            results["워크룸"] = [{"id": w.id, "title": w.title} for w in workroom_results]

        if category in ("fixred", "all"):
            fixred_results = Fixred.objects.filter(content__icontains=query)
            if sort == "popular":
                fixred_results = fixred_results.order_by("-like_count")
            elif sort == "latest":
                fixred_results = fixred_results.order_by("-created_at")
            results["픽레드"] = [{"id": f.id, "content": f.content} for f in fixred_results]

        if category in ("user", "all"):
            user_results = User.objects.filter(
                Q(nickname__icontains=query)
                | Q(position__name__icontains=query)
                | Q(language__name__icontains=query)
                | Q(stack__name__icontains=query)
            ).distinct()
            results["프로필"] = [{"id": u.id, "nickname": u.nickname} for u in user_results]

        return Response({"검색어": query, "검색 결과": results}, status=status.HTTP_200_OK)


@extend_schema(
    summary="검색 기록 조회 및 생성",
    description="현재 로그인 유저의 검색 기록을 조회하거나 새 키워드를 등록합니다.",
    request=SearchHistorySerializer,
    responses={200: SearchHistorySerializer(many=True)},
)
# 검색 리스트 생성, 조회
class SearchHistoryView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchHistorySerializer

    def get_queryset(self):
        user = self.request.user
        return SearchHistory.objects.filter(user=user).order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user
        keyword = serializer.validated_data.get("keyword")
        # 중복 검색어 저장 방지
        if not SearchHistory.objects.filter(user=user, keyword=keyword).exists():
            serializer.save(user=user)


@extend_schema(
    summary="검색 기록 전체 삭제",
    description="현재 로그인 유저의 모든 검색 기록을 삭제합니다.",
    responses={200: OpenApiResponse(description="삭제 성공 메시지 반환")},
)
# 검색 기록 삭제
class SearchHistoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        SearchHistory.objects.filter(user=user).delete()
        return Response({"message": "검색 기록이 삭제되었습니다."}, status=status.HTTP_200_OK)
