import random

from django.core.cache import cache
from django.core.mail import send_mail
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from app.accounts.models import User
from app.accounts.serializer import SignupSerializer, UserSerializer


# ✅ 회원가입
@extend_schema(
    summary="회원가입",
    description="사용자 정보를 입력받아 회원가입을 진행합니다. 인증번호가 이메일로 전송됩니다.",
    request=SignupSerializer,
    responses={
        201: OpenApiResponse(description="회원가입 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
    },
    tags=["회원"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False
        user.save()
        code = str(random.randint(100000, 999999))
        cache.set(f"email_verification:{user.email}", code, timeout=300)
        send_mail(
            subject="[Fixlog] 이메일 인증번호",
            message=f"아래 인증번호를 회원가입 화면에 입력해주세요:\n인증번호: {code}",
            from_email="noreply@fixlog.com",
            recipient_list=[user.email],
        )
        return Response({"message": "회원가입 완료! 이메일로 인증번호를 확인해주세요."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 이메일 인증번호 확인
@extend_schema(
    summary="이메일 인증번호 확인",
    description="이메일로 받은 6자리 인증번호를 입력하여 계정을 활성화합니다.",
    request={
        "type": "object",
        "properties": {
            "email": {"type": "string"},
            "code": {"type": "string"},
        },
        "required": ["email", "code"],
    },
    responses={
        200: OpenApiResponse(description="이메일 인증 완료"),
        400: OpenApiResponse(description="인증 실패"),
        404: OpenApiResponse(description="사용자 없음"),
    },
    tags=["회원"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_code(request):
    email = request.data.get("email")
    code = request.data.get("code")
    if not email or not code:
        return Response({"error": "이메일과 인증번호가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
    cached_code = cache.get(f"email_verification:{email}")
    if cached_code != code:
        return Response({"error": "인증번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        cache.delete(f"email_verification:{email}")
        return Response({"message": "이메일 인증이 완료되었습니다!"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 🔑 JWT 로그인
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["nickname"] = self.user.nickname
        return data


@extend_schema(
    summary="내 프로필 조회 및 수정",
    description="로그인된 사용자의 정보를 조회하거나 수정합니다.",
    request=UserSerializer,
    responses={
        200: UserSerializer,
        400: OpenApiResponse(description="입력값 오류"),
        401: OpenApiResponse(description="인증 필요"),
    },
    tags=["회원"],
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PATCH":
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원정보가 수정되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "허용되지 않은 요청입니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(
    summary="JWT 로그인",
    description="이메일과 비밀번호를 사용하여 JWT 토큰을 발급합니다.",
    request=CustomTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description="로그인 성공 및 토큰 발급"),
        401: OpenApiResponse(description="인증 실패"),
    },
    tags=["회원"],
)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ❌ 회원 탈퇴
@extend_schema(
    summary="회원 탈퇴",
    description="회원 탈퇴 시 계정을 비활성화 처리합니다. 복구 불가.",
    responses={
        200: OpenApiResponse(description="탈퇴 완료"),
        401: OpenApiResponse(description="인증 실패"),
    },
    tags=["회원"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    user = request.user
    user.is_active = False
    user.save()
    return Response({"message": "계정이 비활성화되었습니다."}, status=status.HTTP_200_OK)


# 🔓 로그아웃
@extend_schema(
    summary="로그아웃",
    description="리프레시 토큰을 블랙리스트 처리하여 로그아웃합니다.",
    request={
        "type": "object",
        "properties": {"refresh": {"type": "string"}},
        "required": ["refresh"],
    },
    responses={
        200: OpenApiResponse(description="로그아웃 완료"),
        400: OpenApiResponse(description="토큰 오류"),
        401: OpenApiResponse(description="인증 실패"),
    },
    tags=["회원"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "로그아웃되었습니다."})
    except Exception:
        return Response({"error": "잘못된 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)


# 🔍 다른 사용자 프로필 조회
@extend_schema(
    summary="사용자 프로필 조회",
    description="사용자의 user_id를 통해 공개 정보를 조회합니다.",
    responses={
        200: UserSerializer,
        404: OpenApiResponse(description="존재하지 않는 사용자"),
    },
    tags=["회원"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_profile_view(request, user_id):
    try:
        user = User.objects.get(pk=user_id, is_active=True)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "존재하지 않는 사용자입니다."}, status=status.HTTP_404_NOT_FOUND)
