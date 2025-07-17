import random
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.accounts.serializer import SignupSerializer, UserSerializer
from app.accounts.models import User

# 회원가입 View
@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False
        user.save()

        # 6자리 인증번호 생성
        code = str(random.randint(100000, 999999))

        # Redis에 저장 (5분 유지)
        cache.set(f"email_verification:{user.email}", code, timeout=300)

        # 인증번호 이메일 발송
        send_mail(
            subject="[Fixlog] 이메일 인증번호",
            message=f"아래 인증번호를 회원가입 화면에 입력해주세요:\n인증번호: {code}",
            from_email="noreply@fixlog.com",
            recipient_list=[user.email],
        )

        return Response({"message": "회원가입 완료! 이메일로 인증번호를 확인해주세요."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 인증번호 확인 View
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

# 🔑 JWT 로그인 View
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["nickname"] = self.user.nickname
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 유저 정보(내정보) 조회
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile_view(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 유저 정보(타인정보) 조회
@api_view(["GET"])
@permission_classes([AllowAny])  # 공개 조회 가능하게
def get_user_profile_view(request, user_id):
    try:
        user = User.objects.get(pk=user_id, is_active=True)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "존재하지 않는 사용자입니다."}, status=status.HTTP_404_NOT_FOUND)

# 회원 정보 수정
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "회원정보가 수정되었습니다."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 회원 탈퇴 (is_activate = False 처리)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    user = request.user
    user.is_active = False
    user.save()
    return Response({"message": "계정이 비활성화되었습니다."}, status=status.HTTP_200_OK)

# 로그아웃 (토큰 블랙리스트 처리)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()  # 블랙리스트에 추가
        return Response({"message": "로그아웃되었습니다."})
    except Exception:
        return Response({"error": "잘못된 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
