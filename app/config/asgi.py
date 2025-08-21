import os
from pathlib import Path

from dotenv import load_dotenv
APP_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(APP_DIR.parent / ".env.local")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings.dev")

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from app.fixletter.routing import websocket_urlpatterns
from app.fixletter.ws_auth import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})