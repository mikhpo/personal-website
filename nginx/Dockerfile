# syntax=docker/dockerfile:1

# Используется официальный образ Nginx.
FROM nginx

# Установить пакеты для Certbot.
RUN apt-get update && \
    apt-get install -y \
    cron \
    certbot \
    python3-certbot-nginx

# Скопировать в контейнер скрипт для установки сертификата.
COPY certbot.sh ./
