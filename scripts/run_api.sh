# run_api.sh: migrate → collectstatic → gunicorn 실행 스크립트

set -e  # 에러 발생 시 스크립트 즉시 종료

# Django 설정 모듈 지정
DJANGO_ENV=${DJANGO_ENV:-prod}
export DJANGO_SETTINGS_MODULE=config.settings.$DJANGO_ENV

echo "▶️ DB 마이그레이션 시작..."
poetry run python manage.py makemigrations
poetry run python manage.py migrate --noinput

echo "▶️ 정적 파일 수집 시작..."
poetry run python manage.py collectstatic --noinput

echo "▶️ S3 static 파일 확인..."
poetry run python scripts/verify_static.py

echo "▶️ Gunicorn 프로세스 실행 직전 디버깅 정보:"
if [ "$DJANGO_ENV" = "dev" ]; then
  echo "▶️ 개발 모드로 Gunicorn --reload 실행"
  EXTRA_FILES=$(find /app/app -name "views.py" -type f | awk '{print "--reload-extra-file "$0}' | paste -sd " " -)
  RELOAD="--reload --reload-engine=poll $EXTRA_FILES"
else
  echo "▶️ 배포 모드로 Gunicorn 실행"
  RELOAD=""
fi

exec poetry run gunicorn config.wsgi:application \
     --bind 0.0.0.0:8001 \
     --workers 4 \
     --timeout 60 \
     --log-level debug \
     $RELOAD