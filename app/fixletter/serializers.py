from rest_framework import serializers
from django.db.models import Q
from .models import Fixletter, FixletterBlock, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class FixletterCreateSerializer(serializers.Serializer):
    peer_id = serializers.IntegerField(min_value=1)

    def validate_peer_id(self, value):
        request = self.context["request"]
        me_id = request.user.id

        if me_id == value:
            raise serializers.ValidationError("본인과 픽레터 불가")

        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("상대 사용자가 존재하지 않습니다.")

        a, b = sorted([me_id, value])
        blocked = FixletterBlock.objects.filter(
            Q(blocker_id=a, blocked_id=b, is_active=True) |
            Q(blocker_id=b, blocked_id=a, is_active=True)
        ).exists()
        if blocked:
            raise serializers.ValidationError("차단 상태입니다.")

        return value

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "fixletter", "send_user", "content", "sent_at", "is_read"]

class FixletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixletter
        fields = ["id", "from_user", "to_user", "last_message", "last_sent_at"]