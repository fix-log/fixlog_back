from rest_framework import serializers

from app.accounts.models import User

from .models import Notification


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname"]


class NotificationSerializer(serializers.ModelSerializer):
    sender = SenderSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "target_id",
            "sender",
            "event",
            "is_read",
            "created_at",
        ]


class NotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "is_read"]
