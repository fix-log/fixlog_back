from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from app.chat.consumers import ChatConsumer

# from apps.chat.consumers import ChatConsumer  # 예시: 실제 consumer로 교체 필요

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),  # WebSocket URL 매핑
]
