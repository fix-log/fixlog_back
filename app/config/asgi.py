import os

from channels.auth import JWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application


from app.fixletter.routing import websocket_urlpatterns

# settings 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings.base")

# WebSocket 지원을 위한 ASGI 애플리케이션 구성
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)