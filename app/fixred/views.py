from django.db.models import Prefetch
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, permissions

from .models import Fixred, FixredComment, FixredImage
from .serializers import FixredListSerializer


# Fixred 게시글 목록 (픽레드 피드)
@extend_schema(
    summary="픽레드 게시글 목록(피드) 조회",
    description="Fixred 게시글을 최신순으로 조회합니다.",
    # "following 쿼리파라미터를 주면 팔로잉한 사용자의 글만 조회됩니다.",
    # parameters=[
    #     OpenApiParameter(
    #         name="filter",
    #         #description="'all' 또는 'following' 선택",
    #         required=False,
    #         location=OpenApiParameter.QUERY,
    #     ),
    # ],
    responses={
        200: FixredListSerializer(many=True),
        401: OpenApiResponse(
            description="인증 실패 : 로그인 필요",
        ),
    },
    tags=["픽레드 피드"],
)
class FixredListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  # 로그인 사용자만
    serializer_class = FixredListSerializer

    def get_queryset(self):
        user = self.request.user

        # 기본 쿼리셋은 모든 Fixred 게시글
        queryset = Fixred.objects.select_related("user").prefetch_related("fixredimage_set").order_by("-created_at")

        # 쿼리 파라미터 'filter'가 'following'이면 팔로잉한 사용자의 글만 조회
        mode = self.request.query_params.get("filter", "all").strip().lower()
        if mode == "following":
            following_users = user.following.values_list("id", flat=True)
            queryset = queryset.filter(user_id__in=following_users)

        return queryset


# Fixred 게시글 상세
@extend_schema(
    summary="픽레드 게시글 상세 조회",
    description="Fixred 게시글의 상세 정보를 조회합니다.",
    responses={
        200: FixredListSerializer,
        401: OpenApiResponse(description="인증 실패 : 로그인 필요"),
        404: OpenApiResponse(description="게시글을 찾을 수 없음"),
    },
    tags=["픽레드 게시글"],
)
class FixredDetailView(generics.RetrieveAPIView):
    queryset = Fixred.objects.select_related("user").prefetch_related("fixredimage_set", "comments")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredListSerializer
    lookup_field = "pk"

    def get_queryset(self):
        queryset = Fixred.objects.select_related("user").prefetch_related(
            Prefetch("fixredimage_set", queryset=FixredImage.object.all()),
            Prefetch("comments", queryset=FixredComment.objects.select_related("user").order_by("-created_at")),
        )
        return queryset
