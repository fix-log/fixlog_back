from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import FixRed

# FixRed 게시글 목록 (픽레드 홈)
class FixRedListView(generics.ListAPIView):
    queryset = FixRed.objects.all()
    permission_classes = [permissions.IsAuthenticated]  # 로그인 사용자만

    def get_queryset(self):
        return super().get_queryset()