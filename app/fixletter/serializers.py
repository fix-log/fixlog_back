from rest_framework import serializers
from .models import Fixletter, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "fixletter", "send_user", "content", "sent_at", "is_read"]

class FixletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixletter
        fields = ["id", "from_user", "to_user", "last_message", "last_sent_at"]