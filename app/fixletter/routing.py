from django.urls import re_path
from .consumers import FixletterConsumer

websocket_urlpatterns = [
    re_path(r"ws/fixletter/(?P<fixletter_id>\d+)/$", FixletterConsumer.as_asgi()),
]