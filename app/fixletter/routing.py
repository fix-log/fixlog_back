# app/fixletter/routing.py
from django.urls import re_path
from .consumers_debug import EchoConsumer
from .consumers import FixletterConsumer

websocket_urlpatterns = [
    re_path(r"^ws/ping/$", EchoConsumer.as_asgi()),  # 테스트용
    re_path(r"^ws/fixletter/(?P<fixletter_id>\d+)/$", FixletterConsumer.as_asgi()),
]