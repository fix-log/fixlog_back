from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.accounts.models import User
from app.crew.models import Project
from app.fixred.models import Fixred

from .models import SearchHistory
from .serializers import SearchHistorySerializer


@extend_schema(
    summary="검색 기능",
    description="크루, 픽레드, 유저를 통합 검색합니다.\n 로그인 사용자만 검색어 저장 가능하며, 검색어는 중복 저장되지 않습니다.",
    parameters=[
        OpenApiParameter(name="q", description="검색어", required=True, type=str),
        OpenApiParameter(
            name="category",
            description="검색 카테고리: all | crew | fixred-lasteat | fixred-popular | user",
            required=False,
            type=str,
        ),
    ],
    responses={
        200: OpenApiResponse(description="검색 결과 반환"),
        400: OpenApiResponse(description="검색어 누락"),
    },
    tags=["검색"],
)
# 검색 기능
class SearchView(APIView):
    permission_classes = []

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        category = request.query_params.get("category", "all")  # (all, crew, fixred-popular, fixred-lastet, user)
        user = request.user

        if not query:
            return Response({"error": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 로그인 사용자만 검색어 저장
        if request.user.is_authenticated and request.user.search_history:
            user = request.user
            SearchHistory.objects.get_or_create(user=user, keyword=query)

        results = {}

        try:
            if category in ("crew", "all"):
                crew_results = Project.objects.filter(title__icontains=query)
                results["크루"] = [{"id": c.id, "title": c.title} for c in crew_results]
        except Exception as e:
            results["크루"] = f"크루 검색 실패: {str(e)}"
        try:
            if category in ("fixred_popular", "all"):
                fixred_pop_results = Fixred.objects.filter(content__icontains=query).order_by("-like_count")
                results["픽레드_인기글"] = [
                    {"id": f.id, "content": f.content, "like_count": f.like_count} for f in fixred_pop_results
                ]
        except Exception as e:
            results["픽레드_인기글"] = f"픽레드 인기글 검색 실패: {str(e)}"

        try:
            if category in ("fixred_latest", "all"):
                fixred_last_results = Fixred.objects.filter(content__icontains=query).order_by("-created_at")
                results["픽레드_최신글"] = [
                    {"id": f.id, "content": f.content, "create_at": f.created_at} for f in fixred_last_results
                ]
        except Exception as e:
            results["픽레드_최신글"] = f"픽레드 최신글 검색 실패: {str(e)}"

        try:
            if category in ("user", "all"):
                user_results = User.objects.filter(
                    Q(nickname__icontains=query)
                    | Q(position__name__icontains=query)
                    | Q(language__name__icontains=query)
                    | Q(stack__name__icontains=query)
                ).distinct()
                results["프로필"] = [{"id": u.id, "nickname": u.nickname} for u in user_results]
        except Exception as e:
            results["프로필"] = f"유저 검색 실패: {str(e)}"

        return Response({"검색어": query, "검색 결과": results}, status=status.HTTP_200_OK)


@extend_schema(
    summary="검색 기록 조회 및 생성",
    description="현재 로그인 유저의 검색 기록을 조회하거나 새 키워드를 등록합니다.",
    request=SearchHistorySerializer,
    responses={200: SearchHistorySerializer(many=True)},
    tags=["검색 기록"],
)
# 검색 리스트 조회
class SearchHistoryView(generics.ListCreateAPIView):
    http_method_names = ["get"]
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
    tags=["검색 기록"],
)
# 검색 기록 삭제
class SearchHistoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        SearchHistory.objects.filter(user=user).delete()
        return Response({"message": "검색 기록이 삭제되었습니다."}, status=status.HTTP_200_OK)


@extend_schema(
    summary="검색어 개별 삭제",
    description="로그인 유저의 검색 기록 중 하나를 삭제합니다.",
    responses={
        200: OpenApiResponse(description="삭제 성공"),
        404: OpenApiResponse(description="해당 검색어 찾을 수 없음"),
    },
    tags=["검색 기록"],
)
# 검색 기록 하나만 삭제
class SearchHistoryDeleteOneView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def delete(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            history = SearchHistory.objects.get(id=pk, user=user)
            history.delete()
            return Response({"message": "검색어 삭제 완료"}, status=status.HTTP_200_OK)
        except SearchHistory.DoesNotExist:
            return Response({"error": "해당 검색어를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
