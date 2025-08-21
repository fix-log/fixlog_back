from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Fixletter, Message
from .serializers import FixletterCreateSerializer, FixletterSerializer, MessageSerializer

def chat_test(request):
    return render(request, 'test_chat.html')
def ws_test(request, fixletter_id=None):
    """테스트 페이지: /fixletter/test/<fixletter_id>/"""
    return render(request, "ws_test.html", {"fixletter_id": fixletter_id or ""})

class FixletterCreateView(generics.CreateAPIView):
    """상대 사용자(peer_user_id)와의 픽레터 방을 열거나 기존 방을 반환합니다."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FixletterCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        peer_user_id = serializer.validated_data["peer_id"]

        current_user_id = request.user.id
        fixletter_instance = Fixletter.get_pair(current_user_id, peer_user_id)

        # last_sent_at 비어 있으면 현재 시각으로 초기화
        if not fixletter_instance.last_sent_at:
            fixletter_instance.last_sent_at = timezone.now()
            fixletter_instance.save(update_fields=["last_sent_at"])

        response_payload = {
            "fixletter_id": fixletter_instance.id,
            "created": fixletter_instance.messages.count() == 0,
        }
        return Response(response_payload, status=status.HTTP_200_OK)
    
class FixletterListView(generics.ListAPIView):
    serializer_class = FixletterSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        current_user = self.request.user
        return (
            Fixletter.objects
            .filter(Q(from_user=current_user) | Q(to_user=current_user))
            .select_related("last_message", "from_user", "to_user")
        )

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        current_user = self.request.user
        fixletter_id = self.kwargs["fixletter_id"]
        # 참여자 검증 (404 반환)
        get_object_or_404(
            Fixletter,
            Q(id=fixletter_id) & (Q(from_user=current_user) | Q(to_user=current_user))
        )
        return Message.objects.filter(fixletter_id=fixletter_id).order_by("-sent_at")