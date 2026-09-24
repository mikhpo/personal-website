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

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    curl \
    gnupg \
    gettext \
    locales \
    ca-certificates \
    postgresql-client-${POSTGRES_VERSION} \
    rclone \
    rsync && \
    rm -rf /var/lib/apt/lists/*

# Установить Poetry через pip.
RUN pip install --no-cache-dir poetry

# Установить локаль.
RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG=ru_RU.utf8

# Установить клиент MinIO. Публичные образы MinIO удалены и из Docker Hub, и с
# quay.io, поэтому бинарник скачивается из GitHub releases того же релиза.
# Контрольные суммы зафиксированы: воспроизводимая сборка вместо плавающего
# источника.
ARG TARGETARCH
RUN case "${TARGETARCH}" in \
        amd64) MC_SHA256=01f866e9c5f9b87c2b09116fa5d7c06695b106242d829a8bb32990c00312e891 ;; \
        arm64) MC_SHA256=14c8c9616cfce4636add161304353244e8de383b2e2752c0e9dad01d4c27c12c ;; \
    esac && \
    curl -fsSL -o /tmp/mc "https://github.com/minio/mc/releases/download/RELEASE.2025-08-13T08-35-41Z/mc.linux-${TARGETARCH}.RELEASE.2025-08-13T08-35-41Z" && \
    echo "${MC_SHA256}  /tmp/mc" | sha256sum -c - && \
    install -m 0755 /tmp/mc /usr/local/bin/mc && \
    rm -f /tmp/mc

# Создать каталог для проекта и перейти в него.
ENV WORK_DIR=/srv/website
WORKDIR $WORK_DIR

# Метка, по которой scripts/docker/deploy.sh ограничивает docker image prune
# образами этого проекта, не затрагивая образы других проектов хоста.
LABEL org.opencontainers.image.title="personal-website"

# Установить зависимости Python через Poetry.
COPY pyproject.toml poetry.toml poetry.lock ./
RUN poetry install --no-interaction && \
    poetry cache clear pypi --all

# Скопировать в контейнер основное содержимое проекта.
COPY . .

# Копирование собранного React бандла
COPY --from=node-builder /app/frontend/dist $WORK_DIR/frontend/dist
COPY --from=node-builder /app/frontend/webpack-stats.json $WORK_DIR/frontend/webpack-stats.json

# Компиляция каталогов переводов проекта (backend/locale).
RUN cd backend && poetry run python manage.py compilemessages

# Выполнить скрипт, запускающий сервер.
ENV PYTHONPATH=.
ENTRYPOINT ["/bin/bash", "backend/entrypoint.sh"]
