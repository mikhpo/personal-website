# syntax=docker/dockerfile:1

# Этап 1: Сборка Node.js для фронтенда React
FROM node:20-bookworm AS node-builder

# Создать каталог для проекта и перейти в него.
WORKDIR /app

# Скопировать конфигурационные файлы и зависимости Node.js
COPY package.json package-lock.json .babelrc webpack.config.js ./

# Скопировать исходники frontend
COPY personal_website/frontend ./personal_website/frontend

# Установить зависимости Node.js через npm.
RUN npm ci && \
    npm cache clean --force

# Сборка React приложения
RUN npm run build

# Этап 2: Приложение Python
FROM debian:bookworm

# Обновление и установка общих системных пакетов.
# Версия утилит PostgreSQL должна совпадать с версией кластера.
ENV POSTGRES_VERSION=15
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    cron \
    curl \
    gnupg \
    locales \
    ca-certificates \
    postgresql-client-${POSTGRES_VERSION} \
    rsync \
    python3 \
    python3-pip \
    pipx \
    wget \
    wkhtmltopdf && \
    rm -rf /var/lib/apt/lists/*

# Установить Poetry через pipx и обновить переменную PATH.
RUN pipx ensurepath && \
    pipx install poetry
ENV PATH="/root/.local/bin:$PATH"

# Установить локаль.
RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG=ru_RU.utf8

# Установить клиент MinIO.
RUN wget --no-check-certificate https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/local/bin/mc

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
COPY --from=node-builder /app/personal_website/frontend/dist /app/personal_website/frontend/dist
COPY --from=node-builder /app/webpack-stats.json /app/webpack-stats.json

# Установить расписание запуска скриптов в cron.
RUN bash personal_website/scripts/cronjobs.sh

# Выполнить скрипт, запускающий сервер.
ENV PYTHONPATH=.
ENTRYPOINT ["/bin/bash", "personal_website/entrypoint.sh"]
