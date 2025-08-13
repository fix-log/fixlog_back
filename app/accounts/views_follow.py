from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app.accounts.models import Follow, User


# 📌 공통 팔로워/팔로잉 수 계산
def _counts(user):
    return {
        "followers_count": user.followers.count(),
        "following_count": user.following.count(),
    }


# 🔄 팔로우/언팔로우 토글
@extend_schema(
    summary="팔로우/언팔로우 토글",
    description="팔로우 상태가 아니면 팔로우, 이미 팔로우 중이면 언팔로우합니다.",
    responses={
        200: OpenApiResponse(description="토글 성공"),
        400: OpenApiResponse(description="자기 자신 팔로우 불가"),
        401: OpenApiResponse(description="인증 필요"),
    },
    tags=["팔로우"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_toggle_view(request, user_id):
    target = get_object_or_404(User, pk=user_id, is_active=True)

    if request.user.id == target.id:
        return Response({"error": "자기 자신은 팔로우할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    follow_obj = Follow.objects.filter(follower=request.user, following=target)

    if follow_obj.exists():
        follow_obj.delete()
        return Response({"message": "언팔로우되었습니다.", "is_following": False, **_counts(target)})
    else:
        Follow.objects.create(follower=request.user, following=target)
        return Response({"message": "팔로우되었습니다.", "is_following": True, **_counts(target)})


# 👥 팔로워 목록 (is_followed_by_me 포함)
@extend_schema(
    summary="팔로워 목록 조회",
    description="해당 사용자를 팔로우하는 사람들의 목록과 내가 팔로우 중인지 여부를 반환합니다.",
    tags=["팔로우"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def followers_list_view(request, user_id):
    target = get_object_or_404(User, pk=user_id, is_active=True)
    followers_qs = target.followers.select_related("follower").all()
    follower_users = [f.follower for f in followers_qs]

    followed_by_me = set()
    if request.user.is_authenticated:
        ids = [u.id for u in follower_users]
        if ids:
            followed_by_me = set(
                Follow.objects.filter(follower=request.user, following_id__in=ids).values_list(
                    "following_id", flat=True
                )
            )

    results = [
        {
            "id": u.id,
            "email": u.email,
            "nickname": u.nickname,
            "profile_image": u.profile_image,
            "is_followed_by_me": u.id in followed_by_me,
        }
        for u in follower_users
    ]

    return Response({"user_id": target.id, "count": len(results), "results": results, **_counts(target)})


# 📜 팔로잉 목록 (is_followed_by_me 포함)
@extend_schema(
    summary="팔로잉 목록 조회",
    description="해당 사용자가 팔로우하고 있는 사람들의 목록과 내가 팔로우 중인지 여부를 반환합니다.",
    tags=["팔로우"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def following_list_view(request, user_id):
    target = get_object_or_404(User, pk=user_id, is_active=True)
    following_qs = target.following.select_related("following").all()
    following_users = [f.following for f in following_qs]

    followed_by_me = set()
    if request.user.is_authenticated:
        ids = [u.id for u in following_users]
        if ids:
            followed_by_me = set(
                Follow.objects.filter(follower=request.user, following_id__in=ids).values_list(
                    "following_id", flat=True
                )
            )

    results = [
        {
            "id": u.id,
            "email": u.email,
            "nickname": u.nickname,
            "profile_image": u.profile_image,
            "is_followed_by_me": u.id in followed_by_me,
        }
        for u in following_users
    ]

    return Response({"user_id": target.id, "count": len(results), "results": results, **_counts(target)})
