

#!/bin/sh

echo "▶️ Daphne(WebSocket) 서버 시작..."
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application