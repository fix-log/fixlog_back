#!/bin/sh
# run_api.sh: migrate → collectstatic → gunicorn 실행 스크립트

set -e  # 에러 발생 시 스크립트 즉시 종료

# Django 설정 모듈 지정
export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "▶️ DB 마이그레이션 시작..."
poetry run python manage.py makemigrations
poetry run python manage.py migrate --noinput

echo "▶️ 정적 파일 수집 시작..."
poetry run python manage.py collectstatic --noinput

echo "▶️ Gunicorn 프로세스 실행 직전 디버깅 정보:"
echo "▶️ Gunicorn(WSGI) 서버 시작..."
exec poetry run gunicorn config.wsgi:application \
     --bind 0.0.0.0:8001 \
     --workers 4 \
     --timeout 60 \
     --log-level debug