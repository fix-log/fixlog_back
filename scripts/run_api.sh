

# /bin/sh

echo "▶️ 정적 파일 수집 시작..."
python manage.py collectstatic --noinput

echo "▶️ DB 마이그레이션 시작..."
python manage.py migrate

echo "▶️ Gunicorn 서버 시작..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8001 --workers 4