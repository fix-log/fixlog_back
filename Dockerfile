# Dockerfile

FROM python:3.12.2-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 의존성 파일 복사 및 Poetry 설치
COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction

# 소스 코드 복사
COPY . /app

# 기본 실행 명령
CMD ["gunicorn", "fixlog.wsgi:application", "--bind", "0.0.0.0:8000"]
# Gunicorn으로 애플리케이션을 배포용으로 실행한다.