from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from .models import Fixletter, FixletterBlock, Message

User = get_user_model()


class FixletterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image"]

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
            Q(blocker_id=a, blocked_id=b, is_active=True) | Q(blocker_id=b, blocked_id=a, is_active=True)
        ).exists()
        if blocked:
            raise serializers.ValidationError("차단 상태입니다.")

        return value


class MessageSerializer(serializers.ModelSerializer):
    fixletter_id = serializers.PrimaryKeyRelatedField(read_only=True)
    sender = FixletterUserSerializer(source="send_user", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "fixletter_id", "sender", "content", "sent_at", "is_read"]

class LastMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "content"]

class FixletterSerializer(serializers.ModelSerializer):
    from_user = FixletterUserSerializer(read_only=True)
    to_user= FixletterUserSerializer(read_only=True)
    last_message = LastMessageSerializer(read_only=True)
    class Meta:
        model = Fixletter
        fields = ["id", "from_user", "to_user", "last_message", "last_sent_at"]
