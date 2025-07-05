#!/bin/sh
# run_daphne.sh: migrate → collectstatic → daphne 실행 스크립트

set -e  # 에러 발생 시 스크립트 즉시 종료

export DJANGO_SETTINGS_MODULE=config.settings.dev

echo "▶️ 정적 파일 수집 시작..."
poetry run python manage.py collectstatic --noinput

echo "▶️ Daphne(WebSocket) 서버 시작..."
exec poetry run daphne \
     -b 0.0.0.0 -p 8000 \
     config.asgi:application