from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from app.accounts.models import User

from .models import Fixred, FixredComment, FixredImage
from .serializers import (
    FixredCommentSerializer,
    FixredCreateSerializer,
    FixredDeleteSerializer,
    FixredDetailSerializer,
    FixredListSerializer,
    FixredUpdateSerializer,
)


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
        200: FixredDetailSerializer(many=True),
        401: OpenApiResponse(
            description="인증 실패 : 로그인 필요",
        ),
    },
    tags=["픽레드 피드"],
)
class FixredListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredListSerializer

    def get_queryset(self):
        user = self.request.user
        # 기본 쿼리셋은 모든 Fixred 게시글
        queryset = (
            Fixred.objects.select_related("user")
            .prefetch_related("fixredimage_set")
            .filter(read_permission="all")
            .order_by("-created_at")
        )

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
        200: FixredDetailSerializer,
        401: OpenApiResponse(description="인증 실패 : 로그인 필요"),
        404: OpenApiResponse(description="게시글을 찾을 수 없음"),
    },
    tags=["픽레드 게시글"],
)
class FixredDetailView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Fixred.objects.select_related("user").prefetch_related("fixredimage_set", "comments")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Fixred.objects.select_related("user").prefetch_related(
            Prefetch("fixredimage_set", queryset=FixredImage.objects.all()),
            Prefetch("comments", queryset=FixredComment.objects.select_related("user").order_by("-created_at")),
        )


# Fixred 게시글 추가
@extend_schema(
    summary="픽레드 게시글 작성",
    description="Fixred 게시글을 작성합니다.",
    request=FixredCreateSerializer,
    responses={
        201: OpenApiResponse(description="생성 성공"),
        400: OpenApiResponse(description="유효성 오류"),
        401: OpenApiResponse(description="인증 실패"),
    },
    tags=["픽레드 게시글"],
)
class FixredCreateView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]  # 임시로 인증 없이 사용
    serializer_class = FixredCreateSerializer

    def perform_create(self, serializer):
        # serializer.save(user=self.request.user)
        test_user = User.objects.all()[1]  # 테스트 유저에게 소속시킴 (임시)
        serializer.save(user=test_user)


# Fixred 게시글 수정
@extend_schema(
    summary="픽레드 게시글 수정",
    description="Fixred 게시글을 수정합니다.",
    request=FixredUpdateSerializer,
    responses={
        200: OpenApiResponse(description="수정 성공"),
        400: OpenApiResponse(description="유효성 오류"),
        401: OpenApiResponse(description="인증 실패"),
        404: OpenApiResponse(description="게시글을 찾을 수 없음"),
    },
    tags=["픽레드 게시글"],
)
class FixredUpdateView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # 인증 필수
    # permission_classes = [permissions.AllowAny] # 임시로 인증 없이 사용
    serializer_class = FixredUpdateSerializer

    queryset = Fixred.objects.all()
    lookup_field = "pk"  # URL에서 게시글 ID로 조회

    def perform_update(self, serializer):
        serializer.save()


# Fixred 게시글 삭제
@extend_schema(
    summary="픽레드 게시글 삭제",
    description="Fixred 게시글을 삭제합니다.",
    responses={
        204: OpenApiResponse(description="삭제 성공"),
        401: OpenApiResponse(description="인증 실패"),
        403: OpenApiResponse(description="삭제 권한 없음"),
        404: OpenApiResponse(description="게시글을 찾을 수 없음"),
    },
    tags=["픽레드 게시글"],
)
class FixredDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # 인증 필수
    # permission_classes = [permissions.AllowAny] # 임시로 인증 없이 사용
    serializer_class = FixredDeleteSerializer
    queryset = Fixred.objects.all()
    lookup_field = "pk"

    def perform_destroy(self, instance):
        # 요청한 유저와 작성자가 다르면 삭제 못하게 막기
        if self.request.user != instance.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("게시글 삭제 권한이 없습니다.")
        instance.delete()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        fixred_id = instance.id
        self.perform_destroy(instance)
        return Response({"fixred_id": fixred_id, "message": "픽레드 삭제 완료"}, status=status.HTTP_200_OK)


# Fixred 댓글


@extend_schema(
    summary="픽레드 댓글 목록 및 작성",
    description="해당 픽레드 게시글에 달린 댓글들을 조회하거나 새 댓글을 작성합니다.",
    responses={
        200: FixredCommentSerializer(many=True),
        201: OpenApiResponse(description="댓글 작성 성공"),
        400: OpenApiResponse(description="요청 오류"),
        401: OpenApiResponse(description="인증 실패"),
    },
    tags=["픽레드 댓글"],
)
class FixredCommentView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredCommentSerializer

    def get_queryset(self):
        fixred_id = self.kwargs["fixred_id"]
        return FixredComment.objects.filter(fixred_id=fixred_id).select_related("user").order_by("-created_at")

    def perform_create(self, serializer):
        fixred_id = self.kwargs["fixred_id"]
        fixred = get_object_or_404(Fixred, id=fixred_id)
        serializer.save(user=self.request.user, fixred=fixred)


# Fixred 댓글 삭제
@extend_schema(
    summary="픽레드 댓글 삭제",
    description="픽레드 게시글의 댓글을 삭제합니다.",
    responses={
        200: OpenApiResponse(description="댓글 삭제 성공"),
        401: OpenApiResponse(description="인증 실패"),
        403: OpenApiResponse(description="삭제 권한 없음"),
        404: OpenApiResponse(description="댓글을 찾을 수 없음"),
    },
    tags=["픽레드 댓글"],
)
class FixredCommentDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = FixredComment.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "comment_id"

    def perform_destroy(self, instance):
        if self.request.user != instance.user:
            raise PermissionDenied("댓글 삭제 권한이 없습니다.")
        instance.delete()  # 모델에서 알아서 카운트

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        fixred_id = instance.fixred.id
        comment_id = instance.id
        self.perform_destroy(instance)
        return Response(
            {"fixred_id": fixred_id, "comment_id": comment_id, "message": "댓글 삭제 완료"}, status=status.HTTP_200_OK
        )
