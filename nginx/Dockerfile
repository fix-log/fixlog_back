# nginx용 Dockerfile
FROM nginx:1.25-alpine

# nginx 설정 파일 복사
COPY ./nginx.conf /etc/nginx/nginx.conf

# 정적 파일 복사 (옵션)
# COPY ./static /usr/share/nginx/html

EXPOSE 80