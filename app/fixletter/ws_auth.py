from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

def _get_header(headers, key: bytes):
    for k, v in headers:
        if k.lower() == key:
            return v.decode()
    return None

def _parse_cookies(cookie_header: str) -> dict:
    pairs = [c.strip() for c in (cookie_header or "").split(";") if "=" in c]
    out = {}
    for p in pairs:
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 토큰: query → Authorization → Cookie → subprotocols
        token = None
        query = parse_qs(scope.get("query_string", b"").decode())
        token = (query.get("token") or [None])[0]

        headers = scope.get("headers", [])

        if not token:
            auth = _get_header(headers, b"authorization")
            if auth and auth.lower().startswith("bearer "):
                token = auth.split(" ", 1)[1].strip()

        if not token:
            cookie = _get_header(headers, b"cookie") or ""
            token = _parse_cookies(cookie).get("access")

        if not token:
            sub = scope.get("subprotocols") or []
            if len(sub) >= 2 and (sub[0] or "").lower() == "bearer":
                token = sub[1]

        user = AnonymousUser()
        if token:
            try:
                at = AccessToken(token)
                user_id = at.get("user_id")
                # Django 5 async ORM
                user = await User.objects.aget(pk=user_id)
            except Exception:
                user = AnonymousUser()

        scope["user"] = user
        return await self.app(scope, receive, send)