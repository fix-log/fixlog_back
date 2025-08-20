import datetime
import random

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
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


# Refresh Token을 HttpOnly 쿠키에 저장
def set_refresh_cookie(response, refresh_token):
    expires = timezone.now() + datetime.timedelta(days=30)
    response.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        httponly=True,
        secure=not settings.DEBUG,  # DEBUG=False면 운영 → secure=True
        samesite="Strict",  # CSRF 방지
        expires=expires,
    )
    return response


# 상수
VERIFICATION_TTL = 300  # 5분 (초)
VERIFIED_FLAG_TTL = 300  # 5분 (초)
REQUEST_COOLDOWN = 60  # 60초 재요청 제한
MAX_ATTEMPTS = 5  # 인증번호 최대 시도 횟수


def _verification_key(purpose, email):
    return f"verification:{purpose}:{email}"


def _verified_flag_key(purpose, email):
    return f"verified:{purpose}:{email}"


def _attempts_key(purpose, email):
    return f"attempts:{purpose}:{email}"


def _cooldown_key(purpose, email):
    return f"cooldown:{purpose}:{email}"


# ✉️ 인증번호 요청 (회원가입 & 비밀번호 재설정 공용, 이름 검증 제거)
@api_view(["POST"])
@permission_classes([AllowAny])
def request_verification_code_view(request, purpose):
    email = request.data.get("email")
    if not email:
        return Response({"error": "이메일이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    # password_reset이면 가입 여부 확인
    if purpose == "password_reset":
        if not User.objects.filter(email=email, is_active=True).exists():
            return Response({"error": "해당 이메일로 가입된 사용자가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 재요청 쿨다운 체크 (선택)
    cooldown_k = _cooldown_key(purpose, email)
    if cache.get(cooldown_k):
        return Response(
            {"error": "인증번호를 너무 자주 요청했습니다. 잠시 후 다시 시도해주세요."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    code = f"{random.randint(100000, 999999)}"
    cache.set(_verification_key(purpose, email), code, timeout=VERIFICATION_TTL)
    cache.delete(_attempts_key(purpose, email))  # 코드 재발급 시 시도 횟수 초기화
    cache.set(cooldown_k, True, timeout=REQUEST_COOLDOWN)  # 쿨다운 설정

    subject = "[Fixlog] 이메일 인증번호" if purpose == "signup" else "[Fixlog] 비밀번호 재설정 인증번호"
    send_mail(
        subject=subject,
        message=f"아래 인증번호를 입력해주세요 (유효기간 5분):\n인증번호: {code}",
        from_email="noreply@fixlog.co.kr",
        recipient_list=[email],
    )
    return Response(
        {"message": f"{purpose} 인증번호가 이메일로 전송되었습니다.", "ttl_seconds": VERIFICATION_TTL},
        status=status.HTTP_200_OK,
    )


# ✅ 인증 확인 (공용)
@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_verification_code_view(request, purpose):
    email = request.data.get("email")
    code = request.data.get("code")
    if not email or not code:
        return Response({"error": "이메일과 인증번호가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 시도 횟수 체크 (선택)
    attempts_k = _attempts_key(purpose, email)
    attempts = cache.get(attempts_k) or 0
    if attempts >= MAX_ATTEMPTS:
        return Response(
            {"error": "인증번호 최대 시도 횟수를 초과했습니다. 다시 요청해주세요."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    cached_code = cache.get(_verification_key(purpose, email))
    if cached_code != code:
        cache.set(attempts_k, attempts + 1, timeout=VERIFICATION_TTL)  # 남은 유효시간 동안만 카운트
        remaining = max(0, MAX_ATTEMPTS - (attempts + 1))
        return Response(
            {"error": "인증번호가 일치하지 않습니다.", "remaining_attempts": remaining},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 성공
    cache.set(_verified_flag_key(purpose, email), True, timeout=VERIFIED_FLAG_TTL)
    cache.delete(_verification_key(purpose, email))
    cache.delete(attempts_k)
    return Response(
        {"message": f"{purpose} 인증이 완료되었습니다.", "verified_ttl_seconds": VERIFIED_FLAG_TTL},
        status=status.HTTP_200_OK,
    )


# 🧾 회원가입 (가입 전용: verified:signup:{email} 플래그 확인)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    if not cache.get(_verified_flag_key("signup", email)):
        return Response({"error": "이메일 인증을 먼저 완료해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    user.is_active = True
    user.save()
    cache.delete(_verified_flag_key("signup", email))
    return Response({"message": "회원가입이 완료되었습니다!"}, status=status.HTTP_201_CREATED)


# 🧾 회원가입
@extend_schema(
    summary="회원가입",
    description="이메일 인증이 완료된 사용자만 회원가입이 가능합니다.",
    request=SignupSerializer,
    responses={201: OpenApiResponse(description="회원가입 성공"), 400: OpenApiResponse(description="잘못된 요청")},
    tags=["회원"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        verified = cache.get(f"email_verified:{email}")
        if not verified:
            return Response({"error": "이메일 인증을 먼저 완료해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        user.is_active = True
        user.save()
        cache.delete(f"email_verified:{email}")
        return Response({"message": "회원가입이 완료되었습니다!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔑 커스텀 토큰 직렬화
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["nickname"] = self.user.nickname
        return data


# 🔑 로그인 (Access JSON + Refresh 쿠키)
@extend_schema(
    summary="JWT 로그인",
    description="이메일/비밀번호로 Access Token(JSON)과 Refresh Token(HttpOnly Cookie)을 발급받습니다.",
    request=CustomTokenObtainPairSerializer,
    responses={200: OpenApiResponse(description="로그인 성공"), 401: OpenApiResponse(description="인증 실패")},
    tags=["회원"],
)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        res = Response(
            {
                "access": str(access),  # localStorage 저장용
                "nickname": serializer.user.nickname,
            },
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(res, refresh, secure=False)  # 개발 시 secure=False
        return res


# 🔄 토큰 재발급
@extend_schema(
    summary="Access 토큰 재발급",
    description="쿠키의 Refresh Token을 이용해 새로운 Access Token을 발급받습니다.",
    responses={200: OpenApiResponse(description="재발급 성공"), 401: OpenApiResponse(description="재발급 실패")},
    tags=["회원"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        return Response({"error": "Refresh Token이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        return Response({"access": str(access_token)}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Refresh Token이 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)


# 👤 내 프로필 조회/수정
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
        return Response(serializer.data)
    elif request.method == "PATCH":
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원정보가 수정되었습니다."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "허용되지 않은 요청입니다."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# ❌ 회원 탈퇴
@extend_schema(
    summary="회원 탈퇴",
    description="회원 탈퇴 시 계정을 비활성화 처리합니다.",
    responses={200: OpenApiResponse(description="탈퇴 완료"), 401: OpenApiResponse(description="인증 실패")},
    tags=["회원"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    user = request.user
    user.is_active = False
    user.save()
    return Response({"message": "계정이 비활성화되었습니다."})


# 🚪 로그아웃
@extend_schema(
    summary="로그아웃",
    description="Refresh Token을 블랙리스트 처리하고 쿠키에서 삭제합니다.",
    responses={200: OpenApiResponse(description="로그아웃 완료")},
    tags=["회원"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                # 블랙리스트 처리 실패 시에도 쿠키 삭제는 계속 진행
                pass

        # 응답과 함께 쿠키 삭제
        res = Response({"message": "로그아웃되었습니다."}, status=status.HTTP_200_OK)
        res.delete_cookie("refresh_token")
        return res

    except Exception:
        return Response({"error": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)


# 🔍 다른 사용자 프로필 조회
@extend_schema(
    summary="사용자 프로필 조회",
    description="사용자의 user_id로 공개된 정보를 조회합니다.",
    responses={200: UserSerializer, 404: OpenApiResponse(description="존재하지 않는 사용자")},
    tags=["회원"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_profile_view(request, user_id):
    try:
        user = User.objects.get(pk=user_id, is_active=True)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({"error": "존재하지 않는 사용자입니다."}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="이메일 찾기",
    description="이름과 전화번호를 입력해 가입된 이메일을 반환합니다.",
    request={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "phone_number": {"type": "string"},  # 예: "010-1234-5678"
        },
        "required": ["birth", "phone_number"],
    },
    responses={
        200: OpenApiResponse(description="이메일 반환 성공"),
        404: OpenApiResponse(description="일치하는 정보 없음"),
    },
    tags=["회원"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def find_email_view(request):
    birth = request.data.get("birth")
    phone_number = request.data.get("phone_number")

    try:
        user = User.objects.get(birth=birth, phone_number=phone_number, is_active=True)
        return Response({"email": user.email})
    except User.DoesNotExist:
        return Response({"error": "일치하는 사용자 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 🔑 비밀번호 재설정 (password_reset 전용: verified:password_reset:{email} 확인)
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_view(request):
    email = request.data.get("email")
    new_password = request.data.get("new_password")
    if not email or not new_password:
        return Response({"error": "이메일과 새 비밀번호가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    if not cache.get(_verified_flag_key("password_reset", email)):
        return Response({"error": "이메일 인증을 먼저 완료해주세요."}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return Response({"error": "존재하지 않는 사용자입니다."}, status=status.HTTP_404_NOT_FOUND)

    user.set_password(new_password)
    user.save()
    cache.delete(_verified_flag_key("password_reset", email))
    return Response({"message": "비밀번호가 변경되었습니다."}, status=status.HTTP_200_OK)
