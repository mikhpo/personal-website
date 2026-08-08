# syntax=docker/dockerfile:1

# Этап 1: Сборка Node.js для фронтенда React
FROM node:22-bookworm AS node-builder

# Создать каталог для проекта и перейти в него.
WORKDIR /app

# Скопировать конфигурационные файлы и зависимости Node.js
COPY package.json package-lock.json ./

# Скопировать конфигурационные файлы в frontend/ директорию
COPY frontend/webpack.config.js frontend/.babelrc frontend/jest.config.js frontend/jest.setup.js ./frontend/

# Скопировать исходники frontend
COPY frontend/src ./frontend/src

# Установить зависимости Node.js через npm (создаст node_modules в /app)
RUN npm ci && \
    npm cache clean --force

# Сборка React приложения
RUN npm run build

# Этап 2: Приложение Python
FROM python:3.14-trixie

# Обновление и установка общих системных пакетов.
# Версия утилит PostgreSQL должна совпадать с версией кластера.
ENV POSTGRES_VERSION=17

# Аргументы для условной установки SSL сертификата
ARG POSTGRES_SSL_CERT_DOWNLOAD
ARG POSTGRES_SSL_CERT_URL

# Условная установка SSL сертификата для managed-сервисов
RUN if [ "${POSTGRES_SSL_CERT_DOWNLOAD}" = "1" ] && [ -n "${POSTGRES_SSL_CERT_URL}" ]; then \
        echo "Downloading SSL certificate from $POSTGRES_SSL_CERT_URL..."; \
        mkdir -p ~/.postgresql && \
        wget --quiet "$POSTGRES_SSL_CERT_URL" \
             --output-document ~/.postgresql/root.crt && \
        chmod 0655 ~/.postgresql/root.crt && \
        echo "SSL certificate installed"; \
    else \
        echo "Skipping SSL certificate download"; \
    fi

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    cron \
    curl \
    gnupg \
    locales \
    ca-certificates \
    postgresql-client-${POSTGRES_VERSION} \
    rsync && \
    rm -rf /var/lib/apt/lists/*

# Установить Poetry через pip.
RUN pip install --no-cache-dir poetry

# Установить локаль.
RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG=ru_RU.utf8

# Установить клиент MinIO из официального образа.
COPY --from=minio/mc:latest /usr/bin/mc /usr/local/bin/mc

# Создать каталог для проекта и перейти в него.
ENV WORK_DIR=/srv/website
WORKDIR $WORK_DIR

# Установить зависимости Python через Poetry.
COPY pyproject.toml poetry.toml poetry.lock ./
RUN poetry install --no-interaction && \
    poetry cache clear pypi --all

# Скопировать в контейнер основное содержимое проекта.
COPY . .

# Копирование собранного React бандла
COPY --from=node-builder /app/frontend/dist $WORK_DIR/frontend/dist
COPY --from=node-builder /app/frontend/webpack-stats.json $WORK_DIR/frontend/webpack-stats.json

# Установить расписание запуска скриптов в cron.
RUN bash scripts/cronjobs.sh

# Выполнить скрипт, запускающий сервер.
ENV PYTHONPATH=.
ENTRYPOINT ["/bin/bash", "backend/entrypoint.sh"]
