import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_tokens_for_user(user):
    """사용자를 위한 JWT 토큰 생성"""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def verify_token(token):
    """토큰 검증"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    """토큰에서 사용자 정보 추출"""
    payload = verify_token(token)
    if payload:
        try:
            user = User.objects.get(id=payload["user_id"])
            return user
        except User.DoesNotExist:
            return None
    return None
