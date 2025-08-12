from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from app.fixred.utils.like import toggle_fixred_like
from app.notifications.utils import send_notification

from .models import Fixred, FixredComment, FixredImage
from .serializers import (
    FixredCommentSerializer,
    FixredCreateSerializer,
    FixredDeleteSerializer,
    FixredDetailSerializer,
    FixredListSerializer,
    FixredUpdateSerializer,
)
from .utils.permission import FOLLOWER, MENTION, PUBLIC, can_view_fixred
from .utils.response import fail, ok


# Fixred 게시글 목록 (픽레드 피드)
@extend_schema(
    summary="픽레드 게시글 목록(피드) 조회",
    description="Fixred 게시글을 최신순으로 조회합니다. following 쿼리파라미터를 주면 팔로잉한 사용자의 글만 조회됩니다.",
    parameters=[
        OpenApiParameter(
            name="filter",
            description="following: 사용자가 팔로잉 한 사용자의 게시물만 조회",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
    ],
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        mode = self.request.query_params.get("filter", "all")
        queryset = Fixred.objects.select_related("user").prefetch_related("fixred_images")

        if mode == "following":
            following_user_ids = user.following.values_list("following_id", flat=True)
            queryset = queryset.filter(Q(user__id__in=following_user_ids) & Q(read_permission__in=[PUBLIC, FOLLOWER]))
        else:
            queryset = queryset.filter(
                Q(read_permission=PUBLIC)
                | Q(read_permission=FOLLOWER, user__followers__follower=user)
                | Q(read_permission=MENTION, mentioned_users=user)
                | Q(user=user)
            ).distinct()

        return queryset.order_by("-created_at")


# Fixred 게시글 상세
@extend_schema(
    summary="픽레드 게시글 상세 조회",
    description="Fixred 게시글의 상세 정보를 조회합니다.",
    responses={
        200: FixredDetailSerializer,
        401: OpenApiResponse(description="인증 실패 : 로그인 필요"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="게시글을 찾을 수 없음"),
    },
    tags=["픽레드 게시글"],
)
class FixredDetailView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Fixred.objects.select_related("user").prefetch_related("fixred_images", "comments")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Fixred.objects.select_related("user").prefetch_related(
            Prefetch("fixred_images", queryset=FixredImage.objects.all()),
            Prefetch("comments", queryset=FixredComment.objects.select_related("user").order_by("-created_at")),
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 권한 체크
        if not can_view_fixred(request.user, instance):
            return fail("게시물에 대한 권한이 없습니다.", code=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance)
        data = dict(serializer.data)
        return Response(data, status=status.HTTP_200_OK)


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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fixred = serializer.save(user=request.user)

        # 멘션 알림
        if fixred.read_permission == MENTION:
            for mention_user in fixred.mentioned_users.exclude(id=fixred.user.id):
                send_notification(
                    user=mention_user,
                    sender=fixred.user,
                    type_="fixred",
                    event="mention",
                    target_id=fixred.id,
                )

        data = dict(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED)


# Fixred 게시글 수정
@extend_schema(
    summary="픽레드 게시글 수정",
    description="Fixred 게시글을 수정합니다.",
    request=FixredUpdateSerializer,
    responses={
        200: OpenApiResponse(description="수정 성공"),
        400: OpenApiResponse(description="유효성 오류"),
        401: OpenApiResponse(description="인증 실패"),
        403: OpenApiResponse(description="수정 권한 없음"),
        404: OpenApiResponse(description="게시글을 찾을 수 없음"),
    },
    tags=["픽레드 게시글"],
)
class FixredUpdateView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredUpdateSerializer

    queryset = Fixred.objects.all()
    lookup_field = "pk"  # URL에서 게시글 ID로 조회

    def perform_update(self, serializer):
        instance = self.get_object()
        if self.request.user != instance.user:
            raise PermissionDenied("게시글 수정 권한이 없습니다.")
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
    permission_classes = [permissions.IsAuthenticated]
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
        return ok("픽레드 삭제 완료", fixred_id=fixred_id)


@extend_schema(
    summary="픽레드 댓글 목록 및 작성",
    description="해당 픽레드 게시글에 달린 댓글들을 조회하거나 새 댓글을 작성합니다.",
    responses={
        200: FixredCommentSerializer(many=True),
        201: OpenApiResponse(description="댓글 작성 성공"),
        400: OpenApiResponse(description="요청 오류"),
        401: OpenApiResponse(description="인증 실패"),
        403: OpenApiResponse(description="게시물 권한 없음"),
    },
    tags=["픽레드 댓글"],
)
# Fixred 댓글
class FixredCommentView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixredCommentSerializer

    def get_queryset(self):
        fixred_id = self.kwargs["fixred_id"]
        fixred = get_object_or_404(Fixred, id=fixred_id)
        # 권한체크
        if not can_view_fixred(self.request.user, fixred):
            raise PermissionDenied("게시물에 대한 권한이 없습니다.")
        return FixredComment.objects.filter(fixred_id=fixred_id).select_related("user").order_by("-created_at")

    def perform_create(self, serializer):
        fixred_id = self.kwargs["fixred_id"]
        fixred = get_object_or_404(Fixred, id=fixred_id)
        # 권한체크
        if not can_view_fixred(self.request.user, fixred):
            raise PermissionDenied("게시물에 대한 권한이 없습니다.")

        serializer.save(user=self.request.user, fixred=fixred)
        # 댓글 알림
        if fixred.user != self.request.user:
            send_notification(
                user=fixred.user,
                sender=self.request.user,
                type_="fixred",
                event="comment",
                target_id=fixred.id,
            )


# Fixred 댓글 삭제
@extend_schema(
    summary="픽레드 댓글 삭제",
    description="픽레드 게시글의 댓글을 삭제합니다.",
    responses={
        200: OpenApiResponse(description="댓글 삭제 성공"),
        401: OpenApiResponse(description="인증 실패"),
        403: OpenApiResponse(description="댓글 삭제 권한 없음"),
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


@extend_schema(
    summary="픽레드 좋아요 토글",
    description="픽레드 게시글에 좋아요를 추가하거나 제거합니다.",
    responses={
        200: OpenApiResponse(description="좋아요 토글 성공"),
        401: OpenApiResponse(description="인증 실패"),
        403: OpenApiResponse(description="게시물 권한 없음"),
        404: OpenApiResponse(description="픽레드를 찾을 수 없음"),
    },
    tags=["픽레드 게시글"],
)
# Fixred 좋아요
class FixredLikeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, fixred_id):
        # 권한 체크
        fixred = get_object_or_404(Fixred, id=fixred_id)
        if not can_view_fixred(request.user, fixred):
            from .utils.response import fail

            return fail("게시물에 대한 권한이 없습니다.", code=status.HTTP_403_FORBIDDEN)

        result = toggle_fixred_like(request.user, fixred_id)
        fixred = result["fixred"]
        message = "좋아요 완료" if result["liked"] else "좋아요 취소"
        return Response(
            {"fixred_id": fixred.id, "liked": result["liked"], "message": message, "like_count": fixred.like_count},
            status=status.HTTP_200_OK,
        )
