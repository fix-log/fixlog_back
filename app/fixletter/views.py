from rest_framework import generics, permissions
from django.db.models import Q
from .models import Fixletter, Message
from .serializers import FixletterSerializer, MessageSerializer

class FixletterListView(generics.ListAPIView):
    serializer_class = FixletterSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        u = self.request.user
        return Fixletter.objects.filter(Q(from_user=u) | Q(to_user=u)).select_related("last_message","from_user","to_user")

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        u = self.request.user
        fid = self.kwargs["fixletter_id"]
        # 참여자만 조회
        Fixletter.objects.get(Q(id=fid) & (Q(from_user=u) | Q(to_user=u)))
        return Message.objects.filter(fixletter_id=fid).order_by("-sent_at")