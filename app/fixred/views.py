from rest_framework import generics, permissions

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Fixred
from .serializers import FixredSerializer

# Fixred 게시글 목록 (픽레드 홈)
@extend_schema(
    summary="픽레드 게시글 목록 조회",
    description="Fixred 게시글을 최신순으로 조회합니다."
            "following 쿼리파라미터를 주면 팔로잉한 사용자의 글만 조회됩니다.",
    
    parameters=[
    OpenApiParameter(
        name="filter", 
        description="'all' 또는 'following' 선택", 
        required=False, 
        type=str,
        location=OpenApiParameter.QUERY
    ),],
    responses={
        200: FixredSerializer(many=True),
        400: OpenApiResponse(
            description="잘못된 요청 : 필드 누락 또는 유효성 검사 실패",
            ),
        401: OpenApiResponse(
            description="인증 실패 : 로그인하지 않은 사용자",
        ),
        },
    tags=["픽레드 게시글"],
    
)
class FixredListView(generics.ListAPIView):
    queryset = Fixred.objects.all()
    permission_classes = [permissions.IsAuthenticated]  # 로그인 사용자만

    def get_queryset(self):
        return super().get_queryset()
    
# Fixred 게시글 상세
